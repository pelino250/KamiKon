# KamiKon does not collect government identification numbers

Status: accepted, 2026-10-23. Withdraws the National ID and passport digit fields in `design_docs/design.md`, `design_v2.md`, `design_v3.md` §5.4 and §7.2, and the related Stitch prompts.

## Context
Earlier designs collected the last four digits of a National ID or passport, first at sign-up and later at the first registration for a gated Event. The platform cannot verify the digits. A guard who wants to check identity must look at the physical document, which shows the holder's name. Storing the digits still creates personal data to secure, disclose, retain and delete under Rwanda Law No. 058/2021.

## Decision
- No government identifier, in whole or in part, is collected or stored.
- Hosts mark Events `id_check_at_gate`. Registering for such an Event requires the attendee's name as it appears on their ID, with a disclosure shown before submission.
- Gate rosters list name, affiliation and pass code. Gate Staff compare the name with the physical document.

## Consequences
Identity assurance at the gate rests on the guard's check of the physical ID, as it would with the digits. If a partner institution has a written rule that requires recording an identifier, that requirement is analysed in a new ADR before any field is added.
