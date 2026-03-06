# EVOMTRS Redesign — Brand Repositioning

## 1. Redesign summary

The site has been **repositioned from “clean boutique luxury” to “elite Mercedes / AMG specialist with motorsport and concours credibility.”** This was a full brand-direction correction, not a cosmetic pass.

**What changed:**

- **Visual system:** New design tokens and typography. Near-black/graphite background, gunmetal surfaces, off-white text, deep performance red used in controlled amounts. Headlines: Oswald (narrow, assertive). Body: IBM Plex Sans (technical, readable). Softer serif/lifestyle treatment removed.
- **Copy:** Rewritten to be concrete and specific. Removed abstract “luxury-level execution,” “discerning clients,” “boutique process.” Replaced with “Mercedes/AMG only,” “diagnostics-first,” “5-time Amelia Island Concours champion,” staged build planning, concours-informed standards, Jacksonville / North Florida service area.
- **Structure:** New architecture: Home, Services, Case Studies, About, Proof, FAQ, Contact, Privacy, Terms. Founder (Eric Praxis) is central: dedicated About page, prominent hero/founder sections, “why we are not a general shop” narrative.
- **Homepage:** Cinematic hero (full-bleed image, overlay, clear specialist positioning), trust strip, founder section, services (Diagnostics, Calibration, Restoration, Specialty builds), “why Mercedes only,” featured build, before/after slider, proof dossiers, service area & contact, process, FAQ, footer.
- **Services page:** New. Five categories with “what it includes,” “who it’s for,” “why a specialist”: Diagnostics, Calibration, Restoration, Performance integration, Specialty build planning.
- **About page:** New. Centered on Eric Praxis: who he is, why Mercedes/AMG, what the Amelia Island credential means in practice, why EVOMTRS is not a general shop.
- **Case studies:** Gallery reframed as case-study dossiers (vehicle, objective, condition, strategy, work, outcome). Same URL path `/gallery/`, nav label “Case Studies.”
- **Proof:** Testimonials page reframed as “Proof” with owner-outcome dossiers (client, location, vehicle, problem, work, result). No generic testimonial fluff.
- **Contact:** Intake form and contact block use env-driven content only. All visible “placeholder” and backend-status language removed. Form posts to `EVOMTRS_FORM_ENDPOINT`; copy sets expectation of reply within one business day.
- **Legal:** Terms of Use and Privacy Policy replaced with production-ready, full-length content. Styled consistently; nav/footer aligned with rest of site.
- **Navigation:** Unified nav on all pages: Home, Services, Case Studies, About, Proof, FAQ, Contact + “Start Intake” CTA. Mobile: hamburger and slide-out menu.
- **Components:** Buttons, cards, section headers, proof blocks, process steps, footer, forms refactored into one coherent system (see `public/assets/css/styles.css` design-system comment block).

**What was preserved:**

- Static HTML + env substitution pipeline (`scripts/render_site.py`, `__TOKEN__` in templates).
- Existing image set (all .webp, same paths).
- Before/after comparison slider, reveal-on-scroll, year in footer.
- SEO: canonical, OG/Twitter meta, JSON-LD, sitemap, robots.

---

## 2. Design direction / style guide

**Brand attributes:** Specialist · Technical · Assertive · Disciplined · Founder-driven · Premium · High-trust · Mercedes-only.

**Color system:**

| Role            | Token    | Use |
|-----------------|----------|-----|
| Primary bg      | `--ink`  | Near-black `#08090b` |
| Panel/surface   | `--panel` / `--surface` | Gunmetal / dark steel |
| Line/border     | `--line` | `#1e252c` |
| Muted text      | `--steel`| `#9ca3af` |
| Primary text    | `--ivory`| Off-white `#e5e7eb` |
| Accent          | `--crimson` | Deep red `#a30d15` (controlled) |

**Typography:**

- **Headlines:** Oswald, uppercase, letter-spacing. Narrow, assertive, performance-oriented.
- **Body:** IBM Plex Sans. Clean technical sans, high readability.
- **Labels / kickers:** Uppercase, letter-spacing, crimson or steel. Engineering-inspired.

**Layout:**

- Strong contrast; clear section hierarchy; grid discipline; sharper spacing; minimal radius (`--radius` 8px, `--radius-lg` 12px).
- Motion: reveal on scroll, hover states, no gimmicky animation.
- Premium machine aesthetic, not SaaS or lifestyle editorial.

**Avoid:**

