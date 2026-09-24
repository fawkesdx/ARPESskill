# Moiré BZ (extend bz-overlay) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans after **user approves** this plan. Checkbox steps for tracking.

**Goal:** Document **moiré / mini-BZ** overlay for bilayer / twisted 2D lattices as a subsection of the existing **BZ overlay** skill — not a new skill.

**Architecture:** Docs-only. **Extend** `reference/bz-overlay.md` + example. Capability map: Browser cells for `tools.moire` / enrich `bz_*`. No `reference/moire.md` as a separate skill.

**Tech Stack:** Markdown; upstream `tools.moire` (`moire_reciprocal_vectors`, `hex_moire_lattice_fast`, `moire_bz`) + `tools.bz2d`; PyARPES = single-lattice BZ only unless package has moiré API (verify — likely N/A → A/B/C/**D** or user cell).

**Depends on:** `feat/fs-bend` (pushed). Branch: `feat/moire-bz`.

**Queue:** Former Item 7 — **extend existing** (same anti-proliferation rule).

## Global Constraints

- **One skill name:** BZ overlay. User asks moiré / mini-BZ / twisted bilayer BZ → same recipe doc.
- Need **two** lattices (a, orientation / reciprocal vectors) from **user** — do not invent twist or a₀.
- Prefer general `moire_reciprocal_vectors`; `hex_moire_lattice_fast` = hex equal-type fast path (twist fold [0,30]° caveat; unequal-a less verified — echo upstream).
- Draw with `moire_bz` / `bz2d` Wigner–Seitz — package-first; no DIY hexagon.
- Still prefer **k-converted** map; Γ policy unchanged (`k-and-kz-conversion.md`).
- `pyarpes`: if no moiré API → state gap; offer **D** (viewer) if data on viewer, or user-supplied moiré cell into existing `bz_plot`, or A/B/C — no invent formula.
- Cleavage / V₀ spacing out of scope.
- Local-first; push when asked.

---

## File map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `reference/bz-overlay.md` | Section: Moiré / mini-BZ (gate, inputs, APIs, fences) |
| Modify | `examples/bz_overlay.md` | Short moiré sketch |
| Modify | `reference/backend-capability-map.md` | ID `bz_moire` (or enrich `bz_plot`); Browser = `tools.moire` |
| Modify | `reference/failure-modes.md` | Invent twist/a; hex-fast past 30° without fold; DIY moiré; new skill name |
| Modify | `reference/arpes-viewer-backend.md` | One line → bz-overlay moiré |
| Light | `SKILL.md` | BZ bullet: optional moiré bilayer |
| Skip | New moiré skill / README skill row | **Forbidden** |

---

### Task 1: Extend `bz-overlay.md` + example

**Files:**
- Modify: `reference/bz-overlay.md`
- Modify: `examples/bz_overlay.md`

- [ ] **Step 1: New section `## Moiré / mini-BZ (bilayer)`**

  1. **Gate:** user asks moiré BZ / mini-BZ / twisted bilayer / two-lattice BZ.  
  2. **Backend:** primarily `arpes_viewer` `tools.moire` (+ `bz2d`). PyARPES: N/A for auto moiré → D / user cell / ask.  
  3. **Inputs (ask):** layer1 & layer2 lattice constants or reciprocal vectors; twist (deg) or relative rotation; lattice type if using hex fast path.  
  4. **APIs:** prefer `moire_reciprocal_vectors` → `moire_bz` / WS cell; hex same-type → optional `hex_moire_lattice_fast` with caveats (≤30° or fold; unequal-a prefer general).  
  5. **Overlay** on k-map like single BZ; echo a_moire / gm vectors / twist.  
  6. **Not:** invent graphene twist magic angles; not 3D data-on-BZ.

- [ ] **Step 2: Hard rules / checklist** — one moiré bullet each.

- [ ] **Step 3: Example** — sketch two hex layers + `moire_reciprocal_vectors` / `moire_bz`.

- [ ] **Step 4: Commit**

  ```bash
  git commit -m "docs: moire mini-BZ inside bz-overlay"
  ```

---

### Task 2: Capability + failure + wire

**Files:**
- Modify: `reference/backend-capability-map.md`
- Modify: `reference/failure-modes.md`
- Modify: `reference/arpes-viewer-backend.md`
- Light: `SKILL.md` / `README.md` BZ row only if needed

- [ ] **Step 1:** Capability `bz_moire` — Browser `tools.moire.*`; PyARPES N/A (user cell or D); Ref `bz-overlay.md`. Enrich `bz_plot` Browser note: `bz2d`/`bz3d`.

- [ ] **Step 2: Failure modes**

  | Mistake | Fix |
  |---------||------|
  | Invent twist / a₀ for moiré | Ask both layers |
  | `hex_moire_lattice_fast` past 30° without fold | Fold or use `moire_reciprocal_vectors` |
  | DIY moiré G vectors | Package `tools.moire` |
  | New “moiré skill” | Same BZ overlay skill |
  | Moiré on pyarpes silently DIY | Stop; D / user cell / ask |

- [ ] **Step 3: Commit**

  ```bash
  git commit -m "docs: wire moire BZ into capability map"
  ```

---

## Verification

- [ ] No `reference/moire.md` skill file.
- [ ] Grep: `moire_reciprocal_vectors` in `bz-overlay.md`.
- [ ] README/SKILL: no second skill name “moiré.”
- [ ] `git status` clean.

---

## Out of scope

- Figure composer (Item 8 / maybe).
- Cleavage plane from kz period.
- 3D BZ data overlay.
- Vendoring code.

---

## Execution handoff

After **approve**: implement on `feat/moire-bz`. Local commits. Stop; ask push.
