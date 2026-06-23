# EVOMTRS launch-state smoke matrix

Purpose: map every owner-answer row to local, non-live evidence before any production setup or dispatch work. This matrix is post-owner-answer evidence only. It does not authorize GitHub settings, GitHub variables, GitHub secrets, DNS/custom-domain changes, legal/customer-facing commitments, workflow dispatch, deploy, or production traffic.

Run from repo root after rendering with owner-approved values or synthetic non-secret local examples:

```bash
npm run --silent verify:launch-local
```

For a local ignored `.env.local` preview, use the direct commands instead:

```bash
git check-ignore -q .env.local
python3 scripts/render_site.py public /tmp/evomtrs-local-render --env-file .env.local
python3 scripts/verify_static.py /tmp/evomtrs-local-render --env-file .env.local
python3 scripts/verify_launch_values.py /tmp/evomtrs-local-render --env-file .env.local
```

`EVOMTRS_FORM_ENDPOINT` is secret-handled. Evidence may say only `EVOMTRS_FORM_ENDPOINT=[REDACTED]`, `EVOMTRS_FORM_ENDPOINT=[REPLACE_WITH_FORM_ENDPOINT]`, or the GitHub secret name. Do not paste the raw endpoint into docs, logs, screenshots, Kanban comments, PR bodies, or routine handoffs.

Local green means only: the rendered site is internally consistent with the values used for the render. It does not mean the values are owner-approved, configured in GitHub, legally approved, or safe to deploy.

## Matrix

