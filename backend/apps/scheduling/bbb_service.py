"""
Gooprep BigBlueButton Integration
=================================

Wrapper around python-sage-bbb.

The Gooprep application remains responsible for:
    - Lesson/business logic
    - Tutor/student permissions
    - Lesson IDs
    - Password generation
    - Lesson metadata
    - Recording association

BigBlueButton remains responsible for:
    - Live meetings
    - Participants
    - Audio/video
    - Screen sharing
    - Recording
    - Playback
"""

import hashlib
import logging
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.utils import timezone

from sage_bbb.services.client import BigBlueButtonClient

logger = logging.getLogger(__name__)


class BBBService:
    """
    Gooprep wrapper around python-sage-bbb.

    Keeping BBB access behind this class prevents the rest of the
    application from becoming tightly coupled to the BBB library.
    """

    def __init__(self):
        self.base_url = (
            getattr(settings, "BBB_URL", "")
            or getattr(settings, "BBB_API_URL", "")
            or ""
        ).strip()

        self.secret = (
            getattr(settings, "BBB_KEY", "")
            or getattr(settings, "BBB_SECRET", "")
            or ""
        ).strip()

        self.client: Optional[BigBlueButtonClient] = None

        if not self.base_url or not self.secret:
            logger.warning(
                "BigBlueButton is not configured. "
                "Set BBB_URL and BBB_KEY."
            )
            return

        try:
            self.client = BigBlueButtonClient(
                self.base_url,
                self.secret,
            )

            logger.info(
                "BigBlueButton client initialized successfully."
            )

        except Exception as exc:
            logger.exception(
                "Failed to initialize BigBlueButton client: %s",
                exc,
            )
            self.client = None

    # ==============================================================
    # Configuration
    # ==============================================================

    @property
    def configured(self) -> bool:
        """
        Return True when BBB has been configured successfully.
        """
        return bool(
            self.base_url
            and self.secret
            and self.client
        )

    def _require_client(self) -> BigBlueButtonClient:
        """
        Return the configured BBB client.
        """
        if not self.configured:
            raise RuntimeError(
                "BigBlueButton is not configured. "
                "Set BBB_URL and BBB_KEY in Django settings."
            )

        return self.client

    # ==============================================================
    # Generic helpers
    # ==============================================================

    @staticmethod
    def _response_dict(response: Any) -> Dict[str, Any]:
        """
        Convert different possible sage-bbb response formats
        into a dictionary.
        """

        if response is None:
            return {
                "returncode": "FAILED",
                "message": "Empty response from BigBlueButton.",
            }

        if isinstance(response, dict):
            return response

        if hasattr(response, "model_dump"):
            try:
                return response.model_dump()
            except Exception:
                pass

        if hasattr(response, "dict"):
            try:
                return response.dict()
            except Exception:
                pass

        if hasattr(response, "__dict__"):
            try:
                return dict(response.__dict__)
            except Exception:
                pass

        return {
            "returncode": "SUCCESS",
            "data": response,
        }

    @staticmethod
    def _success(response: Any) -> bool:
        """
        Determine whether a BBB response indicates success.
        """

        if response is None:
            return False

        if isinstance(response, bool):
            return response

        data = BBBService._response_dict(response)

        return_code = (
            data.get("returncode")
            or data.get("returnCode")
            or data.get("success")
        )

        if isinstance(return_code, bool):
            return return_code

        if return_code is not None:
            return str(return_code).strip().upper() in {
                "SUCCESS",
                "TRUE",
                "OK",
            }

        # Some client versions return a successful object without
        # explicitly exposing returncode.
        return True

    @staticmethod
    def _failure(message: str) -> Dict[str, Any]:
        """
        Standardized failure response.
        """
        return {
            "returncode": "FAILED",
            "message": message,
        }

    # ==============================================================
    # Meeting helpers
    # ==============================================================

    @staticmethod
    def make_meeting_id(lesson_id: Any) -> str:
        """
        Generate the BBB meeting ID for a lesson.
        """
        return f"lesson-{lesson_id}"

    @staticmethod
    def generate_password(prefix: str, lesson_id: Any) -> str:
        """
        Generate a deterministic lesson-specific BBB password.

        Passwords are never used as the public meeting identifier.
        """
        raw = f"gooprep-{prefix}-{lesson_id}"

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()[:12]

    # ==============================================================
    # Meetings
    # ==============================================================

    def create_meeting(
        self,
        meeting_id: str,
        meeting_name: str,
        attendee_pw: str,
        moderator_pw: str,
        lesson=None,
        duration_minutes: int = 60,
        record: bool = True,
        auto_start_recording: bool = False,
        allow_start_stop_recording: bool = True,
        webcams_only_for_moderator: bool = False,
        mute_on_start: bool = False,
        welcome_message: Optional[str] = None,
        max_participants: int = 10,
        logo_url: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a BBB meeting.
        """

        client = self._require_client()

        if not welcome_message:
            welcome_message = (
                f"<br>Welcome to <b>{meeting_name}</b> on Gooprep!<br>"
                "Please be respectful and ready to learn."
            )

        params = {
            "name": meeting_name,
            "meeting_id": meeting_id,
            "attendee_pw": attendee_pw,
            "moderator_pw": moderator_pw,
            "record": record,
            "autoStartRecording": auto_start_recording,
            "allowStartStopRecording": allow_start_stop_recording,
            "webcamsOnlyForModerator": webcams_only_for_moderator,
            "muteOnStart": mute_on_start,
            "duration": max(1, int(duration_minutes)),
            "maxParticipants": max(1, int(max_participants)),
            "welcome": welcome_message,
        }

        if logo_url:
            params["logo"] = logo_url

        metadata = dict(meta or {})

        if lesson is not None:
            metadata.update(
                {
                    "platform": "gooprep",
                    "lessonId": str(lesson.id),
                    "tutorId": str(lesson.tutor_id),
                    "studentId": str(lesson.student_id),
                    "subjectId": (
                        str(lesson.subject_id)
                        if lesson.subject_id
                        else ""
                    ),
                    "subject": (
                        lesson.subject.name
                        if lesson.subject_id and lesson.subject
                        else ""
                    ),
                }
            )

        # Add BBB metadata.
        for key, value in metadata.items():
            params[f"meta_{key}"] = str(value)

        try:
            response = client.meetings.create_meeting(
                **params
            )

            result = self._response_dict(response)

            logger.info(
                "BBB meeting created. meeting_id=%s returncode=%s",
                meeting_id,
                result.get("returncode"),
            )

            return result

        except TypeError as exc:
            logger.debug(
                "BBB camelCase parameters rejected; "
                "trying snake_case: %s",
                exc,
            )

            fallback_params = {
                "name": meeting_name,
                "meeting_id": meeting_id,
                "attendee_pw": attendee_pw,
                "moderator_pw": moderator_pw,
                "record": record,
                "auto_start_recording": auto_start_recording,
                "allow_start_stop_recording": (
                    allow_start_stop_recording
                ),
                "webcams_only_for_moderator": (
                    webcams_only_for_moderator
                ),
                "mute_on_start": mute_on_start,
                "duration": max(1, int(duration_minutes)),
                "max_participants": max(1, int(max_participants)),
                "welcome": welcome_message,
            }

            if logo_url:
                fallback_params["logo"] = logo_url

            for key, value in metadata.items():
                fallback_params[f"meta_{key}"] = str(value)

            try:
                response = client.meetings.create_meeting(
                    **fallback_params
                )

                result = self._response_dict(response)

                logger.info(
                    "BBB meeting created using snake_case. "
                    "meeting_id=%s",
                    meeting_id,
                )

                return result

            except Exception as retry_exc:
                logger.exception(
                    "BBB meeting creation failed after retry. "
                    "meeting_id=%s error=%s",
                    meeting_id,
                    retry_exc,
                )

                return self._failure(
                    str(retry_exc)
                )

        except Exception as exc:
            logger.exception(
                "BBB meeting creation failed. "
                "meeting_id=%s error=%s",
                meeting_id,
                exc,
            )

            return self._failure(str(exc))

    # ==============================================================
    # Join URL
    # ==============================================================

    def join_url(
        self,
        meeting_id: str,
        full_name: str,
        password: str,
        user_id: Optional[str] = None,
        avatar_url: Optional[str] = None,
        redirect: bool = True,
        userdata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a BBB join URL.
        """

        client = self._require_client()

        params = {
            "meeting_id": meeting_id,
            "full_name": full_name,
            "password": password,
            "redirect": redirect,
        }

        if user_id:
            params["user_id"] = str(user_id)

        if avatar_url:
            params["avatar_url"] = avatar_url

        if userdata:
            params["userdata"] = userdata

        try:
            url = client.meetings.join_meeting(
                **params
            )

            return str(url)

        except TypeError:
            fallback = {
                "meetingID": meeting_id,
                "fullName": full_name,
                "password": password,
                "redirect": redirect,
            }

            if user_id:
                fallback["userID"] = str(user_id)

            if avatar_url:
                fallback["avatarURL"] = avatar_url

            if userdata:
                for key, value in userdata.items():
                    fallback[
                        f"userdata-{key}"
                    ] = str(value)

            return str(
                client.meetings.join_meeting(
                    **fallback
                )
            )

    # ==============================================================
    # Meeting status
    # ==============================================================

    def end_meeting(
        self,
        meeting_id: str,
        moderator_pw: str,
    ) -> Dict[str, Any]:
        """
        End an active BBB meeting.
        """

        client = self._require_client()

        try:
            response = client.meetings.end_meeting(
                meeting_id=meeting_id,
                password=moderator_pw,
            )

            return self._response_dict(response)

        except TypeError:
            try:
                response = client.meetings.end_meeting(
                    meetingID=meeting_id,
                    password=moderator_pw,
                )

                return self._response_dict(response)

            except Exception as exc:
                logger.exception(
                    "BBB end_meeting failed: %s",
                    exc,
                )

                return self._failure(str(exc))

        except Exception as exc:
            logger.exception(
                "BBB end_meeting failed [%s]: %s",
                meeting_id,
                exc,
            )

            return self._failure(str(exc))

    def is_meeting_running(
        self,
        meeting_id: str,
    ) -> bool:
        """
        Check whether a BBB meeting is currently running.
        """

        client = self._require_client()

        try:
            response = client.meetings.is_meeting_running(
                meeting_id=meeting_id
            )

            if isinstance(response, bool):
                return response

            data = self._response_dict(response)

            running = data.get("running")

            if isinstance(running, bool):
                return running

            return str(
                running or "false"
            ).lower() == "true"

        except Exception as exc:
            logger.warning(
                "BBB meeting status check failed [%s]: %s",
                meeting_id,
                exc,
            )

            return False

    def get_meeting_info(
        self,
        meeting_id: str,
    ) -> Dict[str, Any]:
        """
        Retrieve BBB meeting information.
        """

        client = self._require_client()

        try:
            response = client.meetings.get_meeting_info(
                meeting_id=meeting_id
            )

            return self._response_dict(response)

        except TypeError:
            try:
                response = client.meetings.get_meeting_info(
                    meetingID=meeting_id
                )

                return self._response_dict(response)

            except Exception as exc:
                logger.exception(
                    "BBB get_meeting_info failed [%s]: %s",
                    meeting_id,
                    exc,
                )

                return self._failure(str(exc))

        except Exception as exc:
            logger.exception(
                "BBB get_meeting_info failed [%s]: %s",
                meeting_id,
                exc,
            )

            return self._failure(str(exc))

    def get_meetings(self) -> Dict[str, Any]:
        """
        Retrieve currently running BBB meetings.
        """

        client = self._require_client()

        try:
            response = client.meetings.get_meetings()

            return self._response_dict(response)

        except Exception as exc:
            logger.exception(
                "BBB get_meetings failed: %s",
                exc,
            )

            return self._failure(str(exc))

    # ==============================================================
    # Recordings
    # ==============================================================

    def get_recordings(
        self,
        meeting_id: Optional[str] = None,
        record_id: Optional[str] = None,
        states: str = "published,unpublished",
        offset: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Retrieve BBB recordings.
        """

        client = self._require_client()

        # sage_bbb accepts meeting_id and metadata. BBB's XML API uses
        # state and recordID; do not pass legacy wrapper-only arguments.
        metadata = {}
        if states:
            metadata["state"] = states.split(",")[0]
        if record_id:
            metadata["recordID"] = record_id

        try:
            if not meeting_id:
                # BBB permits an all-recordings request without meetingID.
                # The installed sage_bbb convenience method always adds it.
                raw_response = client.send_request("getRecordings", metadata)
                return self._response_dict(
                    client.parse_response(raw_response.content)
                )

            response = client.recordings.get_recordings(
                meeting_id=meeting_id,
                metadata=metadata,
            )
            return self._response_dict(response)

        except TypeError:
            # Compatibility with older clients that accept only meeting_id.
            try:
                response = client.recordings.get_recordings(
                    meeting_id=meeting_id or "",
                )
                return self._response_dict(response)

            except AttributeError:
                try:
                    response = client.get_recordings(
                        meeting_id=meeting_id or "",
                    )
                    return self._response_dict(response)

                except Exception as exc:
                    logger.exception(
                        "BBB get_recordings failed: %s",
                        exc,
                    )

                    return self._failure(str(exc))

        except Exception as exc:
            logger.exception(
                "BBB get_recordings failed: %s",
                exc,
            )

            return self._failure(str(exc))

    def publish_recording(
        self,
        record_id: str,
        publish: bool = True,
    ) -> Dict[str, Any]:
        """
        Publish or unpublish a BBB recording.
        """

        client = self._require_client()

        try:
            response = client.recordings.publish_recording(
                record_id=record_id,
                publish=publish,
            )

            return self._response_dict(response)

        except AttributeError:
            try:
                response = client.publish_recording(
                    record_id=record_id,
                    publish=publish,
                )

                return self._response_dict(response)

            except Exception as exc:
                logger.exception(
                    "BBB publish_recording failed [%s]: %s",
                    record_id,
                    exc,
                )

                return self._failure(str(exc))

        except Exception as exc:
            logger.exception(
                "BBB publish_recording failed [%s]: %s",
                record_id,
                exc,
            )

            return self._failure(str(exc))

    def delete_recording(
        self,
        record_id: str,
    ) -> Dict[str, Any]:
        """
        Delete a BBB recording.
        """

        client = self._require_client()

        try:
            response = client.recordings.delete_recording(
                record_id=record_id
            )

            return self._response_dict(response)

        except AttributeError:
            try:
                response = client.delete_recording(
                    record_id=record_id
                )

                return self._response_dict(response)

            except Exception as exc:
                logger.exception(
                    "BBB delete_recording failed [%s]: %s",
                    record_id,
                    exc,
                )

                return self._failure(str(exc))

        except Exception as exc:
            logger.exception(
                "BBB delete_recording failed [%s]: %s",
                record_id,
                exc,
            )

            return self._failure(str(exc))

    def update_recording(
        self,
        record_id: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update BBB recording metadata.
        """

        client = self._require_client()

        try:
            response = client.recordings.update_recording(
                record_id=record_id,
                metadata=metadata,
            )

            return self._response_dict(response)

        except AttributeError:
            try:
                response = client.update_recording(
                    record_id=record_id,
                    metadata=metadata,
                )

                return self._response_dict(response)

            except Exception as exc:
                logger.exception(
                    "BBB update_recording failed [%s]: %s",
                    record_id,
                    exc,
                )

                return self._failure(str(exc))

        except Exception as exc:
            logger.exception(
                "BBB update_recording failed [%s]: %s",
                record_id,
                exc,
            )

            return self._failure(str(exc))

    # Backwards-compatible alias.
    update_recordings = update_recording

    # ==============================================================
    # Health
    # ==============================================================

    def get_api_version(self) -> Dict[str, Any]:
        """
        Check BBB API connectivity.
        """

        client = self._require_client()

        try:
            response = client.check_connection()

            return self._response_dict(response)

        except Exception as exc:
            logger.exception(
                "BBB connection check failed: %s",
                exc,
            )

            return self._failure(str(exc))

    def server_healthy(self) -> bool:
        """
        Return True if the BBB server is responding successfully.
        """

        if not self.configured:
            return False

        try:
            response = self.get_api_version()

            return self._success(response)

        except Exception as exc:
            logger.warning(
                "BBB health check failed: %s",
                exc,
            )

            return False

    # ==============================================================
    # Gooprep lesson integration
    # ==============================================================

    def provision_lesson_room(
        self,
        lesson,
    ) -> Dict[str, Any]:
        """
        Create a BBB room for a Gooprep lesson.

        Returns:
            meeting_id
            attendee password
            moderator password
            tutor join URL
            student join URL
            BBB response
        """

        if not self.configured:
            raise RuntimeError(
                "BigBlueButton is not configured."
            )

        meeting_id = self.make_meeting_id(
            lesson.id
        )

        attendee_pw = self.generate_password(
            "attendee",
            lesson.id,
        )

        moderator_pw = self.generate_password(
            "moderator",
            lesson.id,
        )

        # ----------------------------------------------------------
        # Duration
        # ----------------------------------------------------------

        duration = getattr(
            lesson,
            "duration_minutes",
            None,
        )

        if not duration:
            if (
                lesson.start_time
                and lesson.end_time
            ):
                duration = int(
                    (
                        lesson.end_time
                        - lesson.start_time
                    ).total_seconds()
                    / 60
                )

            else:
                duration = 60

        duration = max(
            1,
            int(duration),
        )

        # ----------------------------------------------------------
        # Subject
        # ----------------------------------------------------------

        subject_name = "Tutoring Session"
        subject_id = None

        if lesson.subject_id:
            subject_id = str(
                lesson.subject_id
            )

            if lesson.subject:
                subject_name = (
                    lesson.subject.name
                    or subject_name
                )

        # ----------------------------------------------------------
        # Tutor
        # ----------------------------------------------------------

        tutor_name = (
            lesson.tutor.get_full_name()
            or getattr(
                lesson.tutor,
                "username",
                None,
            )
            or getattr(
                lesson.tutor,
                "email",
                "Tutor",
            )
        )

        # ----------------------------------------------------------
        # Student
        # ----------------------------------------------------------

        student_name = (
            lesson.student.get_full_name()
            or getattr(
                lesson.student,
                "username",
                None,
            )
            or getattr(
                lesson.student,
                "email",
                "Student",
            )
        )

        # ----------------------------------------------------------
        # Welcome message
        # ----------------------------------------------------------

        welcome = (
            f"Welcome to your "
            f"<b>{subject_name}</b> session "
            f"with <b>{tutor_name}</b>!<br>"
            f"Session duration: "
            f"<b>{duration} minutes</b>.<br>"
            "Please make sure your camera and "
            "microphone are working."
        )

        # ----------------------------------------------------------
        # Logo
        # ----------------------------------------------------------

        logo = getattr(
            settings,
            "BBB_LOGO_URL",
            "",
        )

        # ----------------------------------------------------------
        # Metadata
        # ----------------------------------------------------------

        metadata = {
            "platform": "gooprep",
            "lessonId": str(lesson.id),
            "tutorId": str(lesson.tutor_id),
            "studentId": str(lesson.student_id),
            "subjectId": subject_id or "",
            "subject": subject_name,
            "lessonType": lesson.lesson_type,
            "created": timezone.now().isoformat(),
        }

        # ----------------------------------------------------------
        # Create meeting
        # ----------------------------------------------------------

        response = self.create_meeting(
            meeting_id=meeting_id,
            meeting_name=(
                f"{subject_name} - {tutor_name}"
            ),
            attendee_pw=attendee_pw,
            moderator_pw=moderator_pw,
            lesson=lesson,
            duration_minutes=duration + 10,
            record=getattr(
                lesson,
                "record_session",
                True,
            ),
            auto_start_recording=getattr(
                lesson,
                "record_session",
                False,
            ),
            allow_start_stop_recording=True,
            welcome_message=welcome,
            logo_url=logo,
            meta=metadata,
        )

        if not self._success(response):
            raise RuntimeError(
                response.get(
                    "message",
                    "Failed to create "
                    "BigBlueButton meeting.",
                )
            )

        # ----------------------------------------------------------
        # Tutor URL
        # ----------------------------------------------------------

        tutor_avatar = None

        if hasattr(
            lesson.tutor,
            "get_avatar_url",
        ):
            try:
                tutor_avatar = (
                    lesson.tutor.get_avatar_url()
                )
            except Exception:
                tutor_avatar = None

        tutor_join = self.join_url(
            meeting_id=meeting_id,
            full_name=tutor_name,
            password=moderator_pw,
            user_id=str(
                lesson.tutor_id
            ),
            avatar_url=tutor_avatar,
            userdata={
                "role": "tutor",
                "lesson_id": str(lesson.id),
            },
        )

        # ----------------------------------------------------------
        # Student URL
        # ----------------------------------------------------------

        student_avatar = None

        if hasattr(
            lesson.student,
            "get_avatar_url",
        ):
            try:
                student_avatar = (
                    lesson.student.get_avatar_url()
                )
            except Exception:
                student_avatar = None

        student_join = self.join_url(
            meeting_id=meeting_id,
            full_name=student_name,
            password=attendee_pw,
            user_id=str(
                lesson.student_id
            ),
            avatar_url=student_avatar,
            userdata={
                "role": "student",
                "lesson_id": str(lesson.id),
            },
        )

        return {
            "meeting_id": meeting_id,
            "attendee_pw": attendee_pw,
            "moderator_pw": moderator_pw,
            "join_url_tutor": tutor_join,
            "join_url_student": student_join,
            "bbb_base_url": self.base_url,
            "bbb_response": response,
        }

    # ==============================================================
    # Lesson recordings
    # ==============================================================

    def get_lesson_recordings(
        self,
        lesson,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recordings belonging to a Gooprep lesson.
        """

        meeting_id = self.make_meeting_id(
            lesson.id
        )

        response = self.get_recordings(
            meeting_id=meeting_id,
            states="published,unpublished",
        )

        if not response:
            return []

        recordings_container = response.get(
            "recordings",
            {},
        )

        if not recordings_container:
            return []

        raw_recordings = recordings_container.get(
            "recording",
            [],
        )

        if isinstance(
            raw_recordings,
            dict,
        ):
            raw_recordings = [
                raw_recordings
            ]

        results = []

        for recording in raw_recordings:
            if not isinstance(
                recording,
                dict,
            ):
                continue

            playback = recording.get(
                "playback",
                {},
            )

            if not isinstance(
                playback,
                dict,
            ):
                playback = {}

            formats = playback.get(
                "format",
                [],
            )

            if isinstance(
                formats,
                dict,
            ):
                formats = [formats]

            normalized_formats = []

            for fmt in formats:
                if not isinstance(
                    fmt,
                    dict,
                ):
                    continue

                normalized_formats.append(
                    {
                        "type": fmt.get(
                            "type",
                            "",
                        ),
                        "url": fmt.get(
                            "url",
                            "",
                        ),
                        "length": fmt.get(
                            "length",
                            0,
                        ),
                        "preview": fmt.get(
                            "preview",
                            "",
                        ),
                    }
                )

            first_format = (
                formats[0]
                if formats
                and isinstance(
                    formats[0],
                    dict,
                )
                else {}
            )

            results.append(
                {
                    "record_id": recording.get(
                        "recordID",
                        recording.get(
                            "record_id",
                            "",
                        ),
                    ),
                    "name": recording.get(
                        "name",
                        "",
                    ),
                    "state": recording.get(
                        "state",
                        "",
                    ),
                    "start_time": recording.get(
                        "startTime",
                        recording.get(
                            "start_time",
                            "",
                        ),
                    ),
                    "end_time": recording.get(
                        "endTime",
                        recording.get(
                            "end_time",
                            "",
                        ),
                    ),
                    "duration": first_format.get(
                        "length",
                        0,
                    ),
                    "playback_url": first_format.get(
                        "url",
                        "",
                    ),
                    "thumbnail": first_format.get(
                        "preview",
                        "",
                    ),
                    "formats": normalized_formats,
                }
            )

        return results


    def sync_lesson_recordings(self, lesson) -> List[Dict[str, Any]]:
        """Fetch BBB recordings and persist the normalized lesson data."""
        recordings = self.get_lesson_recordings(lesson)
        playback_url = next(
            (
                item.get("playback_url", "")
                for item in recordings
                if item.get("playback_url")
            ),
            "",
        )
        lesson.bbb_recordings = recordings
        lesson.recording_available = bool(recordings)
        lesson.recording_url = playback_url
        lesson.save(
            update_fields=[
                "bbb_recordings",
                "recording_available",
                "recording_url",
                "updated_at",
            ]
        )
        return recordings


# ==============================================================
# Module-level singleton
# ==============================================================

bbb = BBBService()