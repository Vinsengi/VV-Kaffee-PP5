from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    cost_price = forms.DecimalField(min_value=0, max_digits=8, decimal_places=2, help_text="Cost to acquire/produce (EUR).")
    markup_percent = forms.DecimalField(min_value=0, max_digits=5, decimal_places=2, help_text="Markup as percentage (e.g., 25 = 25%).")
    price = forms.DecimalField(min_value=0, max_digits=8, decimal_places=2, disabled=True, required=False, label="Sale price (cost + markup%)")
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
        cost = cleaned.get("cost_price") or 0
        pct = cleaned.get("markup_percent") or 0
        cleaned["price"] = cost * (1 + pct / 100)
        return cleaned
