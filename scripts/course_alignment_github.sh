#!/usr/bin/env bash
# One-off migration of the GitHub planning state to the course weeks in
# docs/teaching/COURSE_ALIGNMENT.md. Run once from the repository root:
#   bash scripts/course_alignment_github.sh
# Read it before running: it pushes, merges, closes issues and protects main.
# Steps are not idempotent. If one fails, fix the cause and resume from it:
#   FROM=6 bash scripts/course_alignment_github.sh
set -euo pipefail

R=pelino250/KamiKon
GH="gh --repo $R"
FROM=${FROM:-0}
W3="Week 3: Containers"; W4="Week 4: Infrastructure as Code"; W5="Week 5: DevSecOps"
W6="Week 6: Observability and Release"; W7="Week 7: Integration"

if [ 0 -ge "$FROM" ]; then
echo "== 0. Bring main up to date before branch protection blocks direct pushes"
git push origin main
gh pr merge 47 --repo "$R" --squash   # Dependabot setup-uv 10.3.1, all checks green
git fetch origin main
git push origin --delete dev   # stale; every commit is already in main (trunk-based, no dev branch)
fi

if [ 1 -ge "$FROM" ]; then
echo "== 1. Labels"
gh label create post-v1 --repo "$R" --color BFD4F2 \
  --description "After v1.0; needs its own ADR (ADR-0005)"
for n in 1 5; do $GH issue edit "$n" --add-label "good first issue" --remove-label good-first-issue; done
gh label delete good-first-issue --repo "$R" --yes
fi

if [ 2 -ge "$FROM" ]; then
echo "== 2. Week milestones (due on the Sunday that ends each week)"
mk() { gh api "repos/$R/milestones" -f title="$1" -f due_on="$2T23:59:59Z" -f description="$3" --silent; }
mk "Week 3: Containers"                  2026-11-01 "Dockerfile, Compose, Kubernetes on kind, branch protection"
mk "Week 4: Infrastructure as Code"      2026-11-08 "terraform/ and ansible/ for Azure staging"
mk "Week 5: DevSecOps"                   2026-11-15 "Container, IaC and code scanning; monolith ADR"
mk "Week 6: Observability and Release"   2026-11-22 "Health, logs, metrics, MONITORING.md, CD to staging with rollback, readiness"
mk "Week 7: Integration"                 2026-11-29 "End-to-end run, architecture diagram, v0.1.0 release"
fi

if [ 3 -ge "$FROM" ]; then
echo "== 3. Close done, duplicate and superseded issues"
cl() { $GH issue close "$1" --reason "$2" --comment "$3"; }
cl 2  "not planned" "Superseded: the flat layout and single settings module stay (review C-25, docs/07_ROADMAP.md §7)."
cl 4  completed     "Done: .github/workflows/ci.yml runs pre-commit, checks, test and workflow-lint."
cl 7  "not planned" "Superseded by session authentication and the /api/v1/ scope in docs/03_API_SPEC.md (ADR-0005)."
cl 8  completed     "Done for Bandit, pip-audit and detect-secrets. CodeQL continues in #34."
cl 5  "not planned" "Superseded by #36 (M1-1 and M1-2)."
cl 32 completed     "Done: README layout, CODEOWNERS, GLOSSARY.md and ADR-0001 match the repository (CODEOWNERS updated for the course paths in the course-alignment PR)."
cl 33 "not planned" "Duplicate of #3, which now carries these acceptance criteria."
cl 41 "not planned" "Superseded by 011d009: checks are written directly in ci.yml and run locally as plain commands."
fi

if [ 4 -ge "$FROM" ]; then
echo "== 4. Post-v1: label and remove from milestones"
for n in 11 23 24 25 26 27 28 29; do $GH issue edit "$n" --add-label post-v1 --remove-milestone; done
fi

