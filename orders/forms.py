from django import forms
from django.utils import timezone

from .models import Order


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        label="Full name",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label="Phone",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    street = forms.CharField(
        max_length=120,
        label="Street",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    house_number = forms.CharField(
        max_length=10,
        required=False,
        label="House Number",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    city = forms.CharField(
        max_length=80,
        label="City",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    postal_code = forms.CharField(
        max_length=20,
        label="Postal code / PLZ",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    country = forms.CharField(
        max_length=60,
        initial="Germany",
        label="Country",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )


class StaffOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status", "notes"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.original_status = None
        instance = kwargs.get("instance")
        if instance:
            self.original_status = instance.status
        super().__init__(*args, **kwargs)

    def clean_status(self):
        new_status = self.cleaned_data["status"]
        current = self.original_status or self.instance.status or "new"

        allowed_transitions = {
            "new": {"pending_fulfillment", "paid", "cancelled"},
            "pending_fulfillment": {"paid", "fulfilled", "cancelled"},
            "paid": {"fulfilled", "refunded", "cancelled"},
            "fulfilled": {"refunded"},
            "cancelled": set(),
            "refunded": set(),
        }

        if new_status == current:
            return new_status

        # Once cancelled/refunded, no other transitions are allowed
        if current in {"cancelled", "refunded"}:
            raise forms.ValidationError("Completed orders cannot be reopened.")

        # Fulfilled orders can only move to refunded
        if current == "fulfilled" and new_status != "refunded":
            raise forms.ValidationError("Fulfilled orders can only be refunded.")

        if new_status not in allowed_transitions.get(current, set()):
            raise forms.ValidationError(
                "Invalid status change for the current workflow."
            )
        return new_status

    def save(self, commit=True):
        order = super().save(commit=False)
        new_status = self.cleaned_data.get("status")
        if new_status == "fulfilled" and not order.fulfilled_at:
            order.fulfilled_at = timezone.now()
        elif new_status != "fulfilled":
            order.fulfilled_at = None

        if commit:
            order.save()
        return order


class OrderCustomerEditForm(forms.ModelForm):
    """
    Minimal edit form for customers to fix contact/shipping details
    before payment.
    """

    class Meta:
        model = Order
        fields = [
            "full_name",
            "email",
            "phone_number",
            "street",
            "house_number",
            "city",
            "postal_code",
            "country",
            "notes",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "street": forms.TextInput(attrs={"class": "form-control"}),
            "house_number": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
