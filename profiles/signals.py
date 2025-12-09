import logging

from allauth.account.signals import user_signed_up
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .emails import send_welcome_email
from .models import Profile

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(user_signed_up)
def handle_user_signed_up(request, user, **kwargs):
    """After signup, send the allauth confirmation email plus our welcome email."""
    try:
        if user.email:
            EmailAddress.objects.add_email(request, user, user.email, confirm=True, signup=True)
    except Exception:
        logger.exception("Failed to send confirmation email for user %s", user.id)

    try:
        send_welcome_email(user)
    except Exception:
        logger.exception("Failed to send welcome email for user %s", user.id)
