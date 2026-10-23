# Deployers are data controllers; the software defaults keep data on the deployer's server

Status: accepted, 2026-10-23.

## Context
Rwanda Law No. 058/2021 requires controllers and processors to register (Article 29), to store personal data in Rwanda unless their registration certificate authorises otherwise (Article 50), and to meet conditions before transferring data abroad (Article 48). The earlier roadmap planned staging on foreign cloud providers and used Sentry, Firebase and third-party email.

## Decision
- The project documents that whoever deploys KamiKon with real users is the controller (`docs/05_DATA_PROTECTION.md`).
- The software loads no third-party scripts, fonts, CDNs, analytics or error trackers by default. Anything that sends data off the server is opt-in and documented as a possible transfer.
- The project does not operate a production service. Any project-run demo uses synthetic data, has sign-up disabled, and is reset daily.
- Staging environments used by maintainers or course cohorts hold synthetic data only.

## Consequences
Some deployers will need Rwandan hosting or an authorisation, which costs more than the cheapest cloud option. The project avoids becoming a controller of data it never needed.
