# Dual-backend (PyARPES + ARPES-data-browser) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire ARPESskill so one user language (capability IDs) maps onto either `pyarpes` or `arpes_viewer` (ARPES-data-browser), with sniff-based load routing (B), missing-fn A/B/C/D, and no silent data-model bridge.

**Architecture:** Docs-only skill update. Extend capability map with a Browser column; add viewer env + backend reference; update stack policy / package-first / folder manifest / SKILL / README. No Python package shipped in this repo. Multi-agent remains parked.

**Tech Stack:** Markdown skill docs; PyARPES (existing); ARPES-data-browser `loader/` + `tools/` (upstream, Qt-free for agents).

**Spec:** `specs/2026-09-24-dual-backend-design.md`  
**Branch:** `feat/dual-backend` (local-first; push only when user asks)

## Global Constraints

- Route **B**: sniff file/beamline; user override wins; ambiguous → ask.
- Missing callable → stop; offer **A/B/C/D** (D = switch backend). Never invent k/EF/Γ.
- No silent `NxsScan` ↔ xarray conversion.
- GUI: scripted `loader`/`tools` default; full viewer UI only if user asks.
- Separate envs: PyARPES 3.8 vs viewer ≥3.9 — never mix installs into one broken venv.
- Do not merge or depend on `feat/multi-agent` for this work.
- Do not commit `.scratch/` upstream clones.
- Living-list: any new capability ID updates `backend-capability-map.md` same change.
- Local commits OK; **do not push** unless user explicitly asks.

---

