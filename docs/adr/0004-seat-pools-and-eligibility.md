# Three Seat Pools per Event; eligibility rules per Access Policy; self-declared campus

Status: accepted, 2026-10-23. Builds on ADR-0001.

## Context
Earlier documents disagreed on the number of quotas (two in the data model, three in the text) and kept a total capacity that could disagree with them. An email domain identifies a University but not a Campus, so `CAMPUS_ONLY` cannot be enforced from email alone. A Hub has no members, so institution and campus policies do not apply to Hub-hosted Events.

## Decision
- Every Event has three Seat Pools: `HOST_MEMBERS`, `VISITING_MEMBERS` and `COMMUNITY_GUESTS`. Event capacity is their sum and is not stored. Each pool has its own waitlist.
- Eligibility and pool assignment follow the table in `docs/02_ARCHITECTURE.md` §5.1.
- Hub-hosted Events may use only `PUBLIC_COMMUNITY` or `OPEN_ALL_UNIVERSITIES`, and their `HOST_MEMBERS` pool is 0.
- A member's home Campus is self-declared, changeable once every 90 days, and revocable by an Approver of that Campus.
- Allocation locks the pool row (`select_for_update()`), with a check constraint as backstop.

## Consequences
`CAMPUS_ONLY` is a softer restriction than `INSTITUTION_ONLY`, and the Organizer UI says so. Organizers set three numbers instead of one total. A deployment that needs different rules can replace the policy class (`KAMIKON_ELIGIBILITY_POLICY`).
