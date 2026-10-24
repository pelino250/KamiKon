from django.conf import settings
from django.db import models


class AppendOnlyError(Exception):
    pass


class AuditEntryQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise AppendOnlyError("Audit entries cannot be changed.")

    def delete(self):
        raise AppendOnlyError("Audit entries cannot be deleted.")


class AuditEntry(models.Model):
    # Null for system actions, and once the actor's account is deleted (FR-18).
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    action = models.CharField(max_length=64)
    target_type = models.CharField(max_length=64)
    target_public_id = models.UUIDField()
    # Public IDs and codes only, never names, emails or free text (05_DATA_PROTECTION.md).
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = AuditEntryQuerySet.as_manager()

    class Meta:
        verbose_name_plural = "audit entries"
        indexes = (models.Index(fields=("target_type", "target_public_id")),)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise AppendOnlyError("Audit entries cannot be changed.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise AppendOnlyError("Audit entries cannot be deleted.")

    def __str__(self):
        return f"{self.action} {self.target_type} {self.target_public_id}"
