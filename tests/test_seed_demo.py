import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from apps.institutions.models import EmailDomain, HostRole, Venue

pytestmark = pytest.mark.django_db


def test_seed_demo_is_synthetic_and_can_run_twice():
    call_command("seed_demo", stdout=None)
    counts = (get_user_model().objects.count(), HostRole.objects.count(), Venue.objects.count())
    call_command("seed_demo", stdout=None)
    assert counts == (4, 4, 4)
    assert (
        get_user_model().objects.count(),
        HostRole.objects.count(),
        Venue.objects.count(),
    ) == counts
    emails = get_user_model().objects.values_list("email", flat=True)
    domains = EmailDomain.objects.values_list("domain", flat=True)
    assert all(value.endswith("example.org") for value in [*emails, *domains])
