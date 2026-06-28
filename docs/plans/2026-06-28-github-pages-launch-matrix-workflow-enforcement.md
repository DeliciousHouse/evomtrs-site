# GitHub Pages Launch-Matrix Workflow Enforcement Implementation Plan

> Implementation note: keep this change split into reviewable commits that preserve the existing hard gates around GitHub Pages settings, variables, secrets, workflow dispatch, and production traffic.

**Goal:** Add a production GitHub Pages workflow guard that runs the EVOMTRS launch-state smoke matrix against the exact GitHub variables/secrets used to render `dist/`, before the Pages artifact can be uploaded or deployed.

**Architecture:** Reuse the existing `scripts/verify_launch_values.py` checker instead of creating a second CI-only verifier. The workflow should build `dist/`, run `scripts/verify_static.py`, run `scripts/verify_launch_values.py`, and only then configure/upload the Pages artifact. `scripts/verify_deploy_posture.py` should also guard that the workflow keeps this ordering so future edits cannot silently remove the production launch-matrix gate.

**Tech Stack:** GitHub Actions, npm scripts, Python stdlib verification scripts, static HTML render output in `dist/`.

---

## Context

Source Kanban task: `t_19e161c6`
Source discovery task: `t_70e9f454`
Board: `evomtrs-site`
Workspace: `/home/node/evomtrs-site`

Current state verified from repo files:

- `.github/workflows/deploy-github-pages.yml:32-52` renders `dist/` with GitHub `vars.*` and `secrets.EVOMTRS_FORM_ENDPOINT`.
- `.github/workflows/deploy-github-pages.yml:54-74` runs `python3 scripts/verify_static.py dist --env-file <(env | grep '^EVOMTRS_' | sort)`.
- `.github/workflows/deploy-github-pages.yml:76-82` configures and uploads the Pages artifact.
- The workflow does not currently invoke `scripts/verify_launch_values.py` before artifact upload.
- `package.json:10-13` already provides local `verify:launch-values`, `verify:launch-local`, `verify:deploy-posture`, and `verify` commands.
- `scripts/verify_launch_values.py` already checks all 22 rows from `docs/launch-state-smoke-matrix.md` and redacts `EVOMTRS_FORM_ENDPOINT` output as `EVOMTRS_FORM_ENDPOINT=[REDACTED]` or `EVOMTRS_FORM_ENDPOINT=[REPLACE_WITH_FORM_ENDPOINT]`.
- `scripts/verify_deploy_posture.py` currently guards deploy-posture docs/scripts, but not workflow launch-matrix invocation.

## Hard gates and non-goals

Do not perform any of these in implementation:

- Do not authorize or mutate GitHub Pages settings.
- Do not create, read, print, or mutate GitHub variables or secrets.
- Do not print the raw `EVOMTRS_FORM_ENDPOINT` value in docs, logs, comments, PR bodies, or handoffs.
- Do not run `gh workflow run`, dispatch a workflow, deploy, change DNS/custom-domain settings, switch production traffic, or make legal/customer-facing commitments.
- Do not change rendered UI/copy unless a verification script exposes a real bug that requires a separately reviewed task.

Allowed endpoint evidence:

- `EVOMTRS_FORM_ENDPOINT=[REDACTED]`
- `EVOMTRS_FORM_ENDPOINT=[REPLACE_WITH_FORM_ENDPOINT]`
- Secret-name-only references, for example `secrets.EVOMTRS_FORM_ENDPOINT`

## Recommended implementation choice

Add a new workflow step after `Verify static output` and before `Configure Pages`:

