# 07: Roadmap to v1.0

Status: replaces the sprint plan in `design_docs/agile_devops_roadmap.md` and `design_docs/PROJECT_README.md` for engineering purposes. Course cohorts map these milestones onto sprints using `docs/teaching/SPRINT_PLAYBOOK.md`; the Advanced DevOps course follows `docs/teaching/COURSE_ALIGNMENT.md` instead. Dates are not set; each milestone ends when its exit criteria pass.

## 1. Milestones

### M0: Foundations
| ID | Item | Exit criterion |
| :--- | :--- | :--- |
| M0-1 | Repository hygiene files (this change): LICENSE, CODE_OF_CONDUCT, SECURITY, CHANGELOG, GOVERNANCE, docs | Merged |
| M0-2 | Docker Compose for development: `web`, `worker`, `db` (PostgreSQL 17), `mailpit`; `make up` or `docker compose up` is the one command | A newcomer reaches the admin login and a green `uv run pytest` in under 10 minutes on a clean machine (G-5) |
| M0-3 | Settings: `DATABASE_URL` and `EMAIL_URL`, decoupled from `DEBUG`; local-socket exception to `sslmode=require` | Existing settings tests extended and passing |
| M0-4 | Replace the custom `User` with the email-login model in §4.2 of the architecture, with `public_id`; regenerate `0001_initial` (no data exists) | Migration check passes; allauth sign-up works |
| M0-5 | Deploy check (`manage.py check --deploy`) in the `checks` job | In CI |
| M0-6 | Move repository to a GitHub organisation with two owners | R-03 mitigated |

### M1: Institutions and identity
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

### M2: Events and discovery
| ID | Item | Exit criterion |
| :--- | :--- | :--- |
| M2-1 | Event, SeatPool, Tag models with all constraints in §4.3 | Constraint tests |
| M2-2 | Create, edit, submit, approve, reject, cancel (FR-20 to FR-27) | Role-by-Host permission tests (E-1) |
| M2-3 | Discovery list, filters, eligibility reasons (FR-30, FR-31) | NFR-02 page weight checked |
| M2-4 | Calendar files and personal feed (FR-33) | Validated with an iCalendar parser in tests |
| M2-5 | Design tokens implemented as CSS custom properties from `design/tokens.json` | No colour literals outside token files; NFR-03 floor met |
| M2-6 | Container image, Trivy, SBOM (`container` stage) | In CI |

### M3: Registration, Gate Pass and scanner
| ID | Item | Exit criterion |
| :--- | :--- | :--- |
| M3-1 | Registration, waitlist, cancellation, promotion (FR-40 to FR-42) | Concurrency test: 500 parallel attempts, zero oversell |
| M3-2 | Signing keys, `passkey` commands, payload format v1 (FR-43, ADR-0002) | Test vectors committed in `tests/vectors/pass_v1.json` |
| M3-3 | Pass page, service worker, email PNG (FR-44) | Works offline in Playwright with network disabled |
| M3-4 | Scanner PWA with bundle, online and offline scans, batch upload, conflicts (FR-45 to FR-47) | Playwright test of the offline path |
| M3-5 | Roster export (FR-48) | Audit entry per export |
| M3-6 | ADR for browser Ed25519 and QR decoding libraries (architecture §6.6) | Merged before M3-4 |
| M3-7 | Pilot partner, if an institution is interested (R-01, R-02, Q-02) | Optional; v1.0 does not wait for one |

### M4: Notifications
FR-50 to FR-54, SPF, DKIM and DMARC guidance, digest scheduling.

### M5: Hardening and release
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
6. A test deployment on synthetic data has followed the deployment guide and `05_DATA_PROTECTION.md` from start to finish; if a pilot deployer exists, their questions have been answered in the documents.
7. Two maintainers with publishing rights exist (R-03).
8. The release is signed and attested, and the changelog is complete.

## 4. Good first issues

Each of these is small, documented, and touches a single module. Label them `good first issue`.

- Add `manage.py check --deploy` with production settings as a step in the `checks` job of `.github/workflows/ci.yml`.
- Add the local-socket exception to the database TLS rule, with a settings test.
- Add a `make` or `just` file with `up`, `test` and `ci` targets that wrap `docker compose`, `pre-commit` and `pytest`.
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
| DevOps | `.github/`, `scripts/`, `docker/`, `compose*.yaml`, `k8s/`, `terraform/`, `ansible/` | CI workflow |

