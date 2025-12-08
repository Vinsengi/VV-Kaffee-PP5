"""Product catalogue models."""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from django.db import models
from django.db.models import Avg
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Simple classification for products."""

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Populate a slug by default for friendlier URLs."""

        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Coffee product with provenance and merchandising details."""

    ROAST_CHOICES = [
        ("light", "Light Roast"),
        ("medium", "Medium Roast"),
        ("dark", "Dark Roast"),
    ]
    GRIND_CHOICES = [
        ("whole", "Whole Beans"),
        ("espresso", "Espresso Grind"),
        ("filter", "Filter Grind"),
        ("french_press", "French Press"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    sku = models.CharField(max_length=30, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    # Coffee specifics
    origin = models.CharField(max_length=120, default="Rwanda")
    farm = models.CharField(max_length=120, blank=True)
    variety = models.CharField(max_length=120, blank=True)
    altitude_masl = models.PositiveIntegerField(null=True, blank=True)
    process = models.CharField(max_length=120, blank=True)
    roast_type = models.CharField(max_length=20, choices=ROAST_CHOICES, default="medium")
    tasting_notes = models.CharField(max_length=200, blank=True)

    # Commercial
    cost_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # EUR
    markup_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percent
    price = models.DecimalField(max_digits=8, decimal_places=2)  # EUR (stored sale price)
    weight_grams = models.PositiveIntegerField(default=250)
    available_grinds = models.CharField(max_length=120, default="whole")  # comma list of GRIND_CHOICES keys

    # Inventory & media
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["sku"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.weight_grams}g)"

    def save(self, *args, **kwargs) -> None:
        """Ensure a stable slug and keep stored price in sync with cost + markup%."""

        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.weight_grams}")

        sale_price = self.sale_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.price = sale_price
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("products:product_detail", kwargs={"slug": self.slug})

    @property
    def weight_kg(self) -> Decimal:
        """Return weight in kilograms for display consistency."""

        return Decimal(self.weight_grams) / Decimal(1000)

    @property
    def is_in_stock(self) -> bool:
        """Indicate whether the product can be purchased right now."""

        return self.is_active and self.stock > 0

    @property
    def available_grind_list(self) -> List[str]:
        """List of permitted grind keys for validation/UI assistance."""

        return [choice.strip() for choice in self.available_grinds.split(",") if choice.strip()]

    def average_rating(self) -> Optional[Decimal]:
        """Average product rating rounded to 1 decimal place."""

        result = self.reviews.aggregate(avg_rating=Avg("rating"))
        avg = result.get("avg_rating")
        if avg is None:
            return None
        return Decimal(str(avg)).quantize(Decimal("0.1"))

    def review_count(self) -> int:
        """Number of submitted reviews for the product."""

        return self.reviews.count()

    def display_price(self) -> str:
        """Human-readable price label for admin and templates."""

        return f"€{self.price:.2f}"

    @property
    def sale_price(self) -> Decimal:
        """Computed sale price based on cost + markup%."""
        cost = self.cost_price or Decimal("0.00")
        pct = self.markup_percent or Decimal("0.00")
        return cost * (Decimal("1.00") + (pct / Decimal("100")))

    @property
    def batch_remaining_grams(self) -> Decimal:
        """Total remaining grams across batches."""
        total = sum((b.remaining_grams or 0) for b in getattr(self, "batches", []).all())
        return Decimal(total)

    @property
    def batch_remaining_kg(self) -> Decimal:
        """Total remaining kg across batches."""
        return (self.batch_remaining_grams / Decimal(1000)).quantize(Decimal("0.001"))

    @property
    def batch_total_cost(self) -> Decimal:
        """Total cost of remaining stock across batches (FIFO-aware store)."""
        total = Decimal("0.00")
        for b in getattr(self, "batches", []).all():
            grams = Decimal(b.remaining_grams or 0)
            kg = grams / Decimal(1000)
            total += kg * (b.unit_cost or Decimal("0.00"))
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def batch_expected_revenue(self) -> Decimal:
        """Expected revenue for remaining stock at current sale price."""
        price = self.price or Decimal("0.00")
        kg = self.batch_remaining_kg
        return (price * kg).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def batch_stock_units(self) -> int:
        """Approximate units in stock based on batches and unit weight."""
        weight = Decimal(self.weight_grams or 1)
        total_remaining = sum(
            (Decimal(b.remaining_grams or 0) for b in getattr(self, "batches", []).all()),
            Decimal("0"),
        )
        if weight <= 0:
            return 0
        # Use floor to avoid overstating stock
        return int(total_remaining // weight)

    def recalc_stock_from_batches(self) -> None:
        """Recompute stock units from remaining grams across batches."""
        self.stock = max(0, self.batch_stock_units())
        self.save(update_fields=["stock"])

    def consume_grams_fifo(self, grams_needed: Decimal) -> Decimal:
        """
        Reduce remaining_grams from batches in FIFO order.
        Returns grams actually consumed.
        """
        if grams_needed <= 0:
            return Decimal("0.00")

        consumed = Decimal("0.00")
        batches = list(self.batches.order_by("received_at", "id"))
        remaining = Decimal(grams_needed)

        for batch in batches:
            avail = Decimal(batch.remaining_grams or 0)
            if avail <= 0:
                continue
            take = min(avail, remaining)
            batch.remaining_grams = int(avail - take)
            batch.save(update_fields=["remaining_grams"])
            consumed += take
            remaining -= take
            if remaining <= 0:
                break

        # optionally sync stock to remaining grams / unit weight
        try:
            total_remaining = sum((Decimal(b.remaining_grams or 0) for b in self.batches.all()), Decimal("0"))
            weight = Decimal(self.weight_grams or 1)
            approx_units = int(total_remaining // weight) if weight > 0 else 0
            self.stock = int(max(0, approx_units))
            self.save(update_fields=["stock"])
        except Exception:
            pass

        return consumed


class ProductBatch(models.Model):
    """Track inventory receipts to support FIFO costing."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="batches")
    received_at = models.DateTimeField(auto_now_add=True)
    quantity_grams = models.PositiveIntegerField(default=0)
    remaining_grams = models.PositiveIntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-received_at"]

    def __str__(self):
        return f"{self.product.name} batch ({self.remaining_grams}g remaining)"

    def save(self, *args, **kwargs):
        if self.remaining_grams is None or self.remaining_grams == 0:
            self.remaining_grams = self.quantity_grams
        super().save(*args, **kwargs)
        try:
            self.product.recalc_stock_from_batches()
        except Exception:
            pass
