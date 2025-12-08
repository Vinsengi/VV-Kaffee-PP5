from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from orders.models import Order
from products.models import Product
from .utils import CART_SESSION_KEY, cart_from_session, compute_summary, grind_label


def cart_detail(request):
    cart = cart_from_session(request.session)
    cart_items, subtotal, shipping, total = compute_summary(cart)
    grind_choices = [(g, grind_label(g)) for g in ["whole", "espresso", "filter", "french_press"]]
    return render(
        request,
        "cart/cart.html",
        {
            "cart_items": cart_items,
            "subtotal": subtotal,
            "shipping": shipping,
            "total": total,
            "grind_choices": grind_choices,
        },
    )


def cart_add(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    cart = cart_from_session(request.session)

    qty = int(request.POST.get("quantity", 1))
    grind = (request.POST.get("grind") or "whole").strip()

    price = product.price
    weight = product.weight_grams
    sku = product.sku

    key = product.slug
    if key not in cart:
        cart[key] = {
            "key": key,
            "slug": key,
            "product_slug": product.slug,
            "name": product.name,
            "price": str(price),
            "quantity": 0,
            "grind": grind,
            "weight_grams": weight,
            "sku": sku,
            "variant_label": "",
            "image_url": product.image.url if product.image else "",
        }
    cart[key]["quantity"] += qty
    cart[key]["grind"] = grind
    cart[key]["price"] = str(price)
    cart[key]["weight_grams"] = weight
    cart[key]["sku"] = sku
    cart[key]["variant_label"] = ""
    request.session.modified = True

    label = product.name
    messages.success(request, f"Added {qty} x {label} to cart.")
    return redirect("cart:detail")


def cart_update(request, slug):
    cart = cart_from_session(request.session)
    if slug in cart:
        qty = max(1, int(request.POST.get("quantity", 1)))
        grind = (request.POST.get("grind") or cart[slug]["grind"]).strip()
        cart[slug]["quantity"] = qty
        cart[slug]["grind"] = grind
        request.session.modified = True
        messages.success(request, "Cart updated.")
    return redirect("cart:detail")


def cart_remove(request, slug):
    cart = cart_from_session(request.session)
    if slug in cart:
        del cart[slug]
        request.session.modified = True
        messages.info(request, "Item removed from cart.")
    return redirect("cart:detail")


def cart_clear(request):
    request.session[CART_SESSION_KEY] = {}
    request.session.modified = True
    messages.info(request, "Cart cleared.")
    return redirect("cart:detail")


def buy_again(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = cart_from_session(request.session)

    for item in order.items.all():
        product = item.product
        key = product.slug
        if key not in cart:
            cart[key] = {
                "key": key,
                "slug": key,
                "product_slug": product.slug,
                "name": product.name,
                "price": str(product.price),
                "quantity": 0,
                "grind": getattr(item, "grind", "whole"),
                "weight_grams": product.weight_grams,
                "sku": product.sku,
                "variant_label": "",
                "image_url": product.image.url if product.image else "",
            }
        cart[key]["quantity"] += item.quantity
        if hasattr(item, "grind"):
            cart[key]["grind"] = item.grind

    request.session.modified = True
    messages.success(request, "Order items added to cart.")
    return redirect("cart:detail")
