from decimal import Decimal, ROUND_HALF_UP

from django import forms

from .models import Product, ProductBatch, PackVariant


class CommaDecimalField(forms.DecimalField):
    """Accept both comma and dot decimal separators."""

    def to_python(self, value):
        if isinstance(value, str):
            value = value.replace(",", ".")
        return super().to_python(value)


class ProductForm(forms.ModelForm):
    cost_price = CommaDecimalField(
        min_value=0,
        max_digits=8,
        decimal_places=2,
        help_text="Cost to acquire/produce (EUR).",
    )
    markup_percent = CommaDecimalField(
        min_value=0,
        max_digits=5,
        decimal_places=2,
        help_text="Markup as percentage (e.g., 25 = 25%).",
    )
    price = CommaDecimalField(
        min_value=0,
        max_digits=8,
        decimal_places=2,
        disabled=True,
        required=False,
        label="Sale price (cost + markup%)",
    )
    weight_grams = forms.IntegerField(min_value=1)
    stock = forms.IntegerField(
        min_value=0,
        required=False,
        error_messages={"min_value": "Inventory cannot be negative."},
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "category",
            "origin",
            "farm",
            "variety",
            "altitude_masl",
            "process",
            "roast_type",
            "tasting_notes",
            "cost_price",
            "markup_percent",
            "price",
            "weight_grams",
            "available_grinds",
            "stock",
            "is_active",
            "image",
            "description",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "tasting_notes": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }

    def clean_available_grinds(self):
        raw = self.cleaned_data.get("available_grinds", "") or ""
        values = [v.strip() for v in raw.split(",") if v.strip()]
        valid_keys = {choice[0] for choice in Product.GRIND_CHOICES}
        invalid = [v for v in values if v not in valid_keys]
        if invalid:
            raise forms.ValidationError(
                f"Invalid grind options: {', '.join(invalid)}"
            )
        return ",".join(values)

    def clean(self):
        cleaned = super().clean()
        cost = cleaned.get("cost_price") or Decimal("0")
        pct = cleaned.get("markup_percent") or Decimal("0")
        price = cost * (Decimal("1") + (pct / Decimal("100")))
        cleaned["price"] = price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return cleaned


class ProductBatchForm(forms.ModelForm):
    class Meta:
        model = ProductBatch
        fields = ["quantity_grams", "remaining_grams", "unit_cost", "note"]
        widgets = {
            "note": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned = super().clean()
        qty = cleaned.get("quantity_grams") or 0
        rem = cleaned.get("remaining_grams")
        if rem is None:
            cleaned["remaining_grams"] = qty
        elif rem > qty:
            raise forms.ValidationError("Remaining grams cannot exceed received grams.")
        return cleaned


class PackVariantForm(forms.ModelForm):
    class Meta:
        model = PackVariant
        fields = ["name", "sku", "pack_weight_grams", "price", "markup_percent", "is_active"]