## 6. Bus factor and maintenance

- Maintainers: one today (`GOVERNANCE.md`). The minimum for v1.0 is two (R-03).
- Weekly maintenance load to plan for: Dependabot merges, triage of new issues within 7 days, security reports acknowledged within 3 working days (`SECURITY.md`).
- If maintenance stops, the README states the project's status; the archive procedure is in `GOVERNANCE.md`.

## 7. Changes to the existing backlog

The 29 open GitHub issues were created from `scripts/sprint_backlog.json`. Apply these changes on GitHub; the JSON has been corrected where it was inconsistent.

| Issue ID | Change | Reason |
| :--- | :--- | :--- |
| US-0.1 | Close as done or keep for design_v3 screens only | Stitch prompts v3 exist |
| US-0.2 | Close as superseded | review C-25 |
| DO-0.3 | Retitle to M0-2; services `web`, `worker`, `db`, `mailpit`; no Redis or Celery | ADR-0007 |
| DO-0.4 | Close as done | CI exists |
| US-1.1 | Split into M1-1 and M1-2 | Scope and synthetic seed |
| US-1.2 | Rewrite to M1-3 | review C-04 |
| US-1.3 | Close; replaced by session auth and the `/api/v1/` scope in `03_API_SPEC.md` | ADR-0005 |
| DO-1.4 | Close as done for Bandit, pip-audit and detect-secrets; CodeQL moves to M1-7 | review C-28 |
| US-2.1 | Title corrected to Access Policy and Delivery Mode (JSON updated) | review C-12 |
| US-2.2 | Remove the design v1 colour values; reference design_v3 tokens | design_v3 replaces v1 |
| US-2.3 | Move to post-v1 (map, v1.1) | review C-16 |
| DO-2.4 | Keep as M2-6 | |
| US-3.1 to US-3.3 | Rewrite to M3-1 to M3-5; remove "Student ID number" and HMAC from criteria | review C-01, review C-06 |
| DO-3.4 | Rewrite: staging on synthetic data only | review C-15 |
| US-4.1, US-4.2 | Keep within M4; email and in-app only | review C-14 |
| DO-4.3 | Reduce to health endpoints and structured logs in v1; Prometheus and Grafana on staging only (ADR-0012) | Scope |
| US-5.1 | Replace with database query optimisation and per-view caching only if NFR-01 fails | No Redis in v1 |
| DO-5.2, DO-5.3 | Keep as M5-1 and M5-3 | |
| US-6.x, DO-6.4, US-7.x, DO-7.3 | Label `post-v1`, remove milestones | review D-03 |
| US-7.2 | Component name corrected to `<AccessPolicyPill />` (JSON updated) | review C-12 |

## 8. Risks

Likelihood and impact are rated Low, Medium or High. A gate is the point in the roadmap where the mitigation must be in place before work continues.

