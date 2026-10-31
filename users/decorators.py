from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.http import JsonResponse
from django.shortcuts import render


def is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def forbidden_response(request):
    if is_ajax(request):
        return JsonResponse({"ok": False, "error": "Permission denied."}, status=403)
    return render(request, "403.html", status=403)


def role_required(*roles):
    """Restrict a view to the given roles, e.g. @role_required(User.Role.ADMIN)."""
    allowed = set(roles)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if is_ajax(request):
                    return JsonResponse({"ok": False, "error": "Login required."}, status=401)
                return redirect_to_login(request.get_full_path())
            if request.user.role not in allowed:
                return forbidden_response(request)
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator