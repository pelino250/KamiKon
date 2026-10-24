# 01: Product Requirements (v1.0)

Status: draft for v1.0. Risks (R-nn) and open questions (Q-nn) are in `07_ROADMAP.md`; review IDs (C-nn, D-nn) are in `history/2026-10-23-review.md`. Domain terms follow `GLOSSARY.md`.

## 1. Summary

KamiKon (*Kaminuza* + *Connect*) is an open-source, self-hostable platform on which universities and partner Hubs in Rwanda publish academic Events, decide who may attend through an Access Policy, and issue Gate Passes that campus security can check, with or without a network connection.

## 2. Problem

Academic events at one Rwandan university are hard to find for students and staff at another, and for alumni, industry and independent learners. When visitors do find them, campus gates often have no list of expected visitors, and organizers have no reliable way to limit seats by audience (host members, visiting members, the public). General platforms handle discovery and ticketing but do not know who belongs to which institution, and their data is not held in Rwanda.

## 3. Users

| Glossary term | Who | Main need in v1 |
| :--- | :--- | :--- |
| Verified Member | Student or staff member whose affiliation with a University is proven by mailbox control | Find Events open to them across universities and get a Gate Pass |
| Community Guest | Anyone without a verified affiliation: alumni, industry professionals, independent learners | Find and register for Events open to the public |
| Organizer | Person allowed to submit Events for a Host | Publish an Event with the right Access Policy and Seat Pools, see the roster, send urgent changes |
| Approver | Person allowed to approve Events for a Host | Review pending Events before they reach a wide audience |
| Gate Staff | Person allowed to scan Gate Passes for a Host's Events | Admit or refuse quickly at the gate, including without network |
| Platform Admin | Operator of a deployment | Register Universities, Campuses, Hubs and email domains; appoint Approvers |

## 4. Goals and non-goals

KamiKon is primarily a teaching project (see `README.md`). The goals below define production quality for the software; none of them depends on an institution adopting it.

### Goals for v1.0
- G-1. A person can find an Event they are eligible for and register in under two minutes on a mid-range phone on a mobile connection.
- G-2. An Organizer can publish an Event with an Access Policy, a Delivery Mode and Seat Pools without help.
- G-3. Gate Staff can verify a Gate Pass in under two seconds, online or offline.
- G-4. A deployer can install KamiKon on one server with PostgreSQL as the only stateful dependency, and can meet Rwanda's data-protection obligations using the documentation.
- G-5. A new contributor can run the project and its tests in under ten minutes.

### Non-goals for v1.0
Paid tickets and payments; native mobile apps (Flutter); a separate SPA; map view; Apple or Google Wallet export; push notifications; real-time WebSocket updates; Q&A, ratings, resource vault and followable organizations; SMS; certificates of participation; multi-session conference timetables (use Indico for those); federation between deployments.

## 5. Functional requirements

Priority: P0 must ship in v1.0; P1 should ship; P2 is v1.1 or later.

### 5.1 Institutions (`apps/institutions`)
| ID | Requirement | Priority | Acceptance criteria |
| :--- | :--- | :--- | :--- |
| FR-01 | Platform Admin manages Universities, Campuses, Venues and Hubs | P0 | CRUD in Django admin; a Campus belongs to exactly one University; a Venue belongs to a Campus or a Hub |
| FR-02 | Platform Admin registers email domains per University with a kind (`MEMBER`, `STAFF_ONLY`, `ALUMNI`) | P0 | Only `MEMBER` and `STAFF_ONLY` domains produce Affiliations; a domain belongs to one University; domain matching is exact on the part after `@`, case-insensitive |
| FR-03 | Platform Admin assigns Host roles (`ORGANIZER`, `APPROVER`, `GATE_STAFF`) to users per Campus or Hub | P0 | A user may hold several roles on several Hosts; every grant and revocation is audit-logged |
| FR-04 | Seed command creates synthetic institutions for development | P0 | `manage.py seed_demo` creates fictional Universities, Campuses, Hubs, users and Events; contains no real personal data and no unconfirmed real domains (Q-05) |