```yaml
      - name: Verify launch values
        env:
          EVOMTRS_SITE_URL: ${{ vars.EVOMTRS_SITE_URL }}
          EVOMTRS_BUSINESS_NAME: ${{ vars.EVOMTRS_BUSINESS_NAME }}
          EVOMTRS_CONTACT_EMAIL: ${{ vars.EVOMTRS_CONTACT_EMAIL }}
          EVOMTRS_CONTACT_PHONE_E164: ${{ vars.EVOMTRS_CONTACT_PHONE_E164 }}
          EVOMTRS_CONTACT_PHONE_DISPLAY: ${{ vars.EVOMTRS_CONTACT_PHONE_DISPLAY }}
          EVOMTRS_TEXT_PHONE_E164: ${{ vars.EVOMTRS_TEXT_PHONE_E164 }}
          EVOMTRS_ADDRESS_LINE1: ${{ vars.EVOMTRS_ADDRESS_LINE1 }}
          EVOMTRS_CITY: ${{ vars.EVOMTRS_CITY }}
          EVOMTRS_STATE: ${{ vars.EVOMTRS_STATE }}
          EVOMTRS_ZIP: ${{ vars.EVOMTRS_ZIP }}
          EVOMTRS_PRICE_RANGE: ${{ vars.EVOMTRS_PRICE_RANGE }}
          EVOMTRS_FOUNDER_NAME: ${{ vars.EVOMTRS_FOUNDER_NAME }}
          EVOMTRS_FOUNDER_ROLE: ${{ vars.EVOMTRS_FOUNDER_ROLE }}
          EVOMTRS_FOUNDER_CREDENTIAL: ${{ vars.EVOMTRS_FOUNDER_CREDENTIAL }}
          EVOMTRS_FORM_ENDPOINT: ${{ secrets.EVOMTRS_FORM_ENDPOINT }}
          EVOMTRS_LEGAL_UPDATED_DATE: ${{ vars.EVOMTRS_LEGAL_UPDATED_DATE }}
          EVOMTRS_DIRECTIONS_URL: ${{ vars.EVOMTRS_DIRECTIONS_URL }}
          EVOMTRS_MAP_EMBED_URL: ${{ vars.EVOMTRS_MAP_EMBED_URL }}
        shell: bash
        run: |
          env | grep '^EVOMTRS_' | sort > /tmp/evomtrs-workflow.env
          python3 scripts/verify_launch_values.py dist --env-file /tmp/evomtrs-workflow.env
```

Why this is safer than directly repeating process substitution:

- It avoids depending on GitHub's default shell behavior for `<(...)` on this specific line.
- It gives both static and launch verifiers the same concrete env-file pattern if the static step is later updated to match.
- The temporary file is runner-local and not uploaded as an artifact.
- The existing launch verifier redacts endpoint evidence before printing.

Direct one-line equivalent is acceptable if the implementer chooses to preserve the existing workflow style:

```yaml
        run: python3 scripts/verify_launch_values.py dist --env-file <(env | grep '^EVOMTRS_' | sort)
```

If using process substitution, explicitly set `shell: bash` on both verification steps so future GitHub runner defaults do not become part of the contract.

## Workflow data flow

```text
GitHub vars/secrets
        |
        v
Render site step
  npm run build
        |
        v
      dist/
        |
        +--> Verify static output
        |      scripts/verify_static.py dist --env-file runner EVOMTRS snapshot
        |
        +--> Verify launch values
        |      scripts/verify_launch_values.py dist --env-file same runner EVOMTRS snapshot
        |      - checks 22 launch rows
        |      - redacts EVOMTRS_FORM_ENDPOINT in output
        |
        v
Configure Pages -> Upload Pages artifact -> deploy job
```

The key invariant: artifact upload must be impossible unless both static verification and launch-value verification have passed against the same configured values used during render.

## What already exists

- Existing render path: `scripts/render_site.py` reads `EVOMTRS_*` values from environment or dotenv and writes `dist/`.
- Existing static verifier: `scripts/verify_static.py` checks required routes, sitemap, robots, local links/assets, unreplaced tokens, and allowed placeholders.
- Existing launch verifier: `scripts/verify_launch_values.py` checks all 22 launch-state rows and redacts `EVOMTRS_FORM_ENDPOINT` evidence.
- Existing deploy-posture verifier: `scripts/verify_deploy_posture.py` prevents legacy deploy posture drift in `package.json`, README, and runbook.
- Existing local commands: `npm run --silent verify`, `npm run --silent verify:launch-local`, and `python3 -m py_compile ...` already provide no-deploy checks.

