# products/views.py
from django.db.models import Avg, Count, Prefetch
from django.views.generic import ListView, DetailView
from orders.models import OrderItem
from reviews.forms import ProductReviewForm
from reviews.models import ProductReview
from .models import Product


class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True)
            .annotate(
                average_rating=Avg("reviews__rating"),
                review_count=Count("reviews"),
            )
            .order_by("-created_at")
        )


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True)
            .prefetch_related(
                Prefetch(
                    "reviews",
                    queryset=ProductReview.objects.select_related("user"),
                )
            )
            .order_by("name")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.object
        # Use product.available_grinds if set, else sensible default
        raw = product.available_grinds or (
            "whole,espresso,filter,french_press"
        )
        values = [g.strip() for g in raw.split(",") if g.strip()]
        choices = [(g, g.replace("_", " ").title()) for g in values]
        ctx["grind_choices"] = choices
        # Access prefetched reviews efficiently
        reviews_list = list(product.reviews.all())
        ctx["reviews"] = reviews_list
        ctx["review_count"] = len(reviews_list)
        # Calculate average from the list to avoid extra query
        if reviews_list:
            total = sum(r.rating for r in reviews_list)
            ctx["average_rating"] = total / len(reviews_list)
        else:
            ctx["average_rating"] = None

        request = self.request
        can_review = False
        existing_review = None

        if request.user.is_authenticated:
            can_review = OrderItem.objects.filter(
                order__user=request.user,
                product=product,
                order__status__in=["paid", "fulfilled", "refunded"],
            ).exists()
            if can_review:
                provided_form = kwargs.get("review_form")
                existing_review = (
                    getattr(provided_form, "instance", None)
                    or ProductReview.objects.filter(
                        user=request.user, product=product
                    ).first()
                )
                ctx["review_form"] = provided_form or ProductReviewForm(
                    instance=existing_review
                )
                ctx["existing_review"] = existing_review
            else:
                ctx["review_form"] = None
        else:
            ctx["review_form"] = None

        ctx["can_review"] = can_review
        return ctx
