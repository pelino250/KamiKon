# Sprint Playbook for Course Cohorts

This playbook applies to students working on KamiKon as part of a course. The Advanced DevOps course does not use it: there KamiKon is the instructor's reference repository, planned in `COURSE_ALIGNMENT.md`. Everyone else follows `CONTRIBUTING.md` only. Where the two differ, `CONTRIBUTING.md` governs what is merged into the main repository; this playbook governs how a cohort organises its work.

## 1. Cadence

Agile Scrum with 2-week sprints. Each sprint takes items from one milestone in `docs/07_ROADMAP.md`. A suggested mapping for a 12-week term:

| Sprint | Milestone items |
| :--- | :--- |
| 0 | M0-2 to M0-5, design review with the maintainer against NFR-03 |
| 1 | M1-1 to M1-4 |
| 2 | M1-5 to M1-8, M2-1 |
| 3 | M2-2 to M2-6 |
| 4 | M3-1 to M3-3 |
| 5 | M3-4 to M3-6, M4 |

Hardening (M5) and post-v1 tracks (Flutter, SPA) are suitable for a following term.

## 2. Board

Work is tracked on the KamiKon Delivery Board (GitHub Projects). It was first generated from `scripts/sprint_backlog.json` by `scripts/setup_github_project.py`; do not rerun them (`COURSE_ALIGNMENT.md` §4).

| Field | Values |
| :--- | :--- |
| Status | Backlog, Ready for Sprint, In Progress, In Review (PR Open), QA / Staging Verified, Done |
| Track | Backend (Django/API), Frontend (UI/UX), DevOps & Infra |
| Priority | P0 - Critical, P1 - High, P2 - Medium, P3 - Nice to Have |
| Story Points | 1, 2, 3, 5, 8 (split anything larger than 8) |
| Sprint | Iteration field |

Issue titles keep an ID prefix: `[US-<sprint>.<n>]` for user stories and `[DO-<sprint>.<n>]` for DevOps tasks.

## 3. Cohort definition of done

On top of the checks in `CONTRIBUTING.md`, a cohort item is done when the change is verified on the cohort's staging environment. Staging holds synthetic data only (`docs/05_DATA_PROTECTION.md`, ADR-0010).

## 4. DevOps Champion

Each sprint one student is the DevOps Champion: they own pipeline health for that sprint, review every `type:devops` pull request, and demonstrate the sprint's DevOps deliverable at the review. Rotate so every student practises both web development and DevOps.

## 5. Reviews

Student track leads are listed in `.github/CODEOWNERS` for their paths during the term, so the maintainer is not the only reviewer (R-16). A pull request from a cohort needs one review from a track lead and one from a maintainer before merging into `main`.

## 6. Open question

Whether cohorts work in this repository or in forks is not decided (Q-08). Until it is, cohorts open pull requests from branches in forks.
