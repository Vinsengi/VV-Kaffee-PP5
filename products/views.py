# products/views.py
from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from orders.models import OrderItem
from reviews.forms import ProductReviewForm
from reviews.models import ProductReview
from .forms import ProductForm, ProductBatchForm
from .models import Product, ProductBatch


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
        reset_review_form = bool(request.GET.get("review_submitted"))

        if request.user.is_authenticated:
            can_review = OrderItem.objects.filter(
                order__user=request.user,
                product=product,
                order__status__in=["paid", "fulfilled", "refunded"],
            ).exists()
            if can_review:
                provided_form = kwargs.get("review_form")
                if provided_form:
                    ctx["review_form"] = provided_form
                elif reset_review_form:
                    # After a successful submit, show a fresh form instead of prefilled values.
                    ctx["review_form"] = ProductReviewForm()
                else:
                    ctx["review_form"] = ProductReviewForm()
            else:
                ctx["review_form"] = None
        else:
            ctx["review_form"] = None

        ctx["can_review"] = can_review
        ctx["review_form_reset"] = reset_review_form
        return ctx


staff_required = user_passes_test(lambda u: u.is_staff)
manager_required = user_passes_test(
    lambda u: u.is_staff and u.has_perm("products.add_product")
)


@login_required
@staff_required
def staff_product_list(request):
    products = list(
        Product.objects.order_by("-created_at").prefetch_related("batches")
    )

    for p in products:
        # Compute based on batches (remaining grams)
        batches = list(p.batches.all())
        total_grams = sum((Decimal(b.remaining_grams or 0) for b in batches), Decimal("0"))
        total_kg = (total_grams / Decimal(1000)).quantize(Decimal("0.001"))
        p.total_kg = total_kg
        p.batch_stock_units = p.batch_stock_units()

        total_cost = Decimal("0.00")
        for b in batches:
            kg = (Decimal(b.remaining_grams or 0) / Decimal(1000))
            total_cost += kg * (b.unit_cost or Decimal("0.00"))
        p.total_cost = total_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        sale_price = Decimal(p.price or 0)
        p.total_revenue = (sale_price * total_kg).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return render(
        request,
        "products/staff_product_list.html",
        {"products": products},
    )


@login_required
@staff_required
def staff_product_detail(request, pk: int):
    product = get_object_or_404(
        Product.objects.prefetch_related("batches"),
        pk=pk,
    )
    batches = list(product.batches.all())
    total_grams = sum((Decimal(b.remaining_grams or 0) for b in batches), Decimal("0"))
    kg_total = (total_grams / Decimal(1000)).quantize(Decimal("0.001"))

    total_cost = Decimal("0.00")
    for b in batches:
        b.quantity_kg = (Decimal(b.quantity_grams or 0) / Decimal(1000)).quantize(Decimal("0.001"))
        b.remaining_kg = (Decimal(b.remaining_grams or 0) / Decimal(1000)).quantize(Decimal("0.001"))
        kg = (Decimal(b.remaining_grams or 0) / Decimal(1000))
        total_cost += kg * (b.unit_cost or Decimal("0.00"))
    total_cost = total_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    unit_price = Decimal(product.price or 0)
    total_revenue = (unit_price * kg_total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    stock_units = product.batch_stock_units()

    return render(
        request,
        "products/staff_product_detail.html",
        {
            "product": product,
            "total_kg": kg_total,
            "total_cost": total_cost,
            "total_revenue": total_revenue,
            "batches": batches,
            "batch_stock_units": stock_units,
        },
    )


@login_required
@manager_required
def staff_product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, "Product created successfully.")
            return redirect("products:staff_product_detail", pk=product.pk)
    else:
        form = ProductForm()

    return render(
        request,
        "products/staff_product_form.html",
        {"form": form, "is_create": True, "product": None},
    )


@login_required
@staff_required
def staff_product_update(request, pk: int):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect("products:staff_product_detail", pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "products/staff_product_form.html",
        {"form": form, "product": product, "is_create": False},
    )


@login_required
@staff_required
def staff_product_delete(request, pk: int):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted.")
        return redirect("products:staff_product_list")
    return render(
        request,
        "products/staff_product_confirm_delete.html",
        {"product": product},
    )


@login_required
@manager_required
def staff_product_batch_add(request, product_id: int):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        form = ProductBatchForm(request.POST)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.product = product
            if batch.remaining_grams is None or batch.remaining_grams == 0:
                batch.remaining_grams = batch.quantity_grams
            batch.save()
            messages.success(request, "Batch added.")
            return redirect("products:staff_product_detail", pk=product.id)
    else:
        form = ProductBatchForm(initial={"remaining_grams": None})

    return render(
        request,
        "products/batch_form.html",
        {"form": form, "product": product, "is_create": True},
    )


@login_required
@manager_required
def staff_product_batch_edit(request, batch_id: int):
    batch = get_object_or_404(ProductBatch, pk=batch_id)
    product = batch.product
    if request.method == "POST":
        form = ProductBatchForm(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            messages.success(request, "Batch updated.")
            return redirect("products:staff_product_detail", pk=product.id)
    else:
        form = ProductBatchForm(instance=batch)

    return render(
        request,
        "products/batch_form.html",
        {"form": form, "product": product, "is_create": False},
    )
