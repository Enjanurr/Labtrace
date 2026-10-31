from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .decorators import role_required
from .forms import (
    DeactivateAccountForm,
    ProfileUpdateForm,
    StyledPasswordChangeForm,
    StyledPasswordResetForm,
    StyledSetPasswordForm,
    UserRoleForm,
)

User = get_user_model()
ADMIN = User.Role.ADMIN


# ---------------------------------------------------------------- profile
@login_required
def profile_view(request):
    # Fresh instance so a failed form never mutates request.user
    account = User.objects.get(pk=request.user.pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("users:profile")
    else:
        form = ProfileUpdateForm(instance=account)
    return render(request, "users/profile.html", {"form": form})


def _is_last_active_admin(user):
    return (
        user.role == ADMIN
        and user.is_active
        and not User.objects.filter(role=ADMIN, is_active=True)
        .exclude(pk=user.pk)
        .exists()
    )


@login_required
def deactivate_account_view(request):
    """Soft-delete: is_active=False. Visits, logs and incidents stay intact."""
    user = request.user
    blocked = _is_last_active_admin(user)

    if request.method == "POST":
        form = DeactivateAccountForm(user, request.POST)
        if blocked:
            messages.error(
                request, "You are the only active admin. Promote another admin first."
            )
        elif form.is_valid():
            user.is_active = False
            user.save(update_fields=["is_active"])
            logout(request)
            messages.success(
                request,
                "Your account was deactivated. An administrator can reactivate it.",
            )
            return redirect("authentication:login")
    else:
        form = DeactivateAccountForm(user)

    return render(request, "users/deactivate.html", {"form": form, "blocked": blocked})


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    form_class = StyledPasswordChangeForm
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:profile")
    success_message = "Password changed."


# --------------------------------------------------------- password reset
# Offline: the "email" is written to the /sent_emails folder (file backend).
class LabPasswordResetView(PasswordResetView):
    form_class = StyledPasswordResetForm
    template_name = "users/password_reset_form.html"
    email_template_name = "users/password_reset_email.txt"
    subject_template_name = "users/password_reset_subject.txt"
    success_url = reverse_lazy("users:password_reset_done")


class LabPasswordResetDoneView(PasswordResetDoneView):
    template_name = "users/password_reset_done.html"


class LabPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = StyledSetPasswordForm
    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy("users:password_reset_complete")


class LabPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"


# ------------------------------------------------------- admin management
def _redirect_back(request, default="users:manage_list"):
    nxt = request.POST.get("next", "")
    if nxt and url_has_allowed_host_and_scheme(
        nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(nxt)
    return redirect(default)


@role_required(ADMIN)
def user_list_view(request):
    qs = User.objects.all().order_by("username")

    q = request.GET.get("q", "").strip()
    role = request.GET.get("role", "")
    status = request.GET.get("status", "")

    if q:
        qs = qs.filter(
            Q(username__icontains=q)
            | Q(email__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
        )
    if role in User.Role.values:
        qs = qs.filter(role=role)
    if status == "active":
        qs = qs.filter(is_active=True)
    elif status == "inactive":
        qs = qs.filter(is_active=False)

    page_obj = Paginator(qs, 15).get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)

    return render(
        request,
        "users/user_list.html",
        {
            "page_obj": page_obj,
            "q": q,
            "role": role,
            "status": status,
            "roles": User.Role.choices,
            "querystring": params.urlencode(),
        },
    )


# Self-targeting is blocked in both actions below, so the acting admin always
# remains an active admin and the system can't be left without one.
@require_POST
@role_required(ADMIN)
def change_role_view(request, pk):
    target = get_object_or_404(User, pk=pk)
    if target.pk == request.user.pk:
        messages.error(request, "You can't change your own role.")
    elif target.is_superuser:
        messages.error(request, "Superuser roles are managed in /admin/.")
    else:
        form = UserRoleForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"{target.username} is now {target.get_role_display()}."
            )
        else:
            messages.error(request, "Invalid role.")
    return _redirect_back(request)


@require_POST
@role_required(ADMIN)
def toggle_active_view(request, pk):
    target = get_object_or_404(User, pk=pk)
    if target.pk == request.user.pk:
        messages.error(request, "You can't deactivate your own account here.")
    elif target.is_superuser:
        messages.error(request, "Superusers are managed in /admin/.")
    else:
        target.is_active = not target.is_active
        target.save(update_fields=["is_active"])
        state = "activated" if target.is_active else "deactivated"
        messages.success(request, f"{target.username} {state}.")
    return _redirect_back(request)