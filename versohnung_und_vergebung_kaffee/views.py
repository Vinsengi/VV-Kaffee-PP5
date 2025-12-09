from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .staff_mode import is_worker


@login_required
def staff_admin_hub(request):
    user = request.user
    if not is_worker(user):
        return redirect("home")

    can_manage_products = (
        user.has_perm("products.view_product")
        or user.has_perm("products.add_product")
        or user.has_perm("products.change_product")
        or user.has_perm("products.delete_product")
    )

    can_manage_orders = (
        user.has_perm("orders.view_order")
        or user.has_perm("orders.add_order")
        or user.has_perm("orders.change_order")
        or user.has_perm("orders.delete_order")
    )

    can_manage_fulfillment = (
        user.has_perm("orders.view_fulfillment")
        or user.groups.filter(name="Fulfillment Department").exists()
    )

    can_use_admin = bool(user.is_staff)

    context = {
        "can_manage_products": can_manage_products,
        "can_manage_orders": can_manage_orders,
        "can_manage_fulfillment": can_manage_fulfillment,
        "can_use_admin": can_use_admin,
    }
    return render(request, "staff_admin_hub.html", context)
