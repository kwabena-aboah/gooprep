import hmac, hashlib, json, uuid
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import Transaction, Subscription, Payout, Dispute
from . import paystack
from .serializers import TransactionSerializer, SubscriptionSerializer, PayoutSerializer, DisputeSerializer

class TransactionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        # Students see payments they made; tutors see payments for their lessons.
        # select_related keeps the earnings table from issuing one query per row.
        if getattr(request.user, 'role', '') == 'tutor':
            qs = Transaction.objects.filter(lesson__tutor=request.user).select_related(
                'payer', 'lesson__subject'
            ).order_by('-created_at')
        else:
            qs = Transaction.objects.filter(payer=request.user).select_related(
                'payer', 'lesson__subject'
            ).order_by('-created_at')
        page_size = int(request.query_params.get('page_size',20))
        page = int(request.query_params.get('page',1))
        total = qs.count()
        data  = TransactionSerializer(qs[(page-1)*page_size:page*page_size], many=True).data
        return Response({'count':total,'results':data})

class PayoutListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        qs = Payout.objects.filter(tutor=request.user).order_by('-requested_at')
        return Response({'count':qs.count(),'results':PayoutSerializer(qs,many=True).data})
    def post(self, request):
        from apps.tutors.models import TutorProfile
        try: tp = TutorProfile.objects.get(user=request.user)
        except: return Response({'error':'Tutor profile not found.'}, status=400)
        amount = float(request.data.get('amount',0))
        if amount < float(settings.MIN_PAYOUT):
            return Response({'error':f'Minimum payout is GHS {settings.MIN_PAYOUT}.'}, status=400)
        if float(tp.pending_payout) < amount:
            return Response({'error':'Insufficient balance.'}, status=400)
        # pending_payout is already the tutor's post-commission balance. Do not
        # deduct a second time; record the gross equivalent and commission for
        # a transparent payout audit trail.
        commission_rate = float(settings.PLATFORM_COMMISSION)
        gross_equivalent = amount / (1 - commission_rate)
        details = {
            **(request.data.get('details', {}) or {}),
            'commission_rate': commission_rate,
            'gross_equivalent': round(gross_equivalent, 2),
            'commission_amount': round(gross_equivalent - amount, 2),
        }
        payout = Payout.objects.create(tutor=request.user, amount=amount,
            method=request.data.get('method','mtn_momo'), details=details)
        tp.pending_payout = float(tp.pending_payout) - amount
        tp.save(update_fields=['pending_payout'])
        try:
            from apps.messaging.guppy import get_or_create_guppy_user, send_push_notification
            gid = get_or_create_guppy_user(request.user)
            if gid: send_push_notification(gid,'💸 Payout Requested',f'GHS {amount:.2f} payout submitted. Processing in 1-2 business days.')
        except Exception: pass
        return Response(PayoutSerializer(payout).data, status=201)

class DisputeListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        from django.db.models import Q
        qs = Dispute.objects.filter(Q(filed_by=request.user)|Q(lesson__tutor=request.user)|Q(lesson__student=request.user))
        return Response({'count':qs.count(),'results':DisputeSerializer(qs,many=True).data})
    def post(self, request):
        from apps.scheduling.models import Lesson
        try: lesson = Lesson.objects.get(id=request.data.get('lesson'))
        except: return Response({'error':'Lesson not found.'}, status=400)
        d = Dispute.objects.create(lesson=lesson, filed_by=request.user,
            reason=request.data.get('reason',''), amount=lesson.price)
        return Response(DisputeSerializer(d).data, status=201)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def paystack_webhook(request):
    signature = request.headers.get('x-paystack-signature', '')
    secret = settings.PAYSTACK_SECRET_KEY
    if secret:
        expected = hmac.new(secret.encode(), request.body, hashlib.sha512).hexdigest()
        if not hmac.compare_digest(expected, signature):
            return Response({'error': 'Invalid signature.'}, status=403)
    try:
        event = json.loads(request.body)
        event_name = event.get('event')
        data = event.get('data', {})
        reference = data.get('reference', '')
        if event_name == 'charge.success':
            _settle_successful_reference(reference)
        elif event_name in ('transfer.success', 'transfer.failed', 'transfer.reversed'):
            payout = Payout.objects.filter(details__reference=reference).first()
            if payout:
                payout.status = 'completed' if event_name == 'transfer.success' else 'failed'
                payout.processed_at = timezone.now()
                payout.save(update_fields=['status', 'processed_at'])
                if payout.status == 'failed':
                    from apps.tutors.models import TutorProfile
                    tp = TutorProfile.objects.filter(user=payout.tutor).first()
                    if tp:
                        tp.pending_payout += payout.amount
                        tp.save(update_fields=['pending_payout'])
    except (TypeError, ValueError, json.JSONDecodeError):
        return Response({'error': 'Invalid webhook payload.'}, status=400)
    return Response({'received': True})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def initiate_payment(request):
    """Create a pending lesson transaction and initialize Paystack."""
    lesson_id = request.data.get('lesson_id')
    method = request.data.get('payment_method', 'card')
    if method not in {'card', 'mtn_momo', 'at_momo', 'tel_cash', 'bank'}:
        return Response({'error': 'Unsupported payment method.'}, status=400)
    from apps.scheduling.models import Lesson
    try:
        lesson = Lesson.objects.filter(
            Q(id=lesson_id) & (Q(student=request.user) | Q(booked_on_behalf=True, booker_email__iexact=request.user.email))
        ).first()
        if not lesson:
            return Response({'error': 'Lesson not found.'}, status=404)
    except Lesson.DoesNotExist:
        return Response({'error': 'Lesson not found.'}, status=404)
    if lesson.payment_status == 'paid':
        return Response({'error': 'This lesson has already been paid for.'}, status=400)

    reference = f'gooprep-{uuid.uuid4().hex[:16]}'
    txn = Transaction.objects.create(
        payer=request.user, lesson=lesson, amount=lesson.price,
        payment_method=method, paystack_ref=reference,
        description=f'Lesson with {lesson.tutor.get_full_name()}',
    )
    try:
        data = paystack.initialize(
            request.user.email, lesson.price, reference,
            f'{settings.FRONTEND_URL}/payments/verify',
            {'type': 'lesson', 'lesson_id': lesson.id, 'booked_on_behalf': lesson.booked_on_behalf},
        )
    except Exception as exc:
        txn.status = 'failed'
        txn.save(update_fields=['status'])
        return Response({'error': str(exc)}, status=502)
    return Response({'authorization_url': data['authorization_url'], 'reference': reference})

