# De-grid (detector MCP/mesh) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans after **user approves** this plan. Checkbox steps for tracking.

**Goal:** Add an agent skill recipe for removing detector grid (ANTARES MCP hex / CASSIOPEE Scienta mesh) via ARPES-data-browser `tools.degrid`, with hard “pixel-locked only / before k” fences.

**Architecture:** Docs-only. New `reference/degrid.md` + capability IDs + SKILL/README/example wire. **Backend: `arpes_viewer` only** (Browser column). PyARPES = N/A → offer **D** if user on `pyarpes` stem. No vendoring of upstream code.

**Tech Stack:** Markdown skill docs; upstream `tools.degrid` (`degrid_map`, `degrid_cut_with_grid`, `degrid_cut_notch`, `not_pixel_locked`).

**Depends on:** Dual-backend (`feat/dual-backend`) — Route B / `arpes_viewer` already shipped.

**Queue:** Item **1 of 8** (SOLEIL/browser leftovers). After merge → next: kz-map process.

## Global Constraints

- Package-first: call `tools.degrid.*` only; no invent Fourier DIY.
- **Do de-grid before** k-convert / FS bend / kz align / smooth / derivative — refuse if not pixel-locked (`not_pixel_locked`); say why.
- Map is its own reference; cut prefers `[grid]` from same lens/pass-energy map; notch fallback warns it also kills PE in those k-regions.
- GUI optional; scripted tools default.
- Living-list: capability rows same change.
- Local-first commits; push/PR only when user asks.
- Do not invent grid period / settings — use upstream defaults unless user overrides Advanced params.

---

## File map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `reference/degrid.md` | When / refuse / map vs cut / save products / checklist |
| Create | `examples/degrid.md` | Short ANTARES map + cut-with-grid sketch |
| Modify | `reference/backend-capability-map.md` | IDs `degrid_map`, `degrid_cut`, `degrid_pixel_lock` (+ Browser symbols) |
| Modify | `SKILL.md` | Hard rule + workflow step + references + examples |
| Modify | `README.md` | One row: De-grid |
| Modify | `reference/failure-modes.md` | De-grid after k / silent notch / invent DIY FFT |
| Modify | `reference/arpes-viewer-backend.md` | One-line cross-link to degrid recipe |

---

### Task 1: `reference/degrid.md` + example

**Files:**
- Create: `reference/degrid.md`
- Create: `examples/degrid.md`

- [ ] **Step 1: Write `degrid.md`**

  Sections:

  1. **Gate** — user asks de-grid / MCP grid / mesh / detector pattern. Not default overview.  
  2. **Backend** — `arpes_viewer` + `arpes-viewer-env.md`. If active `pyarpes` → stop; A/B/C/**D**.  
  3. **Hard refuse** — call / document `not_pixel_locked`: after k, FS correction, kz align, interpolate, smooth, differentiate → refuse + reason. **Do first** on raw detector pixels.  
  4. **Map path** — `tools.degrid.degrid_map(cube, …)` (or wrapped scan API if thin glue). Progress OK. Save de-gridded product + optional `[grid]` pattern to list/`analysis/`. Echo defaults (don’t invent Advanced).  
  5. **Cut path** — prefer `degrid_cut_with_grid` using listed grid from same settings; else `degrid_cut_notch` with **explicit warning** (removes PE in grid Fourier regions).  
  6. **Report** — before/after note; backend; map vs cut; whether grid pattern saved; notch warning if used.  
  7. **Checklist** — pixel-locked? backend? products under `analysis/`?  

  Capability IDs: `degrid_map`, `degrid_cut`, `degrid_pixel_lock` (check helper).

- [ ] **Step 2: Write `examples/degrid.md`** — ANTARES map de-grid then overview; cut using saved grid.

- [ ] **Step 3: Commit (local; push only if asked)**

  ```bash
  git add reference/degrid.md examples/degrid.md
  git commit -m "docs: add detector de-grid workflow (arpes_viewer)"
  ```

---

### Task 2: Capability map + failure + viewer cross-link

**Files:**
- Modify: `reference/backend-capability-map.md`
- Modify: `reference/failure-modes.md`
- Modify: `reference/arpes-viewer-backend.md`

- [ ] **Step 1: Inventory rows**

  | ID | Meaning | PyARPES | Browser | Reference |
  |----|---------|---------|---------|-----------|
  | `degrid_pixel_lock` | Refuse if not on detector pixels | | `tools.degrid.not_pixel_locked` | `degrid.md` |
  | `degrid_map` | Remove grid from map/kz_map | | `tools.degrid.degrid_map` | `degrid.md` |
  | `degrid_cut` | Cut with map grid or notch | | `degrid_cut_with_grid` / `degrid_cut_notch` | `degrid.md` |

- [ ] **Step 2: failure-modes** — after k; DIY FFT; silent notch without warn; de-grid on pyarpes without D.

- [ ] **Step 3: arpes-viewer-backend** — one line under analysis: de-grid → `degrid.md`.

- [ ] **Step 4: Commit**

  ```bash
  git add reference/backend-capability-map.md reference/failure-modes.md reference/arpes-viewer-backend.md
  git commit -m "docs: degrid capability IDs + failure modes"
  ```

---

### Task 3: SKILL + README wire

**Files:**
- Modify: `SKILL.md`
- Modify: `README.md`

- [ ] **Step 1: SKILL** — hard rule (user-asked; pixel-locked; viewer backend); workflow step; references; examples list. Update description frontmatter keyword `degrid` / MCP grid if space allows.

- [ ] **Step 2: README** — table row: De-grid | MCP/mesh via ARPES-data-browser `tools.degrid`; before k.

- [ ] **Step 3: Commit**

  ```bash
  git add SKILL.md README.md
  git commit -m "docs: wire de-grid into SKILL and README"
  ```

---

### Task 4: Verify — stop for user

- [ ] **Step 1: Greps**

  ```bash
  rg -n "degrid" SKILL.md README.md reference/ examples/
  rg -n "degrid_map|degrid_cut|not_pixel_locked" reference/
  ```

- [ ] **Step 2: Report** — ready for push/PR when user says. **Do not push** unless asked.

---

## Out of scope (this item)

- kz-map process, V₀ scan, CASSIOPEE folder, MBS spin deep dive, FS bend, moiré, figure composer (queue 2–8).
- Porting degrid into PyARPES.
- Changing upstream ARPES-data-browser.

## Branch note

Implement on **`feat/degrid`** branched from current `feat/dual-backend` (needs viewer backend docs), unless user prefers stack on `feat/dual-backend` itself. Default: **new `feat/degrid`** so dual-backend PR can merge independently.
