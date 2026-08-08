from django.urls import path
from .views import (
    TransactionListView, PayoutListView, DisputeListView,
    paystack_webhook, initiate_payment, verify_payment,
    SubscriptionView, SubscriptionStatusView, process_payout,
)
urlpatterns = [
    path('transactions/',        TransactionListView.as_view(), name='transactions'),
    path('payouts/',             PayoutListView.as_view(),      name='payouts'),
    path('disputes/',            DisputeListView.as_view(),     name='disputes'),
    path('paystack/webhook/',    paystack_webhook,              name='paystack_webhook'),
    path('initiate/',              initiate_payment,                name='initiate_payment'),
    path('verify/',                verify_payment,                  name='verify_payment'),
    path('subscriptions/',         SubscriptionView.as_view(),      name='subscriptions'),
    path('subscriptions/status/',  SubscriptionStatusView.as_view(), name='subscription_status'),
    path('payouts/<int:pk>/process/', process_payout,               name='process_payout'),
]
