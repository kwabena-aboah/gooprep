# """
# BigBlueButton (BBB) API Integration for Gooprep
# Handles room creation, joining, recordings, and webhooks
# """
# import hashlib
# import urllib.parse
# import urllib.request
# import xml.etree.ElementTree as ET
# import logging
# from django.conf import settings
# from django.utils import timezone

# logger = logging.getLogger(__name__)


# class BBBService:
#     """
#     Full BigBlueButton API v2.6 integration.
#     Docs: https://docs.bigbluebutton.org/development/api/
#     """

#     def __init__(self):
#         configured_url = (getattr(settings, 'BBB_URL', '') or '').strip()
#         self.base_url = self._normalize_base_url(configured_url)
#         self.secret = (
#             getattr(settings, 'BBB_KEY', '')
#             or getattr(settings, 'BBB_SECRET', '')
#             or ''
#         ).strip()

#     @staticmethod
#     def _normalize_base_url(url):
#         """Return the BBB API base URL used by all API calls."""
#         if not url:
#             return ''
#         url = url.rstrip('/') + '/'
#         if url.lower().endswith('/bigbluebutton/api/'):
#             return url
#         if '/bigbluebutton/' in url.lower():
#             prefix = url[:url.lower().index('/bigbluebutton/') + len('/bigbluebutton/')]
#             return prefix + 'api/'
#         return url

#     @property
#     def configured(self):
#         return bool(self.base_url and self.secret)

#     # ------------------------------------------------------------------ #
#     #  Core checksum / URL helpers                                         #
#     # ------------------------------------------------------------------ #

#     def _checksum(self, api_call: str, params: str) -> str:
#         """Generate the SHA-1 checksum required by BBB API v2."""
#         raw = api_call + params + self.secret
#         return hashlib.sha1(raw.encode('utf-8')).hexdigest()

#     def _build_url(self, api_call: str, params: dict) -> str:
#         """Build a signed BBB API URL."""
#         query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
#         checksum = self._checksum(api_call, query)
#         return f"{self.base_url}{api_call}?{query}&checksum={checksum}"

#     def _call_api(self, api_call: str, params: dict) -> dict:
#         """Execute a BBB API call and return parsed XML as dict."""
#         if not self.configured:
#             return {'returncode': 'FAILED', 'message': 'BBB is not configured.'}
#         url = self._build_url(api_call, params)
#         try:
#             with urllib.request.urlopen(url, timeout=15) as resp:
#                 xml_data = resp.read()
#             root = ET.fromstring(xml_data)
#             return self._xml_to_dict(root)
#         except Exception as exc:
#             logger.error(f"BBB API error [{api_call}]: {exc}")
#             return {'returncode': 'FAILED', 'message': str(exc)}

#     def _xml_to_dict(self, element) -> dict:
#         """Recursively convert XML element to dictionary."""
#         result = {}
#         for child in element:
#             if len(child):
#                 result[child.tag] = self._xml_to_dict(child)
#             else:
#                 result[child.tag] = child.text
#         return result

#     # ------------------------------------------------------------------ #
#     #  Meeting / Room management                                           #
#     # ------------------------------------------------------------------ #

#     def create_meeting(
#         self,
#         meeting_id: str,
#         meeting_name: str,
#         attendee_pw: str,
#         moderator_pw: str,
#         lesson=None,
#         duration_minutes: int = 60,
#         record: bool = True,
#         auto_start_recording: bool = False,
#         allow_start_stop_recording: bool = True,
#         webcams_only_for_moderator: bool = False,
#         mute_on_start: bool = False,
#         lock_settings: dict = None,
#         meta: dict = None,
#         welcome_message: str = None,
#         max_participants: int = 10,
#         logo_url: str = None,
#     ) -> dict:
#         """
#         Create a BBB meeting room.
#         Returns the full API response including join URLs.
#         """
#         params = {
#             'meetingID': meeting_id,
#             'name': meeting_name,
#             'attendeePW': attendee_pw,
#             'moderatorPW': moderator_pw,
#             'record': 'true' if record else 'false',
#             'autoStartRecording': 'true' if auto_start_recording else 'false',
#             'allowStartStopRecording': 'true' if allow_start_stop_recording else 'false',
#             'webcamsOnlyForModerator': 'true' if webcams_only_for_moderator else 'false',
#             'muteOnStart': 'true' if mute_on_start else 'false',
#             'duration': str(duration_minutes),
#             'maxParticipants': str(max_participants),
#         }

