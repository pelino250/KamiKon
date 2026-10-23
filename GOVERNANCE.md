# Governance

## 1. Current model

KamiKon is maintainer-led. The project lead is Pelin Mutanguha (GitHub `pelino250`), who is currently the only maintainer. The lead decides on releases, roadmap and acceptance of ADRs, after discussion in the relevant issue or pull request.

This is a known risk (R-03 in `docs/07_ROADMAP.md`): the project needs a second maintainer before v1.0.

## 2. Roles

| Role | Can | Becomes one by |
| :--- | :--- | :--- |
| Contributor | Open issues and pull requests | Contributing |
| Track lead | Review and approve PRs in the paths assigned to them in CODEOWNERS | Invitation by a maintainer after sustained, good-quality contributions in that area |
| Maintainer | Merge, triage, release, manage settings and secrets | Nomination by a maintainer, no objection from other maintainers within 7 days |

Maintainers who are inactive for 6 months are moved to emeritus status and lose write access, and can return on request.

## 3. Decisions

- Day-to-day changes: pull request review.
- Architecture: an ADR in `docs/adr/`, proposed by PR and accepted by a maintainer. With two or more maintainers, an ADR needs approval from one maintainer who did not write it.
- Disagreements are discussed in the issue. With two or more maintainers, an unresolved disagreement is decided by majority, with the project lead breaking ties.

## 4. Name and forks

The Apache License 2.0 does not grant rights to the name "KamiKon" (section 6). Forks and modified deployments may say they are "based on KamiKon", but must not call themselves KamiKon or imply they are the official project.

## 5. Security and conduct

Security reports follow `SECURITY.md`. Conduct reports follow `CODE_OF_CONDUCT.md`.

## 6. If the project stops

If no maintainer is active for 12 months, or the maintainers decide to stop, the README states the status at the top and the repository is archived on GitHub. Released versions remain available under their licence.

## 7. Changes to this document

By pull request, approved by the project lead.
