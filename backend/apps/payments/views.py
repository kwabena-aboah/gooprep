import hmac, hashlib, json
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from .models import Transaction, Payout, Dispute
from .serializers import TransactionSerializer, PayoutSerializer, DisputeSerializer

class TransactionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        qs = Transaction.objects.filter(payer=request.user).order_by('-created_at')
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
        from tutors.models import TutorProfile
        try: tp = TutorProfile.objects.get(user=request.user)
        except: return Response({'error':'Tutor profile not found.'}, status=400)
        amount = float(request.data.get('amount',0))
        if amount < float(settings.MIN_PAYOUT):
            return Response({'error':f'Minimum payout is GHS {settings.MIN_PAYOUT}.'}, status=400)
        if float(tp.pending_payout) < amount:
            return Response({'error':'Insufficient balance.'}, status=400)
        payout = Payout.objects.create(tutor=request.user, amount=amount,
            method=request.data.get('method','mtn_momo'), details=request.data.get('details',{}))
        tp.pending_payout = float(tp.pending_payout) - amount
        tp.save(update_fields=['pending_payout'])
        try:
            from messaging.guppy import get_or_create_guppy_user, send_push_notification
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
        from scheduling.models import Lesson
        try: lesson = Lesson.objects.get(id=request.data.get('lesson'))
        except: return Response({'error':'Lesson not found.'}, status=400)
        d = Dispute.objects.create(lesson=lesson, filed_by=request.user,
            reason=request.data.get('reason',''), amount=lesson.price)
        return Response(DisputeSerializer(d).data, status=201)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def paystack_webhook(request):
    sig    = request.headers.get('x-paystack-signature','')
    secret = settings.PAYSTACK_SECRET_KEY
    if secret:
        expected = hmac.new(secret.encode(), request.body, hashlib.sha512).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return Response({'error':'Invalid signature.'}, status=403)
    try:
        event = json.loads(request.body)
        if event.get('event') == 'charge.success':
            ref = event['data'].get('reference','')
            try:
                txn = Transaction.objects.get(paystack_ref=ref)
                txn.status = 'success'; txn.save(update_fields=['status'])
                if txn.lesson:
                    txn.lesson.payment_status = 'paid'; txn.lesson.save(update_fields=['payment_status'])
                    from tutors.models import TutorProfile
                    try:
                        tp = TutorProfile.objects.get(user=txn.lesson.tutor)
                        net = txn.amount * (1 - settings.PLATFORM_COMMISSION)
                        tp.pending_payout += net; tp.total_earnings += net
                        tp.save(update_fields=['pending_payout','total_earnings'])
                    except: pass
                    try:
                        from messaging.guppy import notify_payment_received
                        notify_payment_received(txn)
                    except: pass
            except Transaction.DoesNotExist: pass
    except Exception: pass
    return Response({'received':True})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def initiate_payment(request):
    """Initiate Paystack payment and return authorization URL."""
    import httpx, uuid
    lesson_id = request.data.get('lesson_id')
    method    = request.data.get('payment_method','card')
    from scheduling.models import Lesson
    try: lesson = Lesson.objects.get(id=lesson_id, student=request.user)
    except: return Response({'error':'Lesson not found.'}, status=404)
    ref = f'gooprep-{uuid.uuid4().hex[:16]}'
    txn = Transaction.objects.create(payer=request.user, lesson=lesson,
        amount=lesson.price, payment_method=method, paystack_ref=ref,
        description=f'Lesson with {lesson.tutor.get_full_name()}')
    secret = settings.PAYSTACK_SECRET_KEY
    if not secret:
        return Response({'error':'Paystack not configured.','ref':ref}, status=503)
    try:
        r = httpx.post('https://api.paystack.co/transaction/initialize',
            headers={'Authorization':f'Bearer {secret}','Content-Type':'application/json'},
            json={'email':request.user.email,'amount':int(float(lesson.price)*100),
                  'reference':ref,'callback_url':f'{settings.FRONTEND_URL}/payments/verify'},
            timeout=10)
        data = r.json()
        if data.get('status'):
            return Response({'authorization_url':data['data']['authorization_url'],'reference':ref})
        return Response({'error':data.get('message','Payment initiation failed.')}, status=400)
    except Exception as e:
        return Response({'error':str(e)}, status=500)