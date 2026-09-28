# MAESTRO measurement log + Pass A manifest (design)

**Date:** 2026-09-28  
**Status:** draft for user review  
**Scope:** MAESTRO-first folder logging; FITS-preferred identity; H5-rich metadata; CSV in data folder; Pass A merge into `analysis/manifest.json`.

## Problem

ARPES skill folder inventory (`analysis/manifest.json`) is weak on beamtime
narrative metadata (comments, T, polarization, SMU, analyzer). The user’s
`maestro_logger.py` already extracts that from MH1 `.h5` into
`MAESTRO_Measurement_Log.csv`, but: (1) H5-only, (2) not the skill default, (3)
not joined to the skill Pass A recipe.

Chat should answer “what did we measure / at what T / which file” from durable
on-disk metadata without dumping catalogs or loading spectra.

## Decisions (locked)

| Topic | Choice |
|-------|--------|
| Trigger output | **B** — CSV in data folder **and** Pass A merge into `analysis/manifest.json` |
| Sibling files | **A** — CSV `File Name` prefers `.fits`; rich columns from sibling `.h5` |
| Script location | **C** — canonical in skill `scripts/`; NAS copy OK if newer |
| Approach | Script-only CSV extractor + thin skill glue (not a package, not docs-only) |
| Graphify | **Out of scope** — do not auto-graphify after log |
| Token note on log | **No blanket note** — script is cheap; warn only if pasting full CSV/log into chat |

## Non-goals

- ANTARES / CASSIOPEE / other beamlines in this change  
- Pass B header peek / Pass C overview as part of the log trigger  
- Changing Measurement Type → skill `kind` (dims still win)  
- Semantic search / graphify / embeddings  
- Recursive multi-level beamtime crawl as default (flat folder; ask or per-leaf if parent)

## Background: FITS vs H5

Sibling MAESTRO exports are the **same scan in different containers**, not a
guaranteed 1:1 attribute clone.

- Evidence (`20260603_01003`): spectrum counts **bit-identical** after axis
  reorder; H5 uses `2D_Data/…`, FITS uses binary-table columns + primary cards.
- Rich lab fields (`Headers`, `Comments`, `0D_Data`) are what the existing
  logger parses — native to **H5**.
- Skill load path still prefers **`.fits` + PyARPES** when present
  (`formats-and-axes.md`).

Hence: FITS = preferred **identity / load path**; H5 = **metadata source** when
present.

## Design

### 1. Canonical logger script

**Path:** `scripts/maestro_measurement_log.py` (port of user’s
`maestro_logger.py`).

**CLI:**

```bash
python scripts/maestro_measurement_log.py "/path/to/maestro/folder"
```

- No interactive `input()` required when path is passed (agent-friendly).
- If no args: optional interactive prompt (keep user habit).

**Output:** `MAESTRO_Measurement_Log.csv` **inside the target folder**, same
filename and **same 14 columns** as today:

1. File Name  
2. Measurement Type  
3. Pre/Post Comments  
4. Photon Energy (eV)  
5. Polarization  
6–9. Cryostat A–D (K)  
10. Manipulator Position  
11. Deflection Settings  
12. SMU 1 & 2 Settings  
13. Analyzer Settings  
14. Energy Resolution  

**Enumerate:** flat `listdir` of that folder (same as current). Nested parent →
agent runs per leaf data dir or asks once.

**Per-stem file pick:**

1. Collect stems that have `.fits`/`.fit` and/or `.h5`.  
2. Prefer `.fits`/`.fit` as CSV `File Name` when present.  
3. Open sibling `.h5` for Headers / Comments / 0D (reuse existing flatten /
   `find_value` / cryo / manip / defl / SMU / analyzer / resolution logic).  
4. H5-only → `File Name` = `.h5`, same parse.  
5. FITS-only → best-effort from FITS cards if easy; else `N/A` fields; do not
   invent MH1 groups. (Full FITS-card parity is YAGNI for v1; identity + note
   is enough.)

**Measurement Type:** keep current heuristic as **log label only**
(`meas_type_log`). Never write it into manifest `kind`.

**Deps:** `h5py`, `numpy`. Sibling FITS presence = filesystem check (astropy
not required for Pass A log).