if [ 5 -ge "$FROM" ]; then
echo "== 5. Product backlog: no course week, titles follow the roadmap IDs"
for n in 1 10 17 18 20 21; do $GH issue edit "$n" --remove-milestone; done
$GH issue edit 6  --remove-milestone --title "[M1-3] Affiliation by mailbox proof, campus selection, expiry and reminder"
$GH issue edit 9  --remove-milestone --title "[US-2.1] As an organizer, I want to create an academic event and set its Access Policy and Delivery Mode"
$GH issue edit 13 --remove-milestone --title "[M3-1] Registration, waitlist, cancellation and promotion"
$GH issue edit 14 --remove-milestone --title "[M3-2, M3-3] Signed Gate Pass (Ed25519), pass page and calendar file"
$GH issue edit 15 --remove-milestone --title "[M3-4, M3-5] Scanner PWA and roster export"
$GH issue edit 20 --title "[M5] Optimise discovery queries; per-view caching only if NFR-01 fails"
$GH issue edit 21 --title "[M5-1] Load test on the reference deployment (NFR-01)"
$GH issue edit 36 --title "[M1-1, M1-2] Institutions in admin and seed command"
for n in 13 14 15; do
  $GH issue comment "$n" --body "This body predates ADR-0002 and ADR-0008. The acceptance criteria are the M3 rows in docs/07_ROADMAP.md; ignore HMAC and student identifiers here."
done
$GH issue comment 6 --body "This body predates ADR-0003 (mailbox proof and expiry). The acceptance criteria are M1-3 in docs/07_ROADMAP.md. #37 describes the earlier domain-match design and needs the same review."
fi

if [ 6 -ge "$FROM" ]; then
echo "== 6. Course-week issues: repurposed"
$GH issue edit 3 --milestone "$W3" --title "[M0-2, M0-3] Dockerfile and Docker Compose for development" --body-file - <<'EOF'
Week 3 practice: containers. Plan: docs/teaching/COURSE_ALIGNMENT.md §3.

## Acceptance criteria
- [ ] `Dockerfile`: pinned base image, multi-stage, non-root user, a comment on every instruction
- [ ] `.dockerignore` excludes `.git`, `.env`, `.venv` and local databases
- [ ] `compose.yaml` with `web`, `db` (PostgreSQL 17) and `mailpit`; named volume for the database
- [ ] Settings read `DATABASE_URL` and `EMAIL_URL`; `DEBUG` no longer selects the database (ADR-0006)
- [ ] Secrets come only from environment variables; `.env.example` lists them
- [ ] `docker compose up --build` serves the admin; migrations apply against PostgreSQL
- [ ] CI builds the image on every PR
- [ ] README quick start uses Compose

The `worker` service waits for M1-6.
EOF
$GH issue edit 12 --milestone "$W5" --title "[M2-6] Container stage: build, Trivy, SBOM, push to ghcr.io" --body-file - <<'EOF'
Week 5 practice: DevSecOps. Plan: docs/teaching/COURSE_ALIGNMENT.md §3.

