# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Apache License 2.0 (`LICENSE`, `NOTICE`).
- Specifications for v1.0 in `docs/`: decisions and audit, product requirements, architecture and data model, interface specification, threat model, data protection guide for deployers, CI/CD and release process, roadmap.
- Architecture decision records 0002 to 0011.
- `CODE_OF_CONDUCT.md` (Contributor Covenant 3.0), `SECURITY.md`, `GOVERNANCE.md`, this changelog.
- Course-cohort process in `docs/teaching/SPRINT_PLAYBOOK.md`.
- Feature request issue template.
- `.python-version` pinning Python 3.14.

### Changed
- `requires-python` bounded to `>=3.14,<3.15`, because Django 6.1.2 does not yet support Python 3.15.
- `CONTRIBUTING.md` limited to the general contribution process; sprint and board process moved to the teaching playbook.
- `README.md` rewritten with status, purpose, a tested quick start and a documentation index.
- `GLOSSARY.md` adds Gate Staff, Seat Pool, Registration, Gate Pass, Check-in, Affiliation and Platform Admin.
- Issue templates no longer use emoji.
- Backlog data: US-2.1 and US-7.2 use Access Policy terms; triage labels and `good first issue` added.
- `setup_github_project.py --prune-default-labels` no longer deletes `good first issue` or `wontfix`.
- `.gitignore` reduced from 717 template lines to the rules this project needs. It no longer ignores `scripts/`, which had kept `scripts/ci.py` (the CI entry point) out of the repository.
- NFR-03 now states the accessibility floor and design checks directly; `design_docs/` stays private.

### Removed
- `requirements.txt`; `uv.lock` is the single source of dependencies.
- Empty `apps/*/tests.py` placeholders. pytest collects only from `tests/`, so tests written there would never run.
- A compiled `.pyc` file that had been committed under `scripts/__pycache__/`.
