from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product_list"),
    path("staff/products/", views.staff_product_list, name="staff_product_list"),
    path(
        "staff/products/create/",
        views.staff_product_create,
        name="staff_product_create",
    ),
    path(
        "staff/products/<int:pk>/",
        views.staff_product_detail,
        name="staff_product_detail",
    ),
    path(
        "staff/products/<int:pk>/edit/",
        views.staff_product_update,
        name="staff_product_update",
    ),
    path(
        "staff/products/<int:pk>/delete/",
        views.staff_product_delete,
        name="staff_product_delete",
    ),
    path(
        "<slug:slug>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),
]
