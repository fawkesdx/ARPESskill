# MAESTRO measurement log (CSV + Pass A merge)

When the user points at an **ALS MAESTRO** flat data folder, extract beamtime
narrative metadata into `MAESTRO_Measurement_Log.csv` on disk, then merge into
`analysis/manifest.json` (Pass A). This is **not** a spectrum load, **not**
Pass B header peek, and **not** graphify.

Pass B / C: `reference/folder-manifest.md`. FITS vs H5 load path:
`reference/formats-and-axes.md`.

---

## When (triggers)

| User intent (examples) | Action |
|------------------------|--------|
| “log the maestro data in XXX” | Logger → CSV in XXX → Pass A merge |
| “build MAESTRO measurement log for XXX” | Same |
| “refresh measurement log for this folder” | Re-run logger (overwrite CSV) → merge |
| Manifest missing / stale after log exists | Merge only if CSV is fresh enough |

**Out of scope on this trigger alone:** Pass B peek, Pass C overview PNGs,
graphify, recursive crawl of nested proposal trees.

**Nested folders:** default = **flat** `listdir` of the resolved leaf folder. If
the user gives a parent with many subfolders, **ask once** or run per leaf — do
not silently walk the whole tree.

---

## Canonical scripts (both CLIs)

From the skill repo root (or with absolute paths):

```bash
python scripts/maestro_measurement_log.py "/path/to/maestro/folder"
python scripts/merge_maestro_log_to_manifest.py "/path/to/maestro/folder"
# optional second arg: analysis root (default: <data_folder>/analysis)
python scripts/merge_maestro_log_to_manifest.py "/path/to/data" "/path/to/analysis"
```

Logger flags:

```bash
python scripts/maestro_measurement_log.py "/path/to/folder" --verbose
```

- **Logger:** writes `<folder>/MAESTRO_Measurement_Log.csv`; exit 0 on success.
- **Merge:** reads that CSV; writes/updates `<analysis>/manifest.json` and
  optional `<analysis>/manifest.md`; prints manifest path on stdout.

Agents should pass the folder path on the command line (no interactive prompt).

---

## FITS-first identity, H5-rich metadata

Per **stem** (basename without extension):

1. Collect stems that have `.h5` and/or `.fits`/`.fit` in the **same flat folder**.
2. CSV column **File Name** prefers `.fits`/`.fit` when present; else `.h5`.
3. If sibling `.h5` exists → parse MH1 `Headers`, `Comments`, `0D_Data` for
   rich columns (same logic as the user’s original logger).
4. **H5-only** → `File Name` = `.h5`; full parse.
5. **FITS-only** → identity = FITS; most columns `N/A` or a fits-only label —
   **do not invent** MH1 groups from FITS in v1.

Skill load path still prefers FITS when both exist (`formats-and-axes.md`).

---

## CSV: 14 columns (fixed)

Written as `MAESTRO_Measurement_Log.csv` **inside the data folder** (not under
`analysis/`). Same header row as legacy loggers — keep compatible with existing
CSVs:

1. File Name  
2. Measurement Type  
3. Pre/Post Comments  
4. Photon Energy (eV)  
5. Polarization  
6. Cryostat A (K)  
7. Cryostat B (K)  
8. Cryostat C (K)  
9. Cryostat D (K)  
10. Manipulator Position  
11. Deflection Settings  
12. SMU 1 & 2 Settings  
13. Analyzer Settings  
14. Energy Resolution  

Parse errors → row with Measurement Type `ERROR` and message (keep current
behavior).

---

## Measurement Type ≠ manifest `kind`

| Field | Meaning |
|-------|---------|
| CSV **Measurement Type** | Heuristic **log label** only (`meas_type_log` in manifest) |
| Manifest **`kind`** | Skill enum from **dims / Pass B peek** — `cut`, `fermi`, `hv`, … |

**Never** copy Measurement Type into `kind`. Pass A merge sets `kind=unknown`
until Pass B (or keeps an existing non-unknown `kind` from a prior peek).

`log_comment` ← Pre/Post Comments only (comment text, not type).

---

## Quiet stdout (logger)

Default logger output is agent-friendly:

- Start: stem count  
- Progress: every 25 files (optional line)  
- End: **CSV path**  
- **`--verbose`:** one line per file  

Do **not** echo the full logger log into chat — summarize instead.

Merge script: print manifest path only.

---

## CSV freshness (reuse)

Before re-running the logger:

- If `MAESTRO_Measurement_Log.csv` exists and its mtime is **≥** the newest
  `.h5`/`.fits`/`.fit` in the folder, **reuse** the CSV unless the user asked
  to refresh.
- Still run **merge** if `analysis/manifest.json` is missing, `data_root` changed,
  or manifest is clearly stale vs CSV.

---

## NAS fork (user copy on disk)

Canonical script: `scripts/maestro_measurement_log.py` in this skill.

If the user points at a **newer** `maestro_logger.py` on the data volume
(e.g. under their beamtime folder), you may run **that path once**, state which
script ran, then merge from the CSV it wrote. Otherwise use the skill script.

---

## Pass A merge (manifest fields)

After CSV exists, run `merge_maestro_log_to_manifest.py`. Join rows by **stem**.

| Manifest field | Source |
|----------------|--------|
| `path` | Prefer `.fits`/`.fit`; else `.h5` |
| `path_alt` | Sibling `.h5` when `path` is FITS |
| `backend` | `pyarpes` |
| `preferred_loader` | `arpes.io.load_data location=MAESTRO` |
| `loader` | `MAESTRO` |
| `log_comment` | Pre/Post Comments |
| `maestro_log` | Structured copy of log columns (see `folder-manifest.md`) |
| `hv_eV` | Parsed from Photon Energy cell when possible |
| `kind` | `unknown` at Pass A unless already set by Pass B |

Full Pass A vs Pass B split: `reference/folder-manifest.md`.

---

## Chat summary (required shape)

Reply with **short** facts only:

- Data folder path  
- N stems / rows logged  
- Optional: counts by Measurement Type (one line)  
- Paths: `…/MAESTRO_Measurement_Log.csv`, `…/analysis/manifest.json`  

**Never** paste the full CSV or full `manifest.json` into chat.

No blanket token note for running logger + merge (cheap). Warn if the user asks
to dump the whole log in chat, or before Pass C full loads (`token-usage.md`).

---

## No graphify

Do **not** auto-run graphify or embedding pipelines after logging. Logging +
Pass A merge only unless the user asks for plots / peek / overview.

---

## Failure pointers

H5 parse errors, empty folders, FITS-only `N/A` columns, treating log type as
`kind`: `reference/failure-modes.md` (when wired). macOS NAS “Bad file
descriptor” on H5 close: logger may still keep the row if data was read.
