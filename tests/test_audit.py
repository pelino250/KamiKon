import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.audit.models import AppendOnlyError, AuditEntry
from apps.audit.services import record

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return get_user_model().objects.create_user("member@example.org")


def test_record_stores_the_target_by_public_id(user):
    entry = record("user.example", user, data={"code": "X"})
    assert (entry.target_type, entry.target_public_id) == ("user", user.public_id)
    assert entry.actor is None
    assert entry.data == {"code": "X"}


def test_entries_cannot_be_changed_or_deleted(user):
    entry = record("user.example", user)
    with pytest.raises(AppendOnlyError):
        entry.save()
    with pytest.raises(AppendOnlyError):
        entry.delete()
    with pytest.raises(AppendOnlyError):
        AuditEntry.objects.update(action="other")
    with pytest.raises(AppendOnlyError):
        AuditEntry.objects.all().delete()


def test_deleting_the_actor_keeps_the_entry(user):
    actor = get_user_model().objects.create_user("actor@example.org")
    record("user.example", user, actor=actor)
    actor.delete()
    assert AuditEntry.objects.get().actor is None


def test_admin_lists_entries_read_only(client, user):
    admin = get_user_model().objects.create_superuser("admin@example.org")
    entry = record("user.example", user, actor=admin)
    client.force_login(admin)
    assert client.get(reverse("admin:audit_auditentry_changelist"), secure=True).status_code == 200
    assert client.get(reverse("admin:audit_auditentry_add"), secure=True).status_code == 403
    url = reverse("admin:audit_auditentry_delete", args=[entry.pk])
    assert client.post(url, {"post": "yes"}, secure=True).status_code == 403
    assert AuditEntry.objects.count() == 1
