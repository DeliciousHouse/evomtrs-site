# EVOMTRS launch-values approval checklist

Purpose: collect only owner-approved launch values before production GitHub Pages deployment. This checklist does not create credentials, change secrets, dispatch workflows, or claim legal approval.

Sources inspected:
- `.env.example`
- `public/index.html`
- `public/contact/index.html`
- `public/about/index.html`
- `public/testimonials/index.html`
- `public/privacy-policy/index.html`
- `public/terms-of-use/index.html`
- `README.md`
- `FINAL_REPORT.md`
- `docs/github-pages-runbook.md`

## Recommended handling

Use public GitHub repository/environment variables for normal public site values. Use GitHub secrets for credential-like or abuse-prone values. `EVOMTRS_FORM_ENDPOINT` must be treated as a GitHub secret unless Brendan/the owner explicitly confirms the endpoint is safe to expose.

Do not deploy until all owner-value rows marked `Needs owner value` or `Needs owner approval` are answered.

## Public GitHub variables

| Value | Why it matters | Recommended handling | Owner question | User impact |
|---|---|---|---|---|
| `EVOMTRS_SITE_URL` | Drives canonical URLs, Open Graph URLs, sitemap, robots, and smoke checks. | Needs owner value. Use the final GitHub Pages/custom domain URL, with no trailing slash. Current docs disagree between `evomtrs.com` and `evomtrs.hidconsult.com`; do not guess. | What exact public production URL should the site use? | Prevents search/social previews and sitemap from pointing at the wrong domain. |
| `EVOMTRS_BUSINESS_NAME` | Appears in structured data and brand metadata. | Safe default: `EVOMTRS`, if owner confirms this is the exact public business/brand name. | Is the public business name exactly `EVOMTRS`? | Keeps brand/search listings consistent. |
| `EVOMTRS_CONTACT_EMAIL` | Used for visible email links and legal contact routes. | Needs owner value. Use a monitored inbox. | What public contact/privacy email should receive customer and legal messages? | Customers and legal/privacy requests land in the right inbox. |
| `EVOMTRS_CONTACT_PHONE_E164` | Powers `tel:` links and structured data telephone value. | Needs owner value. Use E.164 format, e.g. `+1...`; do not publish masked placeholder values. | What public call number should the site use in E.164 format? | Tap-to-call works reliably on mobile. |
| `EVOMTRS_CONTACT_PHONE_DISPLAY` | Human-readable phone number shown in header/footer/contact sections. | Needs owner value. Match the E.164 number unless owner wants a distinct display format. | How should the public call number be displayed? | Visitors can verify the number before tapping or copying it. |
| `EVOMTRS_TEXT_PHONE_E164` | Powers mobile `sms:` quick action. | Needs owner value. Can match call number if texting that line is approved. | Should texting use the same number as calls, or a different SMS-capable number? | Mobile visitors can contact EVOMTRS through the intended channel. |
| `EVOMTRS_ADDRESS_LINE1` | Used in visible address and structured local-business data. | Needs owner value or owner policy. If the street address should not be public, choose a replacement public-location policy before launch. | Should the site publish a street address? If yes, what exact line 1? If no, what location wording should replace it? | Avoids exposing an address unintentionally while keeping location info accurate. |
| `EVOMTRS_CITY` | Used in address, service area copy, and structured data. | Safe default appears to be `Jacksonville`, but owner should confirm. | Is `Jacksonville` the correct public city? | Keeps local SEO and visitor expectations aligned. |
| `EVOMTRS_STATE` | Used in address and structured data. | Safe default appears to be `FL`, but owner should confirm. | Is `FL` the correct public state? | Prevents malformed local-business metadata. |
| `EVOMTRS_ZIP` | Used in structured address and rendered full address. | Needs owner value if publishing an address. If no public address, decide whether ZIP should be removed/withheld in content before launch. | What ZIP should be published, or should ZIP be withheld with the street address? | Avoids shipping placeholder ZIP/address data. |
| `EVOMTRS_PRICE_RANGE` | Used in local-business structured data. | Safe default may remain `$$$` if owner agrees it matches positioning. | Is `$$$` the right public price-range signal? | Sets customer expectations before intake. |
| `EVOMTRS_FOUNDER_NAME` | Appears in About metadata and visible founder sections. | Needs owner approval. Current example value should not be treated as approved proof. | What exact founder name should be public? | Avoids publishing incorrect identity information. |
| `EVOMTRS_FOUNDER_ROLE` | Appears in About copy and founder hero. | Needs owner approval. | What exact founder title/role should be public? | Sets accurate expectations about who leads the shop and work. |
| `EVOMTRS_FOUNDER_CREDENTIAL` | Appears in homepage, About, meta description, and credibility strip. | Needs owner/legal proof approval. Do not publish credential claims unless owner confirms wording and support. | Is the credential claim approved exactly as written, or should it be changed/removed? | Avoids unverified customer-facing credibility claims. |
| `EVOMTRS_LEGAL_UPDATED_DATE` | Shown on Privacy Policy and Terms of Use. | Needs owner/legal approval. Use the date the final legal copy was approved, not an arbitrary build date. | What date should appear as the approved legal updated date? | Keeps legal pages honest and audit-friendly. |
| `EVOMTRS_DIRECTIONS_URL` | Powers mobile directions CTA. | Needs owner value/policy. If no public street address, link should target the approved public location or be removed/reworded. | What URL should the Directions button open? | Prevents visitors from navigating to a generic or wrong location. |
| `EVOMTRS_MAP_EMBED_URL` | Renders map iframe on homepage/contact page. | Needs owner value/policy. If no public street address, use approved city/service-area map or remove map block before launch. | What map embed URL is approved for public display? | Prevents the map from implying a wrong or private location. |

