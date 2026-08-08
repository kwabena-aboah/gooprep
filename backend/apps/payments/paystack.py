"""Small Paystack client used by lesson, subscription, and payout flows."""
import httpx
from django.conf import settings

PAYSTACK_BASE = 'https://api.paystack.co'


def _headers():
    return {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }


def initialize(email, amount, reference, callback_url, metadata=None):
    response = httpx.post(
        f'{PAYSTACK_BASE}/transaction/initialize',
        headers=_headers(),
        json={
            'email': email,
            'amount': int(round(float(amount) * 100)),
            'reference': reference,
            'callback_url': callback_url,
            'metadata': metadata or {},
        },
        timeout=15,
    )
    data = response.json()
    if response.status_code >= 400 or not data.get('status'):
        raise ValueError(data.get('message', 'Paystack initialization failed.'))
    return data['data']


def verify(reference):
    response = httpx.get(
        f'{PAYSTACK_BASE}/transaction/verify/{reference}',
        headers=_headers(),
        timeout=15,
    )
    data = response.json()
    if response.status_code >= 400 or not data.get('status'):
        raise ValueError(data.get('message', 'Paystack verification failed.'))
    return data['data']


def create_transfer_recipient(name, account_number, bank_code):
    response = httpx.post(
        f'{PAYSTACK_BASE}/transferrecipient', headers=_headers(),
        json={'type': 'nuban', 'name': name, 'account_number': account_number, 'bank_code': bank_code},
        timeout=15,
    )
    data = response.json()
    if response.status_code >= 400 or not data.get('status'):
        raise ValueError(data.get('message', 'Paystack recipient creation failed.'))
    return data['data']['recipient_code']


def create_transfer(amount, recipient_code, reference, reason):
    response = httpx.post(
        f'{PAYSTACK_BASE}/transfer', headers=_headers(),
        json={'source': 'balance', 'amount': int(round(float(amount) * 100)),
              'recipient': recipient_code, 'reference': reference, 'reason': reason},
        timeout=15,
    )
    data = response.json()
    if response.status_code >= 400 or not data.get('status'):
        raise ValueError(data.get('message', 'Paystack transfer failed.'))
    return data['data']