#         if welcome_message:
#             params['welcome'] = welcome_message
#         else:
#             params['welcome'] = (
#                 f"<br>Welcome to <b>{meeting_name}</b> on Gooprep!<br>"
#                 "Please be respectful and ready to learn."
#             )

#         if logo_url:
#             params['logo'] = logo_url

#         # Site-wide logo/branding
#         site_logo = getattr(settings, 'BBB_LOGO_URL', '/static/img/gooprep_logo.png')
#         if site_logo and not logo_url:
#             params['logo'] = site_logo

#         # Metadata for filtering recordings later
#         if meta:
#             for key, val in meta.items():
#                 params[f'meta_{key}'] = str(val)

#         if lesson:
#             params['meta_lessonId'] = str(lesson.id)
#             params['meta_tutorId'] = str(lesson.tutor_id)
#             params['meta_studentId'] = str(lesson.student_id)
#             params['meta_subject'] = lesson.subject.name if lesson.subject else ''

#         # Lock settings (optional)
#         if lock_settings:
#             for k, v in lock_settings.items():
#                 params[k] = 'true' if v else 'false'

#         response = self._call_api('create', params)
#         logger.info(f"BBB create_meeting [{meeting_id}]: {response.get('returncode')}")
#         return response

#     def join_url(
#         self,
#         meeting_id: str,
#         full_name: str,
#         password: str,
#         user_id: str = None,
#         role: str = 'VIEWER',
#         avatar_url: str = None,
#         create_time: str = None,
#         redirect: bool = True,
#         userdata: dict = None,
#     ) -> str:
#         """
#         Generate a signed join URL for a participant.
#         role: 'MODERATOR' for tutors, 'VIEWER' for students
#         """
#         params = {
#             'meetingID': meeting_id,
#             'fullName': full_name,
#             'password': password,
#             'redirect': 'true' if redirect else 'false',
#             'role': role,
#         }
#         if user_id:
#             params['userID'] = str(user_id)
#         if avatar_url:
#             params['avatarURL'] = avatar_url
#         if create_time:
#             params['createTime'] = create_time
#         if userdata:
#             for k, v in userdata.items():
#                 params[f'userdata-{k}'] = str(v)

#         return self._build_url('join', params)

#     def end_meeting(self, meeting_id: str, moderator_pw: str) -> dict:
#         """End an active BBB meeting."""
#         params = {'meetingID': meeting_id, 'password': moderator_pw}
#         return self._call_api('end', params)

#     def is_meeting_running(self, meeting_id: str) -> bool:
#         """Check if a meeting is currently running."""
#         params = {'meetingID': meeting_id}
#         resp = self._call_api('isMeetingRunning', params)
#         return resp.get('running', 'false').lower() == 'true'

#     def get_meeting_info(self, meeting_id: str, moderator_pw: str) -> dict:
#         """Get detailed info about a meeting including attendees."""
#         params = {'meetingID': meeting_id, 'password': moderator_pw}
#         return self._call_api('getMeetingInfo', params)

#     def get_meetings(self) -> dict:
#         """List all active meetings on the BBB server."""
#         return self._call_api('getMeetings', {})

#     # ------------------------------------------------------------------ #
#     #  Recordings                                                          #
#     # ------------------------------------------------------------------ #

#     def get_recordings(
#         self,
#         meeting_id: str = None,
#         record_id: str = None,
#         meta: dict = None,
#         states: str = 'published',
#         offset: int = 0,
#         limit: int = 10,
#     ) -> dict:
#         """Fetch recordings, optionally filtered by meeting or metadata."""
#         params = {'states': states, 'offset': str(offset), 'limit': str(limit)}
#         if meeting_id:
#             params['meetingID'] = meeting_id
#         if record_id:
#             params['recordID'] = record_id
#         if meta:
#             for k, v in meta.items():
#                 params[f'meta_{k}'] = str(v)
#         return self._call_api('getRecordings', params)

