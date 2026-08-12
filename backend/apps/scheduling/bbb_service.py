"""
BigBlueButton (BBB) API Integration for Gooprep
Handles room creation, joining, recordings, and webhooks
"""
import hashlib
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class BBBService:
    """
    Full BigBlueButton API v2.6 integration.
    Docs: https://docs.bigbluebutton.org/development/api/
    """

    def __init__(self):
        configured_url = (getattr(settings, 'BBB_URL', '') or '').strip()
        self.base_url = self._normalize_base_url(configured_url)
        self.secret = (getattr(settings, 'BBB_SECRET', '') or '').strip()

    @staticmethod
    def _normalize_base_url(url):
        """Return the BBB API base URL used by all API calls."""
        if not url:
            return ''
        url = url.rstrip('/') + '/'
        if url.lower().endswith('/bigbluebutton/api/'):
            return url
        if '/bigbluebutton/' in url.lower():
            prefix = url[:url.lower().index('/bigbluebutton/') + len('/bigbluebutton/')]
            return prefix + 'api/'
        return url

    @property
    def configured(self):
        return bool(self.base_url and self.secret)

    # ------------------------------------------------------------------ #
    #  Core checksum / URL helpers                                         #
    # ------------------------------------------------------------------ #

    def _checksum(self, api_call: str, params: str) -> str:
        """Generate the SHA-1 checksum required by BBB API v2."""
        raw = api_call + params + self.secret
        return hashlib.sha1(raw.encode('utf-8')).hexdigest()

    def _build_url(self, api_call: str, params: dict) -> str:
        """Build a signed BBB API URL."""
        query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        checksum = self._checksum(api_call, query)
        return f"{self.base_url}{api_call}?{query}&checksum={checksum}"

    def _call_api(self, api_call: str, params: dict) -> dict:
        """Execute a BBB API call and return parsed XML as dict."""
        if not self.configured:
            return {'returncode': 'FAILED', 'message': 'BBB is not configured.'}
        url = self._build_url(api_call, params)
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                xml_data = resp.read()
            root = ET.fromstring(xml_data)
            return self._xml_to_dict(root)
        except Exception as exc:
            logger.error(f"BBB API error [{api_call}]: {exc}")
            return {'returncode': 'FAILED', 'message': str(exc)}

    def _xml_to_dict(self, element) -> dict:
        """Recursively convert XML element to dictionary."""
        result = {}
        for child in element:
            if len(child):
                result[child.tag] = self._xml_to_dict(child)
            else:
                result[child.tag] = child.text
        return result

    # ------------------------------------------------------------------ #
    #  Meeting / Room management                                           #
    # ------------------------------------------------------------------ #

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
        lock_settings: dict = None,
        meta: dict = None,
        welcome_message: str = None,
        max_participants: int = 10,
        logo_url: str = None,
    ) -> dict:
        """
        Create a BBB meeting room.
        Returns the full API response including join URLs.
        """
        params = {
            'meetingID': meeting_id,
            'name': meeting_name,
            'attendeePW': attendee_pw,
            'moderatorPW': moderator_pw,
            'record': 'true' if record else 'false',
            'autoStartRecording': 'true' if auto_start_recording else 'false',
            'allowStartStopRecording': 'true' if allow_start_stop_recording else 'false',
            'webcamsOnlyForModerator': 'true' if webcams_only_for_moderator else 'false',
            'muteOnStart': 'true' if mute_on_start else 'false',
            'duration': str(duration_minutes),
            'maxParticipants': str(max_participants),
        }

        if welcome_message:
            params['welcome'] = welcome_message
        else:
            params['welcome'] = (
                f"<br>Welcome to <b>{meeting_name}</b> on Gooprep!<br>"
                "Please be respectful and ready to learn."
            )

        if logo_url:
            params['logo'] = logo_url

        # Site-wide logo/branding
        site_logo = getattr(settings, 'BBB_LOGO_URL', '/static/img/gooprep_logo.png')
        if site_logo and not logo_url:
            params['logo'] = site_logo

        # Metadata for filtering recordings later
        if meta:
            for key, val in meta.items():
                params[f'meta_{key}'] = str(val)

        if lesson:
            params['meta_lessonId'] = str(lesson.id)
            params['meta_tutorId'] = str(lesson.tutor_id)
            params['meta_studentId'] = str(lesson.student_id)
            params['meta_subject'] = lesson.subject.name if lesson.subject else ''

        # Lock settings (optional)
        if lock_settings:
            for k, v in lock_settings.items():
                params[k] = 'true' if v else 'false'

        response = self._call_api('create', params)
        logger.info(f"BBB create_meeting [{meeting_id}]: {response.get('returncode')}")
        return response

    def join_url(
        self,
        meeting_id: str,
        full_name: str,
        password: str,
        user_id: str = None,
        role: str = 'VIEWER',
        avatar_url: str = None,
        create_time: str = None,
        redirect: bool = True,
        userdata: dict = None,
    ) -> str:
        """
        Generate a signed join URL for a participant.
        role: 'MODERATOR' for tutors, 'VIEWER' for students
        """
        params = {
            'meetingID': meeting_id,
            'fullName': full_name,
            'password': password,
            'redirect': 'true' if redirect else 'false',
            'role': role,
        }
        if user_id:
            params['userID'] = str(user_id)
        if avatar_url:
            params['avatarURL'] = avatar_url
        if create_time:
            params['createTime'] = create_time
        if userdata:
            for k, v in userdata.items():
                params[f'userdata-{k}'] = str(v)

        return self._build_url('join', params)

    def end_meeting(self, meeting_id: str, moderator_pw: str) -> dict:
        """End an active BBB meeting."""
        params = {'meetingID': meeting_id, 'password': moderator_pw}
        return self._call_api('end', params)

    def is_meeting_running(self, meeting_id: str) -> bool:
        """Check if a meeting is currently running."""
        params = {'meetingID': meeting_id}
        resp = self._call_api('isMeetingRunning', params)
        return resp.get('running', 'false').lower() == 'true'

    def get_meeting_info(self, meeting_id: str, moderator_pw: str) -> dict:
        """Get detailed info about a meeting including attendees."""
        params = {'meetingID': meeting_id, 'password': moderator_pw}
        return self._call_api('getMeetingInfo', params)

    def get_meetings(self) -> dict:
        """List all active meetings on the BBB server."""
        return self._call_api('getMeetings', {})

    # ------------------------------------------------------------------ #
    #  Recordings                                                          #
    # ------------------------------------------------------------------ #

    def get_recordings(
        self,
        meeting_id: str = None,
        record_id: str = None,
        meta: dict = None,
        states: str = 'published',
        offset: int = 0,
        limit: int = 10,
    ) -> dict:
        """Fetch recordings, optionally filtered by meeting or metadata."""
        params = {'states': states, 'offset': str(offset), 'limit': str(limit)}
        if meeting_id:
            params['meetingID'] = meeting_id
        if record_id:
            params['recordID'] = record_id
        if meta:
            for k, v in meta.items():
                params[f'meta_{k}'] = str(v)
        return self._call_api('getRecordings', params)

    def publish_recording(self, record_id: str, publish: bool = True) -> dict:
        """Publish or unpublish a recording."""
        params = {'recordID': record_id, 'publish': 'true' if publish else 'false'}
        return self._call_api('publishRecordings', params)

    def delete_recording(self, record_id: str) -> dict:
        """Permanently delete a recording."""
        params = {'recordID': record_id}
        return self._call_api('deleteRecordings', params)

    def update_recordings(self, record_id: str, meta: dict) -> dict:
        """Update recording metadata."""
        params = {'recordID': record_id}
        for k, v in meta.items():
            params[f'meta_{k}'] = str(v)
        return self._call_api('updateRecordings', params)

    # ------------------------------------------------------------------ #
    #  BBB Health / Server                                                 #
    # ------------------------------------------------------------------ #

    def get_api_version(self) -> dict:
        """Check BBB server version and availability."""
        return self._call_api('', {})

    def server_healthy(self) -> bool:
        """Quick health check — returns True if BBB is reachable."""
        try:
            resp = self.get_api_version()
            return resp.get('returncode') == 'SUCCESS'
        except Exception:
            return False

    # ------------------------------------------------------------------ #
    #  High-level helpers for Gooprep lesson flow                        #
    # ------------------------------------------------------------------ #

    def provision_lesson_room(self, lesson) -> dict:
        """Create a BBB room and signed join URLs for a lesson."""
        if not self.configured:
            raise RuntimeError('BigBlueButton is not configured.')

        logo = getattr(settings, 'BBB_LOGO_URL', '')
        meeting_id = f'lesson-{lesson.id}'
        attendee_pw = hashlib.md5(f'att-{lesson.id}'.encode()).hexdigest()[:12]
        moderator_pw = hashlib.md5(f'mod-{lesson.id}'.encode()).hexdigest()[:12]
        duration = max(1, int((lesson.end_time - lesson.start_time).total_seconds() / 60))
        subject_name = lesson.subject.name if lesson.subject else 'Tutoring Session'
        tutor_name = lesson.tutor.get_full_name() or lesson.tutor.email
        student_name = lesson.student.get_full_name() or lesson.student.email
        welcome = (
            f'Welcome to your <b>{subject_name}</b> session with <b>{tutor_name}</b>!<br>'
            f'Session duration: <b>{duration} minutes</b>.<br>'
            'Please make sure your camera and microphone are working.'
        )
        self.create_meeting(
            meeting_id=meeting_id,
            meeting_name=f'{subject_name} - {tutor_name}',
            attendee_pw=attendee_pw,
            moderator_pw=moderator_pw,
            lesson=lesson,
            duration_minutes=duration + 10,
            record=lesson.record_session,
            auto_start_recording=lesson.record_session,
            welcome_message=welcome,
            logo_url=logo,
            meta={'platform': 'gooprep', 'subject': subject_name,
                  'created': timezone.now().isoformat()},
        )
        tutor_join = self.join_url(
            meeting_id, tutor_name, moderator_pw, str(lesson.tutor.id),
            role='MODERATOR', avatar_url=lesson.tutor.get_avatar_url(),
        )
        student_join = self.join_url(
            meeting_id, student_name, attendee_pw, str(lesson.student.id),
            role='VIEWER', avatar_url=lesson.student.get_avatar_url(),
        )
        return {
            'meeting_id': meeting_id,
            'attendee_pw': attendee_pw,
            'moderator_pw': moderator_pw,
            'join_url_tutor': tutor_join,
            'join_url_student': student_join,
            'bbb_base_url': self.base_url,
        }

    def get_lesson_recordings(self, lesson) -> list:
        """Fetch all recordings for a specific lesson."""
        meeting_id = f"lesson-{lesson.id}"
        resp = self.get_recordings(meeting_id=meeting_id, states='published,unpublished')
        recordings = resp.get('recordings', {})
        if not recordings:
            return []
        raw = recordings.get('recording', [])
        if isinstance(raw, dict):
            raw = [raw]
        result = []
        for rec in raw:
            formats = rec.get('playback', {}).get('format', [])
            if isinstance(formats, dict):
                formats = [formats]
            result.append({
                'record_id': rec.get('recordID', ''),
                'name': rec.get('name', ''),
                'state': rec.get('state', ''),
                'start_time': rec.get('startTime', ''),
                'end_time': rec.get('endTime', ''),
                'duration': rec.get('playback', {}).get('format', [{}])[0].get('length', 0) if formats else 0,
                'playback_url': formats[0].get('url', '') if formats else '',
                'thumbnail': formats[0].get('preview', {}).get('images', {}).get('image', [{}])[0].get('#text', '') if formats else '',
                'formats': [{'type': f.get('type', ''), 'url': f.get('url', ''), 'length': f.get('length', 0)} for f in formats],
            })
        return result


# Module-level singleton
bbb = BBBService()
