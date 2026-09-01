import hashlib
import json
import logging

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import BBBWebhookEvent, Lesson
from .bbb_service import bbb

logger = logging.getLogger(__name__)


def _get_event_id(payload):
    """
    Extract an event identifier from common BBB webhook
    payload structures.
    """

    return (
        payload.get("id")
        or payload.get("eventId")
        or payload.get("event_id")
        or payload.get("event", {}).get("id")
    )


def _get_event_type(payload):

    return (
        payload.get("event")
        if isinstance(
            payload.get("event"),
            str,
        )
        else (
            payload.get("event", {}).get("name")
            if isinstance(
                payload.get("event"),
                dict,
            )
            else None
        )
        or payload.get("eventType")
        or payload.get("event_type")
        or payload.get("name")
        or "unknown"
    )


def _get_meeting_id(payload):

    candidates = [
        payload.get("meetingId"),
        payload.get("meetingID"),
        payload.get("meeting_id"),
    ]

    event = payload.get("event")

    if isinstance(event, dict):
        candidates.extend(
            [
                event.get("meetingId"),
                event.get("meetingID"),
                event.get("meeting_id"),
            ]
        )

    meeting = payload.get("meeting")

    if isinstance(meeting, dict):
        candidates.extend(
            [
                meeting.get("meetingId"),
                meeting.get("meetingID"),
                meeting.get("meeting_id"),
            ]
        )

    for value in candidates:
        if value:
            return str(value)

    return ""


def _get_record_id(payload):

    candidates = [
        payload.get("recordId"),
        payload.get("recordID"),
        payload.get("record_id"),
    ]

    event = payload.get("event")

    if isinstance(event, dict):
        candidates.extend(
            [
                event.get("recordId"),
                event.get("recordID"),
                event.get("record_id"),
            ]
        )

    recording = payload.get("recording")

    if isinstance(recording, dict):
        candidates.extend(
            [
                recording.get("recordId"),
                recording.get("recordID"),
                recording.get("record_id"),
            ]
        )

    for value in candidates:
        if value:
            return str(value)

    return ""


def _fallback_event_id(payload):
    """
    Generate a deterministic ID if BBB does not provide one.

    This prevents duplicate delivery from creating duplicate
    database events.
    """

    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )

    return hashlib.sha256(
        serialized.encode()
    ).hexdigest()


@csrf_exempt
def bbb_webhook(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "detail": "POST required."
            },
            status=405,
        )

    # --------------------------------------------------------------
    # Optional shared webhook secret
    # --------------------------------------------------------------

    expected_secret = getattr(
        settings,
        "BBB_WEBHOOK_SECRET",
        "",
    )

    if expected_secret:

        supplied_secret = (
            request.headers.get(
                "X-BBB-Webhook-Secret"
            )
            or request.GET.get(
                "secret"
            )
        )

        if supplied_secret != expected_secret:

            return JsonResponse(
                {
                    "detail": "Invalid webhook secret."
                },
                status=403,
            )

    # --------------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------------

    try:
        payload = json.loads(
            request.body.decode(
                "utf-8"
            )
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):

        return JsonResponse(
            {
                "detail": "Invalid JSON."
            },
            status=400,
        )

    if not isinstance(
        payload,
        dict,
    ):
        return JsonResponse(
            {
                "detail": "JSON object expected."
            },
            status=400,
        )

    event_type = _get_event_type(
        payload
    )

    meeting_id = _get_meeting_id(
        payload
    )

    record_id = _get_record_id(
        payload
    )

    event_id = (
        _get_event_id(payload)
        or _fallback_event_id(payload)
    )

    # --------------------------------------------------------------
    # Persist event
    # --------------------------------------------------------------

    try:

        with transaction.atomic():

            event, created = (
                BBBWebhookEvent.objects.get_or_create(
                    event_id=event_id,
                    defaults={
                        "event_type": event_type,
                        "meeting_id": meeting_id,
                        "record_id": record_id,
                        "payload": payload,
                    },
                )
            )

            if not created:

                # Already received.
                if event.processed:

                    return JsonResponse(
                        {
                            "received": True,
                            "duplicate": True,
                            "processed": True,
                        }
                    )

                event.payload = payload
                event.save(
                    update_fields=[
                        "payload"
                    ]
                )

    except Exception:

        logger.exception(
            "Failed storing BBB webhook."
        )

        return JsonResponse(
            {
                "detail": (
                    "Could not store webhook."
                )
            },
            status=500,
        )

    # --------------------------------------------------------------
    # Process event
    # --------------------------------------------------------------

    try:

        process_bbb_event(
            event,
            payload,
        )

        event.processed = True
        event.processed_at = timezone.now()
        event.processing_error = ""

        event.save(
            update_fields=[
                "processed",
                "processed_at",
                "processing_error",
            ]
        )

        return JsonResponse(
            {
                "received": True,
                "processed": True,
                "event_id": event_id,
            }
        )

    except Exception as exc:

        logger.exception(
            "BBB webhook processing failed."
        )

        event.processed = False
        event.processing_error = str(
            exc
        )

        event.save(
            update_fields=[
                "processed",
                "processing_error",
            ]
        )

        # Return 500 so the webhook provider can retry.
        return JsonResponse(
            {
                "received": True,
                "processed": False,
                "error": str(exc),
            },
            status=500,
        )


def process_bbb_event(
    event,
    payload,
):

    meeting_id = event.meeting_id
    event_type = event.event_type

    if not meeting_id:
        logger.warning(
            "BBB webhook has no meeting ID: %s",
            event.id,
        )
        return

    try:

        lesson = Lesson.objects.get(
            bbb_meeting_id=meeting_id
        )

    except Lesson.DoesNotExist:

        logger.warning(
            "No lesson found for BBB meeting %s",
            meeting_id,
        )

        return

    event_name = event_type.lower()

    # --------------------------------------------------------------
    # Meeting started
    # --------------------------------------------------------------

    if (
        "meeting"
        in event_name
        and (
            "start"
            in event_name
            or "created"
            in event_name
        )
    ):

        lesson.bbb_status = "running"

        if not lesson.bbb_started_at:
            lesson.bbb_started_at = (
                timezone.now()
            )

        if lesson.status in {
            "pending",
            "confirmed",
        }:
            lesson.status = "in_progress"

        lesson.save(
            update_fields=[
                "bbb_status",
                "bbb_started_at",
                "status",
                "updated_at",
            ]
        )

        return

    # --------------------------------------------------------------
    # Meeting ended
    # --------------------------------------------------------------

    if (
        "meeting"
        in event_name
        and (
            "end"
            in event_name
            or "ended"
            in event_name
            or "destroy"
            in event_name
        )
    ):

        lesson.bbb_status = "ended"

        if not lesson.bbb_ended_at:
            lesson.bbb_ended_at = (
                timezone.now()
            )

        if lesson.status == "in_progress":
            lesson.status = "completed"

        lesson.save(
            update_fields=[
                "bbb_status",
                "bbb_ended_at",
                "status",
                "updated_at",
            ]
        )

        # Attempt to retrieve recordings.
        try:
            bbb.sync_lesson_recordings(
                lesson
            )
        except Exception:
            logger.exception(
                "Recording sync after meeting "
                "end failed for lesson %s",
                lesson.id,
            )

        return

    # --------------------------------------------------------------
    # Recording published / ready
    # --------------------------------------------------------------

    if (
        "record"
        in event_name
        or "playback"
        in event_name
    ):

        try:

            bbb.sync_lesson_recordings(
                lesson
            )

        except Exception:
            logger.exception(
                "Recording sync failed for lesson %s",
                lesson.id,
            )

        return