#     def publish_recording(self, record_id: str, publish: bool = True) -> dict:
#         """Publish or unpublish a recording."""
#         params = {'recordID': record_id, 'publish': 'true' if publish else 'false'}
#         return self._call_api('publishRecordings', params)

#     def delete_recording(self, record_id: str) -> dict:
#         """Permanently delete a recording."""
#         params = {'recordID': record_id}
#         return self._call_api('deleteRecordings', params)

#     def update_recordings(self, record_id: str, meta: dict) -> dict:
#         """Update recording metadata."""
#         params = {'recordID': record_id}
#         for k, v in meta.items():
#             params[f'meta_{k}'] = str(v)
#         return self._call_api('updateRecordings', params)

#     # ------------------------------------------------------------------ #
#     #  BBB Health / Server                                                 #
#     # ------------------------------------------------------------------ #

#     def get_api_version(self) -> dict:
#         """Check BBB server version and availability."""
#         return self._call_api('', {})

#     def server_healthy(self) -> bool:
#         """Quick health check — returns True if BBB is reachable."""
#         try:
#             resp = self.get_api_version()
#             return resp.get('returncode') == 'SUCCESS'
#         except Exception:
#             return False

#     # ------------------------------------------------------------------ #
#     #  High-level helpers for Gooprep lesson flow                        #
#     # ------------------------------------------------------------------ #

#     def provision_lesson_room(self, lesson) -> dict:
#         """Create a BBB room and signed join URLs for a lesson."""
#         if not self.configured:
#             raise RuntimeError('BigBlueButton is not configured.')

#         logo = getattr(settings, 'BBB_LOGO_URL', '')
#         meeting_id = f'lesson-{lesson.id}'
#         attendee_pw = hashlib.md5(f'att-{lesson.id}'.encode()).hexdigest()[:12]
#         moderator_pw = hashlib.md5(f'mod-{lesson.id}'.encode()).hexdigest()[:12]
#         duration = max(1, int((lesson.end_time - lesson.start_time).total_seconds() / 60))
#         subject_name = lesson.subject.name if lesson.subject else 'Tutoring Session'
#         tutor_name = lesson.tutor.get_full_name() or lesson.tutor.email
#         student_name = lesson.student.get_full_name() or lesson.student.email
#         welcome = (
#             f'Welcome to your <b>{subject_name}</b> session with <b>{tutor_name}</b>!<br>'
#             f'Session duration: <b>{duration} minutes</b>.<br>'
#             'Please make sure your camera and microphone are working.'
#         )
#         self.create_meeting(
#             meeting_id=meeting_id,
#             meeting_name=f'{subject_name} - {tutor_name}',
#             attendee_pw=attendee_pw,
#             moderator_pw=moderator_pw,
#             lesson=lesson,
#             duration_minutes=duration + 10,
#             record=lesson.record_session,
#             auto_start_recording=lesson.record_session,
#             welcome_message=welcome,
#             logo_url=logo,
#             meta={'platform': 'gooprep', 'subject': subject_name,
#                   'created': timezone.now().isoformat()},
#         )
#         tutor_join = self.join_url(
#             meeting_id, tutor_name, moderator_pw, str(lesson.tutor.id),
#             role='MODERATOR', avatar_url=lesson.tutor.get_avatar_url(),
#         )
#         student_join = self.join_url(
#             meeting_id, student_name, attendee_pw, str(lesson.student.id),
#             role='VIEWER', avatar_url=lesson.student.get_avatar_url(),
#         )
#         return {
#             'meeting_id': meeting_id,
#             'attendee_pw': attendee_pw,
#             'moderator_pw': moderator_pw,
#             'join_url_tutor': tutor_join,
#             'join_url_student': student_join,
#             'bbb_base_url': self.base_url,
#         }

