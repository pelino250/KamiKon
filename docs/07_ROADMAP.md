# 07 — Roadmap to v1.0

Status: replaces the sprint plan in `design_docs/agile_devops_roadmap.md` and `design_docs/PROJECT_README.md` for engineering purposes. Course cohorts map these milestones onto sprints using `docs/teaching/SPRINT_PLAYBOOK.md`. Dates are not set; each milestone ends when its exit criteria pass.

## 1. Milestones

### M0 — Foundations
| ID | Item | Exit criterion |
| :--- | :--- | :--- |
| M0-1 | Repository hygiene files (this change): LICENSE, CODE_OF_CONDUCT, SECURITY, CHANGELOG, GOVERNANCE, docs | Merged |
| M0-2 | Docker Compose for development: `web`, `worker`, `db` (PostgreSQL 17), `mailpit`; `make up` or `docker compose up` is the one command | A newcomer reaches the admin login and a green `scripts/ci.py test` in under 10 minutes on a clean machine (G-5) |
| M0-3 | Settings: `DATABASE_URL` and `EMAIL_URL`, decoupled from `DEBUG`; local-socket exception to `sslmode=require` | Existing settings tests extended and passing |
| M0-4 | Replace the custom `User` with the email-login model in §4.2 of the architecture, with `public_id`; regenerate `0001_initial` (no data exists) | Migration check passes; allauth sign-up works |
| M0-5 | `deploy-check` stage | In CI |
| M0-6 | Move repository to a GitHub organisation with two owners | R-03 mitigated |

### M1 — Institutions and identity
| ID | Item | Exit criterion |
| :--- | :--- | :--- |
| M1-1 | `apps.institutions` models and admin (FR-01 to FR-03) | Tests per constraint |
| M1-2 | `seed_demo` with synthetic data only (FR-04) | Runs in CI; reviewed for real names and domains |
| M1-3 | Affiliation by mailbox proof, campus selection, expiry and reminder (FR-12 to FR-14) | End-to-end test; attempt limits enforced |
| M1-4 | Data export and deletion (FR-18) | Test that deletion anonymises registrations |
| M1-5 | `apps.audit` (FR-61) | Role grants recorded |
| M1-6 | Tasks backend: `django-tasks-db` with an integration test of enqueue and worker (R-07) | Test green on Django 6.1 |
| M1-7 | CI: `imports`, `licenses`, `codeql`, `scorecard` | In CI |
| M1-8 | Remove the empty `apps.community` | Merged |

### M2 — Events and discovery
| ID | Item | Exit criterion |
| :--- | :--- | :--- |
| M2-1 | Event, SeatPool, Tag models with all constraints in §4.3 | Constraint tests |
| M2-2 | Create, edit, submit, approve, reject, cancel (FR-20 to FR-27) | Role-by-Host permission tests (E-1) |
| M2-3 | Discovery list, filters, eligibility reasons (FR-30, FR-31) | NFR-02 page weight checked |
| M2-4 | Calendar files and personal feed (FR-33) | Validated with an iCalendar parser in tests |
| M2-5 | Design tokens implemented as CSS custom properties from `design/tokens.json` | No colour literals outside token files; NFR-03 floor met |
| M2-6 | Container image, Trivy, SBOM (`container` stage) | In CI |

### M3 — Registration, Gate Pass and scanner
| ID | Item | Exit criterion |
| :--- | :--- | :--- |
| M3-1 | Registration, waitlist, cancellation, promotion (FR-40 to FR-42) | Concurrency test: 500 parallel attempts, zero oversell |
| M3-2 | Signing keys, `passkey` commands, payload format v1 (FR-43, ADR-0002) | Test vectors committed in `tests/vectors/pass_v1.json` |
| M3-3 | Pass page, service worker, email PNG (FR-44) | Works offline in Playwright with network disabled |
| M3-4 | Scanner PWA with bundle, online and offline scans, batch upload, conflicts (FR-45 to FR-47) | Playwright test of the offline path |
| M3-5 | Roster export (FR-48) | Audit entry per export |
| M3-6 | ADR for browser Ed25519 and QR decoding libraries (architecture §6.6) | Merged before M3-4 |
| M3-7 | Pilot partner confirmed (R-01, R-02, Q-02) | Named partner; otherwise follow the fallback in `00_DECISIONS_AND_AUDIT.md` §6 |

### M4 — Notifications
FR-50 to FR-54, SPF, DKIM and DMARC guidance, digest scheduling.

### M5 — Hardening and release
| ID | Item | Exit criterion |
| :--- | :--- | :--- |
| M5-1 | Load test on the reference deployment (NFR-01) | Results published in `docs/performance/` |
| M5-2 | ASVS 5.0 Level 2 self-assessment (`04_THREAT_MODEL.md` §5) | Every listed chapter assessed |
| M5-3 | Deployment guide, backup and restore drill | Restore tested from a nightly backup |
| M5-4 | Kinyarwanda attendee strings reviewed (Q-06) | Reviewer sign-off |
| M5-5 | Release pipeline with attestations (`06_CI_CD_AND_RELEASES.md` §4) | `gh attestation verify` succeeds on a release candidate |
| M5-6 | Upgrade to Django 6.2 LTS if released (R-09) | CI green |
| M5-7 | Trademark searches (Q-10) | Recorded |

