# EVOMTRS owner launch answers and routing checklist

Purpose: capture final owner launch answers and route each answer to the correct operator task without exposing secrets, inventing approvals, or authorizing deploy/setup work.

This document is not production approval. It does not authorize GitHub settings changes, GitHub environment changes, repository variables, repository secrets, DNS/custom-domain changes, workflow dispatch, deploy, production traffic switch, or legal/customer-facing commitments.

This document is not production approval. A row marked `approved-public` or `approved-secret` means the value is ready to route to the correct future task. It does not authorize GitHub setup, secret creation, workflow dispatch, deploy, DNS changes, production traffic, or legal/customer-facing commitments.

Do not fill this checklist from examples, historical reports, generated placeholders, or prior assumptions. Leave rows `blocked` until owner/Brendan written approval exists for the exact field or decision.

## Source hierarchy

Use this order when reconciling launch answers:

1. Owner/Brendan written approval for the specific field or decision.
2. This checklist row, after an owner answer is recorded.
3. `docs/launch-owner-questions.md` for the questions that still need owner answers.
4. `docs/launch-values-approval-checklist.md` for variable/secret/legal/proof handling.
5. `docs/github-pages-runbook.md` for setup, smoke, and rollback commands after approval.
6. `.env.example` only for local preview/example values, never production approval.

Historical reports and example values are not owner approval.

## Redaction contract

Never paste raw `EVOMTRS_FORM_ENDPOINT` into this document, Kanban, docs, PR comments, chat, screenshots, logs, rendered artifacts, or routine handoffs.

Allowed wording:

```text
EVOMTRS_FORM_ENDPOINT=[REDACTED]
```

Allowed evidence:

- Provider/backend name, if owner permits.
- Multipart readiness: yes/no/unknown.
- Spam controls: confirmed/unconfirmed.
- GitHub secret name exists: yes/no, without printing the raw value.
- Non-sensitive test outcome, if owner/provider permits.

Forbidden evidence:

- Raw endpoint URL.
- Token-bearing form URL.
- API key, webhook secret, OAuth credential, provider secret, or hidden provider path.
- Screenshots/logs that reveal the endpoint.
- Customer lead payloads from test submissions.

If the raw endpoint appears in a comment/doc/log, stop routing and escalate as a secret-handling incident. Do not copy it into another artifact.

If the raw `EVOMTRS_FORM_ENDPOINT` appears in a doc, comment, PR body, screenshot, log, or rendered artifact, stop work and escalate as a secret-handling incident. Do not copy the value into another artifact while explaining the issue.

## Allowed statuses

Only these statuses are allowed:

- `approved-public`: owner answer is safe for public GitHub variable or public site copy.
- `approved-secret`: owner approved a secret value, but this document records only `[REDACTED]`; raw value moves only through approved GitHub secret setup.
- `needs-copy-change`: owner answer conflicts with current site copy/assets/claims, so launch needs a reviewed repo-change task before setup or dispatch.
- `not-ready-fallback-approved`: owner confirms the primary path is not ready, but approves an honest call/text fallback that avoids broken intake promises.
- `blocked`: answer is missing, contradictory, unapproved, secret-handling unsafe, or still behind a Brendan hard gate.

Do not use `done`, `ok`, `pending`, `approved`, `n/a`, or free-form status text.

## Routing rules

| Status/action | Route to | Rule |
|---|---|---|
| `needs-copy-change` | `dept-eng` docs/code task | Requires reviewed repo diff, local verify, and QA smoke before setup/dispatch. |
| `approved-public` GitHub value | `dept-devops` after Brendan hard gate | Configure only after explicit approval for GitHub variables/settings/environment. |
| `approved-secret` | Brendan hard gate then `dept-devops` | Configure only through approved secret path; evidence must say `EVOMTRS_FORM_ENDPOINT=[REDACTED]`. |
| QA-ready after merge/setup | `dept-qa` | Smoke rendered values, contact links, legal/proof copy, canonical URLs, and no raw secret leakage. |
| deploy/settings/DNS/legal commitment | Brendan hard gate | Do not treat product/doc approval as deploy approval. |
| missing/contradictory answer | blocked | Leave blocked with notes/contradictions. |

