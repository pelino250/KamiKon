# 04 — Threat Model (STRIDE)

Status: draft for v1.0. Review at every minor release and whenever a trust boundary changes. Architecture references are to `02_ARCHITECTURE.md`.

## 1. Assets

| Asset | Why it matters |
| :--- | :--- |
| A-1 Pass signing private key | Whoever holds it can mint valid Gate Passes for every Event in the deployment |
| A-2 Personal data: email, display and legal names, affiliations, registrations, check-ins | Obligations under Rwanda Law No. 058/2021; harm to attendees if exposed |
| A-3 Gate roster downloaded to scanner devices | Personal data outside the server, on staff phones |
| A-4 Host roles (Organizer, Approver, Gate Staff, Platform Admin) | Control over what is published, who is admitted and who sees rosters |
| A-5 Seat availability | Fairness of allocation for popular Events |
| A-6 Release artifacts (container images, source releases) | Supply chain for every self-hoster |
| A-7 Django `SECRET_KEY`, database credentials, SMTP credentials | Session forgery, database access, sender reputation |

## 2. Trust boundaries

1. Internet to reverse proxy (TLS).
2. Proxy to Django web process.
3. Web and worker processes to PostgreSQL.
4. Worker to SMTP relay (often a third party; see `05_DATA_PROTECTION.md` §4).
5. Server to scanner device (bundle download, scan upload); the device is outside the operator's control.
6. GitHub Actions to the container registry (release pipeline).

## 3. Threats and controls

Status: **Designed** means specified in this documentation; **Present** means it exists in the repository today.

### 3.1 Spoofing

| ID | Threat | Control | Status |
| :--- | :--- | :--- | :--- |
| S-1 | Forged Gate Pass | Ed25519 signature, private key only on the server (ADR-0002) | Designed |
| S-2 | User claims an institutional address they do not own | Mailbox proof, code expiry, attempt limits (ADR-0003, F-17) | Designed |
| S-3 | Graduate keeps member eligibility | 12-month expiry and re-verification; `ALUMNI` domain kind | Designed |
| S-4 | Credential stuffing on Organizer or Admin accounts | allauth rate limits; TOTP required for Platform Admins, offered to Host roles (FR-19); Django password validators | Designed |
| S-5 | Session hijacking | Secure, HttpOnly, SameSite=Lax cookies; HSTS; `SECURE_SSL_REDIRECT` | Present in `settings.py` for production |
| S-6 | Attendee shows a screenshot of someone else's pass | Single-use check-in; roster name checked against physical ID at `id_check_at_gate` Events | Designed; residual risk at offline gates (T-3) |
| S-7 | Phishing emails that imitate a deployment | SPF, DKIM and DMARC guidance in the deployment guide; emails never ask for passwords | Designed |

### 3.2 Tampering

| ID | Threat | Control | Status |
| :--- | :--- | :--- | :--- |
| T-1 | Altered pass payload (Event, time window, Seat Pool) | Signature covers every field with a domain-separation prefix | Designed |
| T-2 | Organizer changes an Event after approval to widen its audience | Changing `access_policy`, or increasing `VISITING_MEMBERS` or `COMMUNITY_GUESTS` capacity, on an approved Event returns it to `PENDING_APPROVAL` (FR-24) | Designed |
| T-3 | Duplicate admission at two offline gates | Accepted risk; detected at reconciliation (ADR-0002) | Designed (accepted) |
| T-4 | Overselling seats through concurrent requests | Row lock and check constraint (§5.2) | Designed |
| T-5 | CSRF on registration, scan, admin actions | Django CSRF middleware; DRF session auth enforces CSRF | Present (middleware) |
| T-6 | Malicious dependency or compromised GitHub Action | Lock file with hashes; actions pinned by commit SHA; Dependabot; `pip-audit`; artifact attestations (`06_CI_CD_AND_RELEASES.md`) | Partly present (SHA pins, Dependabot, pip-audit) |
| T-7 | Workflow injection through PR titles or branch names | `pr-title.yml` uses `pull_request_target` without checking out PR code and with read-only permissions; workflows never interpolate untrusted input into `run:` steps; actionlint in CI | Present; keep this rule |

### 3.3 Repudiation

| ID | Threat | Control | Status |
| :--- | :--- | :--- | :--- |
| R-1 | Approver denies approving an Event, Organizer denies exporting a roster | Append-only audit log (FR-61) | Designed |
| R-2 | Gate Staff dispute a scan result | `CheckIn` rows with device, user and time | Designed |

