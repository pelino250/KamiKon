from .models import AuditEntry


def record(action, target, actor=None, data=None):
    """Append an entry for `target`, any model with a `public_id`."""
    return AuditEntry.objects.create(
        actor=actor,
        action=action,
        target_type=target._meta.model_name,
        target_public_id=target.public_id,
        data=data or {},
    )
