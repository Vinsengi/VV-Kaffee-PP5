from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path("account/", views.account_dashboard, name="account_dashboard"),
    path("account/profile/", views.profile_edit, name="profile_edit"),
    path("account/orders/", views.order_list, name="order_list"),
    path("account/orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("post-login/", views.post_login_redirect, name="post_login_redirect"),
    path("staff-mode/toggle/", views.toggle_staff_mode, name="toggle_staff_mode"),
]
