# Course Alignment: Advanced DevOps

KamiKon is the instructor's reference repository for the Advanced DevOps course (7 weeks). Students build their own cumulative repository. Each week the maintainer adds the same deliverable to KamiKon and tags the result, so students can compare their work with a worked example. Cohorts do not contribute to this repository (Q-08 is answered for this course).

The Formatives and the Summative are team assessments of the students' own projects. KamiKon does not submit them and is not graded against their rubrics. It shows each week's practice working in a real codebase, ideally early in the week so teams see it before their own deadlines.

Teaching infrastructure (`k8s/`, `terraform/`, `ansible/`, staging monitoring) is in scope under ADR-0012. Product work follows `docs/07_ROADMAP.md` on its own schedule.

## 1. Calendar

Weeks 1 and 2 are complete. Week 3 starts on Monday 26 October 2026. Each GitHub milestone is due on the Sunday that ends its week. The assessment column is context only: it shows what student teams are working on that week.

| Week | Dates (2026) | Topic | Student teams' assessment (context) | GitHub milestone | Tag at the end |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | done | DevOps culture, GitHub project management | Formative 1 starts | none | none |
| 2 | done | CI with GitHub Actions, cloud fundamentals | Formative 1 | none | `course-w2` |
| 3 | 26 Oct to 1 Nov | Docker, Compose, Kubernetes | Formative 2, Quiz 1 | `Week 3: Containers` | `course-w3` |
| 4 | 2 to 8 Nov | Terraform on Azure, Ansible | Formative 3 Parts 1 and 2 | `Week 4: Infrastructure as Code` | `course-w4` |
| 5 | 9 to 15 Nov | DevSecOps, microservices | Formative 3 Part 3 | `Week 5: DevSecOps` | `course-w5` |
| 6 | 16 to 22 Nov | Observability, release readiness | Formative 3 due | `Week 6: Observability and Release` | `course-w6` |
| 7 | 23 to 29 Nov | Integration | Summative and viva | `Week 7: Integration` | `course-w7` |

## 2. Weeks 1 and 2: where KamiKon stands

| Practice taught | KamiKon |
| :--- | :--- |
| Repository structure, README, licence, contribution guide | Done |
| GitHub Project board | Done (KamiKon Delivery Board); restructured by this plan |
| Branch protection on `main` | Missing; added by the GitHub change script (§5) |
| `pyproject.toml`, `uv.lock`, pre-commit | Done |
| `.github/workflows/ci.yml` running lint and tests on PRs | Done, with more checks than the course asks for: Bandit, pip-audit, Django checks, PostgreSQL tests, actionlint |
| CI as a required status check | Missing; added with branch protection |

## 3. Weekly deliverables

Each row is one GitHub issue in that week's milestone. "Course" items come from the session slides. "Beyond the course" items are additions the maintainer judged necessary for a sound pipeline. They do not change the product's goals.

### Week 3: Containers

| Issue | Deliverable | Source | Exit criterion |
| :--- | :--- | :--- | :--- |
| #3 (M0-2, M0-3) | `Dockerfile`: pinned base image, multi-stage, non-root user, a comment on every instruction, `.dockerignore`. `compose.yaml` with `web`, `db` (PostgreSQL 17) and `mailpit`, a named volume, settings from environment variables. Settings read `DATABASE_URL` and no longer pick the database from `DEBUG` | Course; roadmap | `docker compose up --build` serves the admin; README documents it |
| #3 | CI builds the image on every PR | Course | `build` job green |
| new | `k8s/`: Deployment, Service, ConfigMap and Secret for a kind cluster; README covering scale-up, scale-down and Pod self-healing | Course | `kubectl apply -f k8s/` works on kind; kubeconform passes in CI |
| new | Branch protection ruleset on `main` with required checks | Course | A PR with a failing check cannot merge |
| this PR | ADR-0012 and this plan | Beyond the course | Merged |

The worker service from M0-2 waits until M1-6 adds the Tasks backend.

### Week 4: Infrastructure as Code

| Issue | Deliverable | Source | Exit criterion |
| :--- | :--- | :--- | :--- |
| new | `terraform/`: resource group, virtual network, subnet, network security group (22 from one address; 80 and 443), public IP with a DNS label, VM; `variables.tf`, `outputs.tf`, README | Course | `terraform apply` and `destroy` both succeed |
| same | Remote state in Azure Storage, a budget alert, `terraform fmt -check`, `validate` and TFLint in CI | Beyond the course | CI job `iac` green |
| new | `ansible/`: installs Docker, deploys the Compose stack, configures the firewall and SSH hardening; inventory generated from Terraform output; README | Course | The second run reports `changed=0` |
| same | Reverse proxy logs no client IP addresses and keeps logs 7 days; Grafana only through an SSH tunnel (ADR-0012) | Beyond the course | Checked in the playbook |
| same | ansible-lint in CI; secrets come from the GitHub `staging` environment, never from files in the repository | Beyond the course | CI job `iac` green |

### Week 5: DevSecOps