## File map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `reference/arpes-viewer-env.md` | Discover/offer viewer Python ≥3.9 env; deps; no mix with arpes38 |
| Create | `reference/arpes-viewer-backend.md` | Route B sniff table; kinds; axis0.role; kinetic spin; Qt-free vs GUI |
| Create | `examples/dual_backend_load.md` | MAESTRO vs ANTARES sniff + override example |
| Modify | `reference/backend-capability-map.md` | Add Browser default column; stack order; backend ids |
| Modify | `reference/package-first.md` | A/B/C/**D** ask shape; dual-backend wording |
| Modify | `reference/folder-manifest.md` | `backend` / `loader` on FileEntry; viewer list_entries peek |
| Modify | `reference/failure-modes.md` | Wrong backend / silent bridge / PCA-on-viewer |
| Modify | `reference/token-usage.md` | Brief note if needed (viewer list_entries cheap) |
| Modify | `SKILL.md` | Stack policy; hard rules; workflow; references |
| Modify | `README.md` | Related tools + adapt-routines line (no novelty claim) |

**Follow-ups (out of this plan):** degrid / moiré / V₀-scan / figure-composer recipes.

---

### Task 1: Viewer env + backend reference

**Files:**
- Create: `reference/arpes-viewer-env.md`
- Create: `reference/arpes-viewer-backend.md`

- [ ] **Step 1: Write `arpes-viewer-env.md`**

  Mirror structure of `pyarpes-env.md` (discover before create; ask before install):

  - Needs: Python ≥3.9, numpy, h5py, scipy; PyQt5/pyqtgraph for GUI only.
  - Suggested names: conda `arpes-viewer` or `~/arpes-viewer-venv` (pick one as recommended; note other OK).
  - Clone/path: user points at [DingPei1995/ARPES-data-browser](https://github.com/DingPei1995/ARPES-data-browser); scripted import needs `ARPES_viewer` on `PYTHONPATH` (or cwd) unless upstream installs later — state honestly.
  - **Hard:** never `pip install` viewer deps into PyARPES 3.8 env.
  - Checklist: discover → offer → verify `import loader` / `import tools` from that tree.

- [ ] **Step 2: Write `arpes-viewer-backend.md`**

  Include:

  1. Backend id `arpes_viewer`.
  2. Route B sniff table (MAESTRO/FITS → pyarpes; ANTARES nxs / CASSIOPEE / MBS krx → viewer; else ask).
  3. Override: user force wins.
  4. Preferred surface: `loader.registry` (`detect`, `list_entries`, `load`) + `tools.*` — no Qt.
  5. GUI: `python ARPES_viewer.py` only on ask / underdetermined handoff.
  6. Kinds summary (`cut`, `map`, `kz_map`, `spin_edc`, `spem_*`, …) — point at upstream README; do not duplicate whole manual.
  7. `axis0.role`: refuse k if not angle.
  8. MBS spin: kinetic until EF — state; don’t fake EF-aligned eV.
  9. Fence: stay on backend for stem unless user chooses **D**.
  10. Cross-link capability map + package-first A/B/C/D.

- [ ] **Step 3: Self-check**

  ```bash
  rg -n "invent|silent.*xarray|NxsScan.*xarray" reference/arpes-viewer-backend.md
  ```

  Expect: only **forbidden** / “no silent bridge” wording.

- [ ] **Step 4: Commit (local only)**

  ```bash
  git add reference/arpes-viewer-env.md reference/arpes-viewer-backend.md
  git commit -m "docs: ARPES-data-browser env + backend reference"
  ```

---

### Task 2: Capability map + package-first A/B/C/D

**Files:**
- Modify: `reference/backend-capability-map.md`
- Modify: `reference/package-first.md`

- [ ] **Step 1: Capability map header / stack order**

  - Add backend id `arpes_viewer` to “Always state active path”.
  - Stack resolution: routed backend env first → decline → user-map → inspect-only.
  - Change inventory table to include **Browser default** column.

- [ ] **Step 2: Fill Browser column (v1 minimum)**

  At least map (symbols from upstream; N/A where none):

  | ID | Browser default (sketch) |
  |----|--------------------------|
  | `load_spectrum` | `loader.registry.load` / soleil / cassiopee / cassiopee_spin |
  | `folder_header_peek` | `loader.registry.list_entries` / `detect` |
  | `folder_manifest` | thin glue (same) |
  | `state_axes` | `NxsScan` kind + axes / `info` |
  | `fit_fermi_edge` | `tools.fermi.fit_fermi_edge` / kzmap fits |
  | `shift_energy` | fermi / kzmap `align` |
  | `fit_peak` / `extract_edc_mdc` | `tools.peaks` + curve helpers |
  | `convert_k` | `tools.kspace.convert_map` / `tools.cutk.convert_cut` |
  | `convert_kz` | `tools.kzconv.to_kz_cube` |
  | `spin_*` (detect/plot as applicable) | `tools.spin` + MBS load |
  | `dichro_*` | `tools.cutops.combine` presets |
  | `decomp_pca` / nmf / ica / factor | **N/A** → D to pyarpes |
  | Others | N/A or fill if obvious in one pass; empty = N/A |

  Note empty Browser cell means N/A → missing menu.

- [ ] **Step 3: package-first ask shape**

  Extend A/B/C block to A/B/C/**D**:

  > … (A) retry same backend, (B) map your project helper, (C) new analysis/ helper, (D) **switch backend** for this stem/step (e.g. PCA on pyarpes). Which?

  Add row: silent NxsScan↔xarray = forbidden; offer D or export only if user asks.

- [ ] **Step 4: Commit (local only)**

  ```bash
  git add reference/backend-capability-map.md reference/package-first.md
  git commit -m "docs: Browser capability column + missing-fn D"
  ```

---

### Task 3: Folder manifest + failure / token notes

**Files:**
- Modify: `reference/folder-manifest.md`
- Modify: `reference/failure-modes.md`
- Modify: `reference/token-usage.md` (only if a row is clearly needed)

- [ ] **Step 1: folder-manifest**

  - Add `backend` (required when known) and optional `loader` to FileEntry fields.
  - Pass B: viewer paths use `list_entries` / detect — structure only.
  - Agent rule: record backend per row; mixed folders OK; ambiguous → ask before full load.

- [ ] **Step 2: failure-modes**

  Add rows e.g.:

  | Symptom | Fix |
  |---------||------|
  | Force PyARPES on ANTARES nxs without ask | Sniff → `arpes_viewer` or ask |
  | PCA on `arpes_viewer` stem silently DIY | Stop; offer D (pyarpes) / B / C |
  | Silent NxsScan ↔ xarray | Forbidden; ask D or user export |
  | Install viewer into arpes38 | Separate env (`arpes-viewer-env.md`) |

- [ ] **Step 3: token-usage** — one line: viewer `list_entries` is cheap; still no full-load folder dump.

- [ ] **Step 4: Commit (local only)**

  ```bash
  git add reference/folder-manifest.md reference/failure-modes.md reference/token-usage.md
  git commit -m "docs: dual-backend folder rows + failure modes"
  ```

---

### Task 4: SKILL + README + example

**Files:**
- Modify: `SKILL.md`
- Modify: `README.md`
- Create: `examples/dual_backend_load.md`

- [ ] **Step 1: SKILL stack policy**

  - Active path: `pyarpes` | `arpes_viewer` | `user-map` | `inspect-only`.
  - After folder/path known: run Route B (or override) before load.
  - Prefer scripted calls on active backend; GUI on ask.
  - Package-first → A/B/C/D.
  - Hard rule one-liner: no silent cross-backend data bridge.

- [ ] **Step 2: SKILL workflow**

  Insert early step: resolve backend (sniff/override) → ensure that env → then load.

- [ ] **Step 3: SKILL references**

  Link `arpes-viewer-env.md`, `arpes-viewer-backend.md`; keep pyarpes-env.

- [ ] **Step 4: README**

  - Related tools: ARPES-data-browser link.
  - Short positioning: adapts routines / dual backend; **not** “first” skill.
  - Optional: cite ERLabPy skill as related agent skill (honesty).

- [ ] **Step 5: Example**

  `examples/dual_backend_load.md`: MAESTRO FITS → pyarpes; ANTARES nxs → viewer; user override; PCA-on-viewer → offer D.

- [ ] **Step 6: Commit (local only)**

  ```bash
  git add SKILL.md README.md examples/dual_backend_load.md
  git commit -m "docs: wire dual-backend into SKILL and README"
  ```

---

### Task 5: Verify (local) — push only if user asks

**Files:** none new — verification only.

- [ ] **Step 1: Greps**

  ```bash
  rg -n "arpes_viewer|Browser default|A/B/C/D|switch backend" SKILL.md reference/ README.md examples/
  rg -n "backend" reference/folder-manifest.md
  rg -n "decomp_pca" reference/backend-capability-map.md
  ```

- [ ] **Step 2: Manual checklist**

  - [ ] ANTARES path documented → `arpes_viewer`
  - [ ] MAESTRO → `pyarpes`
  - [ ] PCA on viewer → D
  - [ ] No novelty / “first” claim in README
  - [ ] `.scratch/` still gitignored

- [ ] **Step 3: Stop**

  Report verification to user. **Do not** `git push` or open PR until user says push / PR / merge.

---

## Execution notes

- Prefer sequential Tasks 1→5 (2 depends on backend doc ids; 4 depends on 1–3 links).
- After merge to main (later): dual-backend live; `feat/multi-agent` still parked separately.
- Upstream API symbols may drift — capability cells say “check installed tree”; do not vendor browser code into this repo.
