from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.institutions.models import Campus, EmailDomain, HostRole, Hub, University, Venue

# Fictional institutions on example.org domains only (FR-04, Q-05). Never add real ones here.
UNIVERSITIES = {
    "LU": (
        "Lakeside University",
        [("lu.example.org", "MEMBER"), ("staff.lu.example.org", "STAFF_ONLY")],
    ),
    "HIT": ("Highland Institute of Technology", [("hit.example.org", "MEMBER")]),
}
CAMPUSES = [
    ("LU", "MAIN", "Main Campus", "Kigali"),
    ("LU", "SOUTH", "South Campus", "Huye"),
    ("HIT", "MAIN", "Main Campus", "Musanze"),
]
HUBS = [("RIH", "Riverside Innovation Hub", "Kigali")]
# (email, display name, role, host short code)
STAFF = [
    ("organizer@demo.example.org", "Demo Organizer", "ORGANIZER", "LU/MAIN"),
    ("approver@demo.example.org", "Demo Approver", "APPROVER", "LU/MAIN"),
    ("gate@demo.example.org", "Demo Gate Staff", "GATE_STAFF", "LU/MAIN"),
    ("hub.organizer@demo.example.org", "Demo Hub Organizer", "ORGANIZER", "RIH"),
]


class Command(BaseCommand):
    help = "Create synthetic institutions, Venues, users and Host roles. Safe to run again."

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()
        hosts = {}
        for code, (name, domains) in UNIVERSITIES.items():
            university, _ = University.objects.get_or_create(
                short_code=code, defaults={"name": name}
            )
            for domain, kind in domains:
                EmailDomain.objects.get_or_create(
                    domain=domain,
                    defaults={
                        "university": university,
                        "kind": kind,
                        "confirmed_by_institution_at": now,
                    },
                )
        for uni, code, name, city in CAMPUSES:
            campus, _ = Campus.objects.get_or_create(
                university=University.objects.get(short_code=uni),
                short_code=code,
                defaults={"name": name, "city": city},
            )
            hosts[f"{uni}/{code}"] = {"campus": campus}
        for code, name, city in HUBS:
            hub, _ = Hub.objects.get_or_create(
                short_code=code, defaults={"name": name, "city": city}
            )
            hosts[code] = {"hub": hub}
        for host in hosts.values():
            Venue.objects.get_or_create(name="Main Hall", **host, defaults={"capacity": 200})

        users = get_user_model().objects
        for email, display_name, role, host in STAFF:
            user = users.filter(email__iexact=email).first()
            if user is None:
                # No password; set one with `manage.py changepassword <email>`.
                user = users.create_user(email, display_name=display_name)
            HostRole.objects.get_or_create(user=user, role=role, **hosts[host])

        self.stdout.write(
            self.style.SUCCESS(f"Seeded {len(hosts)} Hosts and {len(STAFF)} staff users.")
        )
