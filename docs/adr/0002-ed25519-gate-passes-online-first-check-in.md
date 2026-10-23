# Gate Passes are Ed25519-signed; check-in is online-first with offline reconciliation

Status: accepted, 2026-10-23. Supersedes the HMAC-SHA256 design in `design_docs/features_and_architecture.md`.

## Context
Passes must be verifiable at gates without network access, and must not be forgeable. HMAC (RFC 2104) is symmetric: verifying offline would put the minting key on every scanner phone. pretix solved the same problem with Ed25519 signatures and documents that offline signature-based scanning cannot detect a ticket used twice.

## Decision
- Each pass carries a compact binary payload (format in `docs/02_ARCHITECTURE.md` §6.1) signed with Ed25519 (RFC 8032). The private key exists only on the server; scanners receive public keys by `key_id`.
- The payload contains no personal data.
- Online scans record check-ins in the database under a unique constraint, so a second use is rejected.
- Offline scans verify the signature, time window and revocation list locally, de-duplicate per device, and upload later; cross-device duplicates are reported to the Organizer as conflicts.

## Consequences
- A pass can be admitted twice at two offline gates. This is accepted and mitigated by online-first scanning, single-device mode for strict gates, and conflict reporting.
- Revocations made after a scanner's last bundle refresh are not seen offline.
- Key rotation must keep retired public keys available until all passes signed with them expire.
- The format is versioned; changing it is a public-interface change under Semantic Versioning.