### 5.2 Accounts and affiliation (`apps/accounts`)
| ID | Requirement | Priority | Acceptance criteria |
| :--- | :--- | :--- | :--- |
| FR-10 | Sign up with email and password; email is the login identifier | P0 | Account inactive for registration until the email is confirmed by a single-use link; passwords checked by Django validators |
| FR-11 | Age confirmation | P0 | Sign-up requires confirming the user is 16 or older (review D-20); no date of birth stored |
| FR-12 | Add a university affiliation by proving control of an institutional mailbox | P0 | A code or link sent to the address; on success the Affiliation is `VERIFIED` with `expires_at` 12 months later (review D-06) |
| FR-13 | Choose a home Campus within the verified University | P0 | Self-declared; changeable at most once every 90 days; Campus Approvers can revoke the campus claim |
| FR-14 | Re-verification | P0 | Reminder email 30 days before expiry; on expiry the Affiliation becomes `EXPIRED` and the user is treated as a Community Guest |
| FR-15 | Community Guest profile: display name, optional organization and role label | P0 | Shown to Organizers on the roster only |
| FR-16 | Legal name for gated events | P0 | A Host may mark Events `id_check_at_gate`; registering for such an Event requires a name as on the attendee's ID, with the disclosure text in §7 |
| FR-17 | ID-photo review for universities without student email | P2 | Feature flag `KAMIKON_ID_REVIEW_ENABLED`, off by default (Q-09); image deleted when decided or after 30 days |
| FR-18 | Self-service data export and account deletion | P0 | JSON export of the user's data; deletion removes the account and anonymises registrations; both completed within the 30-day response period of Articles 18 to 20 |
| FR-19 | Optional two-factor authentication for Organizers, Approvers, Gate Staff and Platform Admins | P1 | TOTP through `django-allauth`; Platform Admins required to enable it |

### 5.3 Events (`apps/events`)
| ID | Requirement | Priority | Acceptance criteria |
| :--- | :--- | :--- | :--- |
| FR-20 | Organizer creates an Event for a Host they hold the `ORGANIZER` role on | P0 | Fields per `02_ARCHITECTURE.md` §4.3; Host is a Campus or a Hub; organizer label is free text |
| FR-21 | Access Policy and Delivery Mode are independent | P0 | Four Access Policies, three Delivery Modes (ADR-0001); Hub-hosted Events limited to `PUBLIC_COMMUNITY` and `OPEN_ALL_UNIVERSITIES` |
| FR-22 | Seat Pools | P0 | Capacity per pool `HOST_MEMBERS`, `VISITING_MEMBERS`, `COMMUNITY_GUESTS`; pools not allowed by the Access Policy must be zero; `PUBLIC_COMMUNITY` Events must have `COMMUNITY_GUESTS` above zero; online-only Events may have unlimited capacity |
| FR-23 | Approval | P0 | `PUBLIC_COMMUNITY` and `OPEN_ALL_UNIVERSITIES` Events go to `PENDING_APPROVAL`; an Approver of the same Host approves or rejects with a reason; Events by an Approver of that Host publish immediately and are audit-logged |
| FR-24 | Edit after publication | P0 | Changes to start time, end time, venue or online link are marked urgent and notify registered attendees (FR-51); changing the Access Policy or increasing `VISITING_MEMBERS` or `COMMUNITY_GUESTS` on an approved Event returns it to `PENDING_APPROVAL` |
| FR-25 | Cancel | P0 | Status `CANCELLED` with a reason; all Gate Passes revoked; attendees notified |
| FR-26 | Tags | P1 | Up to five tags from a deployment-managed list |
| FR-27 | Online link visibility | P0 | The online link is shown only to registered attendees |

### 5.4 Discovery (`apps/discovery`)
| ID | Requirement | Priority | Acceptance criteria |
| :--- | :--- | :--- | :--- |
| FR-30 | Date-grouped list of upcoming published Events | P0 | Default filter "Events I can attend" on; one tap shows all; ineligible Events state why in words |
| FR-31 | Filters: date range, University or Hub, Delivery Mode, tag | P0 | Combinable; reflected in the URL |
| FR-32 | Full-text search over title, abstract, speakers, Host name | P1 | PostgreSQL full-text search |
| FR-33 | Calendar export | P0 | Per-Event `.ics`; personal feed of registered Events at a secret URL that the user can reset |
| FR-34 | Map view | P2 | Online only, configurable tile provider (review C-16) |

### 5.5 Registration and Gate Pass (`apps/tickets`)
| ID | Requirement | Priority | Acceptance criteria |
| :--- | :--- | :--- | :--- |
| FR-40 | Register for an Event the user is eligible for | P0 | Seat Pool chosen by the rules in `02_ARCHITECTURE.md` §5; seat allocation is race-free under concurrent requests (test with parallel requests on PostgreSQL) |
| FR-41 | Waitlist per Seat Pool | P0 | First in, first out; a cancellation in a pool promotes the next person in that pool; promotion stops at Event start; promoted users are emailed |
| FR-42 | Cancel own registration | P0 | Until Event start; frees the seat; revokes the pass |
| FR-43 | Gate Pass issued on confirmation for in-person and hybrid Events | P0 | Ed25519-signed payload (ADR-0002) rendered as a QR code; human-readable pass code for manual entry |
| FR-44 | Pass works offline | P0 | The pass page is stored by the PWA after first view; opening it offline shows the QR code, Event title, time, gate instructions and "Available offline" |
| FR-45 | Scanner | P0 | Gate Staff open the scanner for an Event; online scans check in on the server; offline scans verify the signature locally and queue; manual pass-code entry works online, and offline when the roster was downloaded |
| FR-46 | Scan results in words | P0 | `VALID`, `ALREADY_USED`, `WRONG_EVENT`, `NOT_YET_VALID`, `EXPIRED`, `REVOKED`, `BAD_SIGNATURE`, `UNKNOWN_KEY`; distinct sound and vibration for valid and invalid |
| FR-47 | Offline reconciliation | P0 | Queued scans upload on reconnect; duplicates across devices appear in the Organizer's conflict list |
| FR-48 | Gate roster export | P0 | CSV and printable HTML grouped by Seat Pool; contains name, affiliation (University or "Community Guest") and pass code; nothing else |

