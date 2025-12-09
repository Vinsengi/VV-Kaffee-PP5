
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django import forms
from orders.models import Order, OrderItem
from products.models import Product
from products.views import ProductDetailView
from .forms import ProductReviewForm
from .models import ProductReview, ExperienceFeedback


@login_required
def order_review(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"),
                              pk=order_id, user=request.user)
    if order.status not in ("paid", "fulfilled", "refunded"):
        return redirect("profiles:account_dashboard")

    # Products eligible to review (from this order)
    items = order.items.all()
    return render(request, "reviews/order_review.html", {"order": order, "items": items})


@login_required
def create_or_update_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    # ensure user actually purchased this product
    purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status__in=["paid", "fulfilled", "refunded"],
    ).exists()
    if not purchased:
        messages.error(request, "You can only review products you have purchased.")
        return redirect(product.get_absolute_url())

    if request.method == "POST":
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, "Thanks for sharing your review!")
            return redirect(f"{product.get_absolute_url()}?review_submitted=1")

        detail_view = ProductDetailView()
        detail_view.request = request
        detail_view.object = product
        ctx = detail_view.get_context_data(review_form=form)
        return render(request, detail_view.template_name, ctx)

    return redirect(product.get_absolute_url())


@login_required
def experience_review(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    try:
        instance = order.experiencefeedback
    except ExperienceFeedback.DoesNotExist:
        instance = None

    class ExpForm(forms.ModelForm):
        class Meta:
            model = ExperienceFeedback
            fields = ["rating", "comment"]
            widgets = {
                "rating": forms.Select(attrs={"class": "form-select"}),
                "comment": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            }

    if request.method == "POST":
        form = ExpForm(request.POST, instance=instance)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.user = request.user
            fb.order = order
            fb.save()
            messages.success(request, "Thanks for rating your experience!")
            return redirect("orders:my_order_detail", order_id=order.id)
    else:
        form = ExpForm(instance=instance)

    return render(request, "reviews/experience_form.html", {"order": order, "form": form})