| ID | Risk | Likelihood | Impact | Mitigation | Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| R-01 | No institution adopts it | High | Low for the teaching goal; High for real use | Keep it a complete teaching codebase; when an institution shows interest, define a pilot and success metrics with it (Q-02) | When an institution shows interest |
| R-02 | Campus security does not accept KamiKon passes, so the gate pass has no value | Medium | High | Pilot with a named security office; the roster export works even without scanning | Before any deployment with real users |
| R-03 | Bus factor of one: the maintainer becomes unavailable | High | High | Move the repository to a GitHub organisation with a second owner; document release and key procedures; appoint a second maintainer before v1.0 | Before v1.0 |
| R-04 | Signing key leaked or lost | Low | High | Key only on the server, loaded from a secret file; key ID in every pass; rotation and revocation runbook; tests that scanners reject unknown key IDs | Before M3 ends |
| R-05 | Duplicate entry through offline scanning | Medium | Medium | Online-first scanning; post-sync conflict report; single-device mode documented for strict gates | Before M3 ends |
| R-06 | Deployer stores data abroad or sends it to foreign SaaS without authorisation (Art. 48, 50) | High | High (for the deployer) | Telemetry off by default; `docs/05_DATA_PROTECTION.md` checklist; deployment guide states the obligation in the first section | Before v1.0 |
| R-07 | `django-tasks-db` (beta, PyPI classifiers list Django 5.2 and 6.0 only) breaks on Django 6.1 or 6.2 | Medium | Medium | Integration test of enqueue plus worker in CI; application code only uses `django.tasks`; fallback backend is Celery with Valkey | M1 (first task) and every Django minor upgrade |
| R-08 | Other dependencies lag Django releases (`drf-spectacular`, `whitenoise`, `django-cors-headers`, `django-prometheus` classifiers stop at 6.0) | Medium | Low | Test suite runs against the locked versions; Dependabot; avoid optional dependencies in v1 | Every Django upgrade |
| R-09 | Django 6.1 extended support ends December 2027 | Certain | Medium | Move to Django 6.2 LTS (due April 2027, extended support to April 2030) before or at v1.0 | v1.0 |
| R-10 | Name conflict: "Kami-Con" is an anime convention running since 2009 in Alabama; "Kami" is used by other products | Low | Medium | Search the Rwanda Development Board and USPTO registers before the v1.0 announcement; keep the domain and organisation names consistent | Before v1.0 announcement |
| R-11 | Email domain list is wrong or incomplete (shared domains, alumni domains) | High | Medium | Domains are seeded only after confirmation by the institution; Platform Admin can mark a domain as staff-only or alumni | M1 |
| R-12 | Scope creep back to four frontends, maps, wallet and community features | High | High | Roadmap lists them as post-v1; issues for them are labelled `post-v1` and closed from milestones. Teaching infrastructure under ADR-0012 adds no runtime service to the product | Every milestone review |
| R-13 | Personal data enters the repository through fixtures, screenshots or issue reports | Medium | High | Seed data is synthetic and generated; issue templates warn; detect-secrets and review | Continuous |
| R-14 | Kinyarwanda translation quality on gate messages | Medium | Medium | Fluent reviewer signs off on attendee strings; gate strings tested first | Before v1.0 |
| R-15 | Mass email from a deployment marked as spam, so urgent changes are missed | Medium | Medium | Document SPF, DKIM and DMARC setup; in-app notification list as a second channel | M4 |
| R-16 | Course cohorts generate low-quality PRs that the single maintainer cannot review | High | Medium | CODEOWNERS per track with student leads; cohort work in forks or a cohort branch; review rules in the playbook | Each cohort start |

## 9. Open questions

These need answers from the maintainer or from partners. Nothing in the specifications assumes an answer.

| ID | Question | Blocks |
| :--- | :--- | :--- |
| Q-01 | The project brief's one-line description was left unfilled. Confirm the README one-liner, which is taken from the existing README. | README |
| Q-02 | Which institution and which Hub will pilot, and what success metrics and targets will they accept (time to find an event, registration completion, share of passes scanned successfully at the gate)? | A pilot, if one happens |
| Q-03 | Who is the second maintainer or organisation owner? | v1.0 (R-03) |
| Q-05 | Which email domains are confirmed by which institutions? None may be seeded until confirmed. | M1 seed data |
| Q-06 | Who reviews the Kinyarwanda strings? | v1.0 Kinyarwanda |
| Q-07 | Will the project run a public demo? If yes, who hosts it and under whose name (it must stay synthetic-only, ADR-0010)? | Demo |
| Q-08 | Is the course cohort expected to contribute in this repository or in forks? Answered for the Advanced DevOps course: neither; KamiKon is the instructor's reference repository (`docs/teaching/COURSE_ALIGNMENT.md`). Open for future cohorts. | `docs/teaching/SPRINT_PLAYBOOK.md` |
| Q-09 | Should the ID-photo review fallback for universities without student email be built in v1, given that it introduces image storage and moderation work? It is specified behind a feature flag, off by default. | M1 scope |
| Q-10 | Trademark searches at the Rwanda Development Board and USPTO for "KamiKon": who performs them, and when? | v1.0 announcement |
| Q-11 | The design tokens (colours, type, radii) are not published; they exist only in the maintainer's private design notes. Publish the values as `design/tokens.json`, and point US-0.1 and US-2.2 at that file. | M2-5 |