| # | Owner-answer row | Rendered evidence | Command or browser action | Pass criteria | Redaction / blocked notes | Next owner if failed |
|---|---|---|---|---|---|---|
| 1 | Domain: `EVOMTRS_SITE_URL`, no trailing slash | Canonical links, Open Graph URLs, `sitemap.xml`, `robots.txt` | `python3 scripts/verify_launch_values.py /tmp/evomtrs-local-render --env-file .env.local`; optional browser view-source on home and required routes | Canonical, sitemap, and robots all use the approved URL with no trailing slash drift | Final production URL and first dispatch remain Brendan hard gates | Brendan hard gate then dept-devops |
| 2 | Contact: `EVOMTRS_BUSINESS_NAME` | Homepage local-business structured data and brand metadata | Script output row `Contact: EVOMTRS_BUSINESS_NAME`; browser inspect home metadata | Rendered structured data name matches owner-approved business name | Do not infer from examples or historical reports | dept-devops or dept-eng |
| 3 | Contact: `EVOMTRS_CONTACT_EMAIL` | `mailto:` links, privacy contact, terms contact | Script output row `Contact: EVOMTRS_CONTACT_EMAIL`; browser click/copy email links on contact/legal pages | Visible links and legal contact routes use the monitored owner-approved inbox | Email must be monitored before launch | dept-devops |
| 4 | Contact: `EVOMTRS_CONTACT_PHONE_E164` and `EVOMTRS_CONTACT_PHONE_DISPLAY` | Visible phone copy, `tel:` links, structured-data telephone when not placeholder | Script output row `Contact: EVOMTRS_CONTACT_PHONE_E164 / DISPLAY`; mobile/browser click call CTAs | Approved phone renders with matching `tel:` link, or placeholder preview renders honest pending-phone fallback | Placeholder `.env.example` must remain preview-only and not be treated as approval | dept-devops |
| 5 | SMS: `EVOMTRS_TEXT_PHONE_E164` or remove/reword SMS CTAs | Mobile quick-action `sms:` links or pending-phone fallback | Script output row `SMS: EVOMTRS_TEXT_PHONE_E164`; mobile/browser inspect quick actions | SMS CTA points to approved SMS-capable number, or site no longer promises texting | If SMS is not monitored, route a copy-change task before setup/dispatch | dept-devops or dept-eng |
| 6 | Location/map: street address publish policy | Header/footer/contact address, home service-area block, structured local-business address | Script output row `Location/map: street address publish policy`; browser inspect home/contact/footer | Approved public street/ZIP render, or owner-approved city/service-area fallback renders without private address | Do not expose private, placeholder, or wrong street address | dept-devops or dept-eng |
| 7 | Location/map: `EVOMTRS_DIRECTIONS_URL` | Directions CTAs on home/contact/mobile quick actions | Script output row `Location/map: EVOMTRS_DIRECTIONS_URL`; browser open directions in new tab | Directions link targets the owner-approved public destination | Generic city maps are acceptable only if owner explicitly approves that policy | dept-devops or dept-eng |
| 8 | Location/map: `EVOMTRS_MAP_EMBED_URL` | Home and contact map iframe `src` | Script output row `Location/map: EVOMTRS_MAP_EMBED_URL`; browser inspect map iframe on home/contact | Map embed matches approved location policy and loads without implying a private/wrong location | If no public location is approved, remove/reword map through reviewed repo task | dept-devops or dept-eng |
| 9 | Location/map: service area and `EVOMTRS_PRICE_RANGE` | Visible service-area copy and structured-data price range | Script output row `Location/map: service area and EVOMTRS_PRICE_RANGE`; browser inspect home/contact/service area | Rendered copy and structured data match owner-approved service area and price signal | Jacksonville/Ponte Vedra/Amelia Island/St. Johns/North Florida wording is customer-facing and needs approval | dept-devops or dept-eng |
| 10 | Form: provider/backend name | Owner-answer checklist provider/readiness notes, not public render | Checklist review plus script row `Form: provider/backend name` | Provider/backend readiness is recorded without secrets | Provider may be public only if owner permits. Raw endpoint stays out of docs | dept-product |
| 11 | Form: `EVOMTRS_FORM_ENDPOINT` | Contact form `action`, redacted script evidence | `python3 scripts/verify_launch_values.py ...`; inspect only whether action exists, not the raw value in shared evidence | Placeholder renders `[REPLACE_WITH_FORM_ENDPOINT]`, or approved secret render is reported only as `EVOMTRS_FORM_ENDPOINT=[REDACTED]`; raw value is not printed by the script | Stop and escalate if the raw endpoint appears in docs, logs, screenshots, Kanban, PR body, or rendered artifacts shared as evidence | Brendan hard gate then dept-devops |
| 12 | Form: multipart readiness and spam controls | Contact form `enctype="multipart/form-data"`, fields, optional photos | Script output row `Form: multipart readiness and spam controls`; browser inspect form fields | Form shape matches provider readiness confirmation for name, phone, email, vehicle, budget, timeline, notes, optional photos | Do not submit real customer lead data. Non-sensitive test submission only if owner/provider permits | dept-product then dept-devops/QA |
| 13 | Form: fallback policy if endpoint is not ready | Non-live intake notice, pending help text, call fallback | Script output row `Form: fallback policy if endpoint is not ready`; browser inspect contact page | Placeholder endpoint shows honest non-live/fallback copy; approved endpoint shows live-intake copy only after readiness approval | Use `not-ready-fallback-approved` only with explicit owner approval | dept-eng then dept-qa |
| 14 | Legal: Privacy Policy approval | `/privacy-policy/` title, copy, contact, updated date | Script output row `Legal: Privacy Policy approval`; browser read privacy page | Privacy page renders approved copy/date and monitored contact email | Do not imply counsel/legal approval unless confirmed | Brendan hard gate if legal commitment, otherwise dept-eng for copy edits |
| 15 | Legal: Terms of Use approval | `/terms-of-use/` title, copy, contact, updated date | Script output row `Legal: Terms of Use approval`; browser read terms page | Terms page renders approved copy/date and monitored contact email | Do not imply counsel/legal approval unless confirmed | Brendan hard gate if legal commitment, otherwise dept-eng for copy edits |
| 16 | Legal: `EVOMTRS_LEGAL_UPDATED_DATE` | `Last updated:` on privacy and terms pages | Script output row `Legal: EVOMTRS_LEGAL_UPDATED_DATE`; browser inspect both legal pages | Both legal pages show the owner/legal approval date, not an arbitrary build date | Date is public and must come from owner/legal approval | dept-devops |
| 17 | Proof/claims: founder name, role, credential | Home founder section, About page, metadata, credibility strip | Script output row `Proof/claims: founder name, role, credential`; browser inspect home/about | Only owner-approved identity/title/credential wording renders | Unsupported credential routes to reviewed copy-change task | dept-devops or dept-eng |
| 18 | Proof/claims: A.L., M.R., J.T. proof dossiers and visible assets | Home proof section and `/testimonials/` owner outcome dossiers | Script output row `Proof/claims: A.L., M.R., J.T. dossiers/assets`; browser inspect proof page and visible assets | Dossiers, locations, vehicles, results, and assets are approved or removed/reworded before launch | No unapproved customer initials, outcomes, screenshots, or assets | dept-eng then dept-qa |
| 19 | Proof/claims: Mercedes/AMG-only positioning | Nav, services, about, footer, FAQ, structured copy | Script output row `Proof/claims: Mercedes/AMG-only positioning`; browser scan required routes | Customer-facing positioning matches owner-approved specialty | If positioning changes, route reviewed copy-change task before setup/dispatch | dept-eng then dept-qa |
| 20 | Proof/claims: one-business-day response promise | Contact page metadata/copy and home response card | Script output row `Proof/claims: one-business-day response promise`; browser inspect home/contact | Promise remains only if owner confirms operations can support it | If not supportable, remove/reword through reviewed copy-change task | dept-eng then dept-qa |
| 21 | Dispatch: first manual GitHub Pages dispatch from `main` | No local rendered evidence. Workflow/run evidence only after explicit approval | Confirm row remains blocked in checklist. Do not run `gh workflow run` as part of this matrix | Before dispatch, settings/variables/secrets are configured and owner/Brendan approval exists; after dispatch, capture workflow name, branch, run ID, time, result, smoke | This matrix never authorizes workflow dispatch, deploy, or production traffic | Brendan hard gate then dept-devops |
| 22 | Rollback: smoke owner, rollback owner, launch-window contact path | Checklist/runbook ownership notes, not public render | Confirm owner availability is recorded before any approved dispatch | Smoke owner, rollback owner, launch window, and contact path are known before production action | DNS/CNAME/custom-domain rollback changes require approval | Brendan hard gate then dept-devops/QA |

## Required local verification before review

```bash
npm run --silent verify
python3 -m py_compile scripts/render_site.py scripts/verify_static.py scripts/verify_launch_values.py
git diff --check
```

Expected:

- Static verification still passes.
- Launch-value verification reports 22 rows and keeps hard gates visible.
- Python compile passes for all scripts.
- Diff check passes.
- No raw `EVOMTRS_FORM_ENDPOINT` appears in output. Evidence says only `EVOMTRS_FORM_ENDPOINT=[REDACTED]`, `EVOMTRS_FORM_ENDPOINT=[REPLACE_WITH_FORM_ENDPOINT]`, or a secret-name-only statement.