PLAN_PRICES = {
    'pro': {'monthly': 89, 'annual': 71},
    'institution': {'monthly': 499, 'annual': 399},
}


class SubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        subscription = Subscription.objects.filter(user=request.user, status='active').first()
        return Response({'subscription': SubscriptionSerializer(subscription).data if subscription else None})

    def post(self, request):
        plan = request.data.get('plan', '').lower()
        cycle = request.data.get('billing_cycle', 'monthly')
        if plan not in PLAN_PRICES or cycle not in ('monthly', 'annual'):
            return Response({'error': 'Invalid subscription plan or billing cycle.'}, status=400)
        amount = PLAN_PRICES[plan][cycle]
        ref = f'gooprep-sub-{request.user.id}-{uuid.uuid4().hex[:12]}'
        subscription = Subscription.objects.create(user=request.user, plan=plan, billing_cycle=cycle, amount=amount, paystack_ref=ref)
        try:
            data = paystack.initialize(request.user.email, amount, ref, f'{settings.FRONTEND_URL}/payments/verify', {'type': 'subscription', 'subscription_id': subscription.id})
        except Exception as exc:
            subscription.status = 'failed'; subscription.save(update_fields=['status'])
            return Response({'error': str(exc)}, status=502)
        return Response({'authorization_url': data['authorization_url'], 'reference': ref}, status=201)


class SubscriptionStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        subscription = Subscription.objects.filter(user=request.user).order_by('-created_at').first()
        return Response({'subscription': SubscriptionSerializer(subscription).data if subscription else None})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_payment(request):
    reference = request.query_params.get('reference')
    if not reference:
        return Response({'error': 'Payment reference is required.'}, status=400)
    try:
        result = paystack.verify(reference)
    except Exception as exc:
        return Response({'error': str(exc)}, status=502)
    if result.get('status') != 'success':
        return Response({'paid': False, 'message': 'Payment was not completed.'})
    _settle_successful_reference(reference)
    return Response({'paid': True, 'message': 'Payment confirmed successfully.'})


def _settle_successful_reference(reference):
    txn = Transaction.objects.filter(paystack_ref=reference).select_related('lesson').first()
    if txn and txn.status != 'success':
        txn.status = 'success'; txn.save(update_fields=['status'])
        if txn.lesson and txn.lesson.payment_status != 'paid':
            txn.lesson.payment_status = 'paid'
            txn.lesson.status = 'confirmed'
            txn.lesson.save(update_fields=['payment_status', 'status'])
            from apps.tutors.models import TutorProfile
            tp = TutorProfile.objects.filter(user=txn.lesson.tutor).first()
            if tp:
                net = txn.amount * (1 - settings.PLATFORM_COMMISSION)
                tp.pending_payout += net; tp.total_earnings += net
                tp.save(update_fields=['pending_payout', 'total_earnings'])

    if txn and txn.status == 'success' and txn.lesson and not (txn.metadata or {}).get('receipt_email_sent'):
        try:
            from apps.notifications import send_paid_lesson_receipt
            send_paid_lesson_receipt(txn)
            txn.metadata = {**(txn.metadata or {}), 'receipt_email_sent': True}
            txn.save(update_fields=['metadata'])
        except Exception:
            import logging
            logging.getLogger(__name__).exception('Paid lesson receipt delivery failed for transaction %s', txn.pk)

    subscription = Subscription.objects.filter(paystack_ref=reference).first()
    if subscription and subscription.status != 'active':
        now = timezone.now()
        subscription.status = 'active'; subscription.starts_at = now
        subscription.expires_at = now + timedelta(days=365 if subscription.billing_cycle == 'annual' else 30)
        subscription.save(update_fields=['status', 'starts_at', 'expires_at'])
        user = subscription.user; user.subscription_plan = subscription.plan; user.subscription_expires = subscription.expires_at
        user.save(update_fields=['subscription_plan', 'subscription_expires'])


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def process_payout(request, pk):
    payout = Payout.objects.select_related('tutor').filter(pk=pk, status='pending').first()
    if not payout:
        return Response({'error': 'Pending payout not found.'}, status=404)
    details = payout.details or {}
    try:
        recipient = paystack.create_transfer_recipient(payout.tutor.get_full_name(), details['number'], details.get('bank_code', '057'))
        reference = f'gooprep-payout-{payout.id}-{uuid.uuid4().hex[:8]}'
        transfer = paystack.create_transfer(payout.amount, recipient, reference, f'Gooprep payout #{payout.id}')
    except (KeyError, ValueError) as exc:
        return Response({'error': str(exc)}, status=400)
    payout.status = 'processing'; payout.details = {**details, 'recipient_code': recipient, 'transfer_code': transfer.get('transfer_code'), 'reference': reference}
    payout.save(update_fields=['status', 'details'])
    return Response(PayoutSerializer(payout).data)
