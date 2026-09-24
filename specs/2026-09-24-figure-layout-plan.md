# Publication figure layout (user-asked) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans after **user approves** this plan. Checkbox steps for tracking.

**Goal:** Document **publication multi-panel figure layout** (journal mm widths, shared clim/limits, outside labels) via ARPES-data-browser `tools.figure` — gated user-asked recipe, **not** default overview and **not** a fake “analysis skill” sibling to k/kz.

**Architecture:** Docs-only. **New** `reference/figure-layout.md` (nothing clean to extend: overview = quick report; `stack-plots.md` = waterfall viz). One README/SKILL row under user-asked figures. Capability IDs. No claim this replaces scientific recipes.

**Tech Stack:** Markdown; upstream `tools.figure` (`Figure`, `Panel`, `FigureStyle`, `JOURNAL_PRESETS`, …) + `tools.export`; paint may live in `ui.figure` — prefer headless model + export; GUI only if user asks.

**Depends on:** `feat/moire-bz` (pushed). Branch: `feat/figure-layout`.

**Queue:** Former Item 8 (maybe) — user asked to do it. Framed as **layout/export**, not physics analysis.

## Global Constraints

- **Gate:** user asks publication figure / journal panel layout / Nature|PRB column / multi-panel paper figure. **Not** default quick-report trios (`default-overview-plots.md`).
- Package-first: `tools.figure` on `arpes_viewer`. On `pyarpes`: matplotlib `GridSpec` / constrained layout OK for simple panels; do **not** invent a full journal composer clone — offer A/B/C/**D** if they need viewer presets.
- Shared clim / axis limits across panels when comparing; labels on outside edges — state assumptions.
- Width in **mm** from `JOURNAL_PRESETS` or user; echo preset name + font pt.
- Save PNG/PDF under `analysis/figures/`; style JSON optional if upstream supports.
- Token: do not dump huge panel payloads in chat.
- Local-first; push when asked.

---

## File map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `reference/figure-layout.md` | Gate / backends / presets / panel rules / checklist |
| Create | `examples/figure_layout.md` | Short Nature-column sketch |
| Modify | `reference/backend-capability-map.md` | IDs e.g. `figure_compose`, `figure_journal_preset` |
| Modify | `reference/failure-modes.md` | Use composer for overview; invent sizes; silent mismatched clim |
| Modify | `reference/arpes-viewer-backend.md` | One-line cross-link |
| Modify | `SKILL.md` / `README.md` | One user-asked row — **Publication figure** (layout), not “new analysis skill” hype |
| Skip | Extending overview as publication | Keep overview separate |

---

### Task 1: `figure-layout.md` + example

**Files:**
- Create: `reference/figure-layout.md`
- Create: `examples/figure_layout.md`

- [ ] **Step 1: Write reference**

  Sections: Gate; Backend; JOURNAL_PRESETS table (cite upstream, don’t invent mm); Panel model (`Figure`/`Panel`); shared scale/limits; export path; vs overview / stack-plots; checklist.

- [ ] **Step 2: Example** — 2-panel sketch + preset.

- [ ] **Step 3: Commit**

  ```bash
  git commit -m "docs: publication figure layout (tools.figure)"
  ```

---

### Task 2: Wire capability + failure + SKILL/README

**Files:**
- Modify: `reference/backend-capability-map.md`
- Modify: `reference/failure-modes.md`
- Modify: `reference/arpes-viewer-backend.md`
- Modify: `SKILL.md`, `README.md`

- [ ] **Step 1: Capabilities** — `figure_compose`, `figure_journal_preset` → `figure-layout.md`.

- [ ] **Step 2: Failure modes** — composer ≠ overview; invent journal width; mismatched clim without echo; DIY full composer on pyarpes when viewer needed.

- [ ] **Step 3: SKILL hard rule / workflow** — if user asks pub figure → `figure-layout.md`. README one row.

- [ ] **Step 4: Commit**

  ```bash
  git commit -m "docs: wire figure layout into SKILL and capability map"
  ```

---

## Verification

- [ ] Grep: `JOURNAL_PRESETS` / `tools.figure` in `figure-layout.md`.
- [ ] Overview doc unchanged as quick-report source of truth.
- [ ] README row wording = layout/export, not “new ARPES analysis.”
- [ ] `git status` clean.

---

## Out of scope

- Replacing `default-overview-plots.md` / `stack-plots.md`.
- Full Qt figure GUI as required path.
- Vendoring painter code.
- Cleavage / other leftovers.

---

## Execution handoff

After **approve**: implement on `feat/figure-layout`. Local commits. Stop; ask push.
