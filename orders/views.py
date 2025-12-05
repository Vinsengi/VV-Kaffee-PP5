# orders/views.py
import json
import logging
import stripe
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from django.contrib import messages

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from products.models import Product
from cart.utils import cart_from_session, compute_summary
from .forms import CheckoutForm
from .models import Order, OrderItem
from django.contrib.admin.views.decorators import staff_member_required

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
import os
from reportlab.lib.units import cm

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.http import HttpResponseForbidden, Http404

from django.utils import timezone
from django.db.models import F
from django.views.decorators.http import require_POST
from datetime import timedelta
from .emails import send_order_pending_email
from .emails import send_order_paid_notifications

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


def _to_cents(amount_decimal: Decimal) -> int:
    # Quantize first to avoid float rounding issues
    amt = amount_decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int((amt * 100).to_integral_value(rounding=ROUND_HALF_UP))


@transaction.atomic
def checkout(request):
    cart = cart_from_session(request.session)
    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect("cart:detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # 1) Create Order (pending)
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=form.cleaned_data["full_name"],
                email=form.cleaned_data["email"],
                phone_number=form.cleaned_data.get("phone_number", ""),
                street=form.cleaned_data["street"],
                house_number=form.cleaned_data.get("house_number", ""),
                city=form.cleaned_data["city"],
                postal_code=form.cleaned_data["postal_code"],
                country=form.cleaned_data.get("country", "Germany"),
                status="new",
            )

            # 2) Copy items from session cart into OrderItems + compute totals
            items, subtotal, shipping, total = compute_summary(cart)
            for item in items:
                try:
                    product = Product.objects.get(slug=item["slug"], is_active=True)
                except Product.DoesNotExist:
                    messages.warning(
                        request,
                        f"Item '{item['name']}' is no longer available and was skipped."
                    )
                    continue

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name_snapshot=product.name,
                    unit_price=item["price"],
                    quantity=item["quantity"],
                    grind=item["grind"],
                    weight_grams=item["weight_grams"] or product.weight_grams,
                )

            order.subtotal = subtotal
            order.shipping = shipping
            order.total = total
            order.save(update_fields=["subtotal", "shipping", "total"])

            # 3) Send "pending" email (non-blocking)
            try:
                send_order_pending_email(order)
            except Exception:
                logger.exception("Pending email failed for order %s", order.id)

            # 4) Create PaymentIntent
            first_name = items[0]["name"] if items else "order"
            extra = f" +{len(items) - 1} more" if len(items) > 1 else ""
            pi_description = f"VV Kaffee - {first_name}{extra}"

            intent = stripe.PaymentIntent.create(
                amount=_to_cents(order.total),
                currency="eur",
                metadata={"order_id": str(order.id), "email": order.email},
                receipt_email=order.email,
                description=pi_description,
                automatic_payment_methods={"enabled": True},
            )
            order.payment_intent_id = intent.id
            order.save(update_fields=["payment_intent_id"])

            # 5) Clear session cart
            request.session["cart"] = {}
            request.session.modified = True

            # 6) Go to pay page to render Payment Element
            return redirect("orders:pay", order_id=order.id)
        # If form invalid, fall through to render with errors

    else:
        # GET: prefill from profile if logged in
        if request.user.is_authenticated:
            from profiles.models import Profile
            profile, _ = Profile.objects.get_or_create(user=request.user)
            initial = {
                "full_name": profile.full_name or "",
                "email": request.user.email or "",
                "phone_number": profile.phone or "",
                "street": profile.street or "",
                "house_number": profile.house_number or "",
                "city": profile.city or "",
                "postal_code": profile.postcode or "",
                "country": profile.country or "Germany",
            }
            form = CheckoutForm(initial=initial)
        else:
            form = CheckoutForm()

    # Render checkout with summary
    items, subtotal, shipping, total = compute_summary(cart)
    return render(
        request,
        "orders/checkout.html",
        {"form": form, "items": items, "subtotal": subtotal, "shipping": shipping, "total": total},
    )


