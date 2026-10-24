from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchQuery
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.events.models import Event, EventTag, SeatPool, Tag
from apps.institutions.models import Campus, Hub, University, Venue

pytestmark = pytest.mark.django_db


@pytest.fixture
def campus():
    university = University.objects.create(name="Fictional University", short_code="FU")
    return Campus.objects.create(university=university, name="Main", short_code="MAIN", city="X")


@pytest.fixture
def hub():
    return Hub.objects.create(name="Fictional Hub", short_code="FH", city="X")


@pytest.fixture
def make_event(campus):
    user = get_user_model().objects.create_user("organizer@example.org")
    venue = Venue.objects.create(name="Hall", campus=campus, capacity=100)

    def make(save=True, **fields):
        starts_at = timezone.now() + timedelta(days=7)
        event = Event(
            slug=f"event-{Event.objects.count()}",
            title="Fictional lecture",
            abstract="Synthetic abstract.",
            category=Event.Category.LECTURE,
            host_campus=campus,
            venue=venue,
            created_by=user,
            access_policy=Event.AccessPolicy.OPEN_ALL_UNIVERSITIES,
            delivery_mode=Event.DeliveryMode.IN_PERSON,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=2),
        )
        for name, value in fields.items():
            setattr(event, name, value)
        if save:
            event.save()
        return event

    return make


def test_valid_event_is_searchable(make_event):
    event = make_event(abstract="Kubernetes in practice")
    query = SearchQuery("kubernetes", config="simple")
    assert Event.objects.filter(search_vector=query).get() == event


@pytest.mark.parametrize(
    ("fields", "constraint"),
    [
        ({"host_campus": None, "venue": None, "delivery_mode": "ONLINE"}, "one_host"),
        ({"ends_at": timezone.now()}, "ends_after_start"),
        ({"venue": None}, "venue_required"),
        (
            {"venue": None, "delivery_mode": "HYBRID", "online_url": "https://example.org/"},
            "venue_required",
        ),
        ({"online_url": "https://example.org/"}, "online_url"),
        ({"venue": None, "delivery_mode": "ONLINE"}, "online_url"),
        ({"delivery_mode": "HYBRID"}, "online_url"),
    ],
)
def test_event_check_constraints(make_event, fields, constraint):
    with pytest.raises(IntegrityError, match=f"events_event_{constraint}"):
        make_event(**fields)


def test_hub_events_allow_only_open_policies(make_event, hub):
    common = {"host_campus": None, "host_hub": hub, "venue": None, "delivery_mode": "ONLINE"}
    common["online_url"] = "https://example.org/"
    make_event(access_policy="PUBLIC_COMMUNITY", **common)
    with pytest.raises(IntegrityError, match="events_event_hub_policy"):
        make_event(access_policy="INSTITUTION_ONLY", **common)


def test_venue_must_belong_to_the_host(make_event, hub):
    event = make_event(save=False)
    event.full_clean()
    event.venue = Venue.objects.create(name="Hub Hall", hub=hub, capacity=50)
    with pytest.raises(ValidationError, match="Host"):
        event.full_clean()


def test_seat_pool_is_unique_per_kind_and_never_oversold(make_event):
    event = make_event()
    SeatPool.objects.create(event=event, kind="HOST_MEMBERS", capacity=10)
    with pytest.raises(IntegrityError, match="events_seatpool_unique"):
        SeatPool.objects.create(event=event, kind="HOST_MEMBERS", capacity=10)


def test_seat_pool_cannot_exceed_capacity(make_event):
    pool = SeatPool.objects.create(event=make_event(), kind="HOST_MEMBERS", capacity=1)
    pool.confirmed_count = 2
    with pytest.raises(IntegrityError, match="events_seatpool_not_oversold"):
        pool.save()


def test_only_online_events_have_unlimited_seats(make_event):
    with pytest.raises(ValidationError, match="unlimited"):
        SeatPool(event=make_event(), kind="HOST_MEMBERS", capacity=None).full_clean()
    online = make_event(venue=None, delivery_mode="ONLINE", online_url="https://example.org/")
    SeatPool(event=online, kind="HOST_MEMBERS", capacity=None).full_clean()


@pytest.mark.parametrize(
    ("policy", "on_hub", "kind", "allowed"),
    [
        ("INSTITUTION_ONLY", False, "HOST_MEMBERS", True),
        ("INSTITUTION_ONLY", False, "VISITING_MEMBERS", False),
        ("CAMPUS_ONLY", False, "COMMUNITY_GUESTS", False),
        ("PUBLIC_COMMUNITY", False, "COMMUNITY_GUESTS", True),
        ("PUBLIC_COMMUNITY", True, "HOST_MEMBERS", False),
        ("OPEN_ALL_UNIVERSITIES", True, "VISITING_MEMBERS", True),
    ],
)
def test_pools_the_policy_never_assigns_have_no_seats(
    make_event, hub, policy, on_hub, kind, allowed
):
    fields = {"access_policy": policy}
    if on_hub:
        fields |= {"host_campus": None, "host_hub": hub, "venue": None}
        fields |= {"delivery_mode": "ONLINE", "online_url": "https://example.org/"}
    event = make_event(**fields)
    SeatPool(event=event, kind=kind, capacity=0).full_clean()
    pool = SeatPool(event=event, kind=kind, capacity=10)
    if allowed:
        pool.full_clean()
    else:
        with pytest.raises(ValidationError, match="no seats"):
            pool.full_clean()


def test_event_has_at_most_five_unique_tags(make_event):
    event = make_event()
    tags = [Tag.objects.create(slug=f"tag-{i}", name=f"Tag {i}") for i in range(6)]
    for tag in tags[:5]:
        EventTag.objects.create(event=event, tag=tag)
    with pytest.raises(ValidationError, match="at most 5"):
        EventTag(event=event, tag=tags[5]).full_clean()
    with pytest.raises(IntegrityError, match="events_eventtag_unique"):
        EventTag.objects.create(event=event, tag=tags[0])
