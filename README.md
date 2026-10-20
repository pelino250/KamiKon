# KamiKon

**KamiKon** (*Kaminuza + Connect*) is an inter-university academic event management, discovery and smart-notification platform for higher-learning institutions and the wider academic and innovation community in Rwanda.

It is built as an industry-grade capstone in which **Web Development**, **Mobile/SPA Engineering** and **DevOps** are integrated into every sprint.

| Phase | Frontend | Backend |
| :--- | :--- | :--- |
| 1. Core Web (MVP) | Django Templates + HTMX / Tailwind | Django modular monolith (service layer) |
| 2. API-First | Swagger / Redoc | Django REST Framework, JWT, `/api/v1/` |
| 3. Mobile Companion | Flutter | `/api/v1/` + FCM |
| 4. Modern SPA | React or Angular | `/api/v1/` + CORS |

## Project Management

- **Board:** KamiKon Delivery Board (GitHub Projects): Status, Track, Priority, Story Points and Sprint fields
- **Milestones:** one per sprint, Sprint 0 → Sprint 7
- **Issues:** created from the *User Story*, *DevOps Task* and *Bug Report* templates
- **How to contribute:** see [CONTRIBUTING.md](CONTRIBUTING.md)

## Re-creating the GitHub Setup

Labels, milestones, the backlog issues and the Project board are generated from [`scripts/sprint_backlog.json`](scripts/sprint_backlog.json):

```bash
gh auth refresh -h github.com -s project      # one-time: allow Projects (v2) access
python3 scripts/setup_github_project.py --dry-run
python3 scripts/setup_github_project.py --start-date 2026-10-19
```

The script is idempotent and safe to re-run. Use `--only labels,milestones,issues,project` to run individual phases.

## Django environment

Copy `.env.example` to `.env` for local development and set `SECRET_KEY` to a unique
secret generated with Django:

```bash
cp .env.example .env
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

`DEBUG=True` uses SQLite and the console email backend for development. Set
`DEBUG=False` in production to use PostgreSQL, secure cookies, HTTPS redirects, and
the SMTP email backend. Production must provide `SECRET_KEY`, `ALLOWED_HOSTS`,
`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `SMTP_HOST`; add
`CSRF_TRUSTED_ORIGINS` when cross-origin POST requests are required. Provide secrets
through the deployment platform rather than committing a `.env` file.
The deployment check warns about HSTS subdomain inclusion and preload; enable these
only when all subdomains are HTTPS-only and the domain meets preload requirements.

## Repository Layout

The layout is flat: the Django project and apps live at the repository root.

```text
.github/            Issue/PR templates, CODEOWNERS, workflows
kamikon/            Django project package (settings, URLs, ASGI/WSGI)
apps/               Django apps (accounts, events, tickets, ...)
tests/              Test suite
design_docs/        Design and architecture notes
docs/               Agent config (docs/agents) and ADRs (docs/adr)
scripts/            GitHub project automation
GLOSSARY.md         Domain vocabulary
```

Later phases add `mobile_flutter/` (Flutter app), `frontend_spa/` (React or Angular) and
deployment files (Dockerfile, Docker Compose) at the root when they are built.
