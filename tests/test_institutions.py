import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.institutions.models import Campus, EmailDomain, HostRole, Hub, University, Venue

pytestmark = pytest.mark.django_db


@pytest.fixture
def campus():
    university = University.objects.create(name="Fictional University", short_code="FU")
    return Campus.objects.create(university=university, name="Main", short_code="MAIN", city="X")


@pytest.fixture
def hub():
    return Hub.objects.create(name="Fictional Hub", short_code="FH", city="X")


def test_domain_is_stored_lower_case_and_unique(campus):
    EmailDomain.objects.create(
        university=campus.university, domain="Mail.Example.org", kind="MEMBER"
    )
    assert EmailDomain.objects.get().domain == "mail.example.org"
    with pytest.raises(IntegrityError):
        EmailDomain.objects.create(
            university=campus.university, domain="MAIL.example.org", kind="ALUMNI"
        )


def test_campus_code_is_unique_within_a_university(campus):
    other = University.objects.create(name="Other University", short_code="OU")
    Campus.objects.create(university=other, name="Main", short_code="MAIN", city="X")
    with pytest.raises(IntegrityError):
        Campus.objects.create(university=campus.university, name="Dup", short_code="MAIN", city="X")


@pytest.mark.parametrize("with_campus, with_hub", [(False, False), (True, True)])
def test_venue_needs_exactly_one_host(campus, hub, with_campus, with_hub):
    with pytest.raises(IntegrityError):
        Venue.objects.create(
            name="Hall", campus=campus if with_campus else None, hub=hub if with_hub else None
        )


def test_host_role_is_unique_per_user_host_and_role(campus):
    user = get_user_model().objects.create_user("organizer@example.org")
    HostRole.objects.create(user=user, campus=campus, role="ORGANIZER")
    HostRole.objects.create(user=user, campus=campus, role="APPROVER")
    with pytest.raises(IntegrityError):
        HostRole.objects.create(user=user, campus=campus, role="ORGANIZER")
