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


## 10. Egypt-first category and regulatory-source map — preliminary research

This section is a screening aid for product design, not a legal opinion and not a substitute for written confirmation from the competent Egyptian authorities. The directory must not infer permission to practice from a degree, job title, association membership, or self-description.

### A. Psychiatrist (طبيب نفسي)

- Treat as a medical-doctor category, not as interchangeable with a non-physician psychotherapist.
- Before publication, verify the underlying medical practice eligibility and the relevant specialty/registration status through the competent Ministry of Health and Egyptian Medical Syndicate channels, as applicable.
- The Egyptian Medical Syndicate's published registration service describes professional registration and specialist/consultant records, and lists supporting requirements for foreign qualifications. Use the official service as a starting point, then confirm the exact lookup and verification procedure directly with the Syndicate.
- Public profile must state the medical qualification and specialty accurately; do not use "psychiatrist" based only on a psychology degree.

Starting reference: https://ems.org.eg/services/registration

### B. Non-physician psychotherapist (معالج نفسي من غير الأطباء النفسيين)

- This is a distinct regulated practice route under Law 71/2009 on Care of Psychiatric Patients, as amended by Law 210/2020.
- The amended provisions establish a committee to regulate practice by non-psychiatrists and state that a non-psychiatrist may not practice psychotherapy without a Ministry of Health and Population license; the law also specifies direct supervision by a specialist physician and qualification/training conditions.
- Therefore, an academic degree, foreign credential evaluation, association membership, or psychotherapy course alone must never be presented as the required practice license.
- For directory publication, require direct confirmation of the current Ministry-issued license, validity/status, and the permitted scope, and record the official source and date checked.
- The executive regulations were amended after the 2020 law; the precise current application checklist and implementation instructions must be confirmed with the Ministry committee/technical secretariat before this category is opened for applications.

Starting legal references:
- Law 71/2009 and amendments: https://manshurat.org/node/14473
- Executive regulations, Ministerial Decree 128/2010 (status amended): https://manshurat.org/node/71205
- Ministry/SIS announcement on formation of the committee (8 Jan 2026): https://mediadr.sis.gov.eg/handle/123456789/118279
- Ministry/SIS announcement on committee meeting and licensing (10 Feb 2026): https://mediadr.sis.gov.eg/xmlui/handle/123456789/120850

### C. Psychologist / clinical psychologist (أخصائي نفسي / أخصائي نفسي إكلينيكي)

- Do not treat this title as automatically equivalent to a licensed non-physician psychotherapist.
- The 2020 amendment's psychotherapy-license route refers to specified clinical psychology academic qualifications and additional conditions, but those qualifications are not themselves the Ministry license to practice psychotherapy.
- Until category-specific legal review confirms the title, activities, and any registration requirements, profiles may describe verified academic qualifications only and must not imply independent authority to provide psychotherapy.
- Do not publish "clinical psychologist", "psychotherapist", "therapist", or equivalent treatment claims unless the title and activity have been separately verified against the current rules and relevant authorization.

### D. Counselor, life coach, trainer, researcher, and educator

- These should not be grouped under a clinical-treatment category by default.
- If included later, use separate non-clinical labels and narrowly describe educational, coaching, training, or research services.
- Do not imply diagnosis, psychotherapy, treatment, or clinical competence without the relevant authorization.
- Consider excluding these categories from the first public pilot until a reviewer-approved scope and consumer-protection wording are established.

### E. Regulatory developments to re-check before pilot

The State Information Service's media portal published Ministry of Health announcements dated 8 January 2026 about forming the committee for regulating psychotherapy by non-psychiatrists, and 10 February 2026 about a committee meeting and licenses granted to applicants. These announcements indicate active implementation activity; they do not replace checking the current law, executive regulations, official licensing records, or obtaining direct written confirmation from the Ministry.

### F. Mandatory verification record for each listed professional

For every profile, retain privately:
- category and exact approved title;
- legal/regulatory basis and competent authority;
- official source or direct authority confirmation;
- credential/license or registration identifier in restricted storage only, if genuinely necessary;
- status and expiry date, where applicable;
- date checked, reviewer, independent approver, and decision;
- permitted service scope and any restrictions;
- applicant's explicit approval of the public profile.

Public-facing profiles should show only the minimum verified summary. Do not expose license numbers, identity documents, certificates, or internal review notes by default.

### G. Gate before enabling any application intake

1. Obtain current written guidance from the Ministry of Health and Population committee/technical secretariat for non-physician psychotherapist licensing.
2. Obtain category-specific confirmation for psychiatrist and psychologist titles/registration from the relevant competent bodies.
3. Have qualified Egyptian counsel review the directory's categories, descriptions, disclaimers, advertising, and liability model.
4. Approve a reviewer checklist and a second-person approval policy.
5. Only then design a secure, private application intake flow.

No live application form or document upload should be activated before these gates are met.


## 12. Approved multi-track directory taxonomy

The Egypt directory will include four distinct tracks. These categories are not interchangeable, and a profile must never appear in a clinical-care search solely because the person is an academic, researcher, trainer, author, or speaker.

### Track 1 — Clinical and regulated practitioners
Psychiatrists, psychologists, and non-physician psychotherapists may be listed only after category-specific review of title, qualifications, applicable license/registration, current status, scope, and official verification source. The legal route for non-physician psychotherapy must be confirmed directly with the Ministry of Health and Population.

### Track 2 — Researchers and academics
Include researchers, university faculty, lecturers, and academic contributors whose qualifications and claims can be checked. Review:
- Degree, field, awarding institution, and year where relevant.
- Current or former institutional affiliation, accurately dated.
- Research interests and methods, without overstating expertise.
- Publications and research output through DOI, journal/publisher, institutional repository, ISBN, or conference records where available.
- Academic titles and appointments only when supported by institutional evidence.

This track is scientific/academic discovery, not clinical authorization. An academic title or publication record does not establish permission to provide psychotherapy or other regulated clinical services.

### Track 3 — Trainers and psychoeducation providers
Include trainers and providers of workshops, awareness sessions, educational programs, and personal-development training when their experience and program claims can be substantiated. Review:
- Training credentials and issuing organizations.
- Program outline, intended audience, learning objectives, and delivery format.
- Relevant teaching/training experience and references where appropriate.
- Clear boundaries: educational content is not diagnosis, psychotherapy, treatment, or emergency care.

Do not permit claims of diagnosing or treating mental disorders unless the person independently holds the required authorization for that activity. Do not use "therapist", "psychotherapist", or clinical titles as a marketing synonym for trainer.

### Track 4 — Authors and speakers
Include authors, public speakers, and science communicators with verifiable books, articles, talks, or educational work. Verify publisher/ISBN, journal, event, or institutional records where possible. Describe contributions factually and do not imply clinical endorsement.

### Cross-track rules
- A person may appear in multiple tracks only when each role is independently evidenced and separately approved.
- Clinical service filters must return only profiles with verified legal authorization and approved scope.
- Academic and training profiles must be excluded from clinical treatment search results unless their separate clinical credentials and authorization are verified.
- No ratings, testimonials, paid ranking, or clinical outcome claims in the first release.
- Public profile fields must be minimal, accurate, consented, and separated from restricted evidence and reviewer notes.

### Launch sequence for the four tracks
1. Define and legally review the clinical category checklist.
2. Define academic evidence and publication-quality rules.
3. Define trainer eligibility, prohibited claims, and educational disclaimer.
4. Define author/speaker evidence rules.
5. Build distinct profile labels and filters only after these rules are approved.
6. Pilot each track separately using synthetic records before inviting real applicants.