### 3.4 Information disclosure

| ID | Threat | Control | Status |
| :--- | :--- | :--- | :--- |
| I-1 | Personal data in the QR code | Payload carries no personal data (§6.1) | Designed |
| I-2 | Lost scanner phone with a roster | Roster optional, minimal fields, deleted 24 hours after the Event or on sign-out; PWA sign-out clears IndexedDB | Designed |
| I-3 | Enumeration of users or registrations through sequential identifiers | UUIDs in URLs (ADR-0011); object-level permission checks on every view | Designed |
| I-4 | Online link of a restricted Event leaks | Shown only to confirmed attendees; residual risk accepted, since attendees can share it | Designed |
| I-5 | Personal calendar feed URL leaks | Random token, resettable; feed contains Event data only | Designed |
| I-6 | Error pages or logs expose data | `DEBUG=False` enforced in production; logs record public IDs, not names or emails; no third-party error tracker by default | Partly present |
| I-7 | Roster exported to CSV and emailed around | Export audit-logged; CSV limited to name, affiliation and code; retention reminder in the file header | Designed |
| I-8 | Secrets committed to the repository | detect-secrets in pre-commit and CI; `.env` ignored | Present |
| I-9 | Developer workstation secrets in IDE files | Keep IDE folders ignored; load keys from the environment | IDE folders ignored by git |
| I-10 | Data transferred abroad through SMTP relays, CDNs or telemetry | No CDN or telemetry by default; deployment guide (`05_DATA_PROTECTION.md`) | Designed |

### 3.5 Denial of service

| ID | Threat | Control | Status |
| :--- | :--- | :--- | :--- |
| D-1 | Registration flood for a popular Event | Per-user rate limits; row locks bounded by a lock timeout; email confirmation required before registration | Designed |
| D-2 | Fake accounts to hold seats | Email confirmation; one registration per user per Event; Organizers can cancel registrations | Designed |
| D-3 | Expensive search queries | Query length limit; indexed full-text search; pagination maximum | Designed |
| D-4 | Email relay quota exhausted by fan-out | Batching and retry with backoff; digest opt-in | Designed |
| D-5 | Scanner upload abuse | Role required; batch size 500; per-device rate limit | Designed |

### 3.6 Elevation of privilege

| ID | Threat | Control | Status |
| :--- | :--- | :--- | :--- |
| E-1 | Organizer of one Host acts on another Host's Events | Every Event view and service checks `HostRole` for the Event's Host; tests for each role and Host combination | Designed |
| E-2 | Self-approval to bypass review | Allowed only for Approvers of the same Host, always audit-logged and shown to other Approvers (review X-11) | Designed |
| E-3 | Django admin exposed to the internet | Admin restricted to `is_staff` with TOTP; deployment guide recommends restricting `/admin/` by network | Designed |
| E-4 | Container breakout or host compromise | Non-root image; read-only filesystem where possible; minimal base image scanned in CI | Designed |

## 4. Safe defaults for self-hosters

The application must refuse to start in production when any of these is not met. Several are already enforced in `kamikon/settings.py`.

| Default | Enforced today |
| :--- | :--- |
| `DEBUG` false unless explicitly set | Yes |
| `SECRET_KEY` of at least 50 characters, not the development prefix | Yes |
| `ALLOWED_HOSTS` set | Yes |
| HTTPS redirect, secure cookies, HSTS one year | Yes |
| Database TLS (`sslmode=require`) unless the host is local | Partly (always required today; local socket exception to add in M0-3) |
| Pass signing key file present, mode 0600, matching the active key | No, added in M3 |
| No third-party telemetry, scripts or fonts | No code yet; checked in review |
| Sign-up open, ID review off, roster download on, retention 90 days | Added with the features |

## 5. ASVS 5.0 coverage plan

Target is Level 2 for v1.0 (NFR-04). Before the v1.0 release, the maintainer records a pass, fail or not-applicable result for each requirement in the ASVS chapters on encoding and sanitisation, validation and business logic, authentication, session management, authorisation, self-contained tokens (Gate Pass), cryptography, secure communication, configuration, data protection, and secure coding and architecture. Results are stored in `docs/security/asvs-v1.0.md`, created during M5.

## 6. Out of scope

Physical security at the gate beyond what the pass and roster provide; compromise of the attendee's own phone; denial of service at network level (the deployer's hosting provider); attacks on PostgreSQL, the operating system or the reverse proxy beyond configuration guidance.
