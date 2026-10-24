# 05: Data Protection Guide for Deployers

Status: draft for v1.0. This is engineering documentation, not legal advice. Each deployer should have its data protection officer or counsel review it. Article numbers refer to Rwanda Law No. 058/2021 of 13/10/2021 relating to the protection of personal data and privacy, read on RwandaLII (https://rwandalii.org/akn/rw/act/law/2021/58/eng@2021-10-15) on 2026-10-23. Where a statement comes from a secondary summary, it is marked "(secondary)".

## 1. Roles

- **The KamiKon project** publishes software. It does not receive or process personal data from deployments, so the project is not a controller for them.
- **A deployer** (a university, a Hub, a consortium or a company) that runs KamiKon for real users decides why and how their data is processed and is the **data controller**. A hosting company that runs the servers for the deployer is usually a **data processor**.
- **The project's own demo**, if one is run (Q-07), uses synthetic seed data only, has sign-up disabled, and is reset daily (ADR-0010). If that ever changes, whoever runs it becomes a controller and this guide applies to them.

## 2. Obligations that apply to a deployer in Rwanda

| Obligation | Article | What it means for a KamiKon deployment |
| :--- | :--- | :--- |
| Register with the supervisory authority | 29 | "A person who intends to be a data controller or a data processor must register with the supervisory authority." The National Cyber Security Authority runs registration through https://dpo.gov.rw; certificates are issued within 30 working days according to its FAQ. Register before going live. |
| Designate a data protection officer | 40 | Required where processing is carried out by a public or private corporate body or legal entity, except courts. Universities and companies are covered. |
| Store personal data in Rwanda | 50 | "The data controller or the data processor stores personal data in Rwanda." Storage outside Rwanda is permitted only with a registration certificate that authorises it. This covers the database, backups and file storage. |
| Transfers outside Rwanda | 48 | Sharing or transferring personal data to a third party outside Rwanda requires one of the conditions in Article 48, for example authorisation from the supervisory authority after showing appropriate safeguards. Foreign SMTP relays, CDNs, error trackers and analytics are transfers. |
| Security measures | 47 | Appropriate, reasonable technical measures against loss, damage or destruction. See `04_THREAT_MODEL.md`. |
| Breach notification to the authority | 43 | Within 48 hours after becoming aware of a breach. |
| Breach communication to data subjects | 45 | Where a breach is likely to result in a high risk to their rights and freedoms. |
| Children | 9 | Processing data of a child under 16 requires consent of a holder of parental responsibility. KamiKon requires users to confirm they are 16 or older (FR-11). |
| Sensitive data | 3(2°), 10 | Sensitive data includes health, biometric and genetic information, religious or philosophical beliefs, political opinion, social origin, criminal records and family details. KamiKon collects none of these. Free-text fields (organization, role label, abstracts) must not be used to collect them. |
| Information at collection, rights notice | 42 (secondary) | Tell users at collection what is collected, why, and their rights. The product shows the disclosures in `01_PRD.md` §7 and links to the deployer's privacy notice. |
| Rights: access, objection, portability, automated decisions | 18, 19, 20, 21 | Respond within 30 days; the data subject may appeal to the authority within 30 days of the response. KamiKon makes no decisions about people solely by automated processing beyond rule-based eligibility, which users can see and query. |
| Penalties | 53 (secondary) | Administrative fines for companies are reported as RWF 2,000,000 to 5,000,000 or 1 percent of the previous year's global turnover. |

The transitional period for controllers already in operation (Article 67, two years from publication) ended on 15 October 2023, according to the supervisory authority's FAQ.

Deployers outside Rwanda follow their own law. This guide has not been checked against any other law.

## 3. Data inventory

| Data | Where | Purpose | Visible to | Default retention |
| :--- | :--- | :--- | :--- | :--- |
| Email, password hash, display name | User | Account and login | The user; Platform Admin | Until account deletion |
| Institutional email, University, home Campus, member role | Affiliation | Eligibility | The user; Platform Admin; University and Campus shown to Organizers and Gate Staff of Events the user registers for | Until deletion; expired Affiliations deleted 12 months after expiry |
| Legal name | User | Name check at `id_check_at_gate` Events | Organizer and Gate Staff of those Events | Until the user clears it or deletes the account |
| Organization, role label | User | Shown on the roster | Organizers of Events the user registers for | Until removed by the user |
| Registrations with name and affiliation snapshots | Registration | Seat allocation, roster | The user; Organizers and Gate Staff of the Event | Snapshots anonymised `KAMIKON_RETENTION_DAYS` (default 90) after the Event ends |
| Check-ins | CheckIn | Single entry, attendance count | Organizers of the Event | Linked to the person until anonymisation, same schedule |
| Downloaded roster on scanner devices | IndexedDB on staff phones | Offline gate lookup | Gate Staff | Deleted 24 hours after Event end or on sign-out |
| Notifications | Notification | In-app list | The user | 180 days |
| ID photo (only if `KAMIKON_ID_REVIEW_ENABLED`) | Private storage | Manual affiliation review | Approvers of the University | Deleted on decision or after 30 days |
| Audit entries | AuditEntry | Accountability | Platform Admin | 2 years; contain public IDs, not names |
| Server logs | Hosting | Operations and security | Operators | 30 days recommended; no request bodies |

Not collected: national ID or passport numbers or digits (ADR-0008), phone numbers, dates of birth, location history, device identifiers other than the scanner's random `device_id`, photographs (except the optional ID review).

## 4. Pre-launch checklist for a deployer

1. Registration certificate obtained from the supervisory authority (Art. 29), including any authorisation for storage or transfer abroad that the deployment needs (Art. 48, 50).
2. Data protection officer designated (Art. 40) and named in the privacy notice.
3. Database, backups and uploaded files hosted in Rwanda, or covered by the authorisation in item 1.
4. SMTP relay: either in Rwanda, or covered by item 1. Record which relay is used.
5. No third-party scripts, fonts, CDNs, analytics or error trackers added, or each one covered by item 1 and listed in the privacy notice.
6. Privacy notice published and linked from the sign-up page, covering the data in §3, purposes, recipients, retention, rights and how to exercise them, and the DPO contact.
7. Retention set (`KAMIKON_RETENTION_DAYS`) and the daily retention task scheduled.
8. Backups encrypted, access-controlled, and a restore tested.
9. Breach procedure (§6) assigned to named people with a 48-hour clock.
10. Email domains in the database confirmed by each institution (Q-05, R-11).
11. Platform Admin and Approver accounts have two-factor authentication enabled.
12. Gate Staff briefed: rosters are personal data; do not photograph or forward them.

## 5. Handling data subject requests

| Request | How KamiKon supports it | Deadline |
| :--- | :--- | :--- |
| Access, portability (Art. 18, 20) | Self-service JSON export at `/account/` and `GET /api/v1/me/export/` | 30 days |
| Rectification | Profile editing; Platform Admin can correct affiliations | 30 days |
| Erasure | Self-service deletion; registrations anonymised, audit entries keep public IDs only | 30 days |
| Objection (Art. 19) | Notification preferences; digest is opt-in; account deletion | 30 days |

## 6. Breach procedure

1. Contain: revoke credentials, rotate `SECRET_KEY` (which signs out all sessions) and database passwords; if the pass signing key may be exposed, follow `SECURITY.md` §5.
2. Assess which data and which people are affected using the audit log and server logs.
3. Notify the supervisory authority within 48 hours of becoming aware (Art. 43).
4. Inform affected people where the breach is likely to result in a high risk (Art. 45).
5. Record the incident, the decision and the timeline. If the cause is a defect in KamiKon, report it privately to the project (`SECURITY.md`).

## 7. What the project does to make compliance possible

- Ships with no third-party telemetry and self-hosted static assets.
- Keeps personal data out of QR codes, logs and audit entries.
- Provides export, deletion and retention mechanisms (FR-18, FR-62).
- Uses synthetic seed data only (`manage.py seed_demo`), so development and CI never need real personal data.
- Documents every place personal data can leave the server (§3, §4).
