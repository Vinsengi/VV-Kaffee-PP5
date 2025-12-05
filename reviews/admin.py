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
    list_display = ("order", "user", "rating", "created_at")
    search_fields = ("user__username", "order__id", "comment")
    list_filter = ("rating", "created_at")
    readonly_fields = ("created_at",)
