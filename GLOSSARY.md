# KamiKon

KamiKon connects Rwandan universities, partner hubs and the wider academic community through events they can discover and attend.

## Language

### Institutions

**University**:
A higher-learning institution, identified by one or more email domains.
_Avoid_: School, college

**Campus**:
A physical site belonging to exactly one University.
_Avoid_: Branch, location

**Hub**:
A non-university partner organisation that hosts Events, such as an innovation space.
_Avoid_: Partner, organisation

### Events

**Event**:
A scheduled academic gathering with a Host, an Access Policy and a Delivery Mode.
_Avoid_: Activity, session

**Host**:
The Campus or Hub an Event belongs to. A club or department is only an organizer's label, never a Host.
_Avoid_: Organizer (a person, not the Host), venue

**Access Policy**:
The rule saying who may attend an Event: public community, open to all universities, institution only, or campus only. Values: `PUBLIC_COMMUNITY`, `OPEN_ALL_UNIVERSITIES`, `INSTITUTION_ONLY`, `CAMPUS_ONLY`. Hub-hosted Events may use only the first two.
_Avoid_: Access Scope, access tier, visibility

**Delivery Mode**:
How an Event is attended: in-person, online or hybrid (`IN_PERSON`, `ONLINE`, `HYBRID`). Independent of Access Policy.
_Avoid_: Format, type

**Seat Pool**:
One of three capacities on an Event: host members (`HOST_MEMBERS`), visiting members (`VISITING_MEMBERS`) and community guests (`COMMUNITY_GUESTS`). Event capacity is their sum. Each pool has its own waitlist.
_Avoid_: Quota, quota bucket, tier

### Attendance

**Registration**:
A person's claim to a seat at an Event: confirmed, waitlisted or cancelled.
_Avoid_: RSVP (fine in UI copy, not in code or specs), booking, ticket

**Gate Pass**:
The signed code issued for a confirmed Registration to an in-person or hybrid Event, shown as a QR code with a human-readable pass code.
_Avoid_: Ticket, QR ticket, visitor pass

**Check-in**:
The record of a Gate Pass being scanned at the gate, with its result.
_Avoid_: Attendance, scan (a scan is the act; the check-in is the record)

### People

**Affiliation**:
A link between a user and a University, verified by proof of control of an institutional mailbox, with an expiry date.
_Avoid_: Badge (UI only), membership

**Verified Member**:
A user holding a verified, unexpired Affiliation with a University.
_Avoid_: Student (not everyone verified is one), affiliated user

**Community Guest**:
A user without a verified, unexpired Affiliation, such as alumni or industry professionals.
_Avoid_: Public user, external user, non-affiliated user

**Organizer**:
A user permitted to submit Events for a Host.
_Avoid_: Host, creator

**Approver**:
A user permitted to approve or reject pending Events for a Host. An Approver's own Events for that Host are approved immediately and recorded in the audit log.
_Avoid_: Moderator, admin, reviewer

**Gate Staff**:
A user permitted to scan Gate Passes for a Host's Events.
_Avoid_: Security, scanner (the scanner is the app), bouncer

**Platform Admin**:
The operator of a deployment, who registers Universities, Campuses, Hubs and email domains and assigns Host roles.
_Avoid_: SuperAdmin, moderator