## 2. Post-v1 tracks

Each starts only after v1.0 and with its own ADR: map view (v1.1); a native client (Flutter), together with token authentication and push channels; an SPA consuming `/api/v1/` with a write API; Apple and Google Wallet export per deployment; followable organizations and post-event resources; multi-session programmes. Issues for these carry the label `post-v1` and no milestone.

## 3. Definition of done for v1.0

1. Every P0 requirement in `01_PRD.md` is implemented with tests.
2. Every required check in `06_CI_CD_AND_RELEASES.md` §2 passes on the release commit.
3. NFR-01 to NFR-08 are measured and the results published.
4. The ASVS self-assessment has no open failure rated high.
5. The README quick start works on a clean machine in under 10 minutes.
6. The deployment guide and `05_DATA_PROTECTION.md` have been read by at least one pilot deployer, and their questions have been answered in the documents.
7. Two maintainers with publishing rights exist (R-03).
8. The release is signed and attested, and the changelog is complete.

## 4. Good first issues

Each of these is small, documented, and touches a single module. Label them `good first issue`.

- Add `deploy-check` as a stage in `scripts/ci.py` with a test in `tests/test_ci_script.py`.
- Add the local-socket exception to the database TLS rule, with a settings test.
- Add a `make` or `just` file with `up`, `test` and `ci` targets that wrap `docker compose` and `scripts/ci.py`.
- Write the `seed_demo` synthetic name generator (no real names; fictional organisations).
- Add the problem-details error handler for DRF (`03_API_SPEC.md` §1).
- Add translations scaffolding: the `rw` entry in `LANGUAGES` with `LANG_INFO`, and `makemessages` in CI.

## 5. Module ownership for contributors

| Area | Paths | Entry point for newcomers |
| :--- | :--- | :--- |
| Institutions and identity | `apps/institutions`, `apps/accounts` | Admin and model constraint tests |
| Events and discovery | `apps/events`, `apps/discovery` | Filters and templates |
| Passes and scanning | `apps/tickets`, `static/pwa/` | Pass format test vectors |
| Notifications | `apps/notifications`, `templates/email/` | Email templates |
| DevOps | `.github/`, `scripts/`, `docker/`, `compose*.yaml` | CI stages |

## 6. Bus factor and maintenance

- Maintainers: one today (`GOVERNANCE.md`). The minimum for v1.0 is two (R-03).
- Weekly maintenance load to plan for: Dependabot merges, triage of new issues within 7 days, security reports acknowledged within 3 working days (`SECURITY.md`).
- If maintenance stops, the README states the project's status; the archive procedure is in `GOVERNANCE.md`.

## 7. Changes to the existing backlog

The 29 open GitHub issues were created from `scripts/sprint_backlog.json`. Apply these changes on GitHub; the JSON has been corrected where it was inconsistent.

| Issue ID | Change | Reason |
| :--- | :--- | :--- |
| US-0.1 | Close as done or keep for design_v3 screens only | Stitch prompts v3 exist |
| US-0.2 | Close as superseded | C-25 |
| DO-0.3 | Retitle to M0-2; services `web`, `worker`, `db`, `mailpit`; no Redis or Celery | ADR-0007 |
| DO-0.4 | Close as done | CI exists |
| US-1.1 | Split into M1-1 and M1-2 | Scope and synthetic seed |
| US-1.2 | Rewrite to M1-3 | C-04 |
| US-1.3 | Close; replaced by session auth and the `/api/v1/` scope in `03_API_SPEC.md` | ADR-0005 |
| DO-1.4 | Close as done for Bandit, pip-audit and detect-secrets; CodeQL moves to M1-7 | C-28 |
| US-2.1 | Title corrected to Access Policy and Delivery Mode (JSON updated) | C-12 |
| US-2.2 | Remove the design v1 colour values; reference design_v3 tokens | design_v3 replaces v1 |
| US-2.3 | Move to post-v1 (map, v1.1) | C-16 |
| DO-2.4 | Keep as M2-6 | |
| US-3.1 to US-3.3 | Rewrite to M3-1 to M3-5; remove "Student ID number" and HMAC from criteria | C-01, C-06 |
| DO-3.4 | Rewrite: staging on synthetic data only | C-15 |
| US-4.1, US-4.2 | Keep within M4; email and in-app only | C-14 |
| DO-4.3 | Reduce to health endpoints and structured logs in v1; Prometheus and Grafana post-v1 | Scope |
| US-5.1 | Replace with database query optimisation and per-view caching only if NFR-01 fails | No Redis in v1 |
| DO-5.2, DO-5.3 | Keep as M5-1 and M5-3 | |
| US-6.x, DO-6.4, US-7.x, DO-7.3 | Label `post-v1`, remove milestones | D-03 |
| US-7.2 | Component name corrected to `<AccessPolicyPill />` (JSON updated) | C-12 |