The implementation should reuse these. Do not build a parallel CI checker.

## NOT in scope

- GitHub repo/environment variable setup, because owner/Brendan approval is still blocked.
- Secret creation or validation through the GitHub API, because this plan must not touch secrets.
- Workflow dispatch or deploy, because first dispatch is a hard gate.
- DNS/custom-domain or traffic changes, because those are production traffic switches.
- Rendered UI/copy changes, because this is workflow enforcement only.
- New test framework setup, because this repo has stdlib Python verification scripts and no test harness directory.

---

## Task 1: Pin the workflow verification order in the plan before coding

**Objective:** Confirm the implementation uses the existing launch verifier immediately before any Pages artifact upload.

**Files:**

- Inspect: `.github/workflows/deploy-github-pages.yml:32-82`
- Inspect: `scripts/verify_launch_values.py:347-400`
- Inspect: `scripts/verify_deploy_posture.py:119-141`

**Step 1: Read the current workflow order**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
workflow = Path('.github/workflows/deploy-github-pages.yml').read_text().splitlines()
for needle in ['Render site', 'Verify static output', 'verify_static.py', 'verify_launch_values.py', 'Configure Pages', 'upload-pages-artifact']:
    matches = [f'{i}: {line}' for i, line in enumerate(workflow, 1) if needle in line]
    print(needle, matches or 'MISSING')
PY
```

Expected now: `verify_launch_values.py` is `MISSING`; `verify_static.py` appears before `Configure Pages` and `upload-pages-artifact`.

**Step 2: Record the intended order**

Expected final order:

```text
Render site
Verify static output
Verify launch values
Configure Pages
Upload Pages artifact
```

**Step 3: Do not edit yet if owner/Brendan production setup is still blocked**

This implementation is safe because it changes only workflow enforcement, but it still must not be treated as approval to dispatch the workflow.

## Task 2: Add the workflow launch-value verification step

**Objective:** Make the GitHub Pages build job fail before artifact upload when configured launch values do not satisfy the 22-row launch-state matrix.

**Files:**

- Modify: `.github/workflows/deploy-github-pages.yml:54-76`

**Step 1: Insert the new workflow step after static verification**

Preferred patch shape:

```yaml
      - name: Verify static output
        env:
          # keep the existing EVOMTRS_* env block unchanged
        shell: bash
        run: |
          env | grep '^EVOMTRS_' | sort > /tmp/evomtrs-workflow.env
          python3 scripts/verify_static.py dist --env-file /tmp/evomtrs-workflow.env

      - name: Verify launch values
        env:
          # same EVOMTRS_* env block as Render site and Verify static output
        shell: bash
        run: |
          env | grep '^EVOMTRS_' | sort > /tmp/evomtrs-workflow.env
          python3 scripts/verify_launch_values.py dist --env-file /tmp/evomtrs-workflow.env
```

If keeping the existing process-substitution style, use this instead:

```yaml
      - name: Verify launch values
        env:
          # same EVOMTRS_* env block as Render site and Verify static output
        shell: bash
        run: python3 scripts/verify_launch_values.py dist --env-file <(env | grep '^EVOMTRS_' | sort)
