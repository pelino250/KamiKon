# Security Policy

## 1. Supported versions

KamiKon has not made a release. Once releases exist: the latest minor release receives security fixes, and the previous minor release receives them for three months after a new minor release.

| Version | Supported |
| :--- | :--- |
| `main` branch (pre-release) | Fixes land here |

## 2. Reporting a vulnerability

Do not open a public issue, discussion or pull request for a vulnerability.

Report privately by either:
1. GitHub private vulnerability reporting: the "Report a vulnerability" button under the repository's Security tab, or
2. Email to **pelmut2000@gmail.com** with "KamiKon security" in the subject.

Include the affected version or commit, steps to reproduce, the impact you expect, and whether the issue is already public.

## 3. What to expect

| Step | Target |
| :--- | :--- |
| Acknowledgement | 3 working days |
| Initial assessment and severity | 10 working days |
| Fix or mitigation for high and critical issues | 30 days, or a published timeline if longer |
| Public advisory | When a fix is available, through a GitHub security advisory with a CVE where applicable |

Reporters are credited in the advisory unless they ask not to be. The project does not run a bug bounty.

## 4. Scope

In scope: code in this repository, the release container images, and the documented default configuration.

Out of scope: deployments run by third parties (report to the operator), social engineering, denial-of-service testing against any deployment, and findings that need a compromised device or server.

Please do not test against deployments you do not own, and do not access other people's data. Good-faith research that follows this policy will not be pursued by the project.

## 5. Gate Pass signing key compromise (for deployers)

If a deployment's pass signing private key may have been exposed:
1. Generate a new key: `manage.py passkey generate`, then `manage.py passkey activate KEY_ID`.
2. Mark the old key compromised: `manage.py passkey compromise OLD_KEY_ID`. This revokes every pass signed with it and queues re-issuance and attendee notification.
3. Ask Gate Staff to refresh scanner bundles before the next Event; scanners reject the compromised key after refresh.
4. Treat it as a security incident under `docs/05_DATA_PROTECTION.md` §6 if personal data may also be affected.

These commands are specified in `docs/02_ARCHITECTURE.md` §6.2 and are implemented in milestone M3.

## 6. Security design

See `docs/04_THREAT_MODEL.md`.
