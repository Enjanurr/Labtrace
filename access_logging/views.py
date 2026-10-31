from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from authentication.models import User
from users.decorators import is_ajax, role_required

from .forms import CheckInForm
from .models import LabVisit

STAFF_ROLES = (User.Role.INSTRUCTOR, User.Role.ADMIN)


@login_required
def check_in_view(request):
    active = LabVisit.objects.filter(
        user=request.user, status=LabVisit.Status.ACTIVE
    ).first()
    if active:
        messages.info(
            request,
            f"You're already checked in at {active.lab_location}. Check out first.",
        )
        return redirect("access_logging:my_visits")

    if request.method == "POST":
        form = CheckInForm(request.POST)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.user = request.user
            try:
                with transaction.atomic():
                    visit.save()
            except IntegrityError:
                # Double-submit / second tab: the DB constraint caught it.
                messages.error(request, "You already have an active visit.")
                return redirect("access_logging:my_visits")
            messages.success(request, f"Checked in at {visit.lab_location}.")
            return redirect("access_logging:my_visits")
    else:
        form = CheckInForm()

    return render(request, "access_logging/check_in.html", {"form": form})


@require_POST
@login_required
def check_out_view(request, pk):
    """AJAX check-out. Owner can close their own visit; staff can close any."""
    with transaction.atomic():
        visit = get_object_or_404(
            LabVisit.objects.select_for_update().select_related("user"), pk=pk
        )
        if visit.user_id != request.user.pk and request.user.role not in STAFF_ROLES:
            return JsonResponse({"ok": False, "error": "Permission denied."}, status=403)
        if visit.status != LabVisit.Status.ACTIVE:
            return JsonResponse(
                {"ok": False, "error": "This visit is already checked out."}, status=409
            )
        open_count = visit.equipment_logs.filter(returned_at__isnull=True).count()
        if open_count:
            return JsonResponse(
                {
                    "ok": False,
                    "error": f"Return {open_count} borrowed item(s) before checking out.",
                },
                status=409,
            )
        visit.check_out()

    who = "You were" if visit.user_id == request.user.pk else f"{visit.user.username} was"
    return JsonResponse(
        {
            "ok": True,
            "duration_minutes": visit.duration_minutes,
            "message": f"{who} checked out. Duration: {visit.duration_minutes} min.",
        }
    )


@login_required
def my_visits_view(request):
    mine = LabVisit.objects.filter(user=request.user)
    current = mine.filter(status=LabVisit.Status.ACTIVE).first()
    history = mine.filter(status=LabVisit.Status.COMPLETED)
    page_obj = Paginator(history, 10).get_page(request.GET.get("page"))
    return render(
        request,
        "access_logging/my_visits.html",
        {"current": current, "page_obj": page_obj},
    )


@role_required(*STAFF_ROLES)
def active_visits_view(request):
    location = request.GET.get("location", "")
    qs = LabVisit.objects.filter(status=LabVisit.Status.ACTIVE).select_related("user")
    if location in settings.LAB_LOCATIONS:
        qs = qs.filter(lab_location=location)
    visits = list(qs)

    # jQuery polling gets JSON: row HTML + count.
    if is_ajax(request):
        return JsonResponse(
            {
                "count": len(visits),
                "html": render_to_string(
                    "access_logging/_active_rows.html",
                    {"visits": visits},
                    request=request,
                ),
            }
        )

    occupancy = (
        LabVisit.objects.filter(status=LabVisit.Status.ACTIVE)
        .values("lab_location")
        .annotate(n=Count("id"))
        .order_by("lab_location")
    )
    return render(
        request,
        "access_logging/active_visits.html",
        {
            "visits": visits,
            "occupancy": occupancy,
            "locations": settings.LAB_LOCATIONS,
            "location": location,
        },
    )