```

**Step 2: Preserve the existing env source split**

Public launch values remain GitHub `vars.*`:

```yaml
EVOMTRS_SITE_URL: ${{ vars.EVOMTRS_SITE_URL }}
```

The endpoint remains a GitHub secret reference:

```yaml
EVOMTRS_FORM_ENDPOINT: ${{ secrets.EVOMTRS_FORM_ENDPOINT }}
```

Do not print, echo, document, or paste the raw endpoint value.

**Step 3: Keep artifact upload gated**

`actions/configure-pages@v5` and `actions/upload-pages-artifact@v3` must stay after both verification steps.

**Step 4: Run read-only workflow inspection**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
text = Path('.github/workflows/deploy-github-pages.yml').read_text()
needles = [
    'python3 scripts/verify_static.py dist',
    'python3 scripts/verify_launch_values.py dist',
    'actions/configure-pages@v5',
    'actions/upload-pages-artifact@v3',
]
positions = {needle: text.find(needle) for needle in needles}
for needle, pos in positions.items():
    print(f'{needle}: {pos}')
if any(pos < 0 for pos in positions.values()):
    raise SystemExit('missing required workflow content')
if not (positions['python3 scripts/verify_static.py dist'] < positions['python3 scripts/verify_launch_values.py dist'] < positions['actions/configure-pages@v5'] < positions['actions/upload-pages-artifact@v3']):
    raise SystemExit('workflow verification/upload order is wrong')
if 'EVOMTRS_FORM_ENDPOINT: ${{ secrets.EVOMTRS_FORM_ENDPOINT }}' not in text:
    raise SystemExit('workflow must source EVOMTRS_FORM_ENDPOINT from GitHub secrets')
print('workflow launch-value gate order: ok')
PY
```

Expected: `workflow launch-value gate order: ok`.

## Task 3: Extend deploy-posture verification to guard workflow launch verification

**Objective:** Prevent future workflow edits from removing or moving launch-value verification after artifact upload.

**Files:**

- Modify: `scripts/verify_deploy_posture.py:9-128`

**Step 1: Add a workflow path constant**

Add near the existing path constants:

```python
WORKFLOW = ROOT / ".github" / "workflows" / "deploy-github-pages.yml"
```

**Step 2: Add a workflow-order checker**

Add a function near the other check helpers:

```python
def check_workflow_launch_value_gate(text: str) -> list[str]:
    failures: list[str] = []
    required = {
        "static verification": "python3 scripts/verify_static.py dist",
        "launch-value verification": "python3 scripts/verify_launch_values.py dist",
        "Pages configuration": "actions/configure-pages@v5",
        "Pages artifact upload": "actions/upload-pages-artifact@v3",
        "endpoint GitHub secret": "EVOMTRS_FORM_ENDPOINT: ${{ secrets.EVOMTRS_FORM_ENDPOINT }}",
    }
    positions: dict[str, int] = {}
    for label, needle in required.items():
        position = text.find(needle)
        positions[label] = position
        if position == -1:
            failures.append(f"deploy workflow missing {label}: {needle}")

    if not failures:
        if not (
            positions["static verification"]
            < positions["launch-value verification"]
            < positions["Pages configuration"]
            < positions["Pages artifact upload"]
        ):
            failures.append(
                "deploy workflow must run static verification, then launch-value verification, before Pages configure/upload"
            )
    return failures
```

**Step 3: Wire it into `main()`**

After reading README/runbook:

```python
    workflow = read_text(WORKFLOW)
```

After current deploy-posture checks:

```python
    failures.extend(check_workflow_launch_value_gate(workflow))
```

**Step 4: Update success output**

Append one success line:

```python
    print("- GitHub Pages workflow runs launch-value verification before artifact upload")
```

**Step 5: Verify negative behavior manually with a temp copy if needed**

Do not mutate the real workflow just to test failure. If a negative test is desired, use a Python temp string inside the interpreter and call the helper directly.

Example:

```bash
python3 - <<'PY'
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('verify_deploy_posture', 'scripts/verify_deploy_posture.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
workflow = Path('.github/workflows/deploy-github-pages.yml').read_text()
print(module.check_workflow_launch_value_gate(workflow))
print(module.check_workflow_launch_value_gate(workflow.replace('python3 scripts/verify_launch_values.py dist', 'python3 scripts/verify_launch_values_REMOVED.py dist')))
PY
```

Expected: first output `[]`; second output contains a missing launch-value verification failure.

## Task 4: Update operator docs only if the final workflow command differs from current runbook wording

**Objective:** Keep operator onboarding accurate without adding new approval authority.

**Files:**

- Modify if needed: `docs/github-pages-runbook.md:76-87`
- Modify if needed: `README.md:63-75`