## Acceptance criteria
- [ ] `container` job builds the image from #3
- [ ] Trivy fails the job on HIGH or CRITICAL findings that have a fix
- [ ] CycloneDX SBOM uploaded as an artifact
- [ ] Image pushed to `ghcr.io/pelino250/kamikon` with the commit SHA tag on `main` only
- [ ] Job permissions: `packages: write` only where the push happens
EOF
$GH issue edit 34 --milestone "$W5" --title "[M0-5, M1-7] Deploy check and CodeQL in CI" --body-file - <<'EOF'
Week 5. The other items of the original DevSecOps issue are done (#8) or covered by the Week 3 branch protection.

## Acceptance criteria
- [ ] `manage.py check --deploy` with production settings runs in the `checks` job
- [ ] CodeQL runs on PRs and weekly
- [ ] `docs/06_CI_CD_AND_RELEASES.md` §2 status updated
EOF
$GH issue edit 19 --milestone "$W6" --title "[DO-4.3] Health endpoints, structured logs, metrics and MONITORING.md" --body-file - <<'EOF'
Week 6. Plan: docs/teaching/COURSE_ALIGNMENT.md §3. Scope: ADR-0012.

## Acceptance criteria
- [ ] `/healthz` (process up) and `/readyz` (database reachable), with tests
- [ ] JSON logs with a correlation ID per request, returned in a response header; no client IP addresses in logs
- [ ] Metrics endpoint not published by the reverse proxy
- [ ] Prometheus and Grafana on the staging VM, deployed by Ansible
- [ ] `MONITORING.md`: RED signals for two user journeys, USE signals for the VM, one alert per signal with threshold, owner and channel, and what is not collected and why
- [ ] No hosted telemetry (ADR-0010)
EOF
$GH issue edit 16 --milestone "$W6" --title "[DO-3.4] CD to staging with smoke test and tested rollback" --body-file - <<'EOF'
Week 6. Plan: docs/teaching/COURSE_ALIGNMENT.md §3. Staging holds synthetic data only (ADR-0010).

## Acceptance criteria
- [ ] `.github/workflows/cd.yml` deploys the `main` image to staging through the Ansible playbook
- [ ] The job runs in the protected `staging` environment
- [ ] No stored Azure credential; if a later job runs Terraform from Actions, it logs in through OIDC
- [ ] A smoke test after deployment fails the run if `/readyz` fails
- [ ] Rollback to the previous image digest is documented and has been run once; run linked here
- [ ] HTTPS on staging with a Let's Encrypt certificate for the public IP's DNS name
EOF
$GH issue edit 22 --milestone "$W6" --title "[M5-3] Staging database backup and restore drill (optional in Week 6)"
fi

if [ 7 -ge "$FROM" ]; then
echo "== 7. Course-week issues: new"
new() { $GH issue create --milestone "$1" --title "$2" --label "$3" --body-file -; }
new "$W3" "[W3] Kubernetes manifests for a local kind cluster" "type:devops,comp:infra" <<'EOF'
Week 3, Session 2 lab. Scope: ADR-0012 (local clusters only).

## Acceptance criteria
- [ ] `k8s/`: Deployment, Service, ConfigMap and Secret template (no real secret committed), PostgreSQL for the cluster
- [ ] `k8s/README.md`: create a kind cluster, load the image, apply, scale to 5 and back to 3, delete a Pod and watch it return
- [ ] kubeconform validates the manifests in CI
EOF
new "$W3" "[W3] Branch protection ruleset on main" "type:devops,comp:ci-cd" <<'EOF'
Week 1 and 2 practice: merges gated by CI. Settings: docs/teaching/COURSE_ALIGNMENT.md §5.
Applied by scripts/course_alignment_github.sh; closed when the first PR merges through it.
EOF
new "$W4" "[W4] Terraform: Azure staging VM" "type:devops,comp:infra" <<'EOF'
Week 4 practice: provisioning with Terraform. Scope: ADR-0012.

## Acceptance criteria
- [ ] `terraform/`: resource group, virtual network, subnet, NSG (22 from one address; 80 and 443), public IP with a DNS label, VM
- [ ] `variables.tf`, `outputs.tf` (public IP, resource IDs), `terraform/README.md`
- [ ] Remote state in Azure Storage; no state or `.tfvars` with secrets in Git
- [ ] Budget alert on the subscription
- [ ] CI: `terraform fmt -check`, `terraform validate`, TFLint
- [ ] `apply` and `destroy` both tested
EOF
new "$W4" "[W4] Ansible: configure, harden and deploy to staging" "type:devops,comp:infra" <<'EOF'
Week 4 practice: configuration management with Ansible. Scope: ADR-0012.

## Acceptance criteria
- [ ] `ansible/`: playbook installs Docker, deploys the Compose stack with synthetic seed data
- [ ] Firewall (22 from one address; 80 and 443) and SSH hardening (no root login, keys only)
- [ ] Reverse proxy logs no client IP addresses; logs kept 7 days (ADR-0012)
- [ ] Grafana reachable only through an SSH tunnel
- [ ] Inventory generated from `terraform output`
- [ ] Second run reports `changed=0`
- [ ] ansible-lint in CI; `ansible/README.md`
EOF
new "$W5" "[W5] Checkov on IaC and a findings log" "type:security,comp:ci-cd" <<'EOF'
Week 5 practice: scanning infrastructure code and triaging findings.

## Acceptance criteria
- [ ] Checkov scans `terraform/` and `k8s/` on every PR
- [ ] One finding triggered on purpose (for example SSH open to 0.0.0.0/0), seen failing, then fixed
- [ ] `docs/security/FINDINGS.md` records every finding from Trivy, Checkov, Bandit and pip-audit with a decision (fix, suppress with reason, accept) and is linked from SECURITY.md
EOF
new "$W5" "[W5] ADR: modular monolith over microservices" "type:docs" <<'EOF'
Week 5, Session 2. Record why KamiKon stays one Django application, stating the strongest case for splitting it (for example the scanner sync or notifications) and what would change the decision. Link the module boundaries in docs/02_ARCHITECTURE.md §3.
EOF
new "$W6" "[W6] Release readiness checklist and DORA metrics" "type:docs,comp:ci-cd" <<'EOF'
Week 6, Session 2.

## Acceptance criteria
- [ ] `docs/RELEASE_READINESS.md`: scored checklist, chosen release strategy and why, rollback plan
- [ ] How deployment frequency, lead time, change failure rate and time to restore are measured from GitHub data
- [ ] Checklist scored once against staging
EOF
new "$W7" "[W7] End-to-end integration, architecture diagram and v0.1.0" "type:devops,comp:ci-cd" <<'EOF'
Week 7 practice: integrating every pipeline stage.

## Acceptance criteria
- [ ] Someone who did not write the code goes from a fresh clone to a deployed, monitored staging using only the READMEs
- [ ] Mermaid diagram of the pipeline and runtime in docs/02_ARCHITECTURE.md
- [ ] `v0.1.0` released through the pipeline in docs/06_CI_CD_AND_RELEASES.md §4; `gh attestation verify` succeeds
EOF
fi

if [ 8 -ge "$FROM" ]; then
echo "== 8. Branch protection on main (COURSE_ALIGNMENT.md §5)"
gh api "repos/$R/rulesets" --method POST --input - <<'EOF'
{
  "name": "main-protection",
  "target": "branch",
  "enforcement": "active",
  "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "required_linear_history"},
    {"type": "pull_request", "parameters": {
      "required_approving_review_count": 0,
      "dismiss_stale_reviews_on_push": true,
      "require_code_owner_review": false,
      "require_last_push_approval": false,
      "required_review_thread_resolution": true}},
    {"type": "required_status_checks", "parameters": {
      "strict_required_status_checks_policy": true,
      "required_status_checks": [
        {"context": "pre-commit", "integration_id": 15368},
        {"context": "checks", "integration_id": 15368},
        {"context": "test", "integration_id": 15368},
        {"context": "workflow-lint", "integration_id": 15368},
        {"context": "pr-title", "integration_id": 15368}]}}
  ]
}
EOF
gh api "repos/$R" --method PATCH -F allow_merge_commit=false -F allow_rebase_merge=true \
  -F allow_squash_merge=true -F delete_branch_on_merge=true --silent
fi

if [ 9 -ge "$FROM" ]; then
echo "== 9. Close the Sprint milestones (now empty)"
for m in 1 2 3 4 5 6 7 8; do gh api "repos/$R/milestones/$m" --method PATCH -f state=closed --silent; done
fi

if [ 10 -ge "$FROM" ]; then
echo "== 10. Tag the end of Week 2"
git tag -a course-w2 -m "Advanced DevOps: state of main at the end of Week 2" origin/main
git push origin course-w2

fi
echo "Done. Manual step: remove the Mobile and SPA options from the Track field of the KamiKon Delivery Board."
