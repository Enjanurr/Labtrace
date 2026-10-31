from django.contrib.auth.views import redirect_to_login
from django.http import JsonResponse

from authentication.models import User

from .decorators import forbidden_response, is_ajax

ADMIN = User.Role.ADMIN
INSTRUCTOR = User.Role.INSTRUCTOR

# Paths reachable without logging in.
EXEMPT_PREFIXES = (
    "/static/",
    "/admin/",  # Django admin has its own login + is_staff check
    "/accounts/login/",
    "/accounts/register/",
    "/users/password-reset/",
)

# (path prefix, roles allowed). Add rules here as new apps get built.
# Anything not listed is open to every authenticated role.
ROLE_RULES = [
    ("/users/manage/", {ADMIN}),
    ("/visits/active/", {INSTRUCTOR, ADMIN}),
    ("/incidents/audit/", {INSTRUCTOR, ADMIN}),
    ("/incidents/manage/", {INSTRUCTOR, ADMIN}),
     ("/equipment/manage/", {INSTRUCTOR, ADMIN}),
]


class RoleBasedAccessMiddleware:
    """Global login requirement + role check by URL prefix."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        if path.startswith(EXEMPT_PREFIXES):
            return self.get_response(request)

        if not request.user.is_authenticated:
            if is_ajax(request):
                return JsonResponse({"ok": False, "error": "Login required."}, status=401)
            return redirect_to_login(request.get_full_path())

        for prefix, roles in ROLE_RULES:
            if path.startswith(prefix) and request.user.role not in roles:
                return forbidden_response(request)

        return self.get_response(request)