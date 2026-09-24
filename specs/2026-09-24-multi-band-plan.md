# Multi-band dispersion fitting (extend EDC/MDC) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans after **user approves** this plan. Checkbox steps for tracking.

**Goal:** Document a proper **multi-band** path (propose-N→confirm, handoff, package continuity only, per-band plots / vF / m\*) inside the existing EDC/MDC fit skill — not a new skill.

**Architecture:** Docs-only. **Extend** `reference/edc-mdc-fitting.md` with Multi-band dispersion + Multi-band handoff. Wire SKILL, failure-modes, capability map, example. Spec: `specs/2026-09-24-multi-band-design.md`.

**Tech Stack:** Markdown; PyARPES `broadcast_model` + prefixed models; viewer `tools.peaks` / `tools.dispersion.fit_dispersion` if mapped. Continuity = N/A unless a real package symbol is verified at implement time.

## Global Constraints

- **One skill:** peak fit / EDC-MDC. No new skill row in README / SKILL description.
- Propose N from mid-cut MDC → **user confirms** before multi-peak broadcast; never silent N.
- Continuity / unswap: **package API only**; if none → “tracks may swap” + A/B/C/D — **no DIY matcher** in docs or examples.
- Full multi-band handoff (Γ / V₀ style) when user cannot drive the fit.
- Per confirmed band: default E vs k + width plots; ask linear vs parabolic → vF and/or m\*.
- Σ stays single-band (`self-energy.md`); multi-peak → stop + ask.
- Local-first; push only when asked.
- No invent axes / physics / tight-binding / orbital labels.

---

## File map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `reference/edc-mdc-fitting.md` | Multi-band pipeline + handoff + checklist rows |
| Modify | `examples/fit_edc_mdc.md` | Multi-band sketch after broadcast section |
| Modify | `reference/backend-capability-map.md` | Step `multi_band_fit`; continuity N/A unless verified |
| Modify | `reference/failure-modes.md` | Invent N; DIY unswap; no handoff; multi-band Σ; collapse tracks; “multi-band skill” |
| Modify | `SKILL.md` | Peak-fitting + workflow bullets; error-handling if needed |
| Modify | `specs/2026-09-24-multi-band-design.md` | Status → Approved (optional one-liner) |
| Skip | New `reference/multi-band.md` / README skill row | **Forbidden** |
| Skip | Any Python track-matcher | **Forbidden** |

---

### Task 1: Multi-band + handoff in `edc-mdc-fitting.md`

**Files:**
- Modify: `reference/edc-mdc-fitting.md`

**Interfaces:**
- Consumes: existing shared rules, EDC vs MDC table, single-peak broadcast, second-stage vF/m\*
- Produces: subsections agents must follow for N>1

- [ ] **Step 1: Insert `### Multi-band dispersion` after “Broadcast fits” (before or after Derived plots — prefer after Broadcast, before Derived plots, and reframe Derived plots to say “per band when multi-peak”)**

  Pipeline block (exact intent):

  ```text
  cut ready (prefer k-space)
    → mid-cut (or user ROI) MDC / overlay → propose N (+ optional labels)
    → MULTI-BAND HANDOFF: user confirms N / labels / energy–k window
    → compose N prefixed peaks + background (package models only)
    → broadcast_model along eV (MDC track)
    → extract centers/widths per prefix
    → continuity: ONLY if mapped package helper exists
         else: “tracks may swap” + A/B/C/D or user re-label
    → default plots per band: E vs k, width vs k (+ width vs E if useful)
    → per band: ask linear vs parabolic → vF and/or m* (stated k window)
    → save analysis/; report band IDs + method
  ```

  Enter flow when user asks multi-band **or** check MDC shows clear multiple peaks
  → **propose N and wait** (never silent multi-peak broadcast).

  Code sketch (prefix composite + broadcast):

  ```python
  from arpes.fits.fit_models import LorentzianModel, AffineBackgroundModel
  from arpes.fits.utilities import broadcast_model

  # After user confirmed N=2, labels a/b
  model = (
      AffineBackgroundModel()
      + LorentzianModel(prefix="a_")
      + LorentzianModel(prefix="b_")
  )
  # Prefer params= hints from a single mid-cut guess_fit
  fit_results = broadcast_model(model, cut_roi, "eV")
  # centers_a = fit_results.F.p("a_center")  # inspect API for install
  # centers_b = fit_results.F.p("b_center")
  ```

  Continuity paragraph: verify install for any track-continuity helper; if none,
  document **N/A** — state tracks may swap at crossings; offer A/B/C/D or user
  re-label. **Do not** document a DIY nearest-center loop.

- [ ] **Step 2: New `### Multi-band handoff (spell it out)`**

  Mirror Γ / V₀ structure:

  1. Plain goal (need N + optional labels for MDC track).
  2. Paths table A–E:

  | Path | What | How agent gets numbers |
  |------|------|------------------------|
  | **A. Confirm propose** | Mid-cut MDC + proposed N | User: `N=2` / edit |
  | **B. You type** | User knows count / labels | `bands: a=inner, b=outer; N=2` |
  | **C. ROI / window** | Energy±k box | Stated slices before broadcast |
  | **D. GUI pick** | Fit GUI **after ask** | Paste N / save; no mind-read Qt |
  | **E. Single-band first** | One clear branch | Label `partial` |

  3. Paste format:

     ```text
     N=2; labels=a,b; eV=[-0.5,0.05]; lineshape=Lorentzian
     ```

  4. Confirm before broadcast; persist `n_bands`, `band_ids`, method.
  5. Unclear → one sharp question; **STOP**.

