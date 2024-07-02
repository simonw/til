# Mocking Stripe signature checks in a pytest fixture

I'm writing some code that accepts webhooks from Stripe. I wanted to simulate hits to this endpoint in my Django tests. Stripe uses a `Stripe-Signature` header and I wanted a way to mock my code so that I didn't need to calculate the correct signature.

Here's the pattern I used:

```python
import pytest
from unittest.mock import patch

@pytest.fixture
def mock_stripe_verify_header():
    with patch("stripe.WebhookSignature.verify_header") as mock_verify:
        mock_verify.return_value = None
        yield mock_verify
```
This gives me a `mock_stripe_verify_header` fixture which I can pass to a test function in order to cause the `verify_header()` method in the Stripe library to always pass - as opposed to raising exceptions, which it does when the signature check fails. The corresponding Django view code that uses this API does so via `stripe.Webhook.construct_event()` and looks like this:

```python
@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as ex:
        # Invalid payload or signature
        return HttpResponse(status=400, content=json.dumps({"error": str(ex)}))
```
Now I can write tests like this one:
```python
STRIPE_PAYLOAD = {
    "id": "evt_test123",
    "object": "event",
    "type": "payment_intent.succeeded",
    "created": 1630000000,
    "data": {
        "object": {
            "id": "pi_test123",
            "object": "payment_intent",
            "amount": 1000,
            "currency": "usd",
        }
    },
    "livemode": False,
    "api_version": "2020-08-27",
}

@pytest.mark.django_db
def test_valid_webhook(client, mock_stripe_verify_header):
    response = client.post(
        WEBHOOK_URL,
        data=json.dumps(STRIPE_PAYLOAD),
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="ignored",
    )
    assert response.status_code == 200
```
Or if I want to test what happens when the signature check fails, I can use `mock_stripe_verify_header.side_effect` to cause it to trigger the expected exception:
```python
def test_invalid_webhook(client, mock_stripe_verify_header):
    mock_stripe_verify_header.side_effect = SignatureVerificationError(
        "Invalid signature", sig_header="ignored"
    )
    response = client.post(
        WEBHOOK_URL,
        data=json.dumps(STRIPE_PAYLOAD),
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="ignored",
    )
    assert response.status_code == 400
    assert response.content == b'{"error": "Invalid signature"}'
```
