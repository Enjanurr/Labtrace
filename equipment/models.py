from django.db import models
from django.db.models import Q


class Condition(models.TextChoices):
    GOOD = "GOOD", "Good"
    DAMAGED = "DAMAGED", "Damaged"
    MALFUNCTIONING = "MALFUNCTIONING", "Malfunctioning"
    MISSING = "MISSING", "Missing"


class Asset(models.Model):
    class Availability(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        BORROWED = "BORROWED", "Borrowed"
        MAINTENANCE = "MAINTENANCE", "Maintenance"
        MISSING = "MISSING", "Missing"

    asset_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    availability_status = models.CharField(
        max_length=20,
        choices=Availability.choices,
        default=Availability.AVAILABLE,
        db_index=True,
    )

    class Meta:
        ordering = ["asset_code"]

    def __str__(self):
        return f"{self.asset_code} - {self.name}"


class EquipmentLog(models.Model):
    # PROTECT: history must survive. Soft-delete users/assets instead.
    visit = models.ForeignKey(
        "access_logging.LabVisit",
        on_delete=models.PROTECT,
        related_name="equipment_logs",
    )
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name="logs")
    borrowed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    pre_condition = models.CharField(max_length=20, choices=Condition.choices)
    post_condition = models.CharField(
        max_length=20, choices=Condition.choices, null=True, blank=True
    )
    pre_condition_img = models.ImageField(
        upload_to="conditions/pre/", null=True, blank=True
    )
    post_condition_img = models.ImageField(
        upload_to="conditions/post/", null=True, blank=True
    )

    class Meta:
        ordering = ["-borrowed_at"]
        constraints = [
            # An asset can have at most one open (unreturned) log.
            models.UniqueConstraint(
                fields=["asset"],
                condition=Q(returned_at__isnull=True),
                name="one_open_log_per_asset",
            ),
        ]

    @property
    def is_open(self):
        return self.returned_at is None

    def __str__(self):
        return f"{self.asset.asset_code} / {self.visit.user.username}"