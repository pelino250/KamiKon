# 03 — Interface Specification (v1.0)

Status: draft for v1.0, written before the API exists. Once an endpoint is implemented, the OpenAPI document generated at `/api/v1/schema/` is the contract for it, and this file keeps only the conventions in §1 and the rate limits in §4. A pull request that changes an endpoint updates the schema; it changes this file only if it changes a convention.

## 1. Conventions

- Base path `/api/v1/`. The version changes only for breaking changes; additive fields are not breaking.
- Authentication: Django session cookie. Unsafe methods require the `X-CSRFToken` header. No bearer tokens in v1 (ADR-0005).
- Identifiers in URLs and bodies are `public_id` values (UUID strings) or slugs, never database integers (ADR-0011).
- Times are ISO 8601 with offset, in UTC (`2026-11-05T12:00:00Z`).
- Enumerations use the exact upper-case values defined in `02_ARCHITECTURE.md` §4.
- Pagination: cursor-based, `?cursor=` with `next` and `previous` links; default 20, maximum 100.
- Errors: `application/problem+json` (RFC 9457) with `type`, `title`, `status`, `detail`, and for validation errors an `errors` object keyed by field.
- Rate limits return 429 with `Retry-After`.

## 2. Web routes (server-rendered)

| Route | Purpose | Access |
| :--- | :--- | :--- |
| `/` | Discovery list (FR-30, FR-31) | Anyone |
| `/events/<slug>/` | Event detail and registration control | Anyone; registration requires sign-in |
| `/events/<slug>.ics` | Calendar file for one Event | Anyone (published Events only) |
| `/events/<slug>/register/` | POST: register; POST `cancel`: cancel own registration | Signed-in user |
| `/passes/` | My upcoming and past passes | Signed-in user |
| `/passes/<public_id>/` | One Gate Pass, cacheable offline | Owner |
| `/calendar/<calendar_token>.ics` | Personal feed | Holder of the token |
| `/organize/` | Events I organize or approve | Organizer, Approver |
| `/organize/events/new/`, `/organize/events/<slug>/edit/` | Create and edit | Organizer of the Host |
| `/organize/events/<slug>/roster/` | Roster, CSV and printable export (FR-48) | Organizer of the Host |
| `/organize/events/<slug>/conflicts/` | Offline scan conflicts (FR-47) | Organizer of the Host |
| `/organize/approvals/` | Pending queue (FR-23) | Approver of the Host |
| `/scan/<slug>/` | Scanner PWA for one Event | Gate Staff or Organizer of the Host |
| `/account/` | Profile, affiliations, notification preferences, export, delete | Signed-in user |
| `/account/affiliations/new/` | Add a University affiliation (FR-12) | Signed-in user |
| `/accounts/...` | Sign-up, login, email confirmation, password reset, TOTP (`django-allauth`) | Anyone |
| `/admin/` | Platform administration | Platform Admin |
| `/healthz`, `/readyz` | Health (FR-60) | Anyone; no details beyond status |

## 3. JSON API

### 3.1 Events

`GET /api/v1/events/` — published, upcoming Events.
Query: `from`, `to` (dates), `host` (University or Hub `short_code`; repeatable), `delivery_mode`, `tag` (slug; repeatable), `eligible` (`true` to restrict to Events the caller can register for), `q` (search text).

Response item:
```json
{
  "public_id": "01928f6e-7c1a-7b3e-9a52-3c1f0e2d4b77",
  "slug": "applied-ai-public-health-colloquium",
  "title": "Applied AI and Public Health Colloquium",
  "category": "SEMINAR",
  "starts_at": "2026-11-05T12:00:00Z",
  "ends_at": "2026-11-05T15:00:00Z",
  "host": {"kind": "CAMPUS", "short_code": "UR-CST", "name": "College of Science and Technology", "university_short_code": "UR"},
  "venue": {"name": "Auditorium 1", "building": "Main Building"},
  "access_policy": "OPEN_ALL_UNIVERSITIES",
  "delivery_mode": "HYBRID",
  "status": "PUBLISHED",
  "seats": [
    {"kind": "HOST_MEMBERS", "capacity": 80, "available": 12},
    {"kind": "VISITING_MEMBERS", "capacity": 50, "available": 0},
    {"kind": "COMMUNITY_GUESTS", "capacity": 0, "available": 0}
  ],
  "eligibility": {"eligible": true, "seat_pool": "VISITING_MEMBERS", "reason": null},
  "tags": ["ai", "public-health"]
}
```
The values above are fictional. `eligibility` is present only for signed-in callers. `reason` is one of `SIGN_IN_REQUIRED`, `EMAIL_NOT_CONFIRMED`, `NOT_VERIFIED_MEMBER`, `NOT_HOST_UNIVERSITY`, `NOT_HOST_CAMPUS`, `NO_GUEST_SEATS`, `EVENT_STARTED`, `EVENT_CANCELLED`, or null.

`GET /api/v1/events/{slug}/` — the same object plus `abstract`, `speakers`, `organizer_label`, `gate_instructions`, `id_check_at_gate`, and `online_url` (only for callers with a `CONFIRMED` registration).

