from django.contrib import admin

from .models import ExperienceFeedback, ProductReview


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_positive", "created_at")
    search_fields = ("product__name", "user__username", "comment", "title")
    list_filter = ("rating", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


@admin.register(ExperienceFeedback)
class ExperienceFeedbackAdmin(admin.ModelAdmin):
    list_display = ("order_reference", "user", "rating", "short_comment", "created_at")
    search_fields = ("order__id", "order__reference", "user__username", "user__email", "comment")
    list_filter = ("rating", "created_at")
    readonly_fields = ("created_at",)
    list_select_related = ("order", "user")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    @admin.display(description="Order")
    def order_reference(self, obj):
        if obj.order:
            return obj.order.reference
        return "-"

    @admin.display(description="Comment")
    def short_comment(self, obj):
        if not obj.comment:
            return ""
        text = str(obj.comment)
        return text if len(text) <= 80 else text[:77] + "..."
