# orders/emails.py
from io import BytesIO
import logging
from decimal import Decimal
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import os

logger = logging.getLogger(__name__)


def _fmt_eur(value) -> str:
    return f"€{Decimal(value or 0):.2f}"


def _build_pdf_bytes(order, title):
    """Build a simple order summary PDF in-memory and return bytes."""
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=60)
    styles = getSampleStyleSheet()
    elements = []

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, "static/branding/logo.png")
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=120, height=50))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(title, styles["Heading2"]))
    elements.append(Spacer(1, 6))

    # Customer + address
    parts = []
    if order.full_name:
        parts.append(order.full_name)
    line1 = " ".join([order.street or "", str(order.house_number or "")]).strip()
    if line1:
        parts.append(line1)
    town = " ".join([order.postal_code or "", order.city or ""]).strip()
    if town:
        parts.append(town)
    if order.country:
        parts.append(order.country)
    elements.append(Paragraph("<br/>".join(parts) or "—", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Table
    data = [["Qty", "Product", "Grind", "Weight (g)", "Unit", "Line"]]
    grand = Decimal("0.00")
    for it in order.items.all():
        unit = it.unit_price or Decimal("0.00")
        qty = it.quantity or 0
        line = unit * qty
        grand += line
        data.append([
            str(qty),
            it.product_name_snapshot,
            it.grind or "-",
            str(it.weight_grams or ""),
            _fmt_eur(unit),
            _fmt_eur(line),
        ])

    data.append(["", "", "", "", "Total", _fmt_eur(grand)])

    table = Table(data, colWidths=[36, 200, 80, 70, 60, 70])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#6F4E37")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 11),
        ("BOTTOMPADDING", (0,0), (-1,0), 7),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (0,1), (0,-1), "CENTER"),
        ("ALIGN", (4,1), (5,-1), "RIGHT"),
    ]))
    elements.append(table)

    # Footer
    def _footer(canv, _doc):
        canv.saveState()
        width, height = A4
        canv.setStrokeColor(colors.grey)
        canv.line(2*cm, 2.6*cm, width - 2*cm, 2.6*cm)
        canv.setFont("Helvetica-Oblique", 9)
        canv.drawString(2*cm, 2.2*cm, "Versöhnung und Vergebung Kaffee – Hopfauerstraße 33, 70563 Stuttgart, Germany")
        canv.drawString(2*cm, 1.7*cm, "Thank you for choosing Versöhnung und Vergebung Kaffee!")
        canv.restoreState()

    doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
    buf.seek(0)
    return buf.read()


def _send_mail_with_optional_pdf(subject, template, context, to_email, pdf_filename=None, pdf_bytes=None):
    text_body = render_to_string(template + ".txt", context)
    html_body = render_to_string(template + ".html", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
        reply_to=[settings.DEFAULT_FROM_EMAIL],
    )
    msg.attach_alternative(html_body, "text/html")

    if pdf_bytes and pdf_filename:
        msg.attach(pdf_filename, pdf_bytes, "application/pdf")

    return msg.send(fail_silently=False)


def send_order_pending_email(order):
    subject = f"Order #{order.id} received – Pending payment"
    if order.user:
        account_url = f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/account/account"
    else:
        account_url = f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/accounts/signup/"
    ctx = {
        "order": order,
        "site_name": getattr(settings, "SITE_NAME", "VV Kaffee"),
        "site_url": getattr(settings, "SITE_URL", "http://127.0.0.1:8000"),
        "account_url": account_url,
    }
    return _send_mail_with_optional_pdf(
        subject=subject,
        template="emails/order_pending",
        context=ctx,
        to_email=order.email,
    )


def send_order_paid_email(order):
    subject = f"Payment confirmed – Order #{order.id}"
    if order.user:
        account_url = f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/account/"
    else:
        account_url = f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/accounts/signup/"
    ctx = {
        "order": order,
        "site_name": getattr(settings, "SITE_NAME", "VV Kaffee"),
        "site_url": getattr(settings, "SITE_URL", "http://127.0.0.1:8000"),
        "account_url": account_url,
    }
    pdf = _build_pdf_bytes(order, f"Order #{order.id} – Paid")
    return _send_mail_with_optional_pdf(
        subject=subject,
        template="emails/order_paid",
        context=ctx,
        to_email=order.email,
        pdf_filename=f"order_{order.id}.pdf",
        pdf_bytes=pdf,
    )


def send_order_paid_internal_email(order, recipients):
    if not recipients:
        return 0

    ctx = {
        "order": order,
        "site_name": getattr(settings, "SITE_NAME", "VV Kaffee"),
        "site_url": getattr(settings, "SITE_URL", "http://127.0.0.1:8000"),
    }
    text_body = render_to_string("emails/order_paid_internal.txt", ctx)
    html_body = render_to_string("emails/order_paid_internal.html", ctx)

    msg = EmailMultiAlternatives(
        subject=f"New paid order #{order.id}",
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
        reply_to=[settings.DEFAULT_FROM_EMAIL],
    )
    msg.attach_alternative(html_body, "text/html")
    return msg.send(fail_silently=False)


def send_order_paid_notifications(order):
    """Send customer confirmation plus internal alert for paid orders."""
    try:
        send_order_paid_email(order)
    except Exception:
        logger.exception("Customer paid email failed for order %s", order.id)

    internal_recipients = getattr(settings, "ORDER_NOTIFICATION_EMAILS", [])
    if not internal_recipients:
        logger.info("No ORDER_NOTIFICATION_EMAILS configured; skipping internal notice for %s", order.id)
        return

    try:
        send_order_paid_internal_email(order, internal_recipients)
    except Exception:
        logger.exception("Internal paid email failed for order %s", order.id)