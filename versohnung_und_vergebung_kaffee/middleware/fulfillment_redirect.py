# versohnung_und_vergebung_kaffee/middleware/fulfillment_redirect.py
from django.shortcuts import redirect
from versohnung_und_vergebung_kaffee.staff_mode import get_staff_mode, is_worker


class FulfillmentPostLoginMiddleware:
    """
    If a logged-in user in 'Fulfillment Department' lands on '/',
    send them to the fulfillment dashboard.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            user = request.user
            if (
                user.is_authenticated
                and request.method == "GET"
                and request.path == "/"
                and is_worker(user)
                and get_staff_mode(request)
            ):
                return redirect("/staff/fulfillment/")
        except Exception:
            pass

        return response
