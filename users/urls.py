from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # Profile
    path("profile/", views.profile_view, name="profile"),
    path("profile/deactivate/", views.deactivate_account_view, name="deactivate"),
    path("password-change/", views.ChangePasswordView.as_view(), name="password_change"),

    # Password reset (offline, file-based email)
    path("password-reset/", views.LabPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", views.LabPasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        views.LabPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("password-reset/complete/", views.LabPasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # Admin-only user management (also guarded by middleware: /users/manage/)
    path("manage/", views.user_list_view, name="manage_list"),
    path("manage/<int:pk>/role/", views.change_role_view, name="manage_role"),
    path("manage/<int:pk>/toggle-active/", views.toggle_active_view, name="manage_toggle"),
]