| Issue | Deliverable | Source | Exit criterion |
| :--- | :--- | :--- | :--- |
| #12 (M2-6) | `container` job: build, Trivy scan that fails on HIGH or CRITICAL with a fix available, CycloneDX SBOM, push to `ghcr.io` on `main` | Course; roadmap | Job green; image pullable |
| new | Checkov on `terraform/` and `k8s/`; findings and triage decisions in `docs/security/FINDINGS.md`, linked from `SECURITY.md` | Course | Every finding has a decision and a reason |
| #34 (M0-5, M1-7) | `manage.py check --deploy` in CI; CodeQL | Roadmap | Both in CI |
| new | ADR: KamiKon stays a modular monolith; microservices rejected, with the strongest case for them stated | Course | ADR merged |

`SECURITY.md` stays the vulnerability disclosure policy. Students keep findings in their own `SECURITY.md`; KamiKon keeps them in a separate file so the reporting instructions stay short.

### Week 6: Observability and release

| Issue | Deliverable | Source | Exit criterion |
| :--- | :--- | :--- | :--- |
| #19 (DO-4.3) | `/healthz` and `/readyz`; structured JSON logs with a request correlation ID; a metrics endpoint the proxy does not publish | Course; roadmap | Tests for both endpoints and the log format |
| #19 | Prometheus and Grafana on staging (ADR-0012); `MONITORING.md` with RED signals for two user journeys, USE signals for the VM, one alert per signal, and what is not collected and why | Course | Dashboard and alert visible on staging |
| #16 (DO-3.4) | `cd.yml`: deploy the image built from `main` to staging through Ansible, behind the protected `staging` environment; post-deploy smoke test; rollback to the previous image digest, tested once | Course | Deployment and rollback runs linked from the PR |
| #16 | No stored Azure credential; OIDC if Terraform later runs from Actions | Beyond the course | No Azure credential in repository secrets |
| new | `docs/RELEASE_READINESS.md`: the scored checklist, release strategy choice, and how DORA's four metrics are measured from GitHub data | Course | Checklist scored once |
| #22 (M5-3), optional | Backup of the staging database and one restore drill | Beyond the course | Restore tested |

### Week 7: Integration

| Issue | Deliverable | Source | Exit criterion |
| :--- | :--- | :--- | :--- |
| new | End-to-end run: from a fresh clone to a deployed, monitored staging, following only the READMEs | Course | Done by someone who did not write the code |
| same | Architecture diagram (Mermaid) of the pipeline and runtime in `docs/02_ARCHITECTURE.md` | Course | Diagram merged |
| same | Release `v0.1.0` through the release pipeline in `06_CI_CD_AND_RELEASES.md` §4: signed tag, SBOM, attestation | Beyond the course | `gh attestation verify` succeeds |

## 4. GitHub planning

- **Milestones.** The five week milestones in §1 replace "Sprint 0" to "Sprint 7". Issues not tied to a course week have no milestone. They stay on the board under the roadmap IDs in `07_ROADMAP.md`.
- **Post-v1.** Flutter, SPA and map issues carry the `post-v1` label and no milestone (ADR-0005).
- **Board.** The KamiKon Delivery Board keeps its Status, Priority and Story Points fields. Remove the Mobile and SPA options from the Track field in the project settings (the API cannot edit options without clearing values).
- **Labels.** GitHub recognises `good first issue`; the script deletes the duplicate `good-first-issue`.
- **Generators.** `scripts/sprint_backlog.json` and `scripts/setup_github_project.py` describe the old sprint plan. Do not run them again; they would recreate the Sprint milestones and duplicate retitled issues.
- **Tags.** `course-wN` tags mark the state of `main` at the end of each week. Students diff two tags to see one week's work. Product work merges in the same weeks, so filter by path to see only the course deliverable: `git diff course-w2 course-w3 -- Dockerfile compose.yaml k8s/ .github/`.

## 5. Branch protection for a single maintainer

`06_CI_CD_AND_RELEASES.md` §3 requires one approving CODEOWNER review. With one maintainer, that blocks every merge, because GitHub does not let authors approve their own PRs. Until a second maintainer exists (R-03), the ruleset requires a PR and the checks `pre-commit`, `checks`, `test`, `workflow-lint` and `pr-title`, with zero required approvals. It also blocks force pushes and deletion and requires linear history. The ruleset accepts squash and rebase merges and rejects merge commits. Rebase merges put each small commit of a product slice on `main`, so learners can step through them. Branches open PRs straight into `main`, as the Week 1 and 2 slides teach; the repository has no `dev` branch. Raise approvals to one when Q-03 is answered.

## 6. Differences from the course examples

- KamiKon uses PostgreSQL in CI and locally; the course's Week 2 demo uses SQLite. Students may use either, but should say which and why.
- KamiKon pins actions by commit SHA. The course slides use version tags. SHA pinning is stricter, and Dependabot keeps the SHAs current.
- The product's data rules (synthetic data only, no government identifiers, no third-party telemetry) come from KamiKon's own ADRs. Students' projects follow their own rules.