### 5.6 Notifications (`apps/notifications`)
| ID | Requirement | Priority | Acceptance criteria |
| :--- | :--- | :--- | :--- |
| FR-50 | Transactional email: confirmation, waitlist, promotion, cancellation, re-verification reminder | P0 | Sent through the task queue; never blocks the request; retried on failure |
| FR-51 | Urgent change email to attendees of an Event | P0 | Subject begins with the change type and the Event name |
| FR-52 | Event reminder 24 hours before start | P1 | One per registration; user can opt out |
| FR-53 | Weekly digest of new Events matching followed tags and Hosts | P1 | Opt-in; unsubscribe link in every digest |
| FR-54 | In-app notification list | P1 | Same events as email; unread count in the header; no real-time push |

### 5.7 Operations
| ID | Requirement | Priority | Acceptance criteria |
| :--- | :--- | :--- | :--- |
| FR-60 | Health endpoints | P0 | `/healthz` (process alive) and `/readyz` (database reachable, migrations applied) |
| FR-61 | Audit log | P0 | Role grants, approvals, self-approvals, cancellations, roster exports, key rotations, data exports and deletions |
| FR-62 | Retention job | P0 | Default: names and affiliations on registrations and check-ins anonymised 90 days after Event end; configurable per deployment |
| FR-63 | Metrics endpoint | P2 | Prometheus format, restricted to the internal network |

## 6. Non-functional requirements

| ID | Requirement |
| :--- | :--- |
| NFR-01 | Performance: on the reference deployment (2 vCPU, 4 GB RAM, PostgreSQL on the same host, 10,000 published Events, 50,000 users), the discovery list responds in under 200 ms at p95 at 50 requests per second; registration in under 500 ms at p95 with 500 concurrent attempts for one Event, with no overselling |
| NFR-02 | Page weight: discovery list under 150 KB transferred on first load excluding fonts; no images in the list |
| NFR-03 | Accessibility: WCAG 2.2 AA. Floor for every screen: text contrast at least 4.5:1 and control borders at least 3:1; no white text on the gold accent (1.82:1); touch targets at least 44×44 px; a visible 2 px focus ring with offset; layouts hold at 150% text scale; body text never below 12 px; an Event card reads as one sentence to a screen reader; the Gate Pass exposes its code as text |
| NFR-04 | Security: OWASP ASVS 5.0 Level 2 as the target for v1.0, assessed per chapter in `04_THREAT_MODEL.md` |
| NFR-05 | Privacy: data minimisation as in `05_DATA_PROTECTION.md`; no third-party scripts, fonts or telemetry loaded by default |
| NFR-06 | Availability: deployment documentation for single-server operation with nightly encrypted backups and a tested restore |
| NFR-07 | Internationalisation: all user-facing strings translatable; English complete; Kinyarwanda for attendee flows after review (review C-17) |
| NFR-08 | Browser support: the two latest versions of Chrome, Firefox, Safari and Samsung Internet; the scanner requires camera access over HTTPS |

## 7. Required disclosures (exact text owned by the deployer)

The product must show, at the point of collection:
- At sign-up: what data is collected, why, who sees it, retention, and the user's rights, linking to the deployer's privacy notice.
- When adding an affiliation: that the University name and home Campus will be shown to Organizers and Gate Staff of Events the user registers for.
- When registering for an Event with `id_check_at_gate`: "Campus security checks ID at this gate. Your name as entered here will be on the gate list for this Event and visible to the Organizer and Gate Staff. KamiKon does not ask for or store your ID number."

## 8. Success metrics

If an institution pilots KamiKon, measure: time from opening the list to completed registration; share of started registrations completed; share of Gate Pass scans that return a result in under two seconds; share of attendees scanned rather than checked manually; number of Events published per Host per month. Targets are agreed with the pilot institution (Q-02). Without a pilot, v1.0 is judged by the goals in §4 and the release criteria.

## 9. Release criteria for v1.0

See `07_ROADMAP.md` §3.
