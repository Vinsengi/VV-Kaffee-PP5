from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_welcome_email(user):
    """Send a simple welcome email to a newly registered user."""
    if not user.email:
        return 0

    site_name = getattr(settings, "SITE_NAME", "VV Kaffee")
    site_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")
    context = {
        "user": user,
        "site_name": site_name,
        "site_url": site_url,
    }

    subject = f"Welcome to {site_name}"
    text_body = render_to_string("emails/welcome_new_user.txt", context)
    html_body = render_to_string("emails/welcome_new_user.html", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
        reply_to=[settings.DEFAULT_FROM_EMAIL],
    )
    msg.attach_alternative(html_body, "text/html")
    return msg.send(fail_silently=False)