## Owner-answer table

| Launch group | Field / decision | Owner answer | Public vs secret | Source of truth | Operator action | Verification evidence | Status | Routing owner | Notes / contradictions |
|---|---|---|---|---|---|---|---|---|---|
| Domain | `EVOMTRS_SITE_URL`, no trailing slash |  | public-variable | owner written answer | configure GitHub variable after hard gate clears | variable name exists in approved scope; smoke `SITE` matches owner URL | blocked | Brendan hard gate then dept-devops | Resolve final production URL before dispatch. |
| Contact | `EVOMTRS_BUSINESS_NAME` |  | public-variable/public-copy | owner written answer | configure variable or create copy-change task | rendered brand/search metadata match approved name | blocked | dept-devops or dept-eng | Do not infer from examples. |
| Contact | `EVOMTRS_CONTACT_EMAIL` |  | public-variable | owner written answer | configure variable | rendered `mailto:` and legal/privacy contact use monitored inbox | blocked | dept-devops | Must be monitored. |
| Contact | `EVOMTRS_CONTACT_PHONE_E164` and `EVOMTRS_CONTACT_PHONE_DISPLAY` |  | public-variable | owner written answer | configure variables | rendered phone and `tel:` links match approved number | blocked | dept-devops | E.164 for link, display for humans. |
| SMS | `EVOMTRS_TEXT_PHONE_E164` or remove/reword SMS CTAs |  | public-variable/public-copy | owner written answer | configure variable or create reviewed copy-change task | `sms:` links work, or site no longer promises texting | blocked | dept-devops or dept-eng | If SMS is not monitored, route to copy-change task. |
| Location/map | Street address publish policy |  | public-variable/public-copy | owner written answer | configure address variables or create copy-change task | home/contact/footer/structured data reflect approved policy | blocked | dept-devops or dept-eng | Do not expose private/wrong address. |
| Location/map | `EVOMTRS_DIRECTIONS_URL` |  | public-variable | owner written answer | configure variable or remove/reword CTA | directions link targets approved public destination | blocked | dept-devops or dept-eng | Generic city map is acceptable only if owner approves. |
| Location/map | `EVOMTRS_MAP_EMBED_URL` |  | public-variable/public-copy | owner written answer | configure variable or create map removal/reword task | map embed matches approved policy | blocked | dept-devops or dept-eng | Must not imply a private or wrong location. |
| Location/map | Service area and `EVOMTRS_PRICE_RANGE` |  | public-copy/public-variable | owner written answer | configure variable or create copy-change task | rendered copy and structured data match owner wording | blocked | dept-devops or dept-eng | Includes Jacksonville, Ponte Vedra, Amelia Island, St. Johns, North Florida, selective out-of-area only if owner approves. |
| Form | Provider/backend name |  | approval-action | owner written answer | record provider readiness, no raw endpoint | provider name and readiness notes recorded without secrets | blocked | dept-product | Provider name may be public unless owner says otherwise. |
| Form | `EVOMTRS_FORM_ENDPOINT` | `[REDACTED]` | secret | approved GitHub secret setup only | configure secret only after hard gate clears | secret name exists; evidence says `EVOMTRS_FORM_ENDPOINT=[REDACTED]`; no raw value printed | blocked | Brendan hard gate then dept-devops | Raw endpoint is excluded from Kanban/docs/comments. |
| Form | Multipart readiness and spam controls |  | approval-action | provider/owner confirmation | route to setup if ready, fallback if not ready | non-sensitive test outcome if permitted; no customer lead data | blocked | dept-product then dept-devops/QA | Current form sends name, phone, email, vehicle, budget, timeline, notes, optional photos. |
| Form | Fallback policy if endpoint is not ready |  | public-copy/approval-action | owner written answer | create fallback copy task or approve current call/text fallback | site does not promise broken form intake | blocked | dept-eng then dept-qa | Use `not-ready-fallback-approved` only with explicit owner approval. |
| Legal | Privacy Policy approval |  | public-copy/approval-action | owner/legal written answer | create reviewed legal copy task if edits needed | `/privacy-policy/` renders approved copy/date | blocked | Brendan hard gate if legal commitment, otherwise dept-eng for copy edits | Do not imply counsel review unless confirmed. |
| Legal | Terms of Use approval |  | public-copy/approval-action | owner/legal written answer | create reviewed legal copy task if edits needed | `/terms-of-use/` renders approved copy/date | blocked | Brendan hard gate if legal commitment, otherwise dept-eng for copy edits | Do not imply counsel review unless confirmed. |
| Legal | `EVOMTRS_LEGAL_UPDATED_DATE` |  | public-variable | owner/legal written answer | configure variable | legal pages render actual approval date | blocked | dept-devops | Must be approval date, not arbitrary build date. |
| Proof/claims | Founder name, role, credential |  | public-variable/public-copy | owner written answer | configure variables or create copy-change task | About/home/meta render only approved identity and credential | blocked | dept-devops or dept-eng | Unsupported credential routes to copy-change. |
| Proof/claims | A.L., M.R., J.T. proof dossiers and visible assets |  | public-copy/approval-action | owner written answer | keep, change, or remove through reviewed repo task | proof/testimonial pages contain only approved claims/assets | blocked | dept-eng then dept-qa | No unapproved customer initials/outcomes. |
| Proof/claims | Mercedes/AMG-only positioning |  | public-copy | owner written answer | keep or create reviewed copy-change task | nav/services/about/footer match approved positioning | blocked | dept-eng then dept-qa | Customer-facing positioning, do not infer. |
| Proof/claims | One-business-day response promise |  | public-copy | owner written answer | keep or create reviewed copy-change task | contact/home copy matches operational commitment | blocked | dept-eng then dept-qa | If not supportable, remove/reword before launch. |
| Dispatch | First manual GitHub Pages dispatch from `main` |  | approval-action | explicit owner/Brendan approval after setup | dispatch only after variables/secrets/settings are configured and approved | workflow name, branch, run ID, dispatch time, result, smoke results | blocked | Brendan hard gate then dept-devops | Product value approval is not deploy approval. |
| Rollback | Smoke owner, rollback owner, launch-window contact path |  | ops-contact/approval-action | owner written answer | record owner availability before dispatch | smoke owner, rollback owner, availability window, run ID, outcome | blocked | Brendan hard gate then dept-devops/QA | DNS/CNAME/custom domain rollback changes require approval. |

## Verification before any implementation PR is ready for review

```bash
git status --short --branch
npm run --silent verify
python3 -m py_compile scripts/render_site.py scripts/verify_static.py
git diff --check
endpoint_name="EVOMTRS_FORM_ENDPOINT"
grep -RIn "${endpoint_name}=.*http\|${endpoint_name}=.*://" README.md docs .env.example public scripts package.json || true
grep -RIn "\[REDACTED\]" docs/owner-launch-answers-routing-checklist.md
grep -RIn "approved-public\|approved-secret\|needs-copy-change\|not-ready-fallback-approved\|blocked" docs/owner-launch-answers-routing-checklist.md
```

Expected:

- Static verification passes.
- Python compile passes.
- Diff check passes.
- No raw `EVOMTRS_FORM_ENDPOINT` URL or token appears in committed docs/code.
- New checklist contains the redaction contract, all required columns, and only approved statuses.

## Future review requirement

Before merge or ship readiness, route the implementation PR through `review` and QA. A docs-only PR is not production approval and must not authorize setup, dispatch, deploy, DNS, or legal/customer-facing claims.
