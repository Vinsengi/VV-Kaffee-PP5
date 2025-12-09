# versohnung_und_vergebung_kaffee/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from profiles import views as profile_views  # for post-login redirect
from . import views as root_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("staff/admin/", root_views.staff_admin_hub, name="staff_admin_hub"),

    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("testbed/", root_views.test_base, name="test_base"),

    path("shop/", include(("products.urls", "products"), namespace="products")),
    path("cart/", include(("cart.urls", "cart"), namespace="cart")),
    path("", include(("orders.urls", "orders"), namespace="orders")),
    path("account/", include(("profiles.urls", "profiles"), namespace="profiles")),

    # ✅ Allauth routes live under /accounts/
    path("accounts/", include("allauth.urls")),

    # Your post-login redirect
    path("post-login/", profile_views.post_login_redirect, name="post_login_redirect"),

    path("reviews/", include(("reviews.urls", "reviews"), namespace="reviews")),
    path("newsletter/", include("newsletter.urls")),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt",
            content_type="text/plain"
        ),
        name="robots_txt",
    ),
    path(
        "sitemap.xml",
        TemplateView.as_view(
            template_name="sitemap.xml",
            content_type="application/xml"
        ),
        name="sitemap_xml",
    ),
]
