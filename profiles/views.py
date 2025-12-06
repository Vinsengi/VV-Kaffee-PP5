# profiles/views.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST

from .forms import ProfileForm
from .models import Profile
from orders.models import Order
from versohnung_und_vergebung_kaffee.staff_mode import (
    get_staff_mode,
    is_worker,
    set_staff_mode,
    staff_roles,
)


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
    if is_worker(request.user) and get_staff_mode(request):
        messages.info(request, "You're in work mode. Redirecting to fulfillment queue.")
        return redirect("orders:fulfillment_paid_orders")

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
    if is_worker(request.user) and get_staff_mode(request):
        messages.info(request, "You're in work mode. Redirecting to fulfillment queue.")
        return redirect("orders:fulfillment_paid_orders")

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
    if is_worker(request.user) and get_staff_mode(request):
        messages.info(request, "You're in work mode. Redirecting to fulfillment queue.")
        return redirect("orders:fulfillment_paid_orders")

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
        if get_staff_mode(request):
            return redirect("orders:fulfillment_paid_orders")
    # Otherwise, to their customer account dashboard
    return redirect("profiles:account_dashboard")


@login_required
@require_POST
def toggle_staff_mode(request):
    """
    Let staff/fulfillment users choose between work mode and customer mode.
    """
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"

    from versohnung_und_vergebung_kaffee.staff_mode import is_worker

    if not is_worker(request.user):
        messages.error(request, "Work mode is only available to staff or fulfillment users.")
        return redirect(next_url)

    desired_mode = request.POST.get("mode") or "staff"
    enable_staff_mode = desired_mode == "staff"

    set_staff_mode(request, enable_staff_mode)
    if enable_staff_mode:
        role_label = ", ".join(staff_roles(request.user))
        messages.success(
            request,
            f"Staff mode enabled. Showing staff tools for: {role_label or 'staff'}.",
        )
    else:
        messages.info(
            request,
            "Customer mode enabled. Staff links are hidden so you can shop normally.",
        )

    return redirect(next_url)
