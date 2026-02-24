from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from orders.models import Order, OrderItem
from products.models import Product
from .models import ProductReview


User = get_user_model()


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class ProductReviewIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass1234")
        self.other_user = User.objects.create_user(username="bob", password="pass1234")

        self.product = Product.objects.create(
            name="Test Coffee",
            sku="SKU123",
            price="10.00",
            weight_grams=250,
            available_grinds="whole,filter",
        )

        self.order = Order.objects.create(
            user=self.user,
            status="paid",
            full_name="Alice Test",
            email="alice@example.com",
            phone_number="",
            street="123 Brew St",
            house_number="1",
            city="Bean Town",
            postal_code="00000",
            country="Wonderland",
        )

        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name_snapshot=self.product.name,
            unit_price=self.product.price,
            quantity=1,
            weight_grams=self.product.weight_grams,
        )

    def test_product_detail_shows_existing_reviews(self):
        ProductReview.objects.create(
            product=self.product,
            user=self.other_user,
            rating=4,
            title="Great cup",
            comment="Tasty notes and smooth finish.",
        )

        response = self.client.get(self.product.get_absolute_url())

        self.assertContains(response, "Reviews")
        self.assertContains(response, "Great cup")
        self.assertContains(response, "Tasty notes")
        self.assertContains(response, "&#9733;")

    def test_authenticated_buyer_can_submit_review(self):
        self.client.login(username="alice", password="pass1234")
        url = reverse("reviews:product_review", args=[self.product.id])

        response = self.client.post(
            url,
            {"rating": 5, "title": "Loved it", "comment": "Fresh and bright."},
            follow=True,
        )

        self.assertContains(response, "Thanks for sharing your review!")
        self.assertTrue(
            ProductReview.objects.filter(
                product=self.product, user=self.user, rating=5
            ).exists()
        )
        self.assertContains(response, "Loved it")

    def test_invalid_review_shows_errors_on_product_page(self):
        self.client.login(username="alice", password="pass1234")
        url = reverse("reviews:product_review", args=[self.product.id])

        response = self.client.post(
            url, {"title": "Missing rating", "comment": "Please rate."}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        self.assertContains(response, "Leave a review")