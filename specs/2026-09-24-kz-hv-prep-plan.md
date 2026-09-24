# hv-stack EF prep (extend k/kz) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans after **user approves** this plan. Checkbox steps for tracking.

**Goal:** Document ARPES-data-browser `tools.kzmap` (box → per-hv EF → align → crop → optional norm) as a **backend subsection** of the existing k/kz skill — not a second user-facing skill.

**Architecture:** Docs-only. **Extend** `reference/k-and-kz-conversion.md` under `## hv → kz`. No new `reference/kz-*.md`, no new SKILL trigger, no new README “skill” row. Capability map: enrich Browser cells for existing IDs; optional step ID only if needed for living-list clarity (still points at same doc).

**Tech Stack:** Markdown; upstream `tools.kzmap` (`region_edc`, `fit_levels`, `align`, `normalise_totals`, `process_kz_map`, `KzMapResult`).

**Depends on:** Dual-backend + de-grid fences (do de-grid before this when grid present). Branch from `feat/degrid`.

**Queue:** Item **2 of 8** (SOLEIL leftovers). Framed as **extend existing**, not new skill.

## Global Constraints

- **One skill name:** “k / kz conversion.” User + LLM see one recipe.
- Package-first: call `tools.kzmap.*` / `tools.kzconv.*`; no invent EF DIY on viewer stem.
- Shared physics QC stays: report `EF_fit(hv)`, spread, hard-stop on junk / pinned / wild; plot under `analysis/`.
- **Order on viewer:** optional de-grid → **kzmap process** → offsets / V₀ → `tools.kzconv.to_kz_cube` (existing `convert_kz` row).
- On `pyarpes`: keep current angle-sum + `broadcast_model` + `shift_by` path; do **not** require `tools.kzmap`.
- If user on wrong backend for data → A/B/C/**D**.
- Local-first; push only when asked.
- Item 3 (V₀ scan / `scan_inner_potential`) **out of scope** — later subsection in same doc.

---

## File map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `reference/k-and-kz-conversion.md` | Backend fork under hv→kz: pyarpes vs arpes_viewer kz_map prep |
| Modify | `examples/convert_k_kz.md` | Short viewer `process_kz_map` sketch (same example file) |
| Modify | `reference/backend-capability-map.md` | Enrich Browser for `fit_fermi_edge` / `shift_energy`; optional `kz_map_align` step ID → same doc |
| Modify | `reference/failure-modes.md` | Skip viewer align; mid-φ default on viewer when box required; confuse kzmap with convert_kz |
| Modify | `reference/arpes-viewer-backend.md` | One-line: hv prep = k-and-kz-conversion (kzmap section) |
| Skip | New `reference/*.md` skill file | **Forbidden this item** |
| Skip | SKILL frontmatter / new README skill row | No second skill signal |

---

### Task 1: Extend `k-and-kz-conversion.md`

**Files:**
- Modify: `reference/k-and-kz-conversion.md`

- [ ] **Step 1: Reframe `## hv → kz` opening**

  Add short **backend fork** table at top of hv section:

  | Active backend | EF-align path | Then convert |
  |----------------|---------------|--------------|
  | `pyarpes` | Angle-summed near-EF + `broadcast_model` / `shift_by` (existing) | `convert_to_kspace` + V₀ |
  | `arpes_viewer` + kind `kz_map` | User **index box** + `tools.kzmap.process_kz_map` (new subsection) | `tools.kzconv.to_kz_cube` + V₀ |

  State: same skill; different package APIs. Do not present as separate capability family.

- [ ] **Step 2: New subsection `### arpes_viewer — kz_map prep (tools.kzmap)`**

  After existing PyARPES EF-align content (or clearly parallel under fork):

  1. **When** — loaded `kz_map` / hv stack on viewer; user asks EF align / “process kz map” / prep before kz convert.  
  2. **Not** — substitute for V₀ / `to_kz_cube`; that remains later in same doc.  
  3. **ROI** — one `index_region` box `((a0,a1),(e0,e1))` inclusive; same index range every hv. Prefer metal-like edge region; state box in report.  
  4. **Call** — prefer `process_kz_map(cube, energy, index_region, temperature=…, normalise=…)` over piecing steps unless debugging.  
  5. **Products** — aligned cube; common E axis (EF=0); `ef` per hv; `ok` mask; `trimmed`; `normalised` flag; report `KzMapResult.summary()` / `spread`.  
  6. **QC** — map onto existing hard-stop spirit: plot EF vs hv; fail if too many non-ok / wild; show interpolated neighbors when `ok` False.  
  7. **Optional norm** — `normalise_totals` only **after** align+crop; flux varies with hv; say when used.  
  8. **Order** — if detector grid: de-grid first (`degrid.md`); refuse confuse with post-k.  
  9. **Then** — continue existing V₀ + convert subsection (`tools.kzconv` on viewer).

- [ ] **Step 3: Pipeline summary**

  Dual bullet/text pipelines (pyarpes vs viewer) in `### Pipeline summary` — still one section.

- [ ] **Step 4: Rules summary row**

  One row: **Viewer kz_map prep** → `tools.kzmap.process_kz_map` (box ROI); then `kzconv`; not a separate skill.

- [ ] **Step 5: Commit (local)**

  ```bash
  git add reference/k-and-kz-conversion.md
  git commit -m "docs: viewer kz_map EF prep inside k/kz conversion"
  ```

---

### Task 2: Example + capability + failure + viewer note

**Files:**
- Modify: `examples/convert_k_kz.md`
- Modify: `reference/backend-capability-map.md`
- Modify: `reference/failure-modes.md`
- Modify: `reference/arpes-viewer-backend.md`

- [ ] **Step 1: Example** — add section “Viewer kz_map prep” in `convert_k_kz.md` (sketch `process_kz_map` + then point to V₀/`to_kz_cube`). Keep PyARPES sections.

- [ ] **Step 2: Capability map**

  - Enrich Browser cells: `fit_fermi_edge` → `tools.kzmap.fit_levels` / `process_kz_map`; `shift_energy` → `tools.kzmap.align`.  
  - Optional ID `kz_map_align` (step): Browser = `process_kz_map`; PyARPES = N/A (use hv EF path above); Ref = `k-and-kz-conversion.md` only.  
  - Do **not** add a second “skill” column or new reference file name.

- [ ] **Step 3: Failure modes**

  | Mistake | Fix |
  |---------||------|
  | Treat kzmap prep as kz conversion | Prep ≠ Å⁻¹; still need V₀ + `kzconv` / `convert_to_kspace` |
  | Skip align on viewer `kz_map` then claim EF | Run `process_kz_map` or state relative |
  | Mid-φ default when viewer expects box | Ask/state index box; same indices all hv |
  | Norm before align | Only after align+crop |
  | New “kz-map skill” in reports | Say k/kz conversion (viewer prep) |

- [ ] **Step 4: `arpes-viewer-backend.md`** — one line under tools: hv EF prep documented in `k-and-kz-conversion.md` (`tools.kzmap`).

- [ ] **Step 5: Commit**

  ```bash
  git add examples/convert_k_kz.md reference/backend-capability-map.md \
    reference/failure-modes.md reference/arpes-viewer-backend.md
  git commit -m "docs: wire viewer kz_map prep into capability map"
  ```

---

### Task 3: SKILL / README — light touch only

**Files:**
- Modify: `SKILL.md` only if hv bullet already lists PyARPES-only wording that would **mislead** on viewer — one clarifying phrase, **no new section title**.
- **Do not** add README skill row for “kz-map process.”

- [ ] **Step 1:** Grep SKILL for “angle-summed” / hv EF; if absolute “PyARPES only,” soften to “active backend package path (`k-and-kz-conversion.md`).”
- [ ] **Step 2:** Commit if changed.

---

## Verification

- [ ] No new `reference/kz-map*.md` or examples-only skill file as top-level skill.
- [ ] Grep: `process_kz_map` appears in `k-and-kz-conversion.md`.
- [ ] Grep README / SKILL: no second skill name “kz-map process.”
- [ ] Capability Browser cells mention `tools.kzmap`.
- [ ] `git status` clean after commits.

---

## Out of scope

- V₀ scan / `scan_inner_potential` (Item 3 — same doc later).
- FS bend, moiré, figure layout, CASSIOPEE folder deep, MBS spin deep.
- Vendoring browser code; Qt GUI as required path.
- Merging to main; push until asked.

---

## Execution handoff

After **approve**: implement Tasks 1–3 on `feat/kz-hv-prep`. Local commits. Stop; ask push/PR.
