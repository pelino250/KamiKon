# 02 — Architecture and Data Model (v1.0)

Status: draft for v1.0. Governs implementation from milestone M1. Terms follow `GLOSSARY.md`; decisions D-nn and risks R-nn are in `00_DECISIONS_AND_AUDIT.md`.

## 1. Context

```text
 Attendee browser / installed PWA          Gate Staff phone (PWA scanner)
            |   HTTPS                                |  HTTPS (when online)
            v                                        v
   +--------------------------------------------------------+
   |  Reverse proxy (TLS)                                   |
   +--------------------------------------------------------+
            |
   +--------------------------------------------------------+
   |  Django web process (Gunicorn)                         |
   |   server-rendered pages (templates + HTMX)             |
   |   /api/v1/ (DRF, session auth) for PWA and scanner     |
   |   static files (WhiteNoise)                            |
   +--------------------------------------------------------+
            |                         |
   +-------------------+     +--------------------------+
   |  PostgreSQL       |<----|  Task worker (db_worker) |---> SMTP relay
   +-------------------+     +--------------------------+
```

One codebase, two processes (web and worker), one stateful service (PostgreSQL). The signing private key is a file mounted into the web and worker processes only. No third-party scripts, fonts, analytics or error trackers are loaded by default (NFR-05).

## 2. Technology choices

| Concern | Choice | Record |
| :--- | :--- | :--- |
| Language and runtime | Python 3.14 (`.python-version`) | D-15 |
| Framework | Django 6.1, moving to 6.2 LTS when released | R-09 |
| Database | PostgreSQL 17 in every environment | ADR-0006 |
| UI | Django templates, HTMX, CSS custom properties from design tokens; no CSS framework required | ADR-0005 |
| Offline | Service worker and IndexedDB in a PWA served by Django | ADR-0005 |
| Authentication | `django-allauth`, email login, sessions, optional TOTP | D-13 |
| API | Django REST Framework under `/api/v1/`, session auth with CSRF | `03_API_SPEC.md` |
| API schema | `drf-spectacular` generating OpenAPI 3 at `/api/v1/schema/` | R-08 |
| Background work | Django Tasks API, `django-tasks-db` backend, `db_worker` process | ADR-0007 |
| Pass signatures | Ed25519 through `cryptography` | ADR-0002 |
| QR rendering | `segno`, server-side SVG and PNG | D-21 |
| Calendar | `icalendar` | FR-33 |
| Static files | `whitenoise` | |
| App server | `gunicorn` | |

## 3. Module boundaries

Each Django app owns its models. Other apps call its `services.py` (writes) and `selectors.py` (reads), never its models' managers directly for writes. Views, forms and API serializers call services; they hold no business rules.

| App | Owns | Depends on |
| :--- | :--- | :--- |
| `apps.institutions` | University, EmailDomain, Campus, Hub, Venue, HostRole | none |
| `apps.accounts` | User, Affiliation | institutions |
| `apps.events` | Event, SeatPool, Tag | institutions, accounts |
| `apps.discovery` | no models; feed, filters, search, calendar feeds | events, accounts |
| `apps.tickets` | Registration, GatePass, SigningKey, CheckIn | events, accounts |
| `apps.notifications` | Notification, Subscription, NotificationPreference, task definitions | events, tickets, accounts |
| `apps.audit` | AuditEntry and `audit.record()` | none (others call it) |

The empty `apps.community` app is removed (C-26). Import rules are checked in CI with an import-linter contract added in milestone M1.

### 3.1 Extension points
- `kamikon.eligibility.EligibilityPolicy`: the class that answers "may this user register, and in which Seat Pool". A deployment can subclass it through the setting `KAMIKON_ELIGIBILITY_POLICY`, for example to add a rule for a specific institution. The default implements §5.
- Email templates live in `templates/email/` and can be overridden by a deployment's template directory.
- `KAMIKON_TILE_URL` and `KAMIKON_TILE_ATTRIBUTION` for the v1.1 map.
- Task backend through Django's `TASKS` setting (ADR-0007).
- Notification channels: `apps.notifications.channels` defines a `Channel` interface; v1 ships `EmailChannel` and `InAppChannel`. Push channels for post-v1 native clients implement the same interface.

