# KamiKon Delivery Board

Agile Scrum board for **KamiKon** (*Kaminuza + Connect*), an inter-university academic event discovery, RSVP and QR gate-pass platform for Rwandan campuses.

Superseded: the course weeks in `docs/teaching/COURSE_ALIGNMENT.md` replace this sprint plan. Do not rerun `setup_github_project.py`; it would recreate the Sprint milestones.

## Sprint Plan

| Sprint | Theme | Length |
| :--- | :--- | :--- |
| 0 | Inception, UI/UX Prototyping & DevOps Foundation | 2 weeks |
| 1 | Universities, Campuses & Academic Identity | 2 weeks |
| 2 | Event Publication, Access Policies & Discovery Feed | 2 weeks |
| 3 | RSVP Engine, Inter-University QR Gate Pass & Calendar Sync | 2 weeks |
| 4 | Smart Notifications, Real-Time Alerts & Background Workers | 2 weeks |
| 5 | Hardening, Load Testing & Phase 1/2 Release | 2 weeks |
| 6 | Post-v1 (ADR-0005): Flutter Mobile App & Push Notifications | 3 weeks |
| 7 | Post-v1 (ADR-0005): Component-Based SPA in React or Angular | 3 weeks |

## Columns (Status)

`Backlog` → `Ready for Sprint` → `In Progress` → `In Review (PR Open)` → `QA / Staging Verified` → `Done`

## Recommended Views (create once in the UI)

1. **Sprint Board**: Board layout grouped by *Status*, filtered with `sprint:@current`.
2. **Backlog Table**: Table layout grouped by *Sprint*, showing Track, Priority and Story Points, with *Sum* enabled on Story Points.
3. **Roadmap**: Roadmap layout using the *Sprint* iteration field, grouped by *Track*.
4. **By Track**: Board layout grouped by *Track*, for track leads and the DevOps Champion.

## Definition of Done

A card moves to **Done** only when it meets its functional acceptance criteria **and** the DevOps DoD: tests, lint and security scans pass in CI, the Docker build passes, and the change is verified on Staging.