**Step 1: Check whether docs already describe launch-value verification**

Run:

```bash
grep -RIn "verify_launch_values.py\|verify:launch-local\|launch-state value" README.md docs/github-pages-runbook.md docs/launch-state-smoke-matrix.md
```

Expected: local preflight docs already mention `verify_launch_values.py` and `verify:launch-local`.

**Step 2: If workflow enforcement is not mentioned, add one sentence to the runbook expected result**

Recommended wording:

```markdown
- The GitHub Pages workflow runs static verification and launch-state value verification against the configured GitHub `EVOMTRS_*` variables/secrets before uploading the Pages artifact.
```

Do not add any raw endpoint value.

**Step 3: Preserve hard-gate language**

Any docs edit must keep this meaning:

```text
Local/workflow green does not authorize GitHub settings, variables, secrets, DNS/custom-domain changes, legal/customer-facing commitments, workflow dispatch, deploy, or production traffic.
```

## Task 5: Run required verification

**Objective:** Prove the implementation changed enforcement only and did not break local no-deploy checks.

**Files:**

- Verify: `.github/workflows/deploy-github-pages.yml`
- Verify: `scripts/render_site.py`
- Verify: `scripts/verify_static.py`
- Verify: `scripts/verify_launch_values.py`
- Verify: `scripts/verify_deploy_posture.py`

**Step 1: Run package verification**

Run:

```bash
npm run --silent verify
```

Expected: exit 0. Output should include deploy-posture success and must not include a raw `EVOMTRS_FORM_ENDPOINT` value.

**Step 2: Run launch-local verification**

Run:

```bash
npm run --silent verify:launch-local
```

Expected: exit 0. Output includes `Rows checked: 22`, `Rows passing: 22`, `Rows failing: 0`, and endpoint evidence is only placeholder/redacted.

**Step 3: Compile Python scripts**

Run:

```bash
python3 -m py_compile scripts/render_site.py scripts/verify_static.py scripts/verify_launch_values.py scripts/verify_deploy_posture.py
```

Expected: exit 0.

**Step 4: Check whitespace**

Run:

```bash
git diff --check
```

Expected: exit 0.

**Step 5: Run read-only workflow syntax/content inspection**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
text = Path('.github/workflows/deploy-github-pages.yml').read_text()
checks = {
    'manual workflow_dispatch only': 'workflow_dispatch:' in text and 'push:' not in text,
    'static verification present': 'python3 scripts/verify_static.py dist' in text,
    'launch verification present': 'python3 scripts/verify_launch_values.py dist' in text,
    'launch verification before upload': text.find('python3 scripts/verify_launch_values.py dist') < text.find('actions/upload-pages-artifact@v3'),
    'endpoint sourced from secret': 'EVOMTRS_FORM_ENDPOINT: ${{ secrets.EVOMTRS_FORM_ENDPOINT }}' in text,
}
for label, ok in checks.items():
    print(f'{label}: {ok}')
if not all(checks.values()):
    raise SystemExit('workflow inspection failed')
