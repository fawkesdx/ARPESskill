# Multi-band dispersion fitting — Design Spec

**Date:** 2026-09-24  
**Status:** Draft for user review  
**Repo:** https://github.com/fawkesdx/ARPESskill  
**Approach:** Extend `edc-mdc-fitting.md` (docs-only; same skill language)

## 1. Purpose

Give agents a **proper multi-band** path when a dispersion cut shows several
bands — without inventing peak count, DIY track-unswap, or a second skill.

Today: thin “prefix multi-peak” note only. Gaps: propose/confirm N, crossing
identity, user handoff, per-band plots / vF / m\*.

**User language:** still one skill — peak fit / EDC-MDC (`edc-mdc-fitting.md`).
Not a new “multi-band skill.”

## 2. Locked decisions

| Decision | Choice |
|----------|--------|
| Peak count | **Propose N** from mid-cut MDC / overlay → **user confirms** before broadcast |
| Crossings / track ID | Continuity **only if mapped package API**; else state “may swap” + A/B/C/D — **no DIY matcher** |
| Handoff | **Full checklist** (Γ / V₀ style) when user cannot drive the fit |
| Per-band physics | **Default:** E vs k + width plots; ask linear vs parabolic → vF and/or m\* per band |
| Deliverable | Docs-only extend fit recipe + wire SKILL / failure-modes / capability / example |
| Σ / self-energy | Unchanged: **single-band only**; multi-peak → stop + ask |
| Skill proliferation | **No** new skill row; subsection inside EDC/MDC fit |

## 3. Architecture (where it lives)

| Artifact | Role |
|----------|------|
| `reference/edc-mdc-fitting.md` | New **Multi-band dispersion** + **Multi-band handoff** subsections |
| `SKILL.md` | Valence fit / hard-rule bullets point at multi-band handoff |
| `reference/failure-modes.md` | Invent N; invent unswap; stuck→no handoff; multi-band Σ; collapse tracks |
| `reference/backend-capability-map.md` | New step id `multi_band_fit` → multi-band subsection; keep `broadcast_fit` / `band_vf_mstar` as building blocks |
| `examples/fit_edc_mdc.md` | Sketch: propose N → confirm → prefixed broadcast → per-band plots / vF |

**Out of v1:** in-repo track-matcher; invent tight-binding / orbital labels;
auto theory band assignment; new package code.

## 4. Agent pipeline

```text
cut ready (prefer k-space)
  → mid-cut (or user ROI) MDC / overlay → propose N (+ optional labels)
  → MULTI-BAND HANDOFF: user confirms N / labels / energy–k window
  → compose N prefixed peaks + background (package models only)
  → broadcast_model along eV (MDC track)  [viewer: mapped cut-fit path]
  → extract centers/widths per prefix
  → continuity: ONLY if mapped package helper exists
       else: “tracks may swap” + A/B/C/D or user re-label
  → default plots per band: E vs k, width vs k (+ width vs E if useful)
  → per band: ask linear vs parabolic → vF and/or m* (stated k window)
  → save analysis/ (params + PNGs); report band IDs + method
```

Single-band path unchanged (existing §§ EDC/MDC). Enter multi-band flow when
user asks multi-band **or** agent sees clear multiple peaks on a check MDC —
then **propose N and wait** (never silent multi-peak broadcast).

## 5. Multi-band handoff (spell it out)

When user sees several bands but does not know how to drive the fit — **do
not invent N**.

1. **Plain goal:** need peak count N (+ optional labels) so MDC broadcast
   tracks each band.
2. **Paths (user picks):**

| Path | What | How agent gets numbers |
|------|------|------------------------|
| **A. Confirm propose** | Agent shows mid-cut MDC + proposed N | User: `N=2` / edit |
| **B. You type** | User knows count / labels | `bands: a=inner, b=outer; N=2` |
| **C. ROI / window** | Energy±k box per band or shared window | Stated slices before broadcast |
| **D. GUI pick** | Launch fit GUI **after ask** | Paste N / save; no mind-read Qt |
| **E. Single-band first** | Fit one clear branch; rest later | Label `partial`; no claim full multi-band |

3. **Paste format** (example):

   ```text
   N=2; labels=a,b; eV=[-0.5,0.05]; lineshape=Lorentzian
   ```

4. **Confirm before broadcast**; persist `n_bands`, `band_ids`, method in
   report / `analysis/`.
5. Still unclear → **one** sharp question; **STOP**.

## 6. Backends

| Backend | Multi-peak broadcast | Continuity | Per-band vF / m\* |
|---------|----------------------|------------|-------------------|
| `pyarpes` | Prefixed models + `broadcast_model` | Mapped helper only if present in install | `LinearModel` / `QuadraticModel` on centers per prefix |
| `arpes_viewer` | `tools.peaks` / cut fit path if mapped | Same rule | `tools.dispersion.fit_dispersion` if mapped |
| Missing callable | Stop A/B/C/**D** | Do not invent | Do not invent |

Capability map must state continuity as **N/A** unless a real package symbol
is verified at implement time (no aspirational API names).

## 7. Hard rules & failure modes

**Rules**

- Never silent N; never silent DIY unswap.
- Name lineshape + background; report **per band**.
- Prefer k-space for vF/m\*; angle → provisional + ask convert.
- Token note before large multi-peak broadcast.
- Continuity: name the mapped API or admit none.

**Failure-modes rows to add**

| Failure | Correct |
|---------|---------|
| Invent peak count N | Propose from mid-cut MDC → confirm; or handoff paths A–E |
| DIY nearest-center unswap | Package continuity only; else “may swap” + A/B/C/D |
| User stuck on multi-band → invent | Spell multi-band handoff |
| Multi-band Σ without ask | Single-band ROI only (`self-energy.md`) |
| Collapse multi-peak to one E(k) track | Per-prefix centers + plots |
| New “multi-band skill” in reports | Say EDC/MDC fit (multi-band step) |

## 8. Relation to existing recipes

| Recipe | Relation |
|--------|----------|
| Single-curve / single-peak broadcast | Unchanged; multi-band is extension when N>1 |
| Core multi-peak (prefixed Gaussians) | Same prefix pattern; valence = MDC-oriented |
| `self-energy.md` | Still single-band; multi-peak stops |
| `band-enhance.md` | Enhance only — not a substitute for multi-peak fit |
| Γ / V₀ handoff | Same spell-it-out pattern; different physics |

## 9. Success criteria

- Agent facing multi-band cut **proposes N**, waits for confirm, then broadcasts.
- Stuck user gets **handoff paths + paste format**.
- No DIY track matcher in skill docs or examples.
- Per confirmed band: default E vs k / width plots; vF/m\* after linear/parabolic ask.
- SKILL + failure-modes + example + capability map wired; README skill table unchanged (no new skill row).

## 10. Implementation note (next)

After this spec is approved: writing-plans → docs-only plan under `specs/`
(same pattern as V₀ / FS-bend). Branch optional; land on `main` when user asks
push.
