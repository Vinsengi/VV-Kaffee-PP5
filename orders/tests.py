from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.staticfiles import storage as static_storage
from django.contrib.staticfiles.storage import StaticFilesStorage
from django.core import mail
from django.test import Client, TestCase, override_settings
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


@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class StaffOrderViewTests(TestCase):
    def setUp(self):
        self._original_storage = static_storage.staticfiles_storage
        static_storage.staticfiles_storage = StaticFilesStorage()
        self.addCleanup(self._restore_static_storage)
        self.staff = User.objects.create_user("staff", password="pw", is_staff=True)
        self.customer = User.objects.create_user("cust", password="pw")
        self.product = Product.objects.create(
            name="Filter Roast",
            sku="F001",
            price=12,
            weight_grams=250,
            stock=10,
        )
        self.order = Order.objects.create(
            user=self.customer,
            full_name="Test Customer",
            email="test@example.com",
            street="Street",
            city="City",
            postal_code="12345",
            house_number="1",
            country="Germany",
            status="paid",
            total=12,
            subtotal=12,
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name_snapshot=self.product.name,
            unit_price=self.product.price,
            quantity=1,
            grind="whole",
            weight_grams=250,
        )
        self.client = Client()

    def _restore_static_storage(self):
        static_storage.staticfiles_storage = self._original_storage

    def test_staff_login_required(self):
        response = self.client.get(reverse("orders:staff_order_list"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_invalid_status_transition_blocked(self):
        self.client.login(username="staff", password="pw")
        url = reverse("orders:staff_order_update", args=[self.order.pk])
        response = self.client.post(url, {"status": "new", "notes": ""})
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "paid")
        self.assertContains(response, "Invalid status change")

    def test_fulfilling_sets_timestamp(self):
        self.client.login(username="staff", password="pw")
        url = reverse("orders:staff_order_update", args=[self.order.pk])
        response = self.client.post(url, {"status": "fulfilled", "notes": "Packed"})
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "fulfilled")
        self.assertIsNotNone(self.order.fulfilled_at)