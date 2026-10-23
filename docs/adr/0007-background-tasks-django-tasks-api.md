# Background work uses Django's Tasks API with a database-backed worker; no Redis in v1

Status: accepted, 2026-10-23.

## Context
The earlier design used Celery with Redis, plus Django Channels for real-time updates. v1 background work is low volume: emails, pass issuance, reminders, retention. Each extra service raises the cost for self-hosters. Redis 7.4 to 7.8 is not under an open-source licence (RSALv2 or SSPLv1). Django 6.0 added a Tasks API but ships no production worker; `django-tasks-db` (BSD-3-Clause) provides a database backend and a `db_worker` command. It is marked beta, and its PyPI classifiers list Django 5.2 and 6.0 only.

## Decision
- Application code defines and enqueues work only through `django.tasks`.
- Production uses `django-tasks-db` with `manage.py db_worker` as a second process. Tests use the immediate backend, plus one integration test that runs the real worker.
- Periodic jobs are enqueued by `manage.py enqueue_periodic` from cron or a systemd timer.
- No WebSockets in v1; the notification count refreshes on page load and through HTMX polling at most once a minute.

## Consequences
PostgreSQL is the only stateful service. If `django-tasks-db` fails on a Django version the project needs (R-07), the fallback is a Celery-based backend with Valkey, which changes configuration and deployment but not application code.
