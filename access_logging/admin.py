from django.contrib import admin

from .models import LabVisit


@admin.register(LabVisit)
class LabVisitAdmin(admin.ModelAdmin):
    list_display = ("user", "lab_location", "purpose", "status", "check_in_time", "check_out_time", "duration_minutes")
    list_filter = ("status", "purpose", "lab_location")
    search_fields = ("user__username", "user__email", "lab_location")
    date_hierarchy = "check_in_time"
    readonly_fields = ("check_in_time",)