import secrets
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone


def new_calendar_token():
    return secrets.token_urlsafe(32)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **fields):
        if not email:
            raise ValueError("Users need an email address.")
        user = self.model(email=self.normalize_email(email), **fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **fields):
        fields.update(is_staff=True, is_superuser=True)
        return self.create_user(email, password, **fields)

    def get_by_natural_key(self, email):
        # Sign-in ignores case, matching the unique index on Lower(email).
        return self.get(email__iexact=email)


class User(AbstractBaseUser, PermissionsMixin):
    """An account that signs in with its email address (02_ARCHITECTURE.md §4.2)."""

    public_id = models.UUIDField(default=uuid.uuid7, unique=True, editable=False)
    # unique=True satisfies auth.E003; the Lower(email) constraint makes it case-insensitive.
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    # Blank unless the user registered for an Event with an ID check at the gate.
    legal_name = models.CharField(max_length=200, blank=True)
    organization = models.CharField(max_length=200, blank=True)
    role_label = models.CharField(max_length=100, blank=True)
    age_confirmed_at = models.DateTimeField(null=True, blank=True)
    calendar_token = models.CharField(max_length=64, unique=True, default=new_calendar_token)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    class Meta:
        constraints = (
            models.UniqueConstraint(Lower("email"), name="accounts_user_email_ci_unique"),
        )

    def __str__(self):
        return self.display_name or self.email

    def reset_calendar_token(self):
        self.calendar_token = new_calendar_token()
        self.save(update_fields=["calendar_token"])
