from django.urls import path

from . import views

app_name = "access_logging"

urlpatterns = [
    path("check-in/", views.check_in_view, name="check_in"),
    path("<int:pk>/check-out/", views.check_out_view, name="check_out"),
    path("mine/", views.my_visits_view, name="my_visits"),
    path("active/", views.active_visits_view, name="active"),
]