- Warm beige/cream luxury palettes, soft serif-heavy editorial look, generic blue, bright red everywhere, playful or fashion-first tone.

Full tokens and component rules are in `public/assets/css/styles.css` (top comment block and `:root`).

---

## 3. Before / after rationale

**Before:** The site read like a generic luxury/editorial automotive site: soft serifs (Cormorant Garamond), “luxury-level execution,” “discerning clients,” “boutique shop.” It felt polished but abstract and lifestyle-oriented, not like an elite Mercedes/AMG specialist with real technical and concours credibility.

**After:** The site immediately states Mercedes/AMG only, diagnostics-first, and founder credential (5-time Amelia Island Concours champion). Visuals are darker and sharper; copy is concrete (platform, problem, work, result). The founder is the reason the shop exists (About page, hero trust bar, founder section). Services are specified (Diagnostics, Calibration, Restoration, Performance integration, Specialty build planning) with “what / who / why specialist.” Proof and case studies are structured as dossiers, not vibes. Contact and legal are production-ready with no visible placeholder language.

**Success criteria met:**

- Visitor thinks: this person really knows Mercedes; this is a serious specialist; the brand has authority; the founder is credible; the work looks precise; the intake process is trustworthy; premium but not soft; technical but not sterile.

---

## 4. Remaining data needed from the owner

The following **must be supplied in `.env`** (or equivalent) for the site to be fully production-ready. Until then, rendered pages will show whatever values are in `.env` (e.g. literal placeholders if left as in `.env.example`).

| Variable | Purpose | Example / note |
|----------|---------|----------------|
| `EVOMTRS_ADDRESS_LINE1` | Street address | Real street, no “[REPLACE…]” in production |
| `EVOMTRS_ZIP` | Zip code | Real zip |
| `EVOMTRS_CONTACT_PHONE_E164` | Click-to-call | e.g. `+19041234567` |
| `EVOMTRS_CONTACT_PHONE_DISPLAY` | Display phone | e.g. `+1 (904) 123-4567` |
| `EVOMTRS_CONTACT_EMAIL` | Contact email | Real inbox |
| `EVOMTRS_TEXT_PHONE_E164` | Click-to-text | Same as or different from phone |
| `EVOMTRS_FORM_ENDPOINT` | Intake form `action` URL | Backend endpoint that accepts the form POST |
| `EVOMTRS_LEGAL_UPDATED_DATE` | “Last updated” on Terms and Privacy | e.g. `2025-03-06` (set in `.env.example`) |
| `EVOMTRS_MAP_EMBED_URL` | Map iframe `src` | Google Maps embed URL for actual address |
| `EVOMTRS_DIRECTIONS_URL` | “Directions” link | Google Maps directions URL |

**Optional but recommended:**

- Replace proof dossiers (A.L., M.R., J.T.) with real client outcomes when available (with permission).
- Add real review links/badges on the Proof page when approved.
- Wire form submission to a backend or form service so intake actually lands in the owner’s workflow; until then, form `action` points to `EVOMTRS_FORM_ENDPOINT` (can be a mailto or external form handler).

---

## 5. Image optimization

- All referenced images are already **.webp** under `public/assets/images/`.
- Responsive sizing is handled via CSS (e.g. `object-fit: cover`, aspect ratios). No new image variants were added in this redesign.
- If you add new assets, run them through the existing conversion workflow (see `scripts/convert-images.sh`) and keep using .webp.

---

## 6. File and route summary

| Route | File | Notes |
|-------|------|--------|
| `/` | `public/index.html` | Home; hero, founder, services, proof, process, FAQ |
| `/services/` | `public/services/index.html` | New; five service categories |
| `/gallery/` | `public/gallery/index.html` | Case studies (dossiers) |
| `/about/` | `public/about/index.html` | New; Eric Praxis, why Mercedes-only |
| `/testimonials/` | `public/testimonials/index.html` | Proof dossiers |
| `/contact/` | `public/contact/index.html` | Intake form + contact; no placeholder copy |
| `/privacy-policy/` | `public/privacy-policy/index.html` | Full privacy policy |
| `/terms-of-use/` | `public/terms-of-use/index.html` | Full terms of use |
| `sitemap.xml` | `public/sitemap.xml` | Includes /services/ and /about/ |

Render command: `./scripts/render-site.sh` (or `python3 scripts/render_site.py public dist`). Output: `dist/`. Docker build copies `public/` and runs render at container start using `runtime/.env`.