There is no event-creation endpoint in v1: Organizers use the web forms. A write API is added with the first non-browser client.

### 3.2 Registrations

`POST /api/v1/events/{slug}/registrations/` — register the caller. Body: `{"legal_name": "..."}`, required only when `id_check_at_gate` is true.
Responses: `201` with a Registration; `200` with the existing one if the caller already holds a non-cancelled registration (F-15); `403` with `reason` as in §3.1; `409` when the Event has started or is cancelled.

Registration object:
```json
{
  "public_id": "01928f70-1b2c-7d4e-8f90-a1b2c3d4e5f6",
  "event": "applied-ai-public-health-colloquium",
  "status": "CONFIRMED",
  "seat_pool": "VISITING_MEMBERS",
  "waitlist_position": null,
  "gate_pass": "01928f70-2c3d-7e4f-9a01-b2c3d4e5f6a7"
}
```
`gate_pass` is null while `issue_gate_pass` is pending, for `WAITLISTED` and for `ONLINE` Events.

`DELETE /api/v1/registrations/{public_id}/` — cancel own registration. `204`; `409` after Event start.

### 3.3 Passes

`GET /api/v1/me/passes/?when=upcoming|past` — the caller's Gate Passes.
```json
{
  "public_id": "01928f70-2c3d-7e4f-9a01-b2c3d4e5f6a7",
  "code": "KK-7Q2M-X4HD",
  "qr_payload": "KK1:...",
  "status": "VALID",
  "valid_from": "2026-11-05T10:00:00Z",
  "valid_until": "2026-11-05T15:00:00Z",
  "event": {"slug": "applied-ai-public-health-colloquium", "title": "Applied AI and Public Health Colloquium", "starts_at": "2026-11-05T12:00:00Z", "gate_instructions": "Main gate, show the pass and an ID"},
  "holder": {"display_name": "Example Attendee", "affiliation": "UR"}
}
```
`qr_payload` is shown in full in real responses; it is elided here. The QR image itself is rendered by the web route, not the API.

### 3.4 Public keys

`GET /api/v1/pass-keys/` — anyone. Returns signing keys whose status is `ACTIVE` or `RETIRED`:
```json
{"keys": [{"key_id": 1, "alg": "Ed25519", "public_key": "base64url", "status": "ACTIVE"}]}
```

### 3.5 Scanner

All scanner endpoints require the `GATE_STAFF` or `ORGANIZER` role on the Event's Host.

`GET /api/v1/scanner/events/{slug}/bundle/?roster=true|false`
```json
{
  "event": {"public_id": "...", "slug": "...", "version": 7, "starts_at": "...", "ends_at": "...", "gate_opens_minutes": 120},
  "server_time": "2026-11-05T09:58:12Z",
  "keys": [{"key_id": 1, "public_key": "base64url"}],
  "revoked_pass_ids": ["..."],
  "roster": [{"pass_id": "...", "code": "KK-7Q2M-X4HD", "name": "Example Attendee", "affiliation": "UR", "seat_pool": "VISITING_MEMBERS"}]
}
```
`roster` is present only when requested. Every roster download writes an audit entry (FR-61).

`POST /api/v1/scanner/events/{slug}/scans/` — one online scan.
Body: `{"client_scan_id": "uuid", "device_id": "string", "scanned_at": "...", "qr_payload": "KK1:..."}` or the same with `"code": "KK-7Q2M-X4HD"` instead of `qr_payload`.
Response `200`:
```json
{"result": "VALID", "first_used_at": null, "holder": {"name": "Example Attendee", "affiliation": "UR", "seat_pool": "VISITING_MEMBERS"}, "event_version": 7}
```
For `ALREADY_USED`, `first_used_at` is set. `holder` is omitted for `BAD_SIGNATURE`, `UNKNOWN_KEY` and `WRONG_EVENT`. A repeated `client_scan_id` returns the original response.

`POST /api/v1/scanner/events/{slug}/scans/batch/` — offline queue upload. Body: `{"device_id": "...", "scans": [ ...up to 500 scan objects with "mode": "OFFLINE" and "local_result" ]}`. Response: one result per `client_scan_id`, including `is_conflict`. Idempotent.

### 3.6 Notifications

`GET /api/v1/me/notifications/?unread=true` and `POST /api/v1/me/notifications/mark-read/` with `{"ids": [...]}` or `{"all": true}`.

### 3.7 Calendar and account data

- `GET /events/{slug}.ics` and `GET /calendar/{calendar_token}.ics` return `text/calendar`.
- `GET /api/v1/me/export/` returns the caller's data as JSON (FR-18); rate-limited to one per hour.

## 4. Rate limits (per deployment defaults)

| Action | Limit |
| :--- | :--- |
| Login attempts | 5 per 15 minutes per account and per IP address (allauth) |
| Affiliation code requests | 5 per hour per user |
| Registration POST | 10 per minute per user |
| Scanner scans | 120 per minute per device |
| Export | 1 per hour per user |
