# Agent instructions

KamiKon is a Django 6.1 project on Python 3.14, managed with uv. Read `README.md` for what it does and `docs/01_PRD.md` for v1.0 scope.

## Commands

```bash
uv sync --locked                        # install
uv run pre-commit run --all-files       # Ruff, file hygiene, secret scan
uv run pytest --cov                     # tests and coverage threshold
uv run python manage.py makemigrations  # after any model change
```

CI (`.github/workflows/ci.yml`) runs these commands plus Django checks, Bandit and pip-audit. A change is done when they pass.

## Before changing code

- Use the terms in `GLOSSARY.md`: Host, Access Policy, Seat Pool, Registration, Gate Pass. Do not invent synonyms.
- Read the ADRs in `docs/adr/` for the area you touch. If your change contradicts one, stop and say so; a new ADR has to replace it first.
- Check `docs/02_ARCHITECTURE.md` for the data model before adding fields or tables.

## Rules

- Never collect government identifiers: no National ID or passport fields (ADR-0008).
- Never add third-party telemetry, scripts, fonts or CDNs (ADR-0010, `docs/05_DATA_PROTECTION.md`).
- Never put real names, email addresses or personal data in code, fixtures or tests. Use `example.org` addresses and synthetic data.
- PostgreSQL is the target database (ADR-0006). Do not rely on SQLite behaviour.
- URLs, the API, templates and logs never expose integer keys. Use `public_id` (UUIDv7); Gate Pass QR codes use a random UUIDv4 `pass_id` instead (ADR-0011).
- Tests go in `tests/`; pytest does not collect them anywhere else.
- No new runtime dependency without the justification in `docs/06_CI_CD_AND_RELEASES.md` §6.
- Commits and PR titles follow Conventional Commits (`feat`, `fix`, `ci`, `build`, `docs`, `refactor`, `test`, `chore`). Do not add AI attribution or `Co-Authored-By` lines.
