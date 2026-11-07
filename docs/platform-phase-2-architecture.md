# Platform Phase 2 — Architecture and Safety Plan

Status: planning specification only. No authentication, database, file upload, user journal, or public submission endpoint is implemented by this document.

## 1. Product boundaries

The current website is a static, content-first site. Keep it that way for public educational content until a separate application backend is selected and reviewed.

Planned platform capabilities:
- Public content: articles, learning paths, self-reflection tools, videos, worksheets.
- Professional directory: public profiles only after manual credential and scope-of-practice verification.
- Professional application workflow: private intake, reviewer decisions, expiry/reverification, and audit trail.
- Optional member accounts: only after a clear purpose, privacy notice, deletion/export process, and security review.
- Community features: deferred until moderation, reporting, escalation, and crisis-response operations are staffed and tested.

Not in scope for the first backend release:
- Clinical records or therapy notes.
- Emergency/crisis chat.
- Diagnosis or automated treatment recommendations.
- Public upload of identity documents or license certificates.
- Open public comments or direct messaging between users and listed professionals.

## 2. Roles and least-privilege access

| Role | Allowed access |
|---|---|
| Visitor | Public content and published directory profiles only |
| Applicant | Their own application status and non-sensitive correspondence |
| Credential reviewer | Assigned applications and verification evidence needed for review |
| Directory editor | Approved public profile fields; cannot approve their own verification |
| Platform administrator | Account and platform configuration; privileged actions logged |
| Moderator (future) | Reported community content only, not private application evidence |

Require multi-factor authentication for staff and reviewers. Separate reviewer approval from profile publication. No applicant can edit a verified status or publish their own profile.

## 3. Professional verification workflow

1. Applicant reads eligibility, privacy, and jurisdiction-specific requirements.
2. Collect only minimum initial information: professional name, contact, country/state, claimed designation, and public regulator lookup details where available.
3. Request supporting evidence only through a dedicated authenticated upload channel after the application is screened.
4. Reviewer checks issuing institution, credential, active registration/license where required, jurisdiction, restrictions/status where legally accessible, and permitted scope of practice.
5. Record source, date checked, reviewer, outcome, expiry/recheck date, and unresolved limitations.
6. A second authorized person approves publication; no self-approval.
7. Applicant reviews the proposed public profile and explicitly consents to publication.
8. Reverify on a schedule and when a credential expires, jurisdiction changes, or a credible concern is reported.
9. Suspend or remove a listing when verification lapses or the public claim can no longer be substantiated; preserve a restricted audit record according to retention policy.

A degree is not a substitute for a practice license. Titles and service claims must follow the laws and regulator rules of the location where services are offered. Do not imply that directory inclusion is an endorsement or guarantee of outcomes.

## 4. Data classification and handling

### Public
Approved display name, approved professional title, jurisdictions, verified credential summary, specialties/areas of focus as substantiated, languages, and public contact route chosen by the professional.

### Restricted
Applicant contact details, application status, reviewer notes, verification source references, and limited supporting evidence.

### Highly sensitive — avoid collecting unless legally necessary
Government identity documents, full license numbers when not needed, health information, therapy notes, payment details, and information about clients/patients.

Controls:
- Never place private evidence in Git, static site files, public object storage, analytics, or public URLs.
- Encrypt data in transit and at rest; restrict access by role and assignment.
- Use short-lived signed upload/download links and malware scanning for files.
- Keep secrets in managed secret storage, never in source code.
- Define retention and secure deletion periods before collection.
- Provide clear privacy notice, consent, access/correction/deletion request process, and incident contact.
- Minimize analytics; do not send application, account, or health-related content to advertising/analytics systems.

## 5. Security and operational requirements

Before launch:
- Threat model covering account takeover, reviewer abuse, ID/document exposure, insecure direct object references, spam, scraping, and privilege escalation.
- MFA for staff; secure passwordless or standards-based authentication for members.
- Secure session management, CSRF protection where applicable, rate limits, bot protection, input validation, output encoding, and strict authorization checks server-side.
- Audit logs for viewing/downloading evidence, verification decisions, role changes, exports, and publication.
- Backups with tested restoration; incident response and breach-notification procedure.
- Dependency scanning, secret scanning, code review, and independent security testing.
- Accessibility and Arabic RTL testing on mobile and desktop.

## 6. Suggested application architecture

Keep the current static website as the public frontend. Add a separate backend application only after selecting a provider and completing a privacy/security review.

Logical components:
- Public site/CDN: static educational pages and published directory data only.
- Authentication service: accounts, MFA, session lifecycle, staff identity.
- Application API: server-side authorization and workflow state transitions.
- Relational database: profiles, applications, verification events, roles, consent, audit metadata.
- Private object storage: encrypted evidence with strict access controls and retention lifecycle.
- Admin console: reviewer queue, decision history, publication approval, re-verification alerts.
- Notification service: minimal email notifications; never include sensitive evidence in email.

Provider selection is intentionally open. Evaluate data residency, contractual privacy terms, access controls, audit capabilities, backups, export/deletion, incident response, and total operating cost before choosing a vendor.

## 7. Delivery sequence and release gates

### Phase 2A — decisions and design
- Confirm whether the first live feature is only a verified professional directory or also member accounts.
- Define launch countries/states and applicable professional categories.
- Select backend/auth/storage providers after due diligence.
- Finalize privacy notice, terms, retention schedule, reviewer policy, and complaints process.

### Phase 2B — private reviewer prototype
- Build authentication and reviewer roles.
- Build private application records and restricted evidence storage.
- Add review queue, audit log, and approval workflow.
- Use synthetic test records only; no real applicant documents.

### Phase 2C — controlled pilot
- Security and privacy review.
- Test access controls, upload permissions, deletion, backup restoration, and incident response.
- Pilot with a small number of invited professionals and documented consent.

### Phase 2D — public directory
- Publish only approved and consented profile fields.
- Add report-a-profile route and clear limitations/disclaimer.
- Monitor expired credentials and complaints.

### Later — member accounts and community
Do not add journals, symptom histories, peer messaging, or open forums until their purpose, legal basis, privacy model, moderation staffing, safety escalation, and data retention are approved. These features can create sensitive health data and additional obligations.

## 8. Definition of done

- No sensitive evidence is publicly accessible or committed to Git.
- Server-side authorization is tested for every role and object.
- No applicant can approve or publish their own profile.
- Every public credential claim has a recorded verification source and date.
- Publication requires explicit professional consent and a separate approval.
- Retention, deletion, export, incident response, and backup restoration are tested.
- Privacy and legal review is complete for each launch jurisdiction.
- Arabic RTL, accessibility, mobile, and desktop QA is signed off.

## 9. Decisions required from the product owner

1. Initial geography: Egypt only, US states, or a limited set of countries/states?
2. First launch: professional directory only, or member accounts as well?
3. Who will serve as credential reviewer and backup approver?
4. What is the approved process for professionals to submit sensitive evidence securely?
5. Which backend/data provider is acceptable after privacy and security due diligence?

Until these decisions and release gates are complete, the public site should continue to show the directory as being prepared and should not collect sensitive applications.
