from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from access_logging.models import LabVisit
from authentication.models import User
from users.decorators import forbidden_response, role_required

from .forms import AssetForm, BorrowForm, ReturnForm
from .models import Asset, Condition, EquipmentLog

STAFF_ROLES = (User.Role.INSTRUCTOR, User.Role.ADMIN)

# What happens to the asset depending on its condition on return
RETURN_STATUS = {
    Condition.GOOD: Asset.Availability.AVAILABLE,
    Condition.DAMAGED: Asset.Availability.MAINTENANCE,
    Condition.MALFUNCTIONING: Asset.Availability.MAINTENANCE,
    Condition.MISSING: Asset.Availability.MISSING,
}


@login_required
def inventory_view(request):
    qs = Asset.objects.all()
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")

    if q:
        qs = qs.filter(Q(asset_code__icontains=q) | Q(name__icontains=q))
    if status in Asset.Availability.values:
        qs = qs.filter(availability_status=status)

    page_obj = Paginator(qs, 15).get_page(request.GET.get("page"))

    # Who currently holds the borrowed items on this page
    open_logs = EquipmentLog.objects.filter(
        asset__in=list(page_obj), returned_at__isnull=True
    ).select_related("visit__user")
    holders = {log.asset_id: log for log in open_logs}
    for asset in page_obj:
        asset.open_log = holders.get(asset.pk)

    params = request.GET.copy()
    params.pop("page", None)

    return render(
        request,
        "equipment/inventory.html",
        {
            "page_obj": page_obj,
            "q": q,
            "status": status,
            "statuses": Asset.Availability.choices,
            "querystring": params.urlencode(),
        },
    )


@login_required
def borrow_view(request):
    visit = LabVisit.objects.filter(
        user=request.user, status=LabVisit.Status.ACTIVE
    ).first()
    if not visit:
        messages.error(request, "Check in to a lab before borrowing equipment.")
        return redirect("access_logging:check_in")

    if request.method == "POST":
        form = BorrowForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    asset = Asset.objects.select_for_update().get(
                        pk=form.cleaned_data["asset"].pk
                    )
                    if asset.availability_status != Asset.Availability.AVAILABLE:
                        form.add_error("asset", "This item was just taken by someone else.")
                    else:
                        log = form.save(commit=False)
                        log.visit = visit
                        log.asset = asset
                        log.save()
                        asset.availability_status = Asset.Availability.BORROWED
                        asset.save(update_fields=["availability_status"])
                        messages.success(request, f"You borrowed {asset}.")
                        return redirect("equipment:mine")
            except IntegrityError:
                form.add_error("asset", "This item was just taken by someone else.")
    else:
        form = BorrowForm(initial={"asset": request.GET.get("asset")})

    return render(request, "equipment/borrow.html", {"form": form, "visit": visit})


@login_required
def return_view(request, pk):
    log = get_object_or_404(
        EquipmentLog.objects.select_related("asset", "visit__user"), pk=pk
    )
    if log.visit.user_id != request.user.pk and request.user.role not in STAFF_ROLES:
        return forbidden_response(request)

    if log.returned_at:
        messages.info(request, "This item was already returned.")
        return redirect("equipment:mine")

    if request.method == "POST":
        form = ReturnForm(request.POST, request.FILES, instance=log)
        if form.is_valid():
            with transaction.atomic():
                entry = form.save(commit=False)
                entry.returned_at = timezone.now()
                entry.save()
                asset = entry.asset
                asset.availability_status = RETURN_STATUS[entry.post_condition]
                asset.save(update_fields=["availability_status"])

            if entry.post_condition == Condition.GOOD:
                messages.success(request, f"{asset.asset_code} returned. Thank you!")
            else:
                messages.warning(
                    request,
                    f"{asset.asset_code} logged as {entry.get_post_condition_display()} "
                    f"and marked {asset.get_availability_status_display()}. "
                    "Consider filing an incident report.",
                )
            return redirect("equipment:mine")
    else:
        form = ReturnForm(instance=log)

    return render(request, "equipment/return.html", {"form": form, "log": log})


@login_required
def my_equipment_view(request):
    mine = EquipmentLog.objects.filter(visit__user=request.user).select_related(
        "asset", "visit"
    )
    current = mine.filter(returned_at__isnull=True)
    history = mine.filter(returned_at__isnull=False)
    page_obj = Paginator(history, 10).get_page(request.GET.get("page"))
    return render(
        request,
        "equipment/my_equipment.html",
        {"current": current, "page_obj": page_obj},
    )


@role_required(*STAFF_ROLES)
def asset_form_view(request, pk=None):
    asset = get_object_or_404(Asset, pk=pk) if pk else None

    if request.method == "POST":
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            saved = form.save()
            messages.success(request, f"{saved} saved.")
            return redirect("equipment:inventory")
    else:
        form = AssetForm(instance=asset)

    return render(request, "equipment/asset_form.html", {"form": form, "asset": asset})