# Contributing to KamiKon

Thank you for helping. This guide applies to everyone. Students in a course cohort additionally follow `docs/teaching/SPRINT_PLAYBOOK.md`.

## 1. Before you start

- Read `docs/01_PRD.md`, then the document for the area you will touch. Use the terms in `GLOSSARY.md`.
- For anything larger than a small fix, comment on an existing issue or open one first, so the approach can be agreed before you write code.
- Look for issues labelled `good first issue`.
- If your change contradicts an ADR in `docs/adr/`, say so in the PR and propose a new ADR. Do not silently override one.

## 2. Set up

Follow the quick start in `README.md`. Then:

```bash
uv run pre-commit install
```

The hook then runs Ruff, file hygiene checks and secret scanning on every commit.

## 3. Branches and commits

Branch from `main`:

```text
<type>/<issue-number>-<short-description>
```

Examples: `feat/14-campus-directory-models`, `fix/52-registration-race`, `devops/5-compose-postgres`, `docs/31-api-errors`.

Commit messages and PR titles follow Conventional Commits:

```text
<type>(<optional scope>): <imperative summary>
```

Types: `feat`, `fix`, `ci`, `build`, `docs`, `refactor`, `test`, `chore`. The `pr-title` check enforces this on PR titles.

Sign off every commit to certify the Developer Certificate of Origin (https://developercertificate.org/), which states that you have the right to submit the work under the project licence:

```bash
git commit -s -m "feat(events): add seat pool constraints"
```

## 4. Checks

Before pushing, run the same checks CI runs:

```bash
uv run pre-commit run --all-files   # lint, format, hygiene, secrets
uv run pytest --cov                 # tests and the coverage threshold
```

The other CI steps (Django checks, Bandit, pip-audit, lockfile) are listed in `.github/workflows/ci.yml`; copy any failing step and run it as written. Until Docker Compose lands (roadmap M0-2), tests reproduce CI only with `DEBUG=False` against PostgreSQL, using the environment variables of the `test` job. With the SQLite quick start, the coverage threshold can fail locally while CI passes.

## 5. Pull requests

- Use the PR template and link the issue (`Closes #123`).
- Keep PRs small and focused; one concern per PR.
- Add or update tests. Coverage is enforced by the threshold in `pyproject.toml`.
- Update documentation in the same PR when behaviour, configuration, the API or the data model changes.
- Add an entry under "Unreleased" in `CHANGELOG.md` for user-visible changes.
- New runtime dependencies need the justification described in `docs/06_CI_CD_AND_RELEASES.md` §6.
- Never commit secrets, real personal data, or screenshots that show real people's data. Use the synthetic seed data.
- A maintainer or CODEOWNER review is required. PRs are squash-merged.

## 6. Issues and labels

Open issues through a template: user story, feature request, DevOps task or bug report.

| Group | Labels |
| :--- | :--- |
| Type | `type:feature`, `type:devops`, `type:bug`, `type:docs`, `type:security` |
| Component | `comp:auth`, `comp:institutions`, `comp:events`, `comp:discovery`, `comp:tickets-qr`, `comp:notifications`, `comp:design`, `comp:ci-cd`, `comp:docker`, `comp:infra`, `comp:observability`, `comp:mobile`, `comp:spa` |
| Triage | `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix` |
| Scope | `post-v1` |
| Learning | `good first issue`, `pair-programming-recommended` |

Security problems are never reported as issues. See `SECURITY.md`.

## 7. Conduct

Participation is governed by `CODE_OF_CONDUCT.md`.

## 8. Licence

By contributing, you agree that your contribution is licensed under the Apache License 2.0, as stated in section 5 of the licence.
