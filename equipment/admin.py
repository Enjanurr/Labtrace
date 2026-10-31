from django.contrib import admin

from .models import Asset, EquipmentLog


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("asset_code", "name", "availability_status")
    list_filter = ("availability_status",)
    search_fields = ("asset_code", "name")


@admin.register(EquipmentLog)
class EquipmentLogAdmin(admin.ModelAdmin):
    list_display = ("asset", "visit", "borrowed_at", "returned_at", "pre_condition", "post_condition")
    list_filter = ("pre_condition", "post_condition")
    search_fields = ("asset__asset_code", "visit__user__username")
    readonly_fields = ("borrowed_at",)