from versohnung_und_vergebung_kaffee import settings
from .staff_mode import get_staff_mode, staff_roles, is_worker


def staff_mode_context(request):
    """
    Inject staff/customer mode flags into templates.
    """
    user = getattr(request, "user", None)
    worker_user = is_worker(user)
    active = get_staff_mode(request) if worker_user else False

    return {
        "staff_mode_active": active,
        "acting_as_customer": worker_user and not active,
        "staff_role_labels": staff_roles(user) if worker_user else [],
        "worker_user": worker_user,
    }


def canonical_url(request):
    base = getattr(settings, "CANONICAL_BASE_URL", "").rstrip("/")
    return {"canonical_url": f"{base}{request.path}"}