PY
```

Expected: all rows print `True`.

## Task 6: Prepare review handoff, not deploy handoff

**Objective:** Route the implementation through review before any ship-readiness claim.

**Files:**

- Inspect: `git diff -- .github/workflows/deploy-github-pages.yml scripts/verify_deploy_posture.py docs/github-pages-runbook.md README.md`

**Step 1: Summarize changed files**

Run:

```bash
git status --short
git diff --stat
git diff -- .github/workflows/deploy-github-pages.yml scripts/verify_deploy_posture.py docs/github-pages-runbook.md README.md
```

Expected: only planned files changed.

**Step 2: Request implementation review before ship readiness**

The implementation PR/task must receive `/review` or `review` before being considered ship-ready.

Review focus:

- Workflow data flow and ordering.
- Secret redaction and evidence safety.
- Failure modes when GitHub vars/secrets are missing or placeholders.
- Branch/environment behavior for `workflow_dispatch` on `main`.
- Deploy-posture guard coverage.
- No accidental deploy, workflow dispatch, GitHub mutation, or traffic switch.

---

## Plan-eng-review coverage

Scope challenge:

- Existing code already solves rendering, static verification, launch-value verification, and deploy-posture checks. The smallest complete change is to wire the existing launch verifier into the workflow and make deploy-posture guard that wiring.
- This should touch 2 required files, `.github/workflows/deploy-github-pages.yml` and `scripts/verify_deploy_posture.py`, plus optional docs if the workflow command style changes. This is below the 8-file complexity smell threshold.
- No new services, classes, dependencies, or GitHub APIs are needed.

Architecture findings:

1. `[P1] (confidence: 9/10) .github/workflows/deploy-github-pages.yml:54-80 — launch-value verification must run before Pages artifact upload.`
   Recommendation: add `Verify launch values` immediately after static verification. This is the smallest diff that closes the production workflow gap.

2. `[P2] (confidence: 8/10) scripts/verify_deploy_posture.py:119-141 — deploy-posture should guard workflow launch verification.`
   Recommendation: add workflow content/order checks so `npm run verify` catches future removal or reordering.

3. `[P2] (confidence: 7/10) .github/workflows/deploy-github-pages.yml:74 — process substitution depends on bash behavior.`
   Recommendation: either set `shell: bash` explicitly or write the EVOMTRS env snapshot to `/tmp/evomtrs-workflow.env` before invoking both verifiers.

Code quality findings:

- Keep the env block explicit even though it repeats. In GitHub Actions, explicit variable source mapping is more auditable than clever YAML generation, and this workflow is a production launch gate.
- Avoid adding a shared workflow action or generated env list in this slice. That would increase moving parts without improving launch safety.
- If duplication becomes painful later, route a separate cleanup task after first dispatch, not in this enforcement slice.

Test review:

```text
CODE PATHS                                                    OPERATOR FLOWS
[+] deploy-github-pages.yml build job                         [+] Manual GitHub Pages dispatch from main
  ├── [existing] Render site with GitHub EVOMTRS values          ├── [GAP -> workflow] missing values fail during build
  ├── [existing] Verify static output                            ├── [GAP -> workflow] bad launch row fails before upload
  ├── [GAP] Verify launch values before artifact upload          └── [existing] deploy remains manual workflow_dispatch
  └── [existing] Upload Pages artifact only after prior steps

[+] verify_deploy_posture.py
  ├── [existing] package deploy script guard
  ├── [existing] canonical GitHub Pages docs guard
  ├── [existing] secret policy docs guard
  └── [GAP] workflow invokes launch verifier before artifact upload

