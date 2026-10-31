from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class LabVisit(models.Model):
    class Purpose(models.TextChoices):
        CLASS = "CLASS", "Class"
        RESEARCH = "RESEARCH", "Research"
        PROJECT = "PROJECT", "Project"
        TESTING = "TESTING", "Testing"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"

    # PROTECT: users are soft-deleted, so history must never cascade away.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lab_visits",
    )
    lab_location = models.CharField(max_length=100, db_index=True)
    purpose = models.CharField(max_length=20, choices=Purpose.choices)
    check_in_time = models.DateTimeField(auto_now_add=True, db_index=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True
    )

    class Meta:
        ordering = ["-check_in_time"]
        constraints = [
            # At most one ACTIVE visit per user, enforced by the database.
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(status="ACTIVE"),
                name="one_active_visit_per_user",
            ),
        ]

    @property
    def is_active_visit(self):
        return self.status == self.Status.ACTIVE

    def check_out(self, when=None):
        """Close the visit and compute the duration in whole minutes."""
        when = when or timezone.now()
        self.check_out_time = when
        self.duration_minutes = max(
            0, int((when - self.check_in_time).total_seconds() // 60)
        )
        self.status = self.Status.COMPLETED
        self.save(update_fields=["check_out_time", "duration_minutes", "status"])

    def __str__(self):
        return f"{self.user.username} @ {self.lab_location} ({self.get_status_display()})"