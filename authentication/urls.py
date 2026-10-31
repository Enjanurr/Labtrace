from django.urls import path

from . import views

app_name = "authentication"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.LabTraceLoginView.as_view(), name="login"),
    path("logout/", views.LabTraceLogoutView.as_view(), name="logout"),
]