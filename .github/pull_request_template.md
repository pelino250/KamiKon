## Summary
<!-- What does this PR change, and why? Keep the PR title in Conventional Commit form, e.g. "feat(events): add access-policy validation". -->

Closes #<!-- issue number -->

## Type of Change
- [ ] `feat` New feature / user story
- [ ] `fix` Bug fix
- [ ] `ci` / `build` Pipeline, Docker or infrastructure change
- [ ] `refactor` Code change with no behaviour change
- [ ] `test` Tests only
- [ ] `docs` Documentation only

## Track
- [ ] Backend (Django/API)
- [ ] Frontend (UI/UX)
- [ ] DevOps & Infra
- [ ] Mobile (Flutter)
- [ ] SPA (React/Angular)

## How Has This Been Tested?
<!-- Commands you ran, test cases added, manual steps. -->
```bash
uv run pre-commit run --all-files
uv run pytest
```

## Screenshots / Evidence
<!-- UI screenshots (mobile + desktop), workflow run links, Grafana panels, etc. -->

## DevOps & Quality Definition of Done
- [ ] Branch follows `<track>/<issue-number>-<short-description>`
- [ ] Commits follow Conventional Commits and are signed off (`git commit -s`)
- [ ] Tests added/updated; the coverage threshold in `pyproject.toml` passes
- [ ] `ruff check` / `ruff format --check` pass locally
- [ ] No secrets, credentials or personal data committed
- [ ] New environment variables added to `.env.example`
- [ ] OpenAPI schema and docs updated (if the API, data model or configuration changed)
- [ ] `CHANGELOG.md` updated under Unreleased (if user-visible)
- [ ] CI is green on this PR
- [ ] At least **1 peer review** requested

## Reviewer Notes
<!-- Anything reviewers should look at closely: migrations, race conditions, security-sensitive code (QR signing, auth), etc. -->
