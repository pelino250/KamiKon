# KamiKon

KamiKon (*Kaminuza* + *Connect*) is an open-source platform on which universities and partner Hubs in Rwanda publish academic Events, decide who may attend, and issue gate passes that campus security can check with or without a network connection.

**Status: pre-alpha.** The repository contains the project skeleton, CI, and the v1.0 specifications. No user-facing feature is implemented yet. Do not deploy it with real users.

## Why

Academic events at one university are hard to find for students and staff at another, and for alumni and industry. When visitors do come, gates often have no list of who is expected. KamiKon combines three things general event platforms do not: eligibility across institutions (verified university affiliation and four Access Policies), separate seat pools for host members, visiting members and the public, and a signed gate pass that works offline. It is designed to be self-hosted, so an institution can keep personal data in Rwanda.

## Quick start (development)

Requirements: Git, and [uv](https://docs.astral.sh/uv/), which installs the pinned Python 3.14 for you.

```bash
git clone https://github.com/pelino250/KamiKon.git
cd KamiKon
uv sync --locked
cp .env.example .env          # DEBUG=True; a development SECRET_KEY is used when blank
uv run python manage.py migrate
uv run python manage.py runserver
```

Open http://127.0.0.1:8000/admin/. To create a login: `uv run python manage.py createsuperuser`.

Run the tests: `uv run pytest`.

This quick start uses SQLite and exists only until the Docker Compose setup lands (roadmap item M0-2). Seat allocation and search need PostgreSQL, so the full suite and the CI coverage gate require PostgreSQL. See ADR-0006.

## Documentation

| Read this | For |
| :--- | :--- |
| [docs/00_DECISIONS_AND_AUDIT.md](docs/00_DECISIONS_AND_AUDIT.md) | Decisions, risks, open questions and sources; start here |
| [docs/01_PRD.md](docs/01_PRD.md) | What v1.0 does and does not do |
| [docs/02_ARCHITECTURE.md](docs/02_ARCHITECTURE.md) | Components, data model, eligibility, gate pass format |
| [docs/03_API_SPEC.md](docs/03_API_SPEC.md) | Web routes and `/api/v1/` |
| [docs/04_THREAT_MODEL.md](docs/04_THREAT_MODEL.md) | Security model |
| [docs/05_DATA_PROTECTION.md](docs/05_DATA_PROTECTION.md) | Obligations for deployers (Rwanda Law No. 058/2021) |
| [docs/06_CI_CD_AND_RELEASES.md](docs/06_CI_CD_AND_RELEASES.md) | Checks, supply chain, versioning |
| [docs/07_ROADMAP.md](docs/07_ROADMAP.md) | Milestones and definition of done for v1.0 |
| [docs/adr/](docs/adr/) | Architecture decision records |
| [GLOSSARY.md](GLOSSARY.md) | Domain vocabulary used everywhere |

## Repository layout

```text
.github/     Issue and PR templates, CODEOWNERS, workflows
kamikon/     Django project package (settings, URLs, ASGI/WSGI)
apps/        Django apps (accounts, events, tickets, ...)
tests/       Test suite
docs/        Specifications, ADRs, teaching playbook
scripts/     CI entry point and GitHub project automation
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Students in a course cohort also read [docs/teaching/SPRINT_PLAYBOOK.md](docs/teaching/SPRINT_PLAYBOOK.md). Everyone follows the [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md). Do not open public issues for them.

## Licence

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
