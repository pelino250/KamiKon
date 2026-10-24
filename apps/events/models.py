import uuid

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q

from apps.institutions.models import Campus, Hub, Venue


class Event(models.Model):
    class Category(models.TextChoices):
        LECTURE = "LECTURE"
        WORKSHOP = "WORKSHOP"
        SEMINAR = "SEMINAR"
        HACKATHON = "HACKATHON"
        CONFERENCE = "CONFERENCE"
        CAREER_FAIR = "CAREER_FAIR"
        COMPETITION = "COMPETITION"
        OTHER = "OTHER"

    class AccessPolicy(models.TextChoices):
        PUBLIC_COMMUNITY = "PUBLIC_COMMUNITY"
        OPEN_ALL_UNIVERSITIES = "OPEN_ALL_UNIVERSITIES"
        INSTITUTION_ONLY = "INSTITUTION_ONLY"
        CAMPUS_ONLY = "CAMPUS_ONLY"

    class DeliveryMode(models.TextChoices):
        IN_PERSON = "IN_PERSON"
        ONLINE = "ONLINE"
        HYBRID = "HYBRID"

    class Status(models.TextChoices):
        DRAFT = "DRAFT"
        PENDING_APPROVAL = "PENDING_APPROVAL"
        PUBLISHED = "PUBLISHED"
        REJECTED = "REJECTED"
        CANCELLED = "CANCELLED"

    public_id = models.UUIDField(default=uuid.uuid7, unique=True, editable=False)
    slug = models.SlugField(max_length=120, unique=True)
    title = models.CharField(max_length=200)
    abstract = models.TextField()
    category = models.CharField(max_length=11, choices=Category)
    speakers = models.TextField(blank=True)
    host_campus = models.ForeignKey(Campus, on_delete=models.PROTECT, null=True, blank=True)
    host_hub = models.ForeignKey(Hub, on_delete=models.PROTECT, null=True, blank=True)
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, null=True, blank=True)
    organizer_label = models.CharField(max_length=200, blank=True)
    # FR-18 decides what account deletion does to created Events (M1-4).
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    access_policy = models.CharField(max_length=21, choices=AccessPolicy)
    delivery_mode = models.CharField(max_length=9, choices=DeliveryMode)
    online_url = models.URLField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    gate_opens_minutes = models.PositiveSmallIntegerField(default=120)
    id_check_at_gate = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=Status, default=Status.DRAFT)
    status_reason = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    # Incremented on every change to time, venue or status (M2-2).
    version = models.PositiveIntegerField(default=1)
    # "simple": no stemming, since Events may be written in English or Kinyarwanda (NFR-07).
    # Queries must use SearchQuery(..., config="simple") to match.
    search_vector = models.GeneratedField(
        expression=SearchVector("title", "abstract", "speakers", config="simple"),
        output_field=SearchVectorField(),
        db_persist=True,
    )
    tags = models.ManyToManyField("Tag", through="EventTag", related_name="events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = (GinIndex(fields=("search_vector",)),)
        constraints = (
            models.CheckConstraint(
                condition=Q(host_campus__isnull=False, host_hub__isnull=True)
                | Q(host_campus__isnull=True, host_hub__isnull=False),
                name="events_event_one_host",
            ),
            models.CheckConstraint(
                condition=Q(host_hub__isnull=True)
                | Q(access_policy__in=("PUBLIC_COMMUNITY", "OPEN_ALL_UNIVERSITIES")),
                name="events_event_hub_policy",
            ),
            models.CheckConstraint(
                condition=Q(ends_at__gt=F("starts_at")), name="events_event_ends_after_start"
            ),
            models.CheckConstraint(
                condition=Q(delivery_mode="ONLINE") | Q(venue__isnull=False),
                name="events_event_venue_required",
            ),
            models.CheckConstraint(
                condition=Q(delivery_mode="IN_PERSON") & Q(online_url="")
                | ~Q(delivery_mode="IN_PERSON") & ~Q(online_url=""),
                name="events_event_online_url",
            ),
        )

    def clean(self):
        # A Venue belongs to one Host; PostgreSQL cannot check this across tables.
        if self.venue and (
            self.venue.campus_id != self.host_campus_id or self.venue.hub_id != self.host_hub_id
        ):
            raise ValidationError({"venue": "The Venue must belong to the Event's Host."})

    def __str__(self):
        return self.title


class SeatPool(models.Model):
    class Kind(models.TextChoices):
        HOST_MEMBERS = "HOST_MEMBERS"
        VISITING_MEMBERS = "VISITING_MEMBERS"
        COMMUNITY_GUESTS = "COMMUNITY_GUESTS"

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="seat_pools")
    kind = models.CharField(max_length=16, choices=Kind)
    # Null means unlimited, allowed only for ONLINE Events.
    capacity = models.PositiveIntegerField(null=True, blank=True)
    confirmed_count = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=("event", "kind"), name="events_seatpool_unique"),
            # Backstop for allocation under select_for_update() (ADR-0004).
            models.CheckConstraint(
                condition=Q(capacity__isnull=True) | Q(confirmed_count__lte=F("capacity")),
                name="events_seatpool_not_oversold",
            ),
        )

    def clean(self):
        event = self.event
        if self.capacity is None and event.delivery_mode != Event.DeliveryMode.ONLINE:
            raise ValidationError({"capacity": "Only online Events may have unlimited seats."})
        if self.capacity != 0 and not self.allowed_for(event):
            raise ValidationError({"capacity": "This Access Policy allows no seats here."})

    def allowed_for(self, event):
        """Whether the Event's Host and Access Policy can assign this pool (§5.1)."""
        if event.host_hub_id:
            return self.kind != self.Kind.HOST_MEMBERS
        if event.access_policy in (
            Event.AccessPolicy.INSTITUTION_ONLY,
            Event.AccessPolicy.CAMPUS_ONLY,
        ):
            return self.kind == self.Kind.HOST_MEMBERS
        return True

    def __str__(self):
        return f"{self.event} {self.kind}"


class Tag(models.Model):
    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class EventTag(models.Model):
    MAX_PER_EVENT = 5

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=("event", "tag"), name="events_eventtag_unique"),
        )

    def clean(self):
        others = EventTag.objects.filter(event_id=self.event_id).exclude(pk=self.pk)
        if others.count() >= self.MAX_PER_EVENT:
            raise ValidationError(f"An Event has at most {self.MAX_PER_EVENT} tags.")
