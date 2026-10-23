# PostgreSQL in every environment; database selection independent of DEBUG

Status: accepted, 2026-10-23.

## Context
`kamikon/settings.py` uses SQLite when `DEBUG` is true and PostgreSQL otherwise. Seat allocation depends on `select_for_update()`, which Django documents as having no effect on SQLite, and discovery depends on PostgreSQL full-text search. Tests on SQLite would pass while production fails. Coupling the database to `DEBUG` also means a debug deployment silently changes database.

## Decision
- PostgreSQL 17 is used for development (Docker Compose), CI and production.
- The connection is configured by `DATABASE_URL`; `DEBUG` no longer selects the database.
- The SQLite quick start remains in the README only until Compose lands (roadmap M0-2), with a warning that it cannot run the full test suite.

## Consequences
Contributors need Docker or a local PostgreSQL. Local and CI test runs measure the same code paths, so coverage and concurrency results agree.
