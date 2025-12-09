from decimal import Decimal, ROUND_HALF_UP

CART_SESSION_KEY = "cart"
FREE_SHIPPING_THRESHOLD = Decimal("39.00")
FLAT_SHIPPING = Decimal("4.90")


def grind_label(value: str) -> str:
    """Make a human-friendly label from a grind key like 'french_press'."""
    return (value or "whole").replace("_", " ").title()


def quantize(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def cart_from_session(session) -> dict:
    """Get/create the cart dict stored in the session."""
    cart = session.get(CART_SESSION_KEY)
    if cart is None:
        cart = {}
        session[CART_SESSION_KEY] = cart
    return cart


def compute_summary(cart: dict):
    """
    Build normalized items with computed line totals,
    and return (items, subtotal, shipping, total).
    """
    items = []
    subtotal = Decimal("0.00")

    for slug_key, item in cart.items():
        price = Decimal(item["price"])
        qty = int(item.get("quantity", 1))
        line_total = quantize(price * qty)
        subtotal += line_total

        key = item.get("key") or slug_key
        product_slug = item.get("product_slug") or slug_key

        items.append({
            "key": key,
            "slug": key,  # backwards compatibility for templates using slug
            "product_slug": product_slug,
            "name": item["name"],
            "sku": item.get("sku", ""),
            "grind": item.get("grind", "whole"),
            "grind_label": grind_label(item.get("grind", "whole")),
            "quantity": qty,
            "price": quantize(price),
            "line_total": line_total,
            "image_url": item.get("image_url", ""),
            "weight_grams": item.get("weight_grams", 0),
            "variant_label": item.get("variant_label") or "",
        })

    subtotal = quantize(subtotal)
    if subtotal == Decimal("0.00"):
        shipping = Decimal("0.00")
    elif subtotal >= FREE_SHIPPING_THRESHOLD:
        shipping = Decimal("0.00")
    else:
        shipping = FLAT_SHIPPING
    shipping = quantize(shipping)
    total = quantize(subtotal + shipping)
    return items, subtotal, shipping, total
