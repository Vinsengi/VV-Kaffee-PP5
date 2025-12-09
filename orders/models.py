"""Order and order item domain models."""

from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from products.models import Product


class Order(models.Model):
    """Customer checkout capturing payment and fulfillment lifecycle."""

    STATUS_CHOICES = [
        ("new", "New"),
        ("pending_fulfillment", "Pending fulfillment"),
        ("paid", "Paid"),
        ("fulfilled", "Fulfilled"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    fulfilled_at = models.DateTimeField(null=True, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )

    # Contact & shipping (Germany-focused but generic)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)

    street = models.CharField(max_length=120)
    house_number = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=80)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=60, default="Germany")

    # Payment/fulfillment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    payment_intent_id = models.CharField(max_length=120, blank=True)  # Stripe PaymentIntent id
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            ("view_fulfillment", "Can access fulfillment (paid picklists)"),
            ("change_fulfillment_status", "Can mark orders fulfilled"),
        ]

    def __str__(self) -> str:
        return f"Order #{self.id} - {self.full_name}"

    def recalc_totals(self, save: bool = True) -> None:
        """Recompute monetary totals from line items.

        The method can be called without persisting to the database to ease
        testing and allow callers to decide when to save.
        """

        subtotal = sum((item.line_total for item in self.items.all()), Decimal("0.00"))
        self.subtotal = subtotal
        # Simple shipping rule example: €4.90 under €39, else free
        self.shipping = Decimal("0.00") if subtotal >= Decimal("39.00") else Decimal("4.90")
        self.total = (self.subtotal + self.shipping).quantize(Decimal("0.01"))
        if save:
            self.save(update_fields=["subtotal", "shipping", "total"])

    @property
    def reference(self) -> str:
        """Human-friendly reference used in receipts and admin."""

        return f"VV-{self.id:06d}"

    @property
    def item_count(self) -> int:
        """Total quantity of products in the order."""

        return sum((item.quantity for item in self.items.all()), 0)

    def is_paid(self) -> bool:
        """Convenience predicate to check payment state."""

        return self.status in {"paid", "fulfilled", "refunded"}


class OrderItem(models.Model):
    """Snapshot of a product inside an order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    product_name_snapshot = models.CharField(max_length=140)  # keep name at purchase time
    unit_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
        null=False,
        blank=False,
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        null=False,
        blank=False,
    )

    grind = models.CharField(max_length=30, blank=True)
    weight_grams = models.PositiveIntegerField(default=250)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.quantity} × {self.product_name_snapshot}"

    @property
    def line_total(self) -> Decimal:
        """Total price for the item line."""

        price = self.unit_price or Decimal("0.00")
        qty = self.quantity or 0
        return (price * qty).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
