from typing import Iterable, List

STAFF_MODE_SESSION_KEY = "staff_mode_active"


def _is_fulfiller(user) -> bool:
    """
    True if the user can fulfill orders (permission or Fulfillment Department group).
    """
    if not getattr(user, "is_authenticated", False):
        return False
    return (
        user.has_perm("orders.view_fulfillment")
        or user.groups.filter(name="Fulfillment Department").exists()
    )


def is_worker(user) -> bool:
    """
    Staff-like users: staff OR fulfillment-only users.
    """
    if not getattr(user, "is_authenticated", False):
        return False
    return bool(getattr(user, "is_staff", False) or _is_fulfiller(user))


def get_staff_mode(request) -> bool:
    """
    Return True if the current user is in staff mode.
    Defaults to True for authenticated staff/fulfillers so they see work tools
    unless they explicitly switch to customer mode.
    """
    user = getattr(request, "user", None)
    if not is_worker(user):
        return False

    stored = request.session.get(STAFF_MODE_SESSION_KEY)
    if stored is None:
        return True
    return bool(stored)


def set_staff_mode(request, enabled: bool) -> None:
    """
    Persist the staff/customer mode choice in the session.
    """
    request.session[STAFF_MODE_SESSION_KEY] = bool(enabled)
    request.session.modified = True


def staff_roles(user) -> List[str]:
    """
    Human friendly staff roles for display (groups fall back to generic labels).
    """
    if not is_worker(user):
        return []

    roles: Iterable[str] = (
        user.groups.values_list("name", flat=True) if hasattr(user, "groups") else []
    )
    roles = [r for r in roles if r]
    labels = list(roles)
    if _is_fulfiller(user) and "Fulfillment Department" not in labels:
        labels.append("Fulfillment")
    if labels:
        return labels
    if getattr(user, "is_superuser", False):
        return ["Admin"]
    if getattr(user, "is_staff", False):
        return ["Staff"]
    return ["Fulfillment"]