## GitHub secret

| Value | Why it matters | Recommended handling | Owner question | User impact |
|---|---|---|---|---|
| `EVOMTRS_FORM_ENDPOINT` | The contact form posts customer names, phone numbers, emails, vehicle details, budget range, timeline, notes, and optional photos to this endpoint. | Store as a GitHub secret. Redact in docs and handoffs as `[REDACTED]`. The endpoint must accept the current multipart POST form or the form should remain protected by call/text fallback. | Which approved form provider/backend endpoint should receive intake submissions, and is it ready for multipart form data? Value: `[REDACTED]`. | Intake either reliably reaches the owner or gracefully falls back to call/text without losing leads. |

## Legal and customer-facing commitments needing approval

| Commitment | Where it appears | Recommended handling | Owner question | User impact |
|---|---|---|---|---|
| Privacy Policy and Terms of Use | `public/privacy-policy/index.html`, `public/terms-of-use/index.html` | Needs legal/owner approval before production. Do not claim counsel review. | Are the current Privacy Policy and Terms approved for production as written? | Reduces legal risk and avoids misleading visitors. |
| "Reply within one business day" | Contact page meta/hero and homepage response card. | Needs operational approval. Keep only if owner can meet it. | Can EVOMTRS commit to replying to new intake within one business day? | Sets a response expectation customers can trust. |
| Proof dossiers/client initials/outcomes | Home page and Proof page. | Needs owner/proof approval. Keep initials/outcomes only if they are truthful and approved; otherwise replace with generic capability copy until real approvals exist. | Are A.L., M.R., J.T. dossiers and outcome claims approved for public use? | Prevents unverifiable testimonials or implied client claims. |
| Founder credential / concours claim | Home page, About page, metadata. | Needs owner/proof approval. | Is the exact credential wording approved and supportable? | Preserves credibility without overclaiming. |
| Service area wording | Home/contact pages and footer badges. | Mostly safe if owner confirms. | Is the public service area `Jacksonville, Ponte Vedra, Amelia Island, St. Johns, North Florida; selective out-of-area` approved? | Helps qualified visitors self-select without overpromising reach. |
| Mercedes/AMG-only positioning | Header/nav copy, services, about, footer. | Safe only if business strategy confirms no general-shop work should be promoted. | Should the site remain explicitly Mercedes/AMG-only? | Filters inbound leads toward the intended specialty. |
| Spam protection / backend readiness | Form behavior and launch readiness. | Needs backend/provider approval. Confirm spam handling before live form launch; otherwise rely on call/text fallback. | What spam-protection or provider controls are approved for the intake form? | Avoids lead loss and spam floods after launch. |
| Final proof/credential approvals | FINAL_REPORT notes and visible marketing claims. | Needs owner approval before production deploy. | Are all proof, credential, image, and customer-claim assets approved for public launch? | Prevents shipping claims or assets the owner would later retract. |

## Approval gate

Before live dispatch/deploy, Brendan or the owner should confirm:

1. Final production URL/domain.
2. All public GitHub variable values above.
3. `EVOMTRS_FORM_ENDPOINT` stored as secret with value `[REDACTED]`.
4. Intake endpoint/provider and spam-protection/backend readiness.
5. Legal copy and updated date.
6. Public address/location/map policy.
7. Proof dossiers, founder credential, service-area wording, and customer-facing claims.
8. Approval to dispatch the manual GitHub Pages workflow after the workflow file is merged.

Recommended default decision: do not deploy until the endpoint, location policy, contact values, legal approval, and proof-claim approvals are explicitly answered. User impact: this keeps the site launch-ready without publishing wrong contact routes, private location data, broken intake, or unsupported credibility claims.
