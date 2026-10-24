from django.db import transaction

from apps.audit.services import record

from .models import HostRole


def _audit_data(host_role):
    host = host_role.campus or host_role.hub
    return {
        "role": host_role.role,
        "host_type": host._meta.model_name,
        "host_public_id": str(host.public_id),
    }


@transaction.atomic
def grant_host_role(host_role: HostRole, granted_by=None) -> HostRole:
    """Save a new, unsaved HostRole and audit the grant (FR-03)."""
    host_role.granted_by = granted_by
    host_role.save()
    record("host_role.granted", host_role.user, actor=granted_by, data=_audit_data(host_role))
    return host_role


@transaction.atomic
def revoke_host_role(host_role: HostRole, revoked_by=None) -> None:
    record("host_role.revoked", host_role.user, actor=revoked_by, data=_audit_data(host_role))
    host_role.delete()
