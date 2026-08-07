from django.urls import path
from .views import TransactionListView, PayoutListView, DisputeListView, paystack_webhook, initiate_payment
urlpatterns = [
    path('transactions/',        TransactionListView.as_view(), name='transactions'),
    path('payouts/',             PayoutListView.as_view(),      name='payouts'),
    path('disputes/',            DisputeListView.as_view(),     name='disputes'),
    path('paystack/webhook/',    paystack_webhook,              name='paystack_webhook'),
    path('initiate/',            initiate_payment,              name='initiate_payment'),
]