#     def get_lesson_recordings(self, lesson) -> list:
#         """Fetch all recordings for a specific lesson."""
#         meeting_id = f"lesson-{lesson.id}"
#         resp = self.get_recordings(meeting_id=meeting_id, states='published,unpublished')
#         recordings = resp.get('recordings', {})
#         if not recordings:
#             return []
#         raw = recordings.get('recording', [])
#         if isinstance(raw, dict):
#             raw = [raw]
#         result = []
#         for rec in raw:
#             formats = rec.get('playback', {}).get('format', [])
#             if isinstance(formats, dict):
#                 formats = [formats]
#             result.append({
#                 'record_id': rec.get('recordID', ''),
#                 'name': rec.get('name', ''),
#                 'state': rec.get('state', ''),
#                 'start_time': rec.get('startTime', ''),
#                 'end_time': rec.get('endTime', ''),
#                 'duration': rec.get('playback', {}).get('format', [{}])[0].get('length', 0) if formats else 0,
#                 'playback_url': formats[0].get('url', '') if formats else '',
#                 'thumbnail': formats[0].get('preview', {}).get('images', {}).get('image', [{}])[0].get('#text', '') if formats else '',
#                 'formats': [{'type': f.get('type', ''), 'url': f.get('url', ''), 'length': f.get('length', 0)} for f in formats],
#             })
#         return result


# # Module-level singleton
# bbb = BBBService()

"""
Gooprep BigBlueButton Integration
---------------------------------

Uses python-sage-bbb instead of the obsolete django-bigbluebutton package.

Package:
python-sage-bbb

Client:
sage_bbb.services.client.BigBlueButtonClient

Environment:
BBB_URL=https://your-bbb-server.com/bigbluebutton/api/
BBB_KEY=your-security-salt

The Gooprep application remains responsible for:
- Lesson/business logic
- Tutor/student permissions
- Meeting IDs
- Password generation
- Lesson metadata
- Recording association
"""

import hashlib
import logging
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.utils import timezone

from sage_bbb.services.client import BigBlueButtonClient

logger = logging.getLogger(**name**)

class BBBService:
"""
Gooprep wrapper around python-sage-bbb.

```
This class keeps the rest of the Gooprep application independent
of the underlying BBB client implementation.
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

    if self.base_url and self.secret:
        try:
            self.client = BigBlueButtonClient(
                self.base_url,
                self.secret,
            )
            logger.info("BigBlueButton client initialized successfully.")
        except Exception as exc:
            logger.exception(
                "Failed to initialize BigBlueButton client: %s",
                exc,
            )
            self.client = None

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

@property
def configured(self) -> bool:
    """Return True when BBB credentials are configured."""
    return bool(self.base_url and self.secret and self.client)

def _require_client(self) -> BigBlueButtonClient:
    """Return the BBB client or raise a useful error."""
    if not self.configured:
        raise RuntimeError(
            "BigBlueButton is not configured. "
            "Set BBB_URL and BBB_KEY."
        )

    return self.client

# ------------------------------------------------------------------
# Generic response helpers
# ------------------------------------------------------------------

@staticmethod
def _success(response: Any) -> bool:
    """
    Determine whether a sage_bbb response represents success.

    The library's response representation can vary between versions,
    so this deliberately accepts the common successful forms.
    """
    if response is None:
        return False

    if isinstance(response, bool):
        return response

    if isinstance(response, dict):
        value = response.get("returncode")

        if value is None:
            value = response.get("returnCode")

        if value is None:
            value = response.get("success")

        if isinstance(value, bool):
            return value

        if value is not None:
            return str(value).upper() in {
                "SUCCESS",
                "TRUE",
                "OK",
            }

    return True

@staticmethod
def _response_dict(response: Any) -> Dict[str, Any]:
    """
    Normalize a library response into a dictionary where possible.
    """
    if isinstance(response, dict):
        return response

    if hasattr(response, "model_dump"):
        try:
            return response.model_dump()
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

# ------------------------------------------------------------------
# Meetings
# ------------------------------------------------------------------

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
    lock_settings: Optional[dict] = None,
    meta: Optional[dict] = None,
    welcome_message: Optional[str] = None,
    max_participants: int = 10,
    logo_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a BBB meeting.

    python-sage-bbb handles the API request and checksum generation.
    """

    client = self._require_client()

    if not welcome_message:
        welcome_message = (
            f"<br>Welcome to <b>{meeting_name}</b> on Gooprep!<br>"
            "Please be respectful and ready to learn."
        )

    # Base parameters supported by BBB.
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
        "duration": duration_minutes,
        "maxParticipants": max_participants,
        "welcome": welcome_message,
    }

    if logo_url:
        params["logo"] = logo_url

    # BBB metadata.
    metadata = dict(meta or {})

    if lesson:
        metadata.update(
            {
                "lessonId": str(lesson.id),
                "tutorId": str(lesson.tutor_id),
                "studentId": str(lesson.student_id),
                "subject": (
                    lesson.subject.name
                    if lesson.subject
                    else ""
                ),
            }
        )

    # The sage_bbb package exposes create_meeting through
    # client.meetings.
    try:
        response = client.meetings.create_meeting(**params)

        result = self._response_dict(response)

        logger.info(
            "BBB create_meeting [%s]: %s",
            meeting_id,
            result.get("returncode", "SUCCESS"),
        )

        return result

    except TypeError:
        """
        Some versions of sage_bbb expose snake_case arguments while
        others follow BBB's original camelCase names.

        Retry with the most common snake_case representation.
        """

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
            "duration": duration_minutes,
            "max_participants": max_participants,
            "welcome": welcome_message,
        }

        if logo_url:
            fallback_params["logo"] = logo_url

        try:
            response = client.meetings.create_meeting(
                **fallback_params
            )

            result = self._response_dict(response)

            logger.info(
                "BBB create_meeting [%s] succeeded using "
                "snake_case parameters.",
                meeting_id,
            )

            return result

        except Exception as exc:
            logger.exception(
                "BBB create_meeting failed [%s]: %s",
                meeting_id,
                exc,
            )

            return {
                "returncode": "FAILED",
                "message": str(exc),
            }

    except Exception as exc:
        logger.exception(
            "BBB create_meeting failed [%s]: %s",
            meeting_id,
            exc,
        )

        return {
            "returncode": "FAILED",
            "message": str(exc),
        }

