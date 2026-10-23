# Integer primary keys inside the database; UUIDv7 public identifiers outside

Status: accepted, 2026-10-23.

## Context
The earlier data model used UUID primary keys everywhere; the only existing migration uses `BigAutoField`. Sequential integers in URLs allow enumeration of users, registrations and passes. UUID primary keys on every table make joins and indexes larger. No production data exists yet, so either choice is cheap now and expensive later.

## Decision
- Every table keeps a `BigAutoField` primary key for internal use.
- Rows exposed in URLs or the API carry `public_id`, a UUIDv7 generated with Python's `uuid.uuid7()` (available from Python 3.14), unique and indexed.
- Gate Pass identifiers inside QR codes use random UUIDv4 (`pass_id`), so their creation time is not revealed.
- APIs, templates and logs never expose integer keys.

## Consequences
Views look objects up by `public_id`. UUIDv7 values reveal creation time to the millisecond, which is acceptable for Events and Registrations but not for passes, hence the exception.