def pay(request, order_id: int):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, pk=order_id, user=request.user)
    else:
        order = get_object_or_404(Order, pk=order_id, user__isnull=True)

    # Check for items
    if order.items.count() == 0:
        messages.error(request, "This order has no items and cannot be paid.")
        return redirect("orders:my_orders")  # Or another appropriate page

    # Check for payment intent
    if not order.payment_intent_id:
        messages.error(request, "Payment not initialized for this order.")
        return redirect("orders:checkout")

    # Build a clean list of items for display
    order_items = []
    subtotal = Decimal("0.00")
    for oi in order.items.select_related("product").all():
        line_total = (oi.unit_price * oi.quantity).quantize(Decimal("0.01"))
        subtotal += line_total
        order_items.append({
            "name": oi.product_name_snapshot,
            "quantity": oi.quantity,
            "unit_price": oi.unit_price,
            "grind": oi.grind,
            "weight_grams": oi.weight_grams,
            "line_total": line_total,
        })

    # fetch PI client secret
    intent = stripe.PaymentIntent.retrieve(order.payment_intent_id)
    client_secret = intent.client_secret

    return render(request, "orders/pay.html", {
        "order": order,
        "order_items": order_items,
        "subtotal": order.subtotal,
        "shipping": order.shipping,
        "total": order.total,
        "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        "client_secret": client_secret,
    })


def continue_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Your payment logic here (redirect to payment page, etc.)
    return redirect("orders:pay", order_id=order.id)


def thank_you(request, order_id: int):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=order_id)

    if order.status != "paid":
        pi_id = request.GET.get("payment_intent") or order.payment_intent_id
        if pi_id:
            try:
                pi = stripe.PaymentIntent.retrieve(pi_id)
                if pi.status == "succeeded":
                    for oi in order.items.select_related("product").all():
                        p = oi.product
                        if p and p.stock is not None:
                            new_stock = max(0, p.stock - oi.quantity)
                            if new_stock != p.stock:
                                p.stock = new_stock
                                p.save(update_fields=["stock"])
                    order.status = "paid"
                    order.save(update_fields=["status"])
                    logger.warning("Order %s reconciled to PAID on thank_you", order.id)

                    # ✅ send paid email here too
                    send_order_paid_notifications(order)
            except Exception:
                logger.exception("Thank_you reconcile error for order %s", order.id)

    return render(request, "orders/thank_you.html", {"order": order})




@csrf_exempt  # Stripe posts from outside; skip CSRF
@transaction.atomic
def stripe_webhook(request):
    # 1) Verify signature
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        logger.warning("Stripe webhook: invalid payload")
        return HttpResponseBadRequest("Invalid payload")
    except stripe.error.SignatureVerificationError:
        logger.warning("Stripe webhook: invalid signature")
        return HttpResponseBadRequest("Invalid signature")

    etype = event["type"]
    logger.warning("Stripe webhook received: %s", etype)

    # 2) Handle PI success (Payment Element flow)
    if etype == "payment_intent.succeeded":
        intent = event["data"]["object"]
        metadata = intent.get("metadata") or {}
        order_id = metadata.get("order_id")
        if not order_id:
            logger.warning("No order_id in PI %s metadata", intent.get("id"))
            return HttpResponse(status=200)

        try:
            order = Order.objects.select_for_update().get(pk=order_id)
        except Order.DoesNotExist:
            logger.warning("Order %s not found for PI %s", order_id, intent.get("id"))
            return HttpResponse(status=200)

        if order.status != "paid":
            # decrement stock
            for oi in order.items.select_related("product").all():
                p = oi.product
                if p and p.stock is not None:
                    new_stock = max(0, p.stock - oi.quantity)
                    if new_stock != p.stock:
                        p.stock = new_stock
                        p.save(update_fields=["stock"])

            order.status = "paid"
            order.save(update_fields=["status"])
            logger.warning("Order %s marked PAID and stock adjusted", order.id)
            
            send_order_paid_notifications(order)

        return HttpResponse(status=200)

    # 3) Ignore other events
    return HttpResponse(status=200)