COVERAGE TARGET: 100% of changed enforcement paths covered by npm verify, verify:launch-local, py_compile, git diff --check, and read-only workflow inspection.
```

Regression tests/checks required:

- `npm run --silent verify` must fail if the workflow no longer contains `python3 scripts/verify_launch_values.py dist`.
- `npm run --silent verify` must fail if launch verification appears after `actions/upload-pages-artifact@v3`.
- `npm run --silent verify:launch-local` must still report 22/22 rows locally.

Performance review:

- The added workflow step scans rendered text files and 22 matrix checks. This is negligible compared with dependency install/build.
- No caching or parallelization needed. Verification must stay sequential because artifact upload must depend on both checks.

Failure modes:

| Failure | Expected behavior | Covered by plan |
|---|---|---|
| GitHub variable missing | `scripts/verify_launch_values.py` exits non-zero with missing env value, before artifact upload | Yes |
| Secret missing | verifier exits non-zero for missing `EVOMTRS_FORM_ENDPOINT`, before artifact upload | Yes |
| Raw endpoint accidentally appears outside expected form action | verifier reports redacted failure, exits non-zero | Yes |
| Workflow launch verifier removed later | `npm run verify` deploy-posture check fails | Yes, after Task 3 |
| Workflow launch verifier moved after upload | `npm run verify` deploy-posture check fails | Yes, after Task 3 |
| Shell process substitution unsupported | use `shell: bash` or temp env file | Yes |

Parallelization:

Sequential implementation, no parallelization opportunity. The workflow edit and deploy-posture guard are tightly coupled and should land in one small diff.

## Plan-devex-review coverage

Developer/operator persona:

- Future implementer: `eng-evomtrs`, working locally before PR/review.
- Operator: repo admin or owner-approved deploy operator preparing first manual GitHub Pages dispatch.
- Reviewer: engineer checking that no deploy authority or secret value leaked into code, docs, logs, PR body, or Kanban.

Current friction:

- Local `verify:launch-local` proves `.env.example` behavior, but the production workflow does not yet prove configured GitHub values before upload.
- Operators could see a green workflow artifact upload even if launch values fail the owner-answer matrix, unless they remember to run the check separately.

Target experience:

- One manual workflow run has a clear `Verify launch values` step.
- If values are wrong or missing, the workflow fails before artifact upload.
- Logs show row-level evidence without raw endpoint leakage.
- Local `npm run verify` catches workflow guard drift before PR review.

DX recommendations:

1. Keep `npm run verify` as the routine local gate and extend deploy-posture, rather than adding another local command operators must remember.
2. Keep `npm run verify:launch-local` separate because it prints the full 22-row matrix and can be noisy for routine posture checks.
3. Name the workflow step `Verify launch values`, not a vague name like `Smoke`, so GitHub Actions logs make the gate obvious.
4. Keep hard-gate language in runbook and handoffs. A green verifier means values are internally consistent, not approved to deploy.

DevEx acceptance criteria:

- A new engineer can discover all required commands from this plan and `docs/github-pages-runbook.md`.
- A reviewer can prove workflow ordering with a read-only Python inspection.
- A deploy operator can identify the exact failing matrix row in GitHub Actions logs without seeing a raw endpoint.

## Review requirement before ship readiness

After implementation, route a standalone review task or PR review using `/review` or `review`.

Review must verify:

- No raw endpoint appears in code, docs, Kanban, PR body, or command output.
- Workflow remains `workflow_dispatch` only.
- `Verify launch values` runs after static verification and before Pages artifact upload.
- `scripts/verify_deploy_posture.py` catches missing or misordered workflow launch verification.
- Required verification commands pass.
- No GitHub settings, secrets, variables, workflow dispatch, deploy, DNS, or traffic changes were made.

## Final verification command list

Run all of these before marking implementation complete:

```bash
npm run --silent verify
npm run --silent verify:launch-local
python3 -m py_compile scripts/render_site.py scripts/verify_static.py scripts/verify_launch_values.py scripts/verify_deploy_posture.py
git diff --check
python3 - <<'PY'
from pathlib import Path
text = Path('.github/workflows/deploy-github-pages.yml').read_text()
checks = {
    'manual workflow_dispatch only': 'workflow_dispatch:' in text and 'push:' not in text,
    'static verification present': 'python3 scripts/verify_static.py dist' in text,
    'launch verification present': 'python3 scripts/verify_launch_values.py dist' in text,
    'launch verification before upload': text.find('python3 scripts/verify_launch_values.py dist') < text.find('actions/upload-pages-artifact@v3'),
    'endpoint sourced from secret': 'EVOMTRS_FORM_ENDPOINT: ${{ secrets.EVOMTRS_FORM_ENDPOINT }}' in text,
}
for label, ok in checks.items():
    print(f'{label}: {ok}')
if not all(checks.values()):
    raise SystemExit('workflow inspection failed')
PY
```

Expected result: all commands exit 0. `verify:launch-local` reports 22 checked rows and endpoint evidence is redacted or placeholder-only.

## Implementation handoff

Recommended child task:

Title: `Implement EVOMTRS GitHub Pages workflow launch-matrix enforcement before artifact upload`

Assignee: `eng-evomtrs`

Acceptance criteria:

- Implements Tasks 1-6 from this plan.
- Does not perform any hard-gated production action.
- Posts verification output summaries only, with raw endpoint values excluded.
- Requests review before ship readiness.
