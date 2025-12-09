from allauth.account.models import EmailAddress
from django.contrib.auth import get_user
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class SignupViewTests(TestCase):
    def test_signup_creates_user_and_redirects(self):
        response = self.client.post(
            reverse("account_signup"),
            {
                "username": "coffee_fan",
                "email": "fan@example.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/post-login/")

        user = get_user_model().objects.get(username="coffee_fan")
        self.assertEqual(user.email, "fan@example.com")
        self.assertTrue(get_user(self.client).is_authenticated)

        email_address = EmailAddress.objects.get(user=user)
        self.assertEqual(email_address.email, "fan@example.com")
        self.assertFalse(email_address.verified)

    def test_signup_missing_username_shows_error(self):
        response = self.client.post(
            reverse("account_signup"),
            {
                "email": "fan@example.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
        )

        response = response.render()

        self.assertEqual(response.status_code, 200)

        form = response.context_data["form"]
        self.assertIn("username", form.errors)
        self.assertEqual(form.errors["username"], ["This field is required."])

        self.assertFalse(get_user_model().objects.filter(email="fan@example.com").exists())