def _format_address(order):
    """Safely join address parts into a single line."""
    parts = []
    street = getattr(order, "street", None)
    house_number = getattr(order, "house_number", None)
    city = getattr(order, "city", None)
    postal = getattr(order, "postal_code", None)
    country = getattr(order, "country", None)

    if street:
        parts.append(f"{street} {house_number or ''}".strip())
    town = " ".join(p for p in [postal, city] if p)
    if town:
        parts.append(town)
    if country:
        parts.append(country)

    return ", ".join(parts) if parts else "—"


def is_fulfiller(user):
    # member of the “Fulfillment Department” group
    return user.is_authenticated and user.groups.filter(name="Fulfillment Department").exists()


@login_required
@permission_required("orders.view_fulfillment", raise_exception=True)
@staff_member_required
def order_picklist(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        pk=order_id
    )
    _ensure_paid_or_superuser(order, request.user)

    # inside order_picklist / order_picklist_pdf
    if order.status not in ("pending_fulfillment", "paid") and not request.user.is_superuser:
        raise Http404

    total_qty = 0
    total_weight = 0
    grand_total = Decimal("0.00")

    for oi in order.items.all():
        qty = oi.quantity or 0
        unit = oi.unit_price or Decimal("0.00")
        total_qty += qty
        total_weight += qty * (oi.weight_grams or 0)
        grand_total += unit * qty

    context = {
        "order": order,
        "total_qty": total_qty,
        "total_weight": total_weight,     # grams
        "grand_total": grand_total,
    }
    return render(request, "orders/picklist.html", context)


