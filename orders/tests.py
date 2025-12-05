from decimal import Decimal
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from orders.models import Order, OrderItem
from products.models import Category, Product


class PaidEmailFlowTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Filter")
        product = Product.objects.create(
            name="Filter Roast",
            sku="FIL-1",
            category=category,
            price=Decimal("12.50"),
            stock=5,
            weight_grams=250,
        )

        self.order = Order.objects.create(
            full_name="Test Customer",
            email="customer@example.com",
            phone_number="",
            street="Teststraße",
            house_number="5",
            city="Berlin",
            postal_code="10115",
            country="Germany",
            status="new",
            payment_intent_id="pi_12345",
            subtotal=Decimal("12.50"),
            shipping=Decimal("0.00"),
            total=Decimal("12.50"),
        )

        OrderItem.objects.create(
            order=self.order,
            product=product,
            product_name_snapshot=product.name,
            unit_price=product.price,
            quantity=1,
            grind="whole",
            weight_grams=product.weight_grams,
        )

        self.webhook_payload = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "metadata": {"order_id": str(self.order.id)},
                    "id": self.order.payment_intent_id,
                }
            },
        }

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        ORDER_NOTIFICATION_EMAILS=["ops@example.com"],
        DEFAULT_FROM_EMAIL="shop@example.com",
    )
    @patch("orders.views.stripe.Webhook.construct_event")
    def test_webhook_sends_customer_and_internal_notifications(self, construct_event):
        construct_event.return_value = self.webhook_payload

        response = self.client.post(
            reverse("orders:stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "paid")

        self.assertEqual(len(mail.outbox), 2)
        recipients = [tuple(msg.to) for msg in mail.outbox]
        self.assertIn(("customer@example.com",), recipients)
        self.assertIn(("ops@example.com",), recipients)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        ORDER_NOTIFICATION_EMAILS=[],
        DEFAULT_FROM_EMAIL="shop@example.com",
    )
    @patch("orders.views.stripe.Webhook.construct_event")
    def test_webhook_sends_customer_even_without_internal_recipients(self, construct_event):
        construct_event.return_value = self.webhook_payload

        response = self.client.post(
            reverse("orders:stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "paid")

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["customer@example.com"])