# ------------------------------------------------------------------
# Join URL
# ------------------------------------------------------------------

def join_url(
    self,
    meeting_id: str,
    full_name: str,
    password: str,
    user_id: Optional[str] = None,
    role: str = "VIEWER",
    avatar_url: Optional[str] = None,
    create_time: Optional[str] = None,
    redirect: bool = True,
    userdata: Optional[dict] = None,
) -> str:
    """
    Generate a signed BBB join URL.
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

    if create_time:
        params["create_time"] = create_time

    if userdata:
        params["userdata"] = userdata

    # sage_bbb documents join_meeting through client.meetings.
    try:
        return client.meetings.join_meeting(
            **params
        )

    except TypeError:
        # Compatibility fallback for installations where
        # sage_bbb exposes BBB parameter names directly.
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

        if create_time:
            fallback["createTime"] = create_time

        if userdata:
            for key, value in userdata.items():
                fallback[f"userdata-{key}"] = str(value)

        # Some sage_bbb versions do not expose a role argument
        # directly. BBB determines moderator access from the
        # moderator password.
        return client.meetings.join_meeting(**fallback)

# ------------------------------------------------------------------
# Meeting information
# ------------------------------------------------------------------

def end_meeting(
    self,
    meeting_id: str,
    moderator_pw: str,
) -> Dict[str, Any]:
    """End an active BBB meeting."""

    client = self._require_client()

    try:
        response = client.meetings.end_meeting(
            meeting_id=meeting_id,
            password=moderator_pw,
        )

        return self._response_dict(response)

    except TypeError:
        response = client.meetings.end_meeting(
            meetingID=meeting_id,
            password=moderator_pw,
        )

        return self._response_dict(response)

    except Exception as exc:
        logger.exception(
            "BBB end_meeting failed [%s]: %s",
            meeting_id,
            exc,
        )

        return {
            "returncode": "FAILED",
            "message": str(exc),
        }

def is_meeting_running(
    self,
    meeting_id: str,
) -> bool:
    """Return whether a BBB meeting is currently running."""

    client = self._require_client()

    try:
        response = client.meetings.is_meeting_running(
            meeting_id=meeting_id
        )

        if isinstance(response, bool):
            return response

        data = self._response_dict(response)

        return str(
            data.get("running", "false")
        ).lower() == "true"

    except Exception as exc:
        logger.warning(
            "BBB is_meeting_running failed [%s]: %s",
            meeting_id,
            exc,
        )
        return False

def get_meeting_info(
    self,
    meeting_id: str,
    moderator_pw: str,
) -> Dict[str, Any]:
    """Retrieve detailed meeting information."""

    client = self._require_client()

    try:
        response = client.meetings.get_meeting_info(
            meeting_id=meeting_id,
        )

        return self._response_dict(response)

    except TypeError:
        response = client.meetings.get_meeting_info(
            meetingID=meeting_id,
        )

        return self._response_dict(response)

    except Exception as exc:
        logger.exception(
            "BBB get_meeting_info failed [%s]: %s",
            meeting_id,
            exc,
        )

        return {
            "returncode": "FAILED",
            "message": str(exc),
        }

def get_meetings(self) -> Dict[str, Any]:
    """Return currently running BBB meetings."""

    client = self._require_client()

    try:
        response = client.meetings.get_meetings()
        return self._response_dict(response)

    except Exception as exc:
        logger.exception(
            "BBB get_meetings failed: %s",
            exc,
        )

        return {
            "returncode": "FAILED",
            "message": str(exc),
        }

# ------------------------------------------------------------------
# Recordings
# ------------------------------------------------------------------

def get_recordings(
    self,
    meeting_id: Optional[str] = None,
    record_id: Optional[str] = None,
    meta: Optional[dict] = None,
    states: str = "published",
    offset: int = 0,
    limit: int = 10,
) -> Dict[str, Any]:
    """Fetch BBB recordings."""

    client = self._require_client()

    try:
        kwargs = {
            "meeting_id": meeting_id,
            "record_id": record_id,
            "states": states,
            "offset": offset,
            "limit": limit,
        }

        kwargs = {
            key: value
            for key, value in kwargs.items()
            if value is not None
        }

        response = client.recordings.get_recordings(
            **kwargs
        )

        return self._response_dict(response)

    except AttributeError:
        """
        Some sage_bbb releases expose recording methods directly
        through the client instead of client.recordings.
        """

        kwargs = {
            "meeting_id": meeting_id,
            "record_id": record_id,
            "states": states,
            "offset": offset,
            "limit": limit,
        }

        kwargs = {
            key: value
            for key, value in kwargs.items()
            if value is not None
        }

        response = client.get_recordings(**kwargs)

        return self._response_dict(response)

    except Exception as exc:
        logger.exception(
            "BBB get_recordings failed: %s",
            exc,
        )

        return {
            "returncode": "FAILED",
            "message": str(exc),
        }

def publish_recording(
    self,
    record_id: str,
    publish: bool = True,
) -> Dict[str, Any]:
    """Publish or unpublish a recording."""

    client = self._require_client()

    try:
        response = client.recordings.publish_recording(
            record_id=record_id,
            publish=publish,
        )

        return self._response_dict(response)

    except AttributeError:
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

        return {
            "returncode": "FAILED",
            "message": str(exc),
        }

def delete_recording(
    self,
    record_id: str,
) -> Dict[str, Any]:
    """Delete a BBB recording."""

    client = self._require_client()

    try:
        response = client.recordings.delete_recording(
            record_id=record_id
        )

        return self._response_dict(response)

    except AttributeError:
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

        return {
            "returncode": "FAILED",
            "message": str(exc),
        }

def update_recordings(
    self,
    record_id: str,
    meta: dict,
) -> Dict[str, Any]:
    """Update recording metadata."""

    client = self._require_client()

    try:
        response = client.recordings.update_recording(
            record_id=record_id,
            metadata=meta,
        )

        return self._response_dict(response)

    except AttributeError:
        response = client.update_recording(
            record_id=record_id,
            metadata=meta,
        )

        return self._response_dict(response)

    except Exception as exc:
        logger.exception(
            "BBB update_recordings failed [%s]: %s",
            record_id,
            exc,
        )

        return {
            "returncode": "FAILED",
            "message": str(exc),
        }

# ------------------------------------------------------------------
# Health
# ------------------------------------------------------------------

def get_api_version(self) -> Dict[str, Any]:
    """Check BBB API connectivity."""

    client = self._require_client()

    try:
        response = client.check_connection()
        return self._response_dict(response)

    except Exception as exc:
        logger.exception(
            "BBB connection check failed: %s",
            exc,
        )

        return {
            "returncode": "FAILED",
            "message": str(exc),
        }

def server_healthy(self) -> bool:
    """Return True when the BBB server responds successfully."""

    if not self.configured:
        return False

    try:
        response = self.get_api_version()

        if isinstance(response, bool):
            return response

        return self._success(response)

    except Exception as exc:
        logger.warning(
            "BBB health check failed: %s",
            exc,
        )
        return False

# ------------------------------------------------------------------
# Gooprep lesson integration
# ------------------------------------------------------------------

def provision_lesson_room(
    self,
    lesson,
) -> Dict[str, Any]:
    """
    Create a BBB room for a Gooprep lesson and generate tutor/student
    join URLs.
    """

    if not self.configured:
        raise RuntimeError(
            "BigBlueButton is not configured."
        )

    meeting_id = f"lesson-{lesson.id}"

    # Deterministic passwords are sufficient for the lesson-specific
    # room because the values are never exposed as the public meeting
    # identifier.
    attendee_pw = hashlib.sha256(
        f"gooprep-attendee-{lesson.id}".encode()
    ).hexdigest()[:12]

    moderator_pw = hashlib.sha256(
        f"gooprep-moderator-{lesson.id}".encode()
    ).hexdigest()[:12]

    duration = max(
        1,
        int(
            (
                lesson.end_time - lesson.start_time
            ).total_seconds()
            / 60
        ),
    )

    subject_name = (
        lesson.subject.name
        if lesson.subject
        else "Tutoring Session"
    )

    tutor_name = (
        lesson.tutor.get_full_name()
        or lesson.tutor.email
    )

    student_name = (
        lesson.student.get_full_name()
        or lesson.student.email
    )

    welcome = (
        f"Welcome to your <b>{subject_name}</b> session "
        f"with <b>{tutor_name}</b>!<br>"
        f"Session duration: <b>{duration} minutes</b>.<br>"
        "Please make sure your camera and microphone are working."
    )

    logo = getattr(
        settings,
        "BBB_LOGO_URL",
        "",
    )

    metadata = {
        "platform": "gooprep",
        "lessonId": str(lesson.id),
        "subject": subject_name,
        "created": timezone.now().isoformat(),
    }

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
                "Failed to create BigBlueButton meeting.",
            )
        )

    # Tutor joins using moderator password.
    tutor_join = self.join_url(
        meeting_id=meeting_id,
        full_name=tutor_name,
        password=moderator_pw,
        user_id=str(lesson.tutor.id),
        role="MODERATOR",
        avatar_url=(
            lesson.tutor.get_avatar_url()
            if hasattr(
                lesson.tutor,
                "get_avatar_url",
            )
            else None
        ),
    )

    # Student joins using attendee password.
    student_join = self.join_url(
        meeting_id=meeting_id,
        full_name=student_name,
        password=attendee_pw,
        user_id=str(lesson.student.id),
        role="VIEWER",
        avatar_url=(
            lesson.student.get_avatar_url()
            if hasattr(
                lesson.student,
                "get_avatar_url",
            )
            else None
        ),
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

# ------------------------------------------------------------------
# Lesson recordings
# ------------------------------------------------------------------

def get_lesson_recordings(
    self,
    lesson,
) -> List[Dict[str, Any]]:
    """
    Retrieve published/unpublished recordings associated with a lesson.
    """

    meeting_id = f"lesson-{lesson.id}"

    response = self.get_recordings(
        meeting_id=meeting_id,
        states="published,unpublished",
    )

    if not response:
        return []

    recordings = response.get(
        "recordings",
        {},
    )

    if not recordings:
        return []

    raw = recordings.get(
        "recording",
        [],
    )

    if isinstance(raw, dict):
        raw = [raw]

    results = []

    for recording in raw:
        playback = recording.get(
            "playback",
            {},
        )

        formats = playback.get(
            "format",
            [],
        )

        if isinstance(formats, dict):
            formats = [formats]

        normalized_formats = []

        for fmt in formats:
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
                }
            )

        first_format = (
            formats[0]
            if formats
            else {}
        )

        results.append(
            {
                "record_id": recording.get(
                    "recordID",
                    "",
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
                    "",
                ),
                "end_time": recording.get(
                    "endTime",
                    "",
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
```

# ----------------------------------------------------------------------

# Module-level singleton

# ----------------------------------------------------------------------

bbb = BBBService()
