from django.conf import settings
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
import stripe

from .models import Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False

    readonly_fields = (
        "product_name_snapshot",
        "unit_price",
        "quantity",
        "grind",
        "weight_grams",
        "line_total_display",
    )
    fields = (
        "product_name_snapshot",
        "unit_price",
        "quantity",
        "grind",
        "weight_grams",
        "line_total_display",
    )

    @admin.display(description="Line total")
    def line_total_display(self, obj):
        if obj is None:
            return "€0.00"
        return f"€{obj.line_total}"


@admin.action(description="Reconcile selected orders with Stripe")
def reconcile_with_stripe(modeladmin, request, queryset):
    updated = 0
    for order in queryset:
        if not order.payment_intent_id:
            continue
        try:
            payment_intent = stripe.PaymentIntent.retrieve(order.payment_intent_id)
        except Exception:
            continue
        if payment_intent.status == "succeeded" and order.status != "paid":
            for order_item in order.items.select_related("product").all():
                product = order_item.product
                if product and product.stock is not None:
                    new_stock = max(0, product.stock - order_item.quantity)
                    if new_stock != product.stock:
                        product.stock = new_stock
                        product.save(update_fields=["stock"])
            order.status = "paid"
            order.save(update_fields=["status"])
            updated += 1
    messages.info(request, f"Reconciled {updated} order(s).")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "full_name",
        "status",
        "item_count_display",
        "total",
        "picklist_link",
        "picklist_pdf_link",
    )
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "payment_intent_id")
    readonly_fields = ("subtotal", "shipping", "total", "created_at", "updated_at")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    actions = [reconcile_with_stripe, "recalculate_totals"]

    @admin.display(description="Items")
    def item_count_display(self, obj):
        return obj.item_count

    @admin.action(description="Recalculate totals for selected orders")
    def recalculate_totals(self, request, queryset):
        for order in queryset:
            order.recalc_totals()

    def picklist_link(self, obj):
        url = reverse("orders:order_picklist", args=[obj.id])
        return format_html('<a href="{}" target="_blank">🧾 Picklist</a>', url)

    def picklist_pdf_link(self, obj):
        url = reverse("orders:order_picklist_pdf", args=[obj.id])
        return format_html('<a class="button" href="{}" target="_blank">📄 PDF Picklist</a>', url)
