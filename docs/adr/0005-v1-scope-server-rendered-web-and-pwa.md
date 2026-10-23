# v1.0 is a server-rendered web app plus a PWA for passes and scanning, with session authentication

Status: accepted, 2026-10-23 (confirmed by the maintainer).

## Context
The earlier plan delivered four frontends (Django templates with HTMX, a DRF API, Flutter, and React or Angular) in 18 weeks, with JWT and session authentication side by side. For one maintainer that means three UIs to keep consistent and a token system with no v1 consumer.

## Decision
- v1.0 ships Django templates with HTMX, and an installable PWA served by the same Django application for offline passes and the scanner.
- `/api/v1/` exists only for what the PWA needs (`docs/03_API_SPEC.md`), authenticated by session cookie with CSRF protection.
- Authentication uses `django-allauth`: email as login identifier, email confirmation, rate limits, optional TOTP.
- Flutter, a separate SPA, token authentication and push notifications are post-v1 tracks, each requiring its own ADR.

## Consequences
Course tracks for mobile and SPA development start after v1.0, against a stable and documented API. Native-app features such as push and wallet integration wait. The codebase has one UI to test for accessibility and translation.
