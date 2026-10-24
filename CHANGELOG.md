# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `AGENTS.md` with commands and project rules for coding agents; `CLAUDE.md` imports it.
- CI workflow with four jobs: `pre-commit` (Ruff, file hygiene, secrets), `checks` (lockfile, Django checks, Bandit, pip-audit), `test` (pytest on PostgreSQL 17) and `workflow-lint` (actionlint).
- Apache License 2.0 (`LICENSE`, `NOTICE`).
- Specifications for v1.0 in `docs/`: decisions and audit, product requirements, architecture and data model, interface specification, threat model, data protection guide for deployers, CI/CD and release process, roadmap.
- Architecture decision records 0002 to 0011.
- `CODE_OF_CONDUCT.md` (Contributor Covenant 3.0), `SECURITY.md`, `GOVERNANCE.md`, this changelog.
- Course-cohort process in `docs/teaching/SPRINT_PLAYBOOK.md`.
- Feature request issue template.
- `.python-version` pinning Python 3.14.
- Email sign-in: the user model has no username, a case-insensitive unique email, a UUIDv7 `public_id` and a resettable calendar token (M0-4).
- `apps.institutions`: Universities, email domains, Campuses, Hubs, Venues and Host roles, managed in the admin (M1-1).
- `manage.py seed_demo` creates synthetic institutions, Venues and staff users (M1-2).
- `apps.audit`: an append-only audit log. Granting or revoking a Host role writes an entry (M1-5, FR-03).
- `apps.events`: Event, Seat Pool and Tag models with the constraints in architecture §4.3 (M2-1).
- A home page built from a shared base template, with translatable strings and self-hosted CSS.

### Changed
- The database connection skips TLS for local hosts and Unix sockets and still requires it for remote hosts.
- README, PRD and roadmap state that KamiKon is primarily a teaching project. Pilot partners are optional, and no milestone or release criterion waits for one.
- `docs/00_DECISIONS_AND_AUDIT.md` moved to `docs/history/2026-10-23-review.md` as a dated record. The risk register and open questions moved to `docs/07_ROADMAP.md`. The README now sends readers to the PRD first.
- `03_API_SPEC.md` defers to the generated OpenAPI schema once an endpoint exists; its table of changes from the earlier draft moved to the history file.
- `requires-python` bounded to `>=3.14,<3.15`, because Django 6.1.2 does not yet support Python 3.15.
- `CONTRIBUTING.md` limited to the general contribution process; sprint and board process moved to the teaching playbook.
- `README.md` rewritten with status, purpose, a tested quick start and a documentation index.
- `GLOSSARY.md` adds Gate Staff, Seat Pool, Registration, Gate Pass, Check-in, Affiliation and Platform Admin.
- Issue templates no longer use emoji.
- Backlog data: US-2.1 and US-7.2 use Access Policy terms; triage labels and `good first issue` added.
- `setup_github_project.py --prune-default-labels` no longer deletes `good first issue` or `wontfix`.
- `.gitignore` reduced from 717 template lines to the rules this project needs.
- NFR-03 now states the accessibility floor and blocking design checks directly; `design_docs/` stays private.

### Removed
- The empty `apps.community` app (M1-8).
- `requirements.txt`; `uv.lock` is the single source of dependencies.
- Empty `apps/*/tests.py` placeholders. pytest collects only from `tests/`, so tests written there would never run.
- A compiled `.pyc` file that had been committed under `scripts/__pycache__/`.
