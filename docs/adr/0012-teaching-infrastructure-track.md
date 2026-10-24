# A teaching infrastructure track: Kubernetes manifests, Terraform and Ansible on Azure, and self-hosted monitoring for staging

Status: proposed, 2026-10-24. Accepted when the maintainer merges it.

## Context
KamiKon is the instructor's reference repository for the Advanced DevOps course (`docs/teaching/COURSE_ALIGNMENT.md`). The course expects one cumulative repository. In it, students write Kubernetes manifests in Week 3, Terraform for an Azure VM in Week 4 with Ansible to configure that VM, security scans in Week 5, and monitoring with a CD workflow in Week 6. The v1.0 scope does not include any of these:
- `06_CI_CD_AND_RELEASES.md` §7 lists staging as optional and names no tooling for it.
- Roadmap §7 reduces DO-4.3 to health endpoints and structured logs, with Prometheus and Grafana moved to post-v1.
- Risk R-12 treats a return to extra infrastructure as scope creep.

The reference repository has to show each week's deliverable, or students cannot compare their work with it.

## Decision
- The repository gains three top-level directories: `k8s/`, `terraform/` and `ansible/`. The names match the paths the course asks students to use. They are a teaching and staging track, not a supported deployment method. Deployers still follow the deployment guide planned for M5, which uses Docker Compose.
- `k8s/` holds manifests for a local cluster (kind or minikube) only. The project does not run a hosted Kubernetes cluster.
- `terraform/` provisions one staging VM on Azure (resource group, virtual network, subnet, network security group, public IP, VM). State lives in an Azure Storage backend, never in the repository. `ansible/` configures that VM and deploys the Compose stack to it.
- Staging holds synthetic data only, with sign-up disabled, as ADR-0010 requires. Visitors' IP addresses are still personal data, so the reverse proxy and the application do not log client IP addresses on staging, and logs are kept for 7 days. With both rules in place, staging stores no personal data, and an Azure region outside Rwanda is acceptable. Putting real user data on Azure needs its own ADR.
- The network security group allows SSH from one address, plus ports 80 and 443 for the site and its Let's Encrypt certificate. Monitoring on staging is self-hosted: Prometheus and Grafana run on the staging VM and are reached through an SSH tunnel, not a public port. The track adds no Azure Monitor, Application Insights or other hosted telemetry (ADR-0010, `05_DATA_PROTECTION.md`). The application exposes metrics only on a path that the reverse proxy does not publish.
- The repository stores no long-lived cloud credentials. Deployment runs Ansible over SSH, with the key in a protected GitHub environment named `staging`. If Terraform later runs from GitHub Actions, it authenticates to Azure through OpenID Connect federation, provided the course's Azure tenant allows app registrations.
- The maintainer destroys staging when nobody is using it. The Terraform code includes a budget alert on the subscription.
- This ADR amends three documents:
  - `06_CI_CD_AND_RELEASES.md` §7: `terraform/` and `ansible/` define staging.
  - Roadmap §7, row DO-4.3: Prometheus and Grafana return for staging only. The product itself adds only health endpoints, structured logs and an unpublished metrics endpoint.
  - Risk R-12: teaching infrastructure is in scope. It must not add services to the product's own runtime.

## Consequences
The repository gains infrastructure code that the maintainer must keep working and up to date, which adds load to R-03. CI gains linting for that code: `terraform fmt` and `validate`, TFLint, Checkov, ansible-lint and kubeconform. A cohort can now diff each week's teaching deliverable against a tagged reference. If the course stops using KamiKon, the maintainer can delete the three directories without touching application code.
