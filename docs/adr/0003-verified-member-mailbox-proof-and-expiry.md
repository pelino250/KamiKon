# Verified Member requires proof of mailbox control and expires after 12 months

Status: accepted, 2026-10-23.

## Context
The earlier design granted a university badge when an email address matched a registered domain. A match shows only what the user typed. Graduates often keep institutional addresses, and some domains are shared across campuses or institutions.

## Decision
- An Affiliation becomes `VERIFIED` only after the user enters a single-use code, or follows a link, sent to the institutional address. Codes expire after 30 minutes; at most 5 requests per hour per user.
- A `VERIFIED` Affiliation expires 12 months after verification unless re-verified; the user is reminded 30 days before.
- An institutional address can be verified for one user at a time.
- Email domains have a kind (`MEMBER`, `STAFF_ONLY`, `ALUMNI`) and must be confirmed by the institution before they produce Affiliations.

## Consequences
Members re-verify once a year. Graduates lose member eligibility within a year, not on graduation day. Institutions must confirm their domains before launch, which is a dependency on partners (Q-05).