- [ ] **Step 3: Update Derived plots + second-stage + checklist**

  - Derived plots table: when multi-peak, **required per prefix / band ID**.
  - Second-stage: run **per band** (ask linear vs parabolic once or per band if unclear).
  - Checklist: new **### Multi-band** items — N confirmed; handoff if stuck; per-band plots; no DIY unswap; no multi-band Σ claim.

- [ ] **Step 4: Cross-link Σ**

  One sentence: multi-peak → do not run `self-energy.md` until single-band ROI.

- [ ] **Step 5: Commit**

  ```bash
  git add reference/edc-mdc-fitting.md
  git commit -m "$(cat <<'EOF'
  docs: multi-band dispersion + handoff in EDC/MDC fit

  Propose-N confirm; package continuity only; per-band vF/m*.
  EOF
  )"
  ```

---

### Task 2: Wire example, capability, failure-modes, SKILL

**Files:**
- Modify: `examples/fit_edc_mdc.md`
- Modify: `reference/backend-capability-map.md`
- Modify: `reference/failure-modes.md`
- Modify: `SKILL.md`
- Optional: `specs/2026-09-24-multi-band-design.md` Status → Approved

**Interfaces:**
- Consumes: Task 1 subsection anchors / headings
- Produces: discoverable wiring for agents

- [ ] **Step 1: Example** — after “Broadcast MDC / EDC”, add `## 4. Multi-band (N>1)`:

  - Propose N from mid MDC → wait for confirm.
  - Prefixed composite + `broadcast_model`.
  - Plot per-prefix E vs k; ask linear/parabolic per band.
  - Note: no DIY unswap; continuity N/A unless package helper named.
  - Link `edc-mdc-fitting.md` multi-band + handoff.

- [ ] **Step 2: Capability map** — insert row after `band_vf_mstar`:

  | ID | Meaning | PyARPES | Browser | Ref |
  |----|---------|---------|---------|-----|
  | `multi_band_fit` | Multi-peak MDC track (N>1) | Prefixed models + `broadcast_model`; propose N→confirm; continuity **N/A** unless verified helper | `tools.peaks` / cut fit + `tools.dispersion.fit_dispersion` if mapped | `edc-mdc-fitting.md` |

  Enrich `broadcast_fit` Ref note: multi-peak → `multi_band_fit` step.

  **Verify before claiming continuity:** grep/read upstream for track continuity;
  if none found, leave Browser/PyARPES continuity as N/A explicitly in the
  multi-band doc (already Task 1).

- [ ] **Step 3: Failure modes** — add rows:

  | Failure | Correct |
  |---------|---------|
  | Invent peak count N | Propose mid-cut MDC → confirm; or multi-band handoff A–E |
  | DIY nearest-center unswap | Package only; else “may swap” + A/B/C/D |
  | User stuck on multi-band → invent | Spell multi-band handoff (`edc-mdc-fitting.md`) |
  | Multi-band Σ without ask | Single-band ROI only (`self-energy.md`) |
  | Collapse multi-peak to one E(k) track | Per-prefix centers + plots |
  | Report a separate “multi-band skill” | One skill: EDC/MDC fit (multi-band step) |

- [ ] **Step 4: SKILL.md**

  Under **Peak fitting** bullet: if clear multi-peak / user asks multi-band →
  propose N → confirm; spell **Multi-band handoff** if stuck; per-band plots +
  vF/m\*; no DIY unswap (`edc-mdc-fitting.md`).

  Workflow step for line analysis: mention multi-band path when N>1.

  Error handling: ambiguous N → handoff / propose-confirm; never silent.

- [ ] **Step 5: Grep verification**

  ```bash
  rg -n "multi.band|Multi-band|multi_band_fit|Propose N" reference/edc-mdc-fitting.md SKILL.md reference/failure-modes.md reference/backend-capability-map.md examples/fit_edc_mdc.md
  rg -n "nearest.center|DIY.*unswap|unswap" reference/edc-mdc-fitting.md examples/fit_edc_mdc.md
  ```

  Expected: handoff + `multi_band_fit` present; **no** DIY unswap recipe.

- [ ] **Step 6: Commit**

  ```bash
  git add examples/fit_edc_mdc.md reference/backend-capability-map.md reference/failure-modes.md SKILL.md specs/2026-09-24-multi-band-design.md
  git commit -m "$(cat <<'EOF'
  docs: wire multi-band fit into SKILL and capability map

  Failure modes + example; no new skill row.
  EOF
  )"
  ```

---

## Spec coverage check

| Spec § | Task |
|--------|------|
| Purpose / one skill | Global + Task 1–2 (no new skill) |
| Propose-N confirm | Task 1 pipeline |
| Package continuity only | Task 1 + Task 2 verify |
| Full handoff A–E | Task 1 Step 2 |
| Per-band plots / vF/m\* | Task 1 Steps 1+3 |
| Capability `multi_band_fit` | Task 2 Step 2 |
| Failure modes | Task 2 Step 3 |
| Σ single-band | Task 1 Step 4 + failure row |
| Example | Task 2 Step 1 |
| Out of v1 (no DIY code) | Global + grep Step 5 |

---

## Done when

- [ ] `edc-mdc-fitting.md` has multi-band pipeline + handoff.
- [ ] SKILL / failure-modes / capability / example wired.
- [ ] Grep shows no DIY unswap; no new README skill row.
- [ ] User asked before push to `origin`.
