# Folder manifest (session inventory)

Before analyzing files in a data folder, build a **durable inventory** on disk
so later turns can **recall** what exists without re-walking raw data or
pasting catalogs into chat.

This is **structured project memory** (JSON + optional Markdown summary) — not
vector RAG. Agents **read/query the file**; they do not embed the beamtime.
**Future (optional):** semantic retrieval (e.g. embeddings or a hosted file-search
API) may sit on top of this manifest without replacing it as the source of truth.

## When

| Situation | Action |
|-----------|--------|
| User points at a **folder** / beamtime / many files | Build or refresh manifest **first** |
| Manifest exists and raw mtimes/hashes unchanged | **Reuse**; do not rebuild unless asked |
| New files added / mtimes changed / user says refresh | Rebuild or patch changed rows |
| Single known file path | Manifest optional; still OK to add one row |

Give a **token note** before a full-folder **spectrum** load
(`reference/token-usage.md`). Prefer: list + **header-only peek** first;
`load_data` / overview only when user asks or for a chosen file.

## Where

```text
analysis/
  manifest.json          # source of truth (required)
  manifest.md            # short human table (optional but recommended)
  figures/…              # overview PNGs linked from rows when present
  kspace/…               # converted products linked when present
```

Paths are relative to the **analysis project root** (not inside the raw data
tree unless the user keeps analysis there).

## `manifest.json` schema

Top level:

```json
{
  "schema_version": 1,
  "created_utc": "ISO-8601",
  "updated_utc": "ISO-8601",
  "data_root": "/absolute/or/relative/raw/folder",
  "skill_ref": "arpes",
  "files": [ /* FileEntry */ ]
}
```

### `FileEntry` fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `stem` | string | yes | Filename without extension |
| `path` | string | yes | Preferred raw path to load |
| `path_alt` | string \| null | no | Sibling `.h5` / `.fits` if both exist |
| `ext` | string | yes | e.g. `.fits`, `.h5` |
| `preferred_loader` | string | yes | e.g. `arpes.io.load_data` + `location=MAESTRO` |
| `size_bytes` | int | yes | |
| `mtime_utc` | string | yes | File mtime ISO-8601 |
| `content_sha256` | string \| null | no | Optional; recompute on refresh if cheap |
| `log_comment` | string \| null | no | From measurement log if matched; comment only |
| `kind` | string | yes | See kind enum below |
| `kind_confidence` | string | no | `high` \| `medium` \| `low` |
| `kind_clues` | string[] | no | e.g. `["swept","span_12eV"]` |
| `shape` | int[] \| null | no | After header peek (NAXIS* / dataset shape) |
| `dims` | string[] \| null | no | Best-effort from header cards / HDF5 names — may be provisional |
| `hv_eV` | number \| null | no | Scalar hv if in header/attrs |
| `energy_span_eV` | number \| null | no | \|Emax−Emin\| if recoverable from header |
| `energy_axis` | string \| null | no | `Ek` \| `Eb` \| `E-EF` \| `ambiguous` |
| `peek_ok` | bool \| null | no | null = not peeked; prefer over legacy `load_ok` |
| `load_ok` | bool \| null | no | Legacy alias of `peek_ok` (header peek, not full load) |
| `load_error` | string \| null | no | Peek failure message |
| `overview_paths` | string[] | no | Relative paths to PNG(s) under `analysis/` |
| `product_paths` | string[] | no | e.g. `analysis/kspace/<stem>_k.npz` |
| `notes` | string \| null | no | Short free text |

### Kind enum

Use these strings (extend only if needed; document in `notes`):

`cut` · `core_level_2d` · `fermi` · `hv` · `xy` · `unknown` · `load_error`

Classify with existing rules: dims first; core-as-2D heuristics; log is comment
only (`reference/default-overview-plots.md`).

## Build / refresh algorithm

1. Enumerate data files under `data_root` (prefer `.fits` when sibling `.h5`
   exists — record both; set `path` to preferred).
2. Match measurement log by stem if a log is available → `log_comment`.
3. Cheap row: stem, paths, ext, size, mtime (and hash if enabled).
4. **Header-only peek** (default Pass B) — fill shape / hv / energy clues /
   kind guess. **Do not** call `arpes.io.load_data` here.
5. Write `manifest.json`; write `manifest.md` summary table (stem, kind, hv,
   shape, peek_ok, comment).
6. Chat: **short summary only** (counts by kind + path to manifest) — not the
   full JSON.

### Pass B — header peek (required method)

Already in the shared env (`astropy`, `h5py` — `pyarpes-env.md`). No new
download.

| Ext | How (no spectrum array) |
|-----|-------------------------|
| `.fits` / `.fit` | `astropy.io.fits.getheader(path)` and/or `fits.open(..., memmap=True)` → read **headers** / column names / `NAXIS*`; **do not** load table `.data` / Fixed_Spectra columns |
| `.h5` / `.hdf5` / NeXus-like | `h5py.File(path, "r")` → attrs + dataset `.shape` / names; **do not** `[:]` full arrays |
| Other | File size + ext only; mark `kind=unknown` / ask |

Extract when present: shape, motor/hv cards (e.g. `mono_eV`, `SF_HV`,
`LMOTOR*`), energy start/delta/n if in header, provisional kind. Echo that
dims/kind from header are **provisional** until a later full load.

```python
from astropy.io import fits

hdr0 = fits.getheader(path, 0)          # primary
# optional: hdr1 = fits.getheader(path, 1)  # table HDU — still header only
# shape clues: NAXIS*, NAXIS1, … or defer until overview load

# MH1 / HDF5
import h5py
with h5py.File(path, "r") as f:
    # walk groups; record dataset shapes + attrs; no f[…][:]
    pass
```

**Full `load_data`:** only Pass **C** (overview) or when user picks a file for
analysis — not for first folder mapping.

### Invalidation

Rebuild or update a row when:

- `mtime_utc` or `content_sha256` differs from the stored entry, or
- user requests refresh, or
- `data_root` changed.

Unchanged rows: keep overview/product links.

## Recall later (required habit)

Before opening raw files for a follow-up task:

1. Load `analysis/manifest.json` if present.
2. Filter by `kind` / stem / hv / `load_ok` as the user asked.
3. Open only the matching `path`s (or linked `product_paths` if analysis
   products suffice).
4. If manifest missing or stale → rebuild (with token note if large).

Do **not** re-paste the full catalog into chat when the manifest is enough.

## Lazy depth (recommended)

| Pass | What | Cost |
|------|------|------|
| **A — listing** | Paths, size, mtime, log comment, preferred ext | Low |
| **B — header peek** | Astropy FITS header / h5py attrs+shapes → shape, hv, kind guess | Low–medium |
| **C — overview** | `load_data` + PNGs per `default-overview-plots.md`; set `overview_paths` | Higher |

Default for a new folder: **A**, then **B** (header only). Sample or full **B**
OK. **C** / PyARPES load only when user wants quick-report figures or picks a
file to analyze.

## Agent rules

1. Manifest before multi-file analysis when a folder is in scope.
2. Prefer recall from manifest over rediscovering the folder.
3. Never dump full intensity arrays into the manifest or into chat.
4. Folder first-map = **header peek only** — no `load_data` / no spectrum.
5. Update `overview_paths` / `product_paths` when those artifacts are written.
6. Keep schema_version bumped if fields change incompatibly.

## Failure modes

See `reference/failure-modes.md` (rebuild every turn; paste full catalog;
ignore stale mtimes; treat log type as kind without dims).
