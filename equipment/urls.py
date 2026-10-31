from django.urls import path

from . import views

app_name = "equipment"

urlpatterns = [
    path("", views.inventory_view, name="inventory"),
    path("borrow/", views.borrow_view, name="borrow"),
    path("logs/<int:pk>/return/", views.return_view, name="return"),
    path("mine/", views.my_equipment_view, name="mine"),
    # Staff only (middleware rule: /equipment/manage/)
    path("manage/new/", views.asset_form_view, name="asset_new"),
    path("manage/<int:pk>/edit/", views.asset_form_view, name="asset_edit"),
]