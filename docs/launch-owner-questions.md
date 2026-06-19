# EVOMTRS owner launch questions

Purpose: answer the launch values that must be approved before the site is deployed to production. Do not paste secrets into this document. Send secret values, especially the form endpoint, through the approved GitHub secret setup path only.

Sources: `.env.example`, `docs/launch-values-approval-checklist.md`, `README.md`, `docs/github-pages-runbook.md`, and the visible `public/` templates.

## 1. Domain and public contact

1. What exact production URL should the site use, with no trailing slash?
   - User impact: canonical links, sitemap, robots.txt, social previews, and smoke checks point to this URL.
   - Historical context: older reports/example values referenced `evomtrs.hidconsult.com`; current README targets `https://evomtrs.com`. The owner must still approve the final production dispatch domain before GitHub Pages setup/dispatch.

2. Is the public business name exactly `EVOMTRS`?
   - User impact: search, structured data, page titles, and brand metadata stay consistent.

3. What monitored public email should receive customer and privacy/legal messages?
   - User impact: form follow-up, customer questions, and legal/privacy requests reach the right inbox.

4. What public phone number should the site use for calls?
   - Provide E.164 format for links, for example `+1...`, and the display format customers should see.
   - User impact: tap-to-call and visible phone copy work on mobile.

5. Should text messages use the same number as calls, or a different SMS-capable number?
   - User impact: mobile visitors text the intended line instead of a non-SMS or unmonitored number.

## 2. Location, service area, and map

1. Should the site publish a street address?
   - If yes, provide the approved public street address, city, state, and ZIP.
   - If no, provide the approved public location wording, such as city-only or service-area-only copy.
   - User impact: the site avoids exposing a private or incorrect address while keeping local information useful.

2. What URL should the Directions button open?
   - User impact: visitors are not routed to a generic city map or wrong location.

3. What map embed is approved for the home and contact pages?
   - User impact: the map does not imply a private, wrong, or unapproved location.

4. Is this service-area wording approved: Jacksonville, Ponte Vedra, Amelia Island, St. Johns, North Florida, with selective out-of-area projects?
   - User impact: customers can self-select before contacting EVOMTRS.

5. Is `$$$` the right public price-range signal?
   - User impact: expectations are set before intake.

## 3. Intake form endpoint and spam handling

1. Which approved form provider or backend should receive intake submissions?
   - Do not put the endpoint value in this document. Record it only as `[REDACTED]` in docs and handoffs.
   - Required variable name: `EVOMTRS_FORM_ENDPOINT`.
   - User impact: intake submissions reach EVOMTRS instead of failing or leaking lead data.

2. Is the endpoint ready for the current multipart form?
   - The form sends name, phone, email, vehicle details, budget range, timeline, notes, and optional photos.
   - User impact: customers do not lose leads after filling out the form.

3. What spam protection or provider controls are approved before launch?
   - User impact: EVOMTRS avoids spam floods without blocking real customers.

4. If the endpoint is not ready, should the form remain protected by call/text fallback until backend readiness is approved?
   - User impact: customers still have a reliable contact path.

## 4. Proof, founder, and customer-facing claims

1. What exact founder name and title should be public?
   - User impact: identity and leadership copy are accurate.

2. Is the founder credential claim approved exactly as written, or should it be changed or removed?
   - Current example: `5-time Amelia Island Concours champion`.
   - User impact: credibility copy stays supportable.

3. Are the A.L., M.R., and J.T. proof dossiers, locations, vehicle descriptions, and outcome claims approved for public use?
   - User impact: the site does not publish unapproved testimonials, client initials, or implied customer results.

4. Is the site approved to stay Mercedes/AMG-only in navigation, services, about copy, and footer copy?
   - User impact: inbound leads match the shop's intended specialty.

5. Can EVOMTRS commit to replying to new intake within one business day?
   - User impact: customers get an expectation the business can meet.

6. Are all visible images, proof assets, credentials, and customer-claim assets approved for launch?
   - User impact: production does not ship assets the owner may later retract.

## 5. Legal copy

1. Are the current Privacy Policy and Terms of Use approved for production as written?
   - User impact: the site avoids implying legal approval that has not happened.

2. What `EVOMTRS_LEGAL_UPDATED_DATE` should appear on the Privacy Policy and Terms of Use?
   - Use the date the final legal copy was approved.
   - User impact: legal pages stay honest and auditable.

## 6. Production dispatch approval

1. After the values above are approved and configured in GitHub variables/secrets, does the owner approve the first manual GitHub Pages workflow dispatch from `main`?
   - User impact: production deployment happens only after launch data, legal copy, form handling, and proof claims are approved.

2. Who should be available for post-deploy smoke checks and rollback decisions?
   - User impact: a bad launch can be caught and reversed quickly.

## Acceptance criteria for owner approval

Owner approval is complete only when all of the following are true:

- Final production URL, business name, email, phone, text number, location policy, map, directions link, service area, price range, founder details, legal date, and visible claims are answered in writing.
- `EVOMTRS_FORM_ENDPOINT` is approved and stored through GitHub secrets or an equivalent approved secret path. The raw value is not committed, pasted into this document, or included in Kanban handoffs.
- Intake backend readiness is confirmed for multipart submissions, or the owner explicitly approves call/text fallback until the endpoint is ready.
- Privacy Policy and Terms of Use are approved for production, with no claim that counsel reviewed them unless that is confirmed.
- Proof dossiers, founder credential wording, service-area wording, Mercedes/AMG-only positioning, images, and customer-facing claims are approved as written or replaced before launch.
- The owner or Brendan approves the first manual GitHub Pages workflow dispatch after the workflow is merged and required GitHub variables/secrets are set.

## Brendan hard gates still in effect

These actions still require Brendan approval and are not authorized by this packet alone:

- Production deploy, workflow dispatch, or traffic switch.
- GitHub repository settings, environment variable, or secret changes.
- Any raw credential, OAuth, billing, account-security, or secret handling decision.
- Legal/customer-facing commitments beyond the owner-approved wording.
- Destructive data changes or force-push/shared-history rewrites.

Until those gates are cleared, the safe default is no production dispatch and no production traffic change.
