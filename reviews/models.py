"""Customer review and feedback models."""

from django.conf import settings
from django.db import models

from products.models import Product


class ProductReview(models.Model):
    """Product-specific rating written by an authenticated user."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="product_reviews")
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    title = models.CharField(max_length=120, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.product} · {self.user} · {self.rating}★"

    @property
    def is_positive(self) -> bool:
        """Highlight 4–5 star reviews for merchandising."""

        return self.rating >= 4

    def display_title(self) -> str:
        """Fallback to product name when no title is provided."""

        return self.title or f"Review for {self.product.name}"


class ExperienceFeedback(models.Model):
    """Overall store experience feedback, optionally linked to an order."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.OneToOneField("orders.Order", on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        who = self.user or "Anonymous"
        oid = self.order_id or "—"
        return f"Experience {self.rating}★ by {who} (order #{oid})"
