# ARPESskill dual backend — Design Spec

**Date:** 2026-09-24  
**Status:** Draft for user review  
**Branch:** `feat/dual-backend`  
**Repo:** https://github.com/fawkesdx/ARPESskill  

## 1. Purpose

Keep one portable Cursor/Claude skill (`arpes`) that speaks **one user
language** (capability IDs + physics recipes), and map each step onto the
**active analysis backend**:

| Backend ID | Package | Typical home |
|------------|---------|--------------|
| `pyarpes` | [PyARPES](https://arpes.readthedocs.io) | ALS / MAESTRO FITS; broad package recipes |
| `arpes_viewer` | [ARPES-data-browser](https://github.com/DingPei1995/ARPES-data-browser) (`ARPES_viewer`) | SOLEIL ANTARES `.nxs`; CASSIOPEE; MBS spin |
| `user-map` | Confirmed project callables | Lab-specific helpers |
| `inspect-only` | xarray / h5py last resort | After installs / maps declined |

Framing (product language): the skill **adapts to different user routines** —
backend, folder vs single-file, scripted vs GUI-on-ask — without inventing
axes or physics.

**Prior art:** Not claiming first ARPES agent skill. Cite PyARPES, ERLabPy
`arpes-analysis` skill, and ARPES-data-browser as related tools
(`specs/2026-09-24-prior-art-survey.md` on `feat/multi-agent`; copy or
cross-link into this branch when implementing README).

## 2. Locked decisions

| Decision | Choice |
|----------|--------|
| Load routing | **B** — sniff file / beamline; user override wins |
| Missing callable on active backend | **Stop and ask** A / B / C / **D** (below) |
| User language | Shared capability IDs; agent maps to backend symbols |
| Multi-agent roles | **Parked** (`feat/multi-agent` untouched by this work) |
| Data bridge | **No silent** `NxsScan` ↔ xarray conversion |
| GUI | Scripted default; launch GUI **only if user asks** (or Γ/ROI underdetermined handoff) |

### Missing-feature menu (locked)

When the skill recipe exists but the **active** backend has no mapped callable:

| Option | Meaning |
|--------|---------|
| **A** | Retry another official entry on the **same** backend |
| **B** | Map a helper **already in the user’s project** → capability ID |
| **C** | Write a **new** thin helper under `analysis/` — only if user clearly chooses C |
| **D** | **Switch backend** for this stem / this step (e.g. PCA on `pyarpes`) — ask first |

Never invent k / EF / Γ formulas or silently reimplement a missing package API.

## 3. Backend ownership (v1)

| Concern | `pyarpes` | `arpes_viewer` |
|---------|-----------|----------------|
| MAESTRO / ALS FITS (+ sibling FITS preference) | **Yes** | No |
| SOLEIL ANTARES `.nxs` | Weak / not primary | **Yes** (`loader.soleil`) |
| CASSIOPEE Scienta text / folders | No | **Yes** (`loader.cassiopee`) |
| CASSIOPEE MBS spin `.krx`/`.txt` | Partial via other paths | **Yes** (`loader.cassiopee_spin`) |
| Sklearn decomp (PCA/NMF/ICA/FA) | **Yes** (`*_along`) | No → use **D** |
| De-grid MCP/mesh | No skill recipe yet | **Yes** (`tools.degrid`) — follow-up recipe |
| Dichroism pattern | Skill pattern + xarray | `tools.cutops.combine` |
| Env | Python **3.8** shared | Python **≥3.9** + PyQt5/numpy/h5py/scipy (GUI optional for scripts) |

`loader/` and `tools/` in ARPES-data-browser are **Qt-free** — preferred agent
surface. Full `ARPES_viewer.py` UI only on ask.

## 4. Load routing algorithm (B)

1. If user set override (`pyarpes` | `arpes_viewer` | `user-map`) → use it.  
2. Else sniff path / siblings / header cheaply:  
   - MAESTRO / ALS-style `.fits` (or FITS preferred over MH1 `.h5`) → `pyarpes`  
   - ANTARES `.nxs` / CASSIOPEE series / MBS `.krx` → `arpes_viewer`  
   - Ambiguous or conflicting cues → **ask** (one sharp question).  
3. Record on the stem (and in `manifest.json` when cataloguing):  
   `backend`, `loader` name, `kind`, path, entry id if any.  
4. Later analysis on that stem **stays** on that backend unless user picks **D**.

### Folder catalog

- Header-only / structure-only first (no full spectrum reads).  
- FITS: existing astropy/h5py peek.  
- Viewer files: `loader.registry.list_entries` / detect (structure) — still not
  full cube load for every row.  
- Each `FileEntry` gains `backend` (and optional `loader`).

## 5. Capability map shape

Extend `reference/backend-capability-map.md`:

| ID | Meaning | PyARPES default | **Browser default** | User (session) | Reference |
|----|---------|-----------------|---------------------|----------------|-----------|

- Empty Browser cell = **N/A on `arpes_viewer`** → if user asks that ID while
  active backend is viewer → missing-feature menu (prefer **D** when PyARPES
  has it, e.g. `decomp_pca`).  
- Living-list rule unchanged: new workflow updates inventory in the same change.  
- Stack resolution order becomes: discover env for **routed** backend → offer
  install → decline → user-map → inspect-only.

Always state: `backend: pyarpes | arpes_viewer | user-map | inspect-only`.

## 6. Physics fences (both backends)

Hard rules in `SKILL.md` still apply:

- No invent axes / units / k formulas / Γ / V₀.  
- EF before quantitative k when the workflow requires it.  
- Quick-report stays angle-space unless user asks momentum.  
- CASSIOPEE spin MBS: energy may stay **kinetic** until EF fit — state that;
  do not pretend EF-aligned `eV` without calibration.  
- Viewer `axis0.role` (T / V / delay / not angle): refuse k-convert when role
  is not angle (package already refuses; skill must echo reason).

## 7. Env policy

| Backend | Doc | Policy |
|---------|-----|--------|
| PyARPES | `reference/pyarpes-env.md` | Reuse `arpes38` / `~/arpes-py38-venv`; ask before create |
| Viewer | **New** `reference/arpes-viewer-env.md` | Discover existing env; ask before create; do **not** install into PyARPES 3.8 env |

Never silently mix both stacks in one broken venv. Scripted imports of
`loader` / `tools` need the viewer env on `PATH` / interpreter for that stem.

## 8. Deliverables (implementation — after this spec approved)

1. `specs/2026-09-24-dual-backend-design.md` (this file).  
2. `reference/arpes-viewer-env.md` — discover / offer / Python ≥3.9 deps.  
3. `reference/arpes-viewer-backend.md` — load routing, kinds, axis0 role,
   ANTARES/CASSIOPEE notes, Qt-free vs GUI.  
4. Update `reference/backend-capability-map.md` — Browser column; stack order;
   reporting backend id.  
5. Update `reference/package-first.md` — A/B/C/**D**; dual-backend ask shape.  
6. Update `SKILL.md` — stack policy, hard rules, workflow load step, references.  
7. Update `reference/folder-manifest.md` — `backend` on rows; viewer list_entries.  
8. Update `reference/failure-modes.md` + `token-usage.md` as needed.  
9. `README.md` — Related tools: ARPES-data-browser; positioning line (adapt
   routines; not “first”).  
10. Optional example: `examples/dual_backend_load.md` (MAESTRO vs ANTARES sniff).  

**Follow-ups (not required for dual-load v1):** skill recipes for **degrid**,
V₀-scan polish, moiré BZ, figure composer — flag from browser survey.

## 9. Non-goals (v1)

- Unifying `NxsScan` and xarray into one in-memory model.  
- Porting MAESTRO loader into the browser or ANTARES into PyARPES.  
- Adding ERLabPy as a third backend (separate decision).  
- Implementing multi-agent Catalog/Overview/Analysis/Report.  
- Claiming novelty over ERLabPy / browser / PyARPES.

## 10. Success criteria

- ANTARES `.nxs` (no override) → `arpes_viewer` load path stated.  
- MAESTRO FITS (no override) → `pyarpes` load path stated.  
- Mixed folder → per-row `backend` in manifest; ambiguous → ask.  
- “Run PCA” on a viewer-backed stem → stop; offer **D** (and A/B/C).  
- Chat always names backend; no silent invent across stacks.  
- User override forces chosen backend even if sniff disagrees.

## 11. Open points (ok to resolve at implementation)

- Exact env name for viewer (`arpes-viewer` conda vs `~/arpes-viewer-venv`).  
- Whether `arpes_viewer` import path needs `PYTHONPATH=…/ARPES_viewer` or a
  future installable package — document whatever upstream supports.  
- How many capability rows get Browser symbols in v1 vs “N/A → D” stubs
  (minimum: load, list_entries, EF, k, kz, peak fit, dichro cutops, spin).

## 12. Git / process

- Develop on **`feat/dual-backend`** (from `main`).  
- Keep **`feat/multi-agent`** parked; do not merge multi-agent into this work.  
- Merge to `main` only after user-approved implementation PR.  
- Do not commit `.scratch/` clones of upstream repos into the skill tree.
