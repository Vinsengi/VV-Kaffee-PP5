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