**Stdout:** quiet enough for agents — progress every N files or final summary;
avoid hundreds of lines forced into chat. Chat summary = counts + CSV path.

**NAS fork:** if user points at a newer local `maestro_logger.py` on the data
disk, prefer that path once and state which script ran; else skill
`scripts/maestro_measurement_log.py`.

### 2. Skill trigger + Pass A merge

**Triggers (examples):**

- “log the maestro data in XXX”  
- “build MAESTRO measurement log for XXX”  
- “refresh measurement log for this folder”

**Agent sequence:**

1. Resolve folder `XXX`.  
2. Run canonical (or newer NAS) logger → write/overwrite
   `XXX/MAESTRO_Measurement_Log.csv`.  
3. Chat: short summary only (N files, counts by Measurement Type, CSV path) —
   **never** paste full CSV.  
4. Pass A merge → `analysis/manifest.json` (+ optional `manifest.md`):  
   - `data_root` = XXX  
   - Join by **stem**  
   - `path` = preferred `.fits` if exists else `.h5`; `path_alt` = sibling  
   - `backend` = `pyarpes` for MAESTRO  
   - `preferred_loader` = `arpes.io.load_data` + `location=MAESTRO` (or micro/nano if known)  
   - `log_comment` ← Pre/Post Comments  
   - Optional object `maestro_log`: hv, pol, cryo A–D, manip, defl, SMU,
     analyzer, energy_res, `meas_type_log`  
   - `kind` = `unknown` until Pass B (dims win)  
5. Pass B / C **not** part of this trigger unless user also asks.

**CSV freshness:** if CSV exists and mtime ≥ newest data file in folder, reuse
unless user says refresh; still merge/update manifest if missing or stale.

**Token policy:** no blanket token note for running the logger. Token note only
if user asks to print/paste the whole log in chat, or for later Pass C full
loads (`token-usage.md`).

### 3. Docs / capability map

| File | Change |
|------|--------|
| `reference/maestro-measurement-log.md` | New: trigger, CLI, FITS-first+H5-meta, columns, NAS fork |
| `reference/folder-manifest.md` | Pass A MAESTRO recipe: run logger → CSV → merge fields |
| `SKILL.md` | Workflow bullet + hard-rule pointer for MAESTRO log trigger |
| `README.md` | One-liner under What it does / layout |
| `reference/backend-capability-map.md` | Row e.g. `maestro_measurement_log` |
| `reference/token-usage.md` | Clarify: logger script cheap; dumping CSV expensive |
| `examples/maestro_measurement_log.md` | Short recipe |
| `scripts/maestro_measurement_log.py` | Canonical script |

Bump `manifest.json` `schema_version` only if `maestro_log` is treated as a
breaking schema change; prefer additive optional field without bump, or bump to
2 if the skill already treats unknown fields as scrubbed — **prefer additive,
no bump** (agents ignore unknown keys safely).

### 4. Failure modes

| Failure | Behavior |
|---------|----------|
| No `.h5` and no `.fits` | Print clear error; no empty fake CSV rows |
| H5 parse error | Row with Measurement Type `ERROR` + message (keep current behavior) |
| macOS NAS “Bad file descriptor” on close | Keep current ignore-if-row-ready behavior |
| Ambiguous nested folders | Ask or run per leaf; do not silent-walk entire proposal tree |
| User Measurement Type vs dims | Log label only; skill `kind` from peek later |

## Success criteria

1. Phrase “log the maestro data in `<folder>`” → CSV appears in that folder with
   FITS-preferred `File Name` when siblings exist, and rich columns still filled
   from H5.  
2. `analysis/manifest.json` updated with stems + `log_comment` / `maestro_log`.  
3. Chat reply is short (counts + paths), not a CSV dump.  
4. Existing 14-column CSV consumers remain compatible.  
5. No graphify step. No forced Pass B/C on log trigger.

## Open points (none blocking)

- FITS-only stem: v1 may leave many columns `N/A` (H5 is the metadata path).  
- Micro vs nano `location=` left as today / ask when needed.

## Approval

- Section 1 (logger): approved  
- Section 2 (trigger + Pass A): approved with token-note amendment  
- Graphify: dropped  
- Location C + siblings A + output B: approved  
