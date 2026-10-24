import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.urls import reverse

from apps.audit.models import AuditEntry
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


def test_admin_records_who_granted_a_host_role(client, campus):
    admin = get_user_model().objects.create_superuser("admin@example.org")
    organizer = get_user_model().objects.create_user("organizer@example.org")
    client.force_login(admin)
    url = reverse("admin:institutions_hostrole_add")
    data = {"user": organizer.pk, "campus": campus.pk, "role": "ORGANIZER"}
    assert client.post(url, data, secure=True).status_code == 302
    assert HostRole.objects.get().granted_by == admin
    for model in ("university", "campus", "hub", "venue", "hostrole"):
        url = reverse(f"admin:institutions_{model}_changelist")
        assert client.get(url, secure=True).status_code == 200


def test_admin_audits_grants_and_revocations(client, campus, hub):
    admin = get_user_model().objects.create_superuser("admin@example.org")
    organizer = get_user_model().objects.create_user("organizer@example.org")
    client.force_login(admin)
    add = reverse("admin:institutions_hostrole_add")
    for host in ({"campus": campus.pk}, {"hub": hub.pk}, {"campus": campus.pk, "role": "APPROVER"}):
        data = {"user": organizer.pk, "role": "ORGANIZER", **host}
        assert client.post(add, data, secure=True).status_code == 302
    granted = AuditEntry.objects.get(action="host_role.granted", data__host_type="hub")
    assert granted.actor == admin
    assert granted.target_public_id == organizer.public_id
    assert granted.data == {
        "role": "ORGANIZER",
        "host_type": "hub",
        "host_public_id": str(hub.public_id),
    }

    first, *rest = HostRole.objects.order_by("pk")
    url = reverse("admin:institutions_hostrole_delete", args=[first.pk])
    assert client.post(url, {"post": "yes"}, secure=True).status_code == 302
    changelist = reverse("admin:institutions_hostrole_changelist")
    data = {"action": "delete_selected", "post": "yes", "_selected_action": [r.pk for r in rest]}
    assert client.post(changelist, data, secure=True).status_code == 302
    assert not HostRole.objects.exists()
    assert AuditEntry.objects.filter(action="host_role.revoked", actor=admin).count() == 3


def test_admin_cannot_change_a_granted_role(client, campus):
    admin = get_user_model().objects.create_superuser("admin@example.org")
    role = HostRole.objects.create(user=admin, campus=campus, role="ORGANIZER")
    client.force_login(admin)
    url = reverse("admin:institutions_hostrole_change", args=[role.pk])
    response = client.get(url, secure=True)
    assert response.status_code == 200
    assert 'name="role"' not in response.content.decode()
    client.post(url, {"user": admin.pk, "campus": campus.pk, "role": "APPROVER"}, secure=True)
    role.refresh_from_db()
    assert role.role == "ORGANIZER"