## 4. Data model

All tables have an integer primary key `id` (`BigAutoField`) used only inside the database. Rows that appear in URLs or the API also have `public_id` (UUIDv7, unique, generated with Python's `uuid.uuid7()`) (ADR-0011). Timestamps are timezone-aware and stored in UTC; display uses `Africa/Kigali` by default (`TIME_ZONE`).

### 4.1 Institutions

**University**: `id`, `public_id`, `name`, `short_code` (unique, for example "UR"), `is_active`.

**EmailDomain**: `id`, `university` (FK), `domain` (unique, lower-case), `kind` (`MEMBER` | `STAFF_ONLY` | `ALUMNI`), `confirmed_by_institution_at` (required before the domain produces Affiliations; R-11, Q-05).

**Campus**: `id`, `public_id`, `university` (FK), `name`, `short_code` (unique within the University), `city`, `latitude`, `longitude` (nullable), `gate_instructions` (text).

**Hub**: `id`, `public_id`, `name`, `short_code` (unique), `city`, `latitude`, `longitude` (nullable), `gate_instructions`.

**Venue**: `id`, `campus` (FK, nullable), `hub` (FK, nullable), `name`, `building`, `room_code`, `capacity` (nullable). Check constraint: exactly one of `campus`, `hub`.

**HostRole**: `id`, `user` (FK), `campus` (FK, nullable), `hub` (FK, nullable), `role` (`ORGANIZER` | `APPROVER` | `GATE_STAFF`), `granted_by` (FK user), `granted_at`. Check constraint: exactly one of `campus`, `hub`. Unique on (`user`, `campus`, `hub`, `role`).

### 4.2 Accounts

**User** (custom, replaces the current `AbstractUser` subclass before any data exists): `id`, `public_id`, `email` (unique, case-insensitive through a functional unique index on `Lower(email)`), `display_name`, `legal_name` (blank unless the user has registered for an `id_check_at_gate` Event), `organization` (blank), `role_label` (blank), `age_confirmed_at`, `calendar_token` (random, resettable), `is_active`, `is_staff`, `is_superuser`, `date_joined`, `last_login`. No username field. Platform Admin is `is_staff` with the `institutions.manage` permission.

**Affiliation**: `id`, `user` (FK), `university` (FK), `email` (the institutional address), `member_role` (`STUDENT` | `STAFF`), `campus` (FK, nullable), `campus_changed_at`, `status` (`PENDING` | `VERIFIED` | `EXPIRED` | `REVOKED`), `method` (`EMAIL_CODE` | `ID_REVIEW`), `verified_at`, `expires_at`, `revoked_by` (FK user, nullable), `revoked_reason`.
Constraints: at most one non-revoked Affiliation per (`user`, `university`); a given institutional `email` is `VERIFIED` for at most one user (partial unique index on `Lower(email)` where `status = 'VERIFIED'`). `STAFF_ONLY` domains force `member_role = STAFF`.

A user is a **Verified Member** of a University when they hold an Affiliation with that University whose status is `VERIFIED` and `expires_at` is in the future. Otherwise they are a **Community Guest**.

### 4.3 Events

**Event**: `id`, `public_id`, `slug` (unique), `title`, `abstract`, `category` (`LECTURE` | `WORKSHOP` | `SEMINAR` | `HACKATHON` | `CONFERENCE` | `CAREER_FAIR` | `COMPETITION` | `OTHER`), `speakers` (text), `host_campus` (FK, nullable), `host_hub` (FK, nullable), `venue` (FK, nullable), `organizer_label` (text, for example a club name), `created_by` (FK user), `access_policy` (`PUBLIC_COMMUNITY` | `OPEN_ALL_UNIVERSITIES` | `INSTITUTION_ONLY` | `CAMPUS_ONLY`), `delivery_mode` (`IN_PERSON` | `ONLINE` | `HYBRID`), `online_url` (blank for `IN_PERSON`), `starts_at`, `ends_at`, `gate_opens_minutes` (default 120), `id_check_at_gate` (bool), `status` (`DRAFT` | `PENDING_APPROVAL` | `PUBLISHED` | `REJECTED` | `CANCELLED`), `status_reason`, `approved_by` (FK, nullable), `approved_at`, `version` (integer, incremented on every change to time, venue or status), `search_vector` (generated), `created_at`, `updated_at`.

Constraints:
- exactly one of `host_campus`, `host_hub`;
- `host_hub` not null implies `access_policy` in (`PUBLIC_COMMUNITY`, `OPEN_ALL_UNIVERSITIES`);
- `ends_at > starts_at`;
- `venue` belongs to the same Host;
- `IN_PERSON` and `HYBRID` require `venue`; `ONLINE` and `HYBRID` require `online_url`.

A "completed" Event is not a status; it is `PUBLISHED` with `ends_at` in the past.

**SeatPool**: `id`, `event` (FK), `kind` (`HOST_MEMBERS` | `VISITING_MEMBERS` | `COMMUNITY_GUESTS`), `capacity` (nullable means unlimited, allowed only for `ONLINE` Events), `confirmed_count`. Unique on (`event`, `kind`). Every Event has three rows; a pool the Access Policy does not allow has capacity 0.

**Tag**: `id`, `slug`, `name`. **EventTag**: (`event`, `tag`), at most five per Event.

### 4.4 Tickets

**Registration**: `id`, `public_id`, `event` (FK), `user` (FK), `seat_pool` (FK), `status` (`CONFIRMED` | `WAITLISTED` | `CANCELLED`), `waitlisted_at`, `confirmed_at`, `cancelled_at`, `name_snapshot`, `affiliation_snapshot` (University short code or "Community Guest", copied at confirmation so the roster does not change if the profile changes). Partial unique index on (`event`, `user`) where `status <> 'CANCELLED'`.

**GatePass**: `id`, `registration` (FK), `pass_id` (UUIDv4, random, unique; this is what the QR code carries), `code` (unique human code, format `KK-XXXX-XXXX` from the Crockford Base32 alphabet, random), `key_id`, `valid_from`, `valid_until`, `status` (`VALID` | `REVOKED`), `revoked_reason`, `issued_at`. At most one `VALID` pass per Registration.

**SigningKey**: `id`, `key_id` (1 to 255, unique), `public_key` (32 bytes), `status` (`ACTIVE` | `RETIRED` | `COMPROMISED`), `created_at`, `retired_at`. The private key is never stored in the database. Exactly one `ACTIVE` key.

**CheckIn**: `id`, `event` (FK), `gate_pass` (FK, nullable when the scanned code could not be resolved), `scanned_by` (FK user), `device_id` (random identifier generated by the scanner PWA), `client_scan_id` (UUID from the device, unique, makes uploads idempotent), `scanned_at` (device clock, corrected by the offset in §6.4), `received_at`, `mode` (`ONLINE` | `OFFLINE`), `result` (`VALID` | `ALREADY_USED` | `WRONG_EVENT` | `NOT_YET_VALID` | `EXPIRED` | `REVOKED` | `BAD_SIGNATURE` | `UNKNOWN_KEY`), `is_conflict` (bool). Partial unique index on `gate_pass` where `result = 'VALID'`: the database enforces single entry for online scans.

### 4.5 Notifications

**Notification**: `id`, `user`, `kind` (`REGISTRATION_CONFIRMED` | `WAITLISTED` | `PROMOTED` | `REGISTRATION_CANCELLED` | `EVENT_CHANGED` | `EVENT_CANCELLED` | `EVENT_APPROVED` | `EVENT_REJECTED` | `REVERIFY_SOON` | `REMINDER`), `event` (FK, nullable), `title`, `body`, `read_at`, `created_at`.

**Subscription**: `id`, `user`, `tag` | `campus` | `hub` (exactly one). **NotificationPreference**: `user` (one-to-one), `reminders` (default true), `weekly_digest` (default false).

### 4.6 Audit

**AuditEntry**: `id`, `actor` (FK, nullable for system), `action` (dotted string, for example `event.self_approved`), `target_type`, `target_public_id`, `data` (JSON, no free-text personal data), `created_at`. Append-only; no update or delete through the application.

### 4.7 Relationships

```text
University 1--* EmailDomain
University 1--* Campus 1--* Venue *--1 Hub
User 1--* Affiliation *--1 University ; Affiliation *--0..1 Campus
User 1--* HostRole *--1 (Campus | Hub)
(Campus | Hub) 1--* Event 1--3 SeatPool
Event 1--* Registration *--1 User ; Registration *--1 SeatPool
Registration 1--* GatePass (one VALID at a time) ; GatePass *--1 SigningKey (by key_id)
Event 1--* CheckIn *--0..1 GatePass
```

## 5. Eligibility and Seat Pools

### 5.1 Who may register

Let *u* be the user, *E* the Event, *H* its Host, and *U(H)* the University of *H* when *H* is a Campus.

| Access Policy | Eligible | Seat Pool |
| :--- | :--- | :--- |
| `PUBLIC_COMMUNITY` | Any active user with a confirmed email | Verified Member of *U(H)*: `HOST_MEMBERS`; Verified Member of another University: `VISITING_MEMBERS`; otherwise `COMMUNITY_GUESTS` |
| `OPEN_ALL_UNIVERSITIES` | Any Verified Member; Community Guests only if the `COMMUNITY_GUESTS` pool capacity is above 0 | As above |
| `INSTITUTION_ONLY` | Verified Members of *U(H)* | `HOST_MEMBERS` |
| `CAMPUS_ONLY` | Verified Members of *U(H)* whose Affiliation campus is *H* | `HOST_MEMBERS` |

Pools that a policy never assigns must have capacity 0: `VISITING_MEMBERS` and `COMMUNITY_GUESTS` for `INSTITUTION_ONLY` and `CAMPUS_ONLY`. A `PUBLIC_COMMUNITY` Event must have `COMMUNITY_GUESTS` above 0, otherwise the policy would be misleading.

For a Hub host there is no *U(H)*: every Verified Member falls into `VISITING_MEMBERS`, and `HOST_MEMBERS` must have capacity 0.

A user who is a Verified Member of several Universities is placed in `HOST_MEMBERS` if any of them is *U(H)*, otherwise `VISITING_MEMBERS`.

Eligibility is evaluated when the user registers and again when a waitlisted registration is promoted. If an Affiliation expires after confirmation, the registration stands.

### 5.2 Allocation

Registration runs in one database transaction:
1. Lock the target `SeatPool` row with `select_for_update()`.
2. If `capacity` is null or `confirmed_count < capacity`: create a `CONFIRMED` Registration, increment `confirmed_count`, and enqueue pass issuance and the confirmation email with `transaction.on_commit()`.
3. Otherwise create a `WAITLISTED` Registration with `waitlisted_at = now()`.

Cancellation locks the same row, decrements the count, and promotes the earliest `WAITLISTED` registration in the same pool whose user is still eligible, if the Event has not started.

Overselling is impossible as long as every write to `confirmed_count` goes through `tickets.services`. A database check constraint `confirmed_count <= capacity` (where capacity is not null) is the backstop.

## 6. Gate Pass design (ADR-0002)

### 6.1 Payload, version 1

| Bytes | Field | Notes |
| :--- | :--- | :--- |
| 0 | format version | `1` |
| 1 | `key_id` | 1 to 255 |
| 2–17 | `pass_id` | 16 bytes, random UUIDv4 |
| 18–33 | Event `public_id` | 16 bytes |
| 34–37 | `valid_from` | unsigned 32-bit, Unix time in minutes, big-endian |
| 38–41 | `valid_until` | same encoding |
| 42 | Seat Pool | 0 `HOST_MEMBERS`, 1 `VISITING_MEMBERS`, 2 `COMMUNITY_GUESTS` |
| 43–106 | Ed25519 signature | over the ASCII string `KAMIKON-PASS-1` followed by bytes 0–42 |

The 107 bytes are encoded with Base45 (RFC 9285) and prefixed with `KK1:`. The result is 165 characters from the QR alphanumeric character set, which keeps the code small enough to scan reliably from a phone screen. The payload contains no personal data.

`valid_from` = `starts_at` minus `gate_opens_minutes`; `valid_until` = `ends_at`.

### 6.2 Keys
- The private key is read from the file named by `KAMIKON_PASS_SIGNING_KEY_FILE` (PEM, PKCS #8). The application refuses to start in production if the file is missing, world-readable, or does not match the `ACTIVE` SigningKey's public key.
- `manage.py passkey generate` creates a key pair, writes the private key with mode 0600, and registers the public key as `RETIRED` until it is activated with `manage.py passkey activate KEY_ID`.
- Rotation: activate a new key; the old key becomes `RETIRED` and stays valid for verification until every pass signed with it has passed `valid_until`.
- Compromise: `manage.py passkey compromise KEY_ID` marks the key `COMPROMISED`; every pass signed with it is revoked and re-issued with the new key, attendees are notified, and scanners refuse the key from their next bundle refresh. The runbook is in `SECURITY.md` §5.

### 6.3 Verification order (server and scanner)
1. Prefix and version known, else `BAD_SIGNATURE`.
2. `key_id` known and not `COMPROMISED`, else `UNKNOWN_KEY`.
3. Signature valid, else `BAD_SIGNATURE`.
4. Event matches the scanner's selected Event, else `WRONG_EVENT`.
5. Time within the window, allowing 10 minutes of tolerance either side, else `NOT_YET_VALID` or `EXPIRED`.
6. `pass_id` not in the revocation list, else `REVOKED`.
7. Online: insert the `CheckIn`; a unique violation returns `ALREADY_USED` with the time of first use. Offline: check the device's local scan log; a match returns `ALREADY_USED`.
8. Otherwise `VALID`.

### 6.4 Scanner bundle
When Gate Staff open the scanner for an Event online, the PWA downloads the scanner bundle (`03_API_SPEC.md` §3.5): the public keys that are not compromised, the revoked `pass_id` list, the Event `version`, the server time, and, if Gate Staff choose "Download gate list", the roster (`pass_id`, code, name snapshot, affiliation snapshot, Seat Pool). The PWA computes the offset between the device and server clocks and applies it to `scanned_at`. The roster is stored in IndexedDB and deleted 24 hours after the Event ends, or on sign-out.

When online, the scanner refreshes the bundle every five minutes and whenever the Event `version` returned with a scan differs from the bundle's.

### 6.5 Offline queue and reconciliation
Offline scans are stored with `client_scan_id` and uploaded in batches on reconnect. The server processes each in `scanned_at` order: the first `VALID` scan of a pass becomes the check-in; later ones are stored with `result = ALREADY_USED` and `is_conflict = true` when they came from a different device. The Organizer's Event page lists conflicts. Uploads are idempotent by `client_scan_id`.

### 6.6 Browser implementation (to confirm at implementation)
Signature verification in the PWA uses Web Crypto Ed25519 where the browser supports it, and a pure-JavaScript Ed25519 library otherwise. Browser support for Ed25519 in Web Crypto, and the choice and licence of the JavaScript library and of the QR decoding library, were not verified in this review. The implementation PR for M3 must record these choices in an ADR with licence checks against `06_CI_CD_AND_RELEASES.md` §6.

### 6.7 Pass delivery
- The pass page `/passes/<public_id>/` renders the QR code as SVG and is cached by the service worker when first viewed.
- The confirmation email includes the QR code as a PNG attachment, so the pass is also available offline in the mail app if the browser has cleared its storage (§8, F-03).
- The human code `KK-XXXX-XXXX` is printed under the QR code for manual entry.

## 7. Background tasks (ADR-0007)

| Task | Trigger | Retry |
| :--- | :--- | :--- |
| `issue_gate_pass` | Registration confirmed | 5 attempts, exponential backoff from 10 s |
| `send_email` | Any notification with an email channel | 5 attempts from 60 s; then marked failed and shown in admin |
| `fan_out_event_change` | Urgent change or cancellation | 3 attempts; batches of 200 recipients |
| `send_reminders` | Every 15 minutes (scheduler) | idempotent per registration |
| `expire_affiliations` | Daily | idempotent |
| `apply_retention` | Daily | idempotent |
| `send_weekly_digest` | Weekly (deployment chooses the day and time) | idempotent per user per week |

Periodic tasks are run by a scheduler. The `django-tasks-db` package provides the worker, but whether it provides scheduling was not verified. Until it is, periodic tasks are enqueued by a `manage.py enqueue_periodic` command run from cron or a systemd timer, documented in the deployment guide.

## 8. Failure modes and recovery

| ID | What goes wrong | Detection | Behaviour and recovery |
| :--- | :--- | :--- | :--- |
| F-01 | Attendee closes the browser before the pass page is cached | Pass page never fetched (server log) | Confirmation email carries the PNG; "Open pass" on any later online visit caches it |
| F-02 | Attendee's phone is offline at the gate and has no cached pass | Gate Staff see no QR | Manual lookup by name in the downloaded roster; check in by code |
| F-03 | Browser clears PWA storage (WebKit's tracking prevention is reported to remove script-written storage for sites not visited for seven days unless the web app is installed; unverified in this review) | Pass missing offline | Prompt to install the PWA after the first registration; email PNG fallback |
| F-04 | Scanner device clock is wrong | Offset larger than 10 minutes when the bundle is fetched | Scanner shows a warning and applies the server offset; if never online, the 10-minute tolerance applies |
| F-05 | Scanner offline for the whole event | No bundle refresh | Works with the last bundle; revocations after the last refresh are not seen; conflicts reconciled at upload |
| F-06 | Upload interrupted halfway | Missing acknowledgements | Retries the whole batch; server de-duplicates by `client_scan_id` |
| F-07 | Event time moved after passes were issued | `version` changes | Passes are revoked and re-issued in one task; attendees get the urgent-change email; scanners see a new version and refresh |
| F-08 | Same pass shown at two offline gates | Conflict at reconciliation | Listed for the Organizer; documented trade-off (ADR-0002) |
| F-09 | Forged or altered QR code | Signature check | `BAD_SIGNATURE` with a distinct tone |
| F-10 | Signing key file missing or wrong in production | Startup check | Process refuses to start; `/readyz` fails; previously issued passes still verify on scanners |
| F-11 | Database unavailable | `/readyz` fails | Proxy returns a static maintenance page; scanners continue offline |
| F-12 | Task worker stopped | Oldest pending task older than 10 minutes, reported on `/readyz` as degraded | Emails and passes are delayed, not lost; tasks run when the worker restarts |
| F-13 | SMTP relay rejects or is down | Task failures | Retries, then a failed state visible in admin; in-app notifications still created |
| F-14 | Popular event: hundreds register in the same second | Lock wait time | Row lock serialises seat allocation per pool; waiting requests return within NFR-01 or time out with "Try again" and no seat is taken |
| F-15 | User registers twice in two tabs | Unique index | Second request returns the existing registration |
| F-16 | Affiliation email domain is shared with another institution or used by alumni | Platform Admin review | Domain kind `ALUMNI` or removal; existing Affiliations revoked with notice |
| F-17 | User enters someone else's institutional address | Mailbox proof | The code goes to the real owner; unused codes expire after 30 minutes; 5 attempts per hour per user |
| F-18 | A dependency stops supporting the Django version in use | CI on the upgrade branch | Pin, patch, or replace (R-07, R-08) |
| F-19 | Approver unavailable; pending Events stall | Pending older than 72 hours | Reminder to all Approvers of the Host; Platform Admin can approve |

## 9. Dependencies and licences

Licences as declared in PyPI metadata on 2026-10-23. All are compatible with distribution under Apache-2.0.

| Package | Version checked | Licence | Declares Django 6.1 support |
| :--- | :--- | :--- | :--- |
| django | 6.1.2 | BSD-3-Clause | n/a |
| psycopg, psycopg-binary | 3.3.6 | LGPL-3.0-only | n/a |
| python-dotenv | 1.2.4 | BSD-3-Clause | n/a |
| djangorestframework | 3.18.3 | BSD-3-Clause | yes |
| drf-spectacular | 0.30.0 | BSD-3-Clause | no (up to 6.0) |
| django-allauth | 65.20.1 | MIT | yes |
| django-htmx | 1.29.0 | MIT | yes |
| django-tasks-db | 0.13.0 | BSD-3-Clause | no (5.2, 6.0) |
| cryptography | 50.0.2 | Apache-2.0 OR BSD-3-Clause | n/a |
| segno | 1.6.6 | BSD | n/a |
| icalendar | 7.3.0 | BSD-2-Clause | n/a |
| whitenoise | 6.12.0 | MIT | no (up to 6.0) |
| gunicorn | 26.2.0 | MIT | n/a |

Notes:
- psycopg is LGPL-3.0. Importing it unmodified from Apache-2.0 code is permitted. Container images that bundle it must include its licence text, and users must remain able to replace it, which a normal Python installation allows. The release pipeline generates a third-party notices file from the SBOM (`06_CI_CD_AND_RELEASES.md` §4).
- PostgreSQL itself runs as a separate service and is not distributed in the application image.
- Frontend assets to add in M2 (HTMX, the Manrope and Noto Sans fonts, the QR decoding and Ed25519 libraries) were not licence-checked in this review. They are self-hosted, never loaded from a CDN, and checked before merge.
- Not used in v1: Redis (licence change from 7.4, C-14), Celery, Django Channels, Firebase, Sentry, `djangorestframework-simplejwt`.

## 10. Configuration

| Variable | Required | Purpose |
| :--- | :--- | :--- |
| `DEBUG` | no (default false) | Development behaviour only; does not select the database |
| `SECRET_KEY` | yes in production | Django secret, at least 50 characters |
| `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` | yes in production | Host validation |
| `DATABASE_URL` | yes | PostgreSQL connection string; `sslmode=require` unless the host is local |
| `EMAIL_URL` or `SMTP_*` | yes in production | Mail relay |
| `DEFAULT_FROM_EMAIL` | yes in production | Sender address |
| `KAMIKON_PASS_SIGNING_KEY_FILE` | yes in production | Path to the Ed25519 private key |
| `KAMIKON_RETENTION_DAYS` | no (default 90) | Days after Event end before roster data is anonymised |
| `KAMIKON_ID_REVIEW_ENABLED` | no (default false) | FR-17 |
| `KAMIKON_ELIGIBILITY_POLICY` | no | Extension point §3.1 |

The move from `DB_*` variables to `DATABASE_URL`, and from `DEBUG`-driven database selection to explicit configuration, is roadmap item M0-3.

## 11. Deployment shape

- Docker Compose file for development (`web`, `worker`, `db`, `mailpit`) and a production example (`web`, `worker`, `db`, reverse proxy), both in milestone M0 and M5.
- Container image: multi-stage build, Python slim base, non-root user, read-only root filesystem where possible, `manage.py check --deploy` passes.
- Backups: nightly `pg_dump`, encrypted, stored where the deployer's data-residency obligations allow (`05_DATA_PROTECTION.md`); restore tested each release.
