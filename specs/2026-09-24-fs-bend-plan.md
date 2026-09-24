# Slit / FS bend correction (extend k/kz) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans after **user approves** this plan. Checkbox steps for tracking.

**Goal:** Make **straight-slit / curved Fermi-edge** correction an explicit step inside the existing **k / kz** skill — same physics PyARPES already documents; map Browser `fs_correction`. **Not** a new skill.

**Architecture:** Docs-only. Extend `reference/k-and-kz-conversion.md`. Clarify that mean EF shift ≠ bend straighten. No `reference/fs-bend.md` skill file. No new README skill row.

**Tech Stack:** Markdown; PyARPES `broadcast_model(AffineBroadenedFD, …, "phi")` + `QuadraticModel` + `G.shift_by`; viewer `tools.analysis.fs_correction` + `tools.kzconv.edge_flatness`.

**Depends on:** Item 2–3 k/kz extensions on `feat/kz-hv-prep`. Branch: `feat/fs-bend` from that tip (not from CASSIOPEE load footnote branch).

**Queue:** Former Item 6 — reframed as **extend existing**, after user confirmed PyARPES already has it.

## Global Constraints

- **One skill:** k / kz. User/LLM see “EF / energy prep before convert,” not “FS bend skill.”
- Distinguish clearly:
  - **Uniform EF** — one shift (mean / per-hv) → edge ≈ 0  
  - **Slit bend** — shift **vs detector angle** (φ / slit) so edge is flat across slit  
- Prefer PyARPES official path; Browser `fs_correction` when on `arpes_viewer`.
- Gate: metal-like edge or user-picked flat feature; warn if no edge (insulator / far from EF).
- Order: optional de-grid → **bend straighten** (if needed) → per-hv EF align (stacks) → Γ / V₀ → convert.
- Check flatness (`edge_flatness` or span of `fd_center(phi)`); warn before kz if bend ≳ ~30 meV (viewer uses ~0.03 eV) — allow convert with warning.
- Package-first; no invent DIY poly outside package / documented viewer API.
- Local-first; push when asked.

---

## File map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `reference/k-and-kz-conversion.md` | New subsection under EF / before convert; dual-backend; fix cut sketch that mean-only shifts |
| Modify | `examples/convert_k_kz.md` | Short bend-correct sketch (PyARPES + optional viewer) |
| Modify | `reference/backend-capability-map.md` | Enrich `fit_fermi_edge` / `shift_energy`; optional step ID `fs_bend_correct` → same doc |
| Modify | `reference/failure-modes.md` | Mean-only when bend present; confuse with hv EF; confuse with band-enhance curvature |
| Modify | `reference/arpes-viewer-backend.md` | One line: FS correction in k-and-kz |
| Light | `SKILL.md` | One phrase under hv/k: straighten slit bend if curved |
| Skip | New skill / README skill row | **Forbidden** |

---

### Task 1: Extend `k-and-kz-conversion.md`

**Files:**
- Modify: `reference/k-and-kz-conversion.md`

- [ ] **Step 1: Add `## Slit bend / FS correction (before convert)`** (or nest under EF section)

  Content:

  1. **What** — straight-slit / analyzer: EF (or flat feature) bows vs detector angle; convert → fake dispersion / fake kz bend.  
  2. **Not** — per-hv mono drift (that’s hv EF align); not band-enhance `curvature`.  
  3. **When** — analysis convert; edge visibly curved vs φ; or `edge_flatness` / `fd_center(phi)` span large; user asks FS / slit correction.  
  4. **`pyarpes`:** cite notebook; pattern `broadcast_model(..., "phi")` → `QuadraticModel` on `fd_center` → `shift_by(edge, "eV")` evaluated on map `phi`. Do **not** stop at mean-only if bend is the problem.  
  5. **`arpes_viewer`:** `tools.analysis.fs_correction` (coeffs from picked flat feature); optional `edge_flatness` warn before `kzconv`.  
  6. **Maps:** fit on slit cut / θ-summed frame (analyzer curvature along slit); apply to full cube.  
  7. **Report:** method, bend span (eV), backend.

- [ ] **Step 2: Adjust cut sketch** — show mean shift as OK when flat; if `fd_center` vs φ disperses, use quadratic path (or ask).

- [ ] **Step 3: Pipeline / rules** — insert bend step; one rules row.

- [ ] **Step 4: Commit**

  ```bash
  git commit -m "docs: slit bend / FS correction inside k/kz"
  ```

---

### Task 2: Example + capability + failure + wire

**Files:**
- Modify: `examples/convert_k_kz.md`
- Modify: `reference/backend-capability-map.md`
- Modify: `reference/failure-modes.md`
- Modify: `reference/arpes-viewer-backend.md`
- Light: `SKILL.md`

- [ ] **Step 1: Example** — PyARPES quadratic-along-phi; note viewer `fs_correction`.

- [ ] **Step 2: Capability** — `fs_bend_correct` step ID: PyARPES = broadcast+quad+shift_by; Browser = `fs_correction` / `edge_flatness`; Ref = `k-and-kz-conversion.md`.

- [ ] **Step 3: Failure modes**

  | Mistake | Fix |
  |---------||------|
  | Mean-only EF when edge bows vs φ | Quadratic / `fs_correction` along slit |
  | Confuse slit bend with hv EF align | φ-dependent vs hv-dependent |
  | Confuse with band-enhance curvature | Different (`band-enhance.md`) |
  | New “FS bend skill” | Same k/kz skill |

- [ ] **Step 4: Commit**

  ```bash
  git commit -m "docs: wire slit bend into capability map"
  ```

---

## Verification

- [ ] No new skill file / README skill row.
- [ ] Grep: `QuadraticModel` or `fs_correction` in `k-and-kz-conversion.md`.
- [ ] Mean vs bend distinction explicit.
- [ ] `git status` clean.

---

## Out of scope

- Moiré / figure layout.
- Cleavage plane (optional later under V₀).
- Invent new fitter; GUI-required path.

---

## Execution handoff

After **approve**: implement on `feat/fs-bend`. Local commits. Stop; ask push.
