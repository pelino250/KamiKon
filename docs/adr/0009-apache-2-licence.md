# The project is licensed under Apache License 2.0

Status: accepted, 2026-10-23 (confirmed by the maintainer).

## Context
The public repository had no licence, which legally means no one may reuse it. Options considered: Apache-2.0, AGPL-3.0 (the model used by pretix and Hi.Events, with added terms), and MIT. The project's audiences are universities, students in coursework, and self-hosting institutions.

## Decision
Apache License 2.0 for all code and documentation in the repository, unless a file states otherwise. Contributions are accepted under the same licence through the inbound-equals-outbound rule in section 5 of the licence, with a Developer Certificate of Origin sign-off on each commit (`CONTRIBUTING.md`).

## Consequences
- Anyone, including commercial hosts, may run modified versions without publishing changes. The project accepts this in exchange for easier institutional and classroom adoption.
- The explicit patent licence and patent-termination clause protect contributors and users more than MIT.
- All current runtime dependencies are under licences compatible with Apache-2.0 (`docs/02_ARCHITECTURE.md` §9). AGPL, GPL and SSPL dependencies are not allowed without an ADR (`docs/06_CI_CD_AND_RELEASES.md` §6).
- The name and any logo are not licensed by Apache-2.0 (section 6 of the licence); `GOVERNANCE.md` states the naming rule for forks.
