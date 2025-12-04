# profiles/views.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect

from .forms import ProfileForm
from .models import Profile
from orders.models import Order


def _ensure_profile(user) -> Profile:
    """
    Make sure the logged-in user has a Profile.
    Returns the Profile instance (created if missing).
    """
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={
            # Safe defaults so NOT NULL constraints are satisfied
            "street": "",
            "house_number": 0,
            "postcode": "",
            "city": "",
            "country": "Germany",
        },
    )
    return profile


@login_required
def account_dashboard(request):
    """
    Simple account hub: shows profile summary + recent orders.
    """
    profile = _ensure_profile(request.user)
    # Most recent 10 orders for this user
    orders = (
        Order.objects.filter(user=request.user)
        .order_by("-created_at")
        .prefetch_related("items")
    )[:10]

    return render(
        request,
        "profiles/account_dashboard.html",
        {
            "profile": profile,
            "orders": orders,
        },
    )


@login_required
def profile_edit(request):
    """
    Edit the user's profile (contact + shipping).
    """
    profile = _ensure_profile(request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profiles:account_dashboard")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "profiles/profile_edit.html", {"form": form})


# Optional: dedicated order views under profiles (nice shortcuts for users)

@login_required
def order_list(request):
    """
    List all orders belonging to the logged-in user.
    """
    orders = (
        Order.objects.filter(user=request.user)
        .order_by("-created_at")
        .prefetch_related("items")
    )
    return render(request, "profiles/order_list.html", {"orders": orders})


@login_required
def order_detail(request, order_id: int):
    """
    Show one order (must belong to the logged-in user).
    """
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        pk=order_id,
        user=request.user,
    )
    return render(request, "profiles/order_detail.html", {"order": order})


@login_required
def post_login_redirect(request):
    # If the user is fulfillment staff, always send them to the staff screen
    if (
        request.user.groups.filter(name="Fulfillment Department").exists()
        or request.user.has_perm("orders.view_fulfillment")
    ):
        return redirect("orders:fulfillment_paid_orders")
    # Otherwise, to their customer account dashboard
    return redirect("profiles:account_dashboard")