def _fmt_money(value) -> str:
    """Format numbers/Decimals as Euro currency."""
    dec = (Decimal(value or 0)
           .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return f"€{dec}"


@login_required
@permission_required("orders.view_fulfillment", raise_exception=True)
def order_picklist_pdf(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=order_id)
    _ensure_paid_or_superuser(order, request.user)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="picklist_order_{order.id}.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=60
    )
    elements = []

    if order.status not in ("pending_fulfillment", "paid") and not request.user.is_superuser:
        raise Http404
    # Logo
    logo_path = os.path.join(settings.BASE_DIR, "static/branding/logo.png")
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=120, height=50))
    elements.append(Spacer(1, 20))

    # Title + info
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    normal = styles["Normal"]

    elements.append(Paragraph(f"Picklist for Order #{order.id}", title_style))
    elements.append(Spacer(1, 6))

    full_name = getattr(order, "full_name", None) or (order.user.username if getattr(order, "user", None) else "Guest")
    email = getattr(order, "email", None) or "—"
    phone = getattr(order, "phone", None) or getattr(order, "phone_number", None) or "—"
    ship_to = _format_address(order)

    elements.append(Paragraph(f"<b>Customer:</b> {full_name}", normal))
    elements.append(Paragraph(f"<b>Email:</b> {email}", normal))
    elements.append(Paragraph(f"<b>Phone:</b> {phone}", normal))
    elements.append(Paragraph(f"<b>Status:</b> {order.get_status_display()}", normal))
    elements.append(Paragraph(f"<b>Ship to:</b> {ship_to}", normal))
    elements.append(Spacer(1, 14))

    # Table header (added Unit € and Line €)
    data = [["", "Qty", "Product", "Grind", "Weight (g)", "Unit €", "Line €"]]

    bean_icon = os.path.join(settings.BASE_DIR, "static/branding/bean.png")
    bean_exists = os.path.exists(bean_icon)

    total_qty = 0
    grand_total = Decimal("0.00")

    for item in order.items.all():
        icon = Image(bean_icon, width=12, height=12) if bean_exists else ""
        unit = item.unit_price or Decimal("0.00")
        line = (unit * (item.quantity or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_qty += (item.quantity or 0)
        grand_total += line

        data.append([
            icon,
            str(item.quantity),
            item.product_name_snapshot,
            item.grind or "-",
            str(item.weight_grams),
            _fmt_money(unit),
            _fmt_money(line),
        ])

    # Totals row
    data.append([
        "", "", "", "", Paragraph("<b>Totals</b>", normal),
        "", Paragraph(f"<b>{_fmt_money(grand_total)}</b>", normal)
    ])

    # Build table (wider, to fit currency cols)
    table = Table(data, colWidths=[20, 36, 180, 80, 70, 60, 70])
    table.setStyle(TableStyle([
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6F4E37")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),

        # Body
        ("BACKGROUND", (0, 1), (-1, -2), colors.beige),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        # Alignment
        ("ALIGN", (1, 1), (1, -2), "CENTER"),  # Qty
        ("ALIGN", (5, 1), (6, -2), "RIGHT"),   # currency cols
        ("ALIGN", (6, -1), (6, -1), "RIGHT"),  # grand total

        # Totals row styling
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#EEE6DD")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.grey),
    ]))
    elements.append(table)

    # Summary under the table
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Total items:</b> {total_qty}", normal))
    elements.append(Paragraph(f"<b>Grand total:</b> {_fmt_money(grand_total)}", normal))

    # Build with footer on each page
    doc.build(elements, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
    return response


def _draw_footer(canvas, doc):
    """Footer on every page."""
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.grey)
    canvas.line(2 * cm, 2.6 * cm, width - 2 * cm, 2.6 * cm)
    canvas.setFont("Helvetica-Oblique", 9)
    canvas.drawString(2 * cm, 2.2 * cm, "Versöhnung und Vergebung Kaffee – Hopfauerstraße 33, 70563 Stuttgart, Germany")
    canvas.drawString(2 * cm, 1.7 * cm, "Thank you for choosing Versöhnung und Vergebung Kaffee!")
    canvas.restoreState()


def _ensure_paid_or_superuser(order, user):
    if order.status == "paid":
        return
    if user.is_superuser:
        return
    # Hide details if not paid
    raise Http404("Order not available")


PACKABLE_STATUSES = ["paid"]


@login_required
@permission_required("orders.view_fulfillment", raise_exception=True)
def fulfillment_paid_orders(request):
    orders = (Order.objects
              .filter(status__in=PACKABLE_STATUSES)
              .order_by("-created_at")
              .prefetch_related("items"))
    q = request.GET.get("q")
    if q:
        orders = orders.filter(full_name__icontains=q) | orders.filter(email__icontains=q)
    return render(request, "orders/fulfillment_list.html", {"orders": orders})


@login_required
# @user_passes_test(is_fulfiller)
@permission_required("orders.change_fulfillment_status", raise_exception=True)
@require_POST
def mark_order_fulfilled(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.status not in ("pending_fulfillment", "paid"):
        # Ignore or show error if it’s not in a packable state
        return redirect("orders:fulfillment_paid_orders")

    order.status = "fulfilled"
    order.fulfilled_at = timezone.now()
    order.save(update_fields=["status", "fulfilled_at"])
    return redirect("orders:fulfillment_paid_orders")


@login_required
def fulfillment_recently_fulfilled(request):
    orders = (Order.objects
              .filter(status="fulfilled")
              .order_by("-created_at")[:20]      # last 20
              .prefetch_related("items"))
    return render(request, "orders/fulfillment_recent.html", {"orders": orders})


@login_required
def my_orders(request):
    orders = (Order.objects
              .filter(user=request.user)
              .order_by("-created_at")
              .prefetch_related("items"))
    return render(request, "orders/my_orders.html", {"orders": orders})


@login_required
def my_order_detail(request, order_id: int):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"),
                              id=order_id, user=request.user)
    return render(request, "orders/my_order_detail.html", {"order": order})