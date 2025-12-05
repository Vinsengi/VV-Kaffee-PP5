"""Newsletter subscriber model."""

from django.db import models


class Subscriber(models.Model):
    """Minimal subscriber record for marketing opt-ins."""

    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.email
