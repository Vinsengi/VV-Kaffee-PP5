from django.contrib import admin

from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "display_price",
        "stock_status",
        "average_rating_display",
        "review_count",
        "is_active",
    )
    list_filter = ("is_active", "category", "roast_type")
    search_fields = ("name", "sku", "tasting_notes", "origin", "farm", "variety", "process")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)

    @admin.display(description="Stock")
    def stock_status(self, obj):
        suffix = " (active)" if obj.is_active else " (inactive)"
        return f"{obj.stock}{suffix}"

    @admin.display(description="Avg. rating")
    def average_rating_display(self, obj):
        rating = obj.average_rating()
        return f"{rating}★" if rating is not None else "—"
