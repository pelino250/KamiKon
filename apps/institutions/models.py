import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils import timezone

# Venues and Host roles belong to exactly one Host: a Campus or a Hub.
ONE_HOST = Q(campus__isnull=False, hub__isnull=True) | Q(campus__isnull=True, hub__isnull=False)


class University(models.Model):
    public_id = models.UUIDField(default=uuid.uuid7, unique=True, editable=False)
    name = models.CharField(max_length=200)
    short_code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "universities"

    def __str__(self):
        return self.short_code


class EmailDomain(models.Model):
    class Kind(models.TextChoices):
        MEMBER = "MEMBER"
        STAFF_ONLY = "STAFF_ONLY"
        ALUMNI = "ALUMNI"

    university = models.ForeignKey(University, on_delete=models.PROTECT, related_name="domains")
    domain = models.CharField(max_length=253, unique=True)
    kind = models.CharField(max_length=10, choices=Kind)
    # No Affiliations from a domain until its institution confirms it (R-11, Q-05).
    confirmed_by_institution_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = (
            models.CheckConstraint(
                condition=Q(domain=Lower("domain")), name="institutions_domain_lower_case"
            ),
        )

    def __str__(self):
        return self.domain

    def save(self, *args, **kwargs):
        self.domain = self.domain.lower()
        super().save(*args, **kwargs)


class Campus(models.Model):
    public_id = models.UUIDField(default=uuid.uuid7, unique=True, editable=False)
    university = models.ForeignKey(University, on_delete=models.PROTECT, related_name="campuses")
    name = models.CharField(max_length=200)
    short_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gate_instructions = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "campuses"
        constraints = (
            models.UniqueConstraint(
                fields=("university", "short_code"), name="institutions_campus_code_unique"
            ),
        )

    def __str__(self):
        return f"{self.university.short_code} {self.name}"


class Hub(models.Model):
    public_id = models.UUIDField(default=uuid.uuid7, unique=True, editable=False)
    name = models.CharField(max_length=200)
    short_code = models.CharField(max_length=20, unique=True)
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gate_instructions = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Venue(models.Model):
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, null=True, blank=True)
    hub = models.ForeignKey(Hub, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=200)
    building = models.CharField(max_length=200, blank=True)
    room_code = models.CharField(max_length=50, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        constraints = (
            models.CheckConstraint(condition=ONE_HOST, name="institutions_venue_one_host"),
        )

    def __str__(self):
        return self.name


class HostRole(models.Model):
    class Role(models.TextChoices):
        ORGANIZER = "ORGANIZER"
        APPROVER = "APPROVER"
        GATE_STAFF = "GATE_STAFF"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="host_roles"
    )
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=10, choices=Role)
    # Null once the granting account is deleted (FR-18).
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    granted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = (
            models.CheckConstraint(condition=ONE_HOST, name="institutions_hostrole_one_host"),
            # One of campus and hub is always null, so nulls must compare equal here.
            models.UniqueConstraint(
                fields=("user", "campus", "hub", "role"),
                nulls_distinct=False,
                name="institutions_hostrole_unique",
            ),
        )

    def __str__(self):
        return f"{self.user} {self.role} at {self.campus or self.hub}"
