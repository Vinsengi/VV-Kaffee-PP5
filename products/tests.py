from django.contrib.auth.models import User
from django.contrib.staticfiles import storage as static_storage
from django.contrib.staticfiles.storage import StaticFilesStorage
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Product


@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class StaffProductViewTests(TestCase):
    def setUp(self):
        self._original_storage = static_storage.staticfiles_storage
        static_storage.staticfiles_storage = StaticFilesStorage()
        self.addCleanup(self._restore_static_storage)
        self.staff = User.objects.create_user("staff", password="pw", is_staff=True)
        self.product = Product.objects.create(
            name="Test Coffee",
            sku="SKU123",
            price=10,
            weight_grams=250,
            stock=5,
        )

    def test_login_required_for_staff_pages(self):
        url = reverse("products:staff_product_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def _restore_static_storage(self):
        static_storage.staticfiles_storage = self._original_storage

    def test_negative_stock_rejected(self):
        client = Client()
        client.login(username="staff", password="pw")
        url = reverse("products:staff_product_update", args=[self.product.pk])
        response = client.post(
            url,
            {
                "name": self.product.name,
                "sku": self.product.sku,
                "price": "10.00",
                "weight_grams": 250,
                "stock": -1,
                "available_grinds": "whole",
                "roast_type": "medium",
                "is_active": "on",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
        self.assertIn(
            "Inventory cannot be negative.",
            response.context["form"].errors.get("stock", []),
        )
