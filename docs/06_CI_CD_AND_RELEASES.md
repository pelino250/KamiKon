# 06: CI/CD, Supply Chain and Releases

Status: the "Present" rows describe `.github/workflows/` as of 2026-10-23; everything else is planned with the milestone shown.

## 1. Principle

Every check is a plain command in `.github/workflows/ci.yml` or a hook in `.pre-commit-config.yaml`, so a contributor can copy any failing step from the workflow and run it locally. Lint, format and secret scanning live in pre-commit, so they run on every local commit as well as in CI.

## 2. Checks

| Check | Tool | CI job | Gate | Status |
| :--- | :--- | :--- | :--- | :--- |
| Lint and format | Ruff (`ruff check`, `ruff format`) | `pre-commit` | Required | Present |
| File hygiene | pre-commit hooks (YAML, end of file, whitespace) | `pre-commit` | Required | Present |
| Secrets | detect-secrets against `.secrets.baseline` | `pre-commit` | Required | Present |
| Lockfile | `uv lock --check` | `checks` | Required | Present |
| Django | `manage.py check`, `makemigrations --check` | `checks` | Required | Present |
| Security | Bandit | `checks` | Required | Present |
| Dependency audit | pip-audit | `checks` | Required | Present |
| Tests | pytest, pytest-django, coverage | `test` | Required | Present; runs on PostgreSQL 17 |
| Workflow lint | actionlint | `workflow-lint` | Required | Present |
| PR title | Conventional Commit PR titles | `pr-title` (own workflow) | Required | Present |
| Deploy check | `manage.py check --deploy` with production settings | `checks` | Required | M0 |
| Import contracts | import-linter contracts for module boundaries (`02_ARCHITECTURE.md` §3) | `checks` | Required | M1 |
| Licences | Licence allow-list over the locked dependency set (§6) | `checks` | Required | M1 |
| CodeQL | GitHub CodeQL for Python and JavaScript | own workflow | Required | M1; availability on public repositories to be confirmed in repository settings |
| Container | Build image, Trivy scan for HIGH and CRITICAL, SBOM | `container` | Required on `main` and releases | M2 |
| End-to-end | Playwright smoke tests of registration, pass and scanner | `e2e` | Required | M3 |
| Accessibility | axe-core run in the Playwright suite | `e2e` | Required | M3 |
| Scorecard | OpenSSF Scorecard, weekly | own workflow | Informational | M1 |

### 2.1 Test rules
- Tests run against PostgreSQL locally (Docker Compose) and in CI (ADR-0006).
- The coverage threshold is set once, in `[tool.coverage.report] fail_under` in `pyproject.toml`, measured on `apps/` only, at 80 percent. It applies from the first PR that adds a domain model (review D-14). Until then the existing value stays, and local test runs match CI only with `DEBUG=False` and PostgreSQL.
- Concurrency tests for seat allocation use real parallel database connections (`TransactionTestCase`), not mocks.
- Tests use the synthetic factories and `seed_demo`; no fixture contains real names or real email addresses. Fictional email addresses use `example.org` or `example.com`.

## 3. Branch protection

Configure a repository ruleset for `main`:
- Require a pull request with one approving review from a CODEOWNER; dismiss stale approvals on new commits.
- Require every "Required" check in §2 to pass, and require branches to be up to date.
- Block force pushes and deletion.
- Require linear history (squash merge only).
- Require signed commits from maintainers (contributors are not required to sign).
- Turn on secret scanning push protection and private vulnerability reporting in repository settings. Whether these are available on the current plan was not verified in this review; check the settings page.

## 4. Release pipeline (M2 onwards)

Triggered by pushing a tag `vMAJOR.MINOR.PATCH` that matches the top entry of `CHANGELOG.md`.

1. Re-run every required check on the tagged commit.
2. Build the container image with Docker Buildx, multi-stage, non-root, and push to `ghcr.io/pelino250/kamikon` with the version tag and the digest. The repository owner path changes if the repository moves to an organisation (R-03).
3. Generate an SBOM in CycloneDX format for the image and for the Python environment.
4. Generate `THIRD_PARTY_NOTICES` from the SBOM, including the LGPL text for psycopg, and include it in the image and the release.
5. Create GitHub artifact attestations for build provenance and for the SBOM. GitHub documents that artifact attestations alone provide SLSA v1.0 Build Level 2, and that public repositories use the Sigstore public-good instance.
6. Scan the pushed image with Trivy; a HIGH or CRITICAL finding without a recorded exception fails the release.
7. Create the GitHub Release with the changelog section, the SBOMs and the notices file.
8. Document verification for self-hosters: `gh attestation verify oci://ghcr.io/pelino250/kamikon:VERSION --owner pelino250`.

Workflow permissions are least-privilege per job: `contents: read` by default, and `packages: write`, `id-token: write` and `attestations: write` only in the release job.

## 5. Versioning

- Semantic Versioning 2.0.0. Until 1.0.0, minor versions may contain breaking changes, which are always listed under "Changed" or "Removed" in the changelog.
- What counts as the public interface: the `/api/v1/` contract, the Gate Pass payload format (§6.1 of the architecture), configuration variables, management commands, and database migrations, which must apply forward from the previous minor release.
- The Gate Pass format version byte changes only with a new format; scanners accept the current and the previous format for one minor release.
- Changelog follows Keep a Changelog 1.1.0, with an "Unreleased" section at the top.
- Supported versions: the latest minor release receives fixes; security fixes for the previous minor release for three months after a new minor release. Stated in `SECURITY.md`.

## 6. Dependency policy

- Allowed licences without review: MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0, ISC, 0BSD, PSF-2.0, Python-2.0, OFL-1.1 (fonts only). LGPL dependencies are allowed when used as unmodified libraries (psycopg). GPL, AGPL, SSPL, RSAL and licences marked as non-open-source require an ADR.
- A new runtime dependency requires a PR note covering its licence, maintenance activity, declared support for the Django version in use, and why the standard library or an existing dependency is not enough.
- Frontend assets are vendored into `static/vendor/` with their licence files, never loaded from a CDN.
- Dependabot opens weekly updates for `uv` and GitHub Actions (present). Security updates are merged within 7 days of release when CI passes.

## 7. Environments and deployment

- Development: Docker Compose (`web`, `worker`, `db`, `mailpit`), M0.
- Staging: optional, for maintainers and course cohorts. It must use synthetic data only unless it meets `05_DATA_PROTECTION.md` §4 (review C-15).
- Production: the project does not run one. Deployers follow the deployment guide added in M5, which covers the Compose production example, reverse proxy and TLS, backups and restore, upgrades (`migrate` before switching traffic), and key management.
