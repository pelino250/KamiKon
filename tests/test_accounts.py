import pytest
from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError
from django.urls import reverse

pytestmark = pytest.mark.django_db
User = get_user_model()
PASSWORD = "correct-horse-battery"  # pragma: allowlist secret


def test_user_signs_in_with_email_regardless_of_case():
    User.objects.create_user("ada@example.org", PASSWORD)
    assert authenticate(username="ADA@example.org", password=PASSWORD)


def test_email_is_unique_regardless_of_case():
    User.objects.create_user("ada@example.org")
    with pytest.raises(IntegrityError):
        User.objects.create_user("Ada@example.org")


def test_public_id_is_uuid7_and_calendar_token_resets():
    user = User.objects.create_user("ada@example.org")
    assert user.public_id.version == 7
    old = user.calendar_token
    user.reset_calendar_token()
    assert user.calendar_token != old


def test_superuser_can_open_the_user_admin(client):
    admin = User.objects.create_superuser("admin@example.org", PASSWORD)
    client.force_login(admin)
    assert client.get(reverse("admin:accounts_user_changelist"), secure=True).status_code == 200
    assert client.get(reverse("admin:accounts_user_add"), secure=True).status_code == 200
