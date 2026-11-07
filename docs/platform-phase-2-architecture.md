# Phase 2 — Egypt-first professional directory plan

Status: approved product direction; planning and static-site preparation only. No backend, authentication, database, application intake, file upload, or public submission endpoint is implemented.

## 1. Approved launch scope

- Geography: Egypt only for the first directory release.
- Product: a verified professional directory only.
- Not part of this release: member accounts, journals, community, public comments, peer messaging, appointment booking, payments, or crisis chat.
- The existing public website remains static and content-first.
- The public directory remains in a clearly labeled preparation state until verification, consent, legal/privacy review, and operational ownership are in place.

A future expansion to other countries requires a separate jurisdiction review and explicit product decision. Do not reuse Egypt verification rules as a proxy for another country.

## 2. Directory audience and professional categories

The directory may consider mental-health professionals whose professional activity is within Egypt. Do not assume a single credential or licensing pathway applies to every category.

Before accepting a category, document:
- The exact professional title the person is legally permitted to use.
- The competent regulator, registration body, or official verification source for that category.
- Whether a license, registration, authorization, or other legal condition is required for the activity claimed.
- Whether the person's current status and any relevant restrictions can be checked through an official source.
- The services and claims that fall within the person's permitted scope.

Do not treat an academic degree, foreign credential evaluation, training certificate, membership in a private association, or self-description as proof of legal authorization to practice. Where requirements are unclear or cannot be independently verified, do not publish a practice claim; refer the case for qualified legal/regulatory review.

## 3. Public profile fields — minimum necessary

Potential public fields, only after approval and explicit consent:
- Professional display name.
- Approved professional title.
- City/governorate or service area in Egypt, if the professional chooses to publish it.
- Academic qualification, awarding institution, and field, accurately described.
- Verified registration/licensing summary and issuing body, where applicable; do not publish full license numbers by default.
- Areas of focus and languages, supported by the professional's training and experience.
- Public contact route selected by the professional.

Never publish identity-document images, private certificates, personal phone/email without consent, client/patient information, or reviewer notes. Do not display an endorsement, guarantee of outcomes, or ranking unless a separately approved and substantiated policy exists.

## 4. Verification workflow

1. Applicant reads the eligibility criteria, privacy notice, and directory limitations.
2. Initial interest captures only professional name, contact route, Egypt practice location, claimed title/category, and public verification references where available.
3. Screen whether the category and claimed title can be assessed against an identified competent authority or reliable official source.
4. Request only the evidence necessary for that category through a dedicated secure channel after the initial screen. No sensitive documents through ordinary email, chat, or public forms.
5. Reviewer records the source checked, date, category-specific criteria, outcome, limitations, and recheck date.
6. A second authorized approver reviews the decision; no self-approval and no approval by the profile owner.
7. Applicant reviews the proposed public profile and gives explicit publication consent.
8. Publish only approved public fields. Keep evidence and reviewer notes private.
9. Recheck on a defined schedule and when status expires, scope/location changes, or a credible concern is received.
10. Suspend or remove a listing when the basis for publication lapses or can no longer be substantiated; retain only the restricted audit information required by the approved retention policy.

## 5. Governance decisions still required

The product direction is approved, but the operational owners are not yet defined:
- Name a primary credential reviewer and a backup approver with appropriate competence.
- Approve category-by-category eligibility rules and official verification sources in Egypt.
- Decide who handles complaints, corrections, suspension, and appeals.
- Obtain qualified Egyptian legal/privacy review before collecting applicant evidence or publishing regulated professional claims.
- Approve privacy notice, consent language, retention/deletion schedule, and incident contact.
- Select a secure backend, authentication, and private evidence-storage provider only after due diligence.

Until these are resolved, the website must not imply that applications are being formally accepted or that credentials are being verified.

## 6. Privacy and security requirements

- Do not commit applicant data or evidence to Git, static files, public storage, analytics, or public URLs.
- Collect the minimum data necessary; avoid government identity documents and full license numbers unless specifically justified and legally reviewed.
- Encrypt data in transit and at rest; enforce least-privilege, assignment-based access.
- Require MFA for reviewers and administrators.
- Use private object storage, short-lived access links, malware scanning, and documented retention/deletion.
- Log evidence access, verification decisions, role changes, and publication approvals.
- Provide a clear privacy notice and process for access, correction, deletion, and complaints.
- Complete a threat model, authorization tests, backup/restore test, incident-response plan, and independent security review before pilot.

## 7. Delivery sequence

### Phase 2A — policy and governance
- Confirm professional categories and titles to consider in Egypt.
- Map each category to competent authorities, official verification sources, and applicable requirements.
- Appoint reviewer and independent approver.
- Complete legal/privacy review and approve applicant-facing policies.

### Phase 2B — private prototype
- Select backend/auth/storage provider after due diligence.
- Build private reviewer workflow, role-based access, evidence storage, audit trail, and publication approval.
- Use synthetic test records only. Do not load real applicant documents.

### Phase 2C — controlled pilot
- Invite a small number of professionals after policies and secure intake are ready.
- Test verification, consent, correction, expiry, suspension, deletion, and complaint handling.
- Complete security, privacy, accessibility, Arabic RTL, mobile, and desktop QA.

### Phase 2D — public Egypt directory
- Publish only verified and consented profiles.
- Make scope, limitations, and correction/reporting routes clear.
- Monitor status changes and re-verification dates.

## 8. Release gates

No public launch until:
- Egypt-specific category rules and verification sources are documented.
- Reviewer and independent approver are appointed.
- Qualified legal/privacy review is complete.
- Secure intake and private evidence storage are implemented and tested.
- Every public professional claim has a recorded verification basis and date.
- Explicit publication consent is recorded.
- Complaints, corrections, suspension, expiry, deletion, and incident procedures are operational.
- No sensitive data is exposed in Git or public assets.
- Arabic RTL, accessibility, mobile, and desktop QA is signed off.

## 9. Explicitly out of scope

No member accounts, therapy journals, symptom histories, clinical records, diagnosis, automated treatment recommendations, emergency chat, community forums, comments, direct messaging, or appointment/payment flows in this launch.

These require separate product approval and additional privacy, legal, security, moderation, and safety review.
