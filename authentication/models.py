from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


def validate_institutional_email(value):
    """Only allow emails from the configured institutional domains."""
    allowed = getattr(settings, "ALLOWED_EMAIL_DOMAINS", ["cit.edu"])
    domain = value.rsplit("@", 1)[-1].lower() if "@" in value else ""
    if domain not in [d.lower() for d in allowed]:
        raise ValidationError(
            "Email must be an institutional address (@%(domains)s).",
            params={"domains": ", @".join(allowed)},
            code="invalid_domain",
        )


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        INSTRUCTOR = "INSTRUCTOR", "Instructor"
        RESEARCHER = "RESEARCHER", "Researcher"
        ADMIN = "ADMIN", "Admin"

    email = models.EmailField(
        "email address",
        unique=True,
        validators=[validate_institutional_email],
        error_messages={"unique": "A user with this email already exists."},
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        db_index=True,
    )
    # NOTE: `is_active` is inherited from AbstractUser (default=True).
    # We use it for soft-deletion: deactivated users can't log in,
    # but their visits, logs and incidents remain intact.

    class Meta:
        ordering = ["username"]

    def save(self, *args, **kwargs):
        # Normalize email so uniqueness is case-insensitive in practice
        if self.email:
            self.email = self.email.strip().lower()
        # Superusers are always ADMIN role
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    # Convenience role helpers (used by RBAC middleware & templates)
    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR

    @property
    def is_researcher(self):
        return self.role == self.Role.RESEARCHER

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_staff_role(self):
        """Instructors and Admins can manage incidents and view audit trails."""
        return self.role in (self.Role.INSTRUCTOR, self.Role.ADMIN)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"