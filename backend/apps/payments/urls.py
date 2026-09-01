from django.urls import path
from .views import (
    TransactionListView, PayoutListView, DisputeListView,
    paystack_webhook, initiate_payment, verify_payment,
    process_payout,
)
urlpatterns = [
    path('transactions/',        TransactionListView.as_view(), name='transactions'),
    path('payouts/',             PayoutListView.as_view(),      name='payouts'),
    path('disputes/',            DisputeListView.as_view(),     name='disputes'),
    path('paystack/webhook/',    paystack_webhook,              name='paystack_webhook'),
    path('initiate/',              initiate_payment,                name='initiate_payment'),
    path('verify/',                verify_payment,                  name='verify_payment'),
    # Subscription plans have been retired. Historical subscription records remain for audit purposes.

    path('payouts/<int:pk>/process/', process_payout,               name='process_payout'),
]
