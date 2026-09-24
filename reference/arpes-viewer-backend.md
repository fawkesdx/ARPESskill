# ARPES-data-browser backend (`arpes_viewer`)

Skill language stays capability IDs + recipes. This doc maps the **`arpes_viewer`**
backend to [ARPES-data-browser](https://github.com/DingPei1995/ARPES-data-browser)
(`ARPES_viewer/loader`, `ARPES_viewer/tools`).

Env: `reference/arpes-viewer-env.md`. Capability symbols: Browser column in
`reference/backend-capability-map.md`.

## Preferred surface (scripted)

Use **Qt-free** modules only:

| Module | Role |
|--------|------|
| `loader.registry` | `detect`, `list_entries`, `load`, `LoadOptions` |
| `loader.soleil` / `cassiopee` / `cassiopee_spin` / `native` | Beamline readers |
| `tools.*` | fermi, kspace, cutk, kzmap, kzconv, peaks, cutops, spin, degrid, … |

Do **not** import `ui.*` for routine analysis. Launch the GUI only when the
user asks (or for an interactive Γ/ROI handoff they accept):

```bash
cd /path/to/ARPES-data-browser/ARPES_viewer
python ARPES_viewer.py
```

## Route B — choose backend before load

1. User override (`pyarpes` | `arpes_viewer` | `user-map`) → use it.  
2. Else sniff (cheap; no full cube read):

| Cue | Backend |
|-----|---------|
| MAESTRO / ALS-style `.fits` (prefer sibling FITS over MH1 `.h5`) | `pyarpes` |
| SOLEIL ANTARES `.nxs` | `arpes_viewer` |
| CASSIOPEE Scienta text / numbered folders | `arpes_viewer` |
| CASSIOPEE MBS `.krx` / spin `.txt` | `arpes_viewer` |
| Ambiguous / conflict | **Ask** (one sharp question) |

3. Record on the stem / manifest row: `backend`, `loader`, `kind`, path, entry.  
4. Later steps on that stem **stay** on that backend unless the user chooses
   missing-feature **D** (switch backend) — see `package-first.md`.

**No silent `NxsScan` ↔ xarray bridge.** Export/convert only if the user asks.

## Load sketch

```python
import os
os.environ.setdefault("PYTHONPATH", "/path/to/ARPES_viewer")  # or set outside

from loader.registry import detect, list_entries, load, LoadOptions

path = "/data/scan.nxs"
print(detect(path))                 # Loader or None
print(list_entries(path))           # structure only — folder peek
scan = load(path, entry=None, options=LoadOptions())  # NxsScan
# scan.kind, axes, info — state in report; never invent labels
```

Override reader / axis order / scanned-axis role via `LoadOptions` when the
user says so (loader dialog semantics, scripted).

## Kinds (summary)

Upstream kinds include: `cut`, `map`, `k_map`, `kz_map`, `kz_map_k`,
`spem_1d`, `spem_4d`, `edc`, `mdc`, `spin_edc`. Full table: upstream README.
Skill recipes reuse the same physics names; map through capability IDs.

## Physics fences (viewer-specific)

- **`axis0.role`:** if the first map axis is not an emission angle
  (temperature, gate voltage, delay, …), **refuse k-conversion** and state
  why (upstream `role_is_angle`).  
- **CASSIOPEE MBS spin:** energy often stays **kinetic** until EF fit — say so;
  do not claim EF-aligned `eV` without calibration.  
- EF before quantitative k when the workflow requires it (same as PyARPES path).  
- Quick-report: angle-space unless user asks momentum.

## When a capability is missing here

Stop. Offer A/B/C/**D** (`package-first.md`). Example: PCA / NMF / ICA are
**N/A** on `arpes_viewer` → prefer **D** switch to `pyarpes` for that step/stem.

**De-grid** (MCP/mesh): `reference/degrid.md` — `tools.degrid`; pixel-locked
only; before k.

**hv / kz_map EF prep:** same skill as k/kz —
`reference/k-and-kz-conversion.md` (`tools.kzmap.process_kz_map` then
`tools.kzconv.to_kz_cube`). Not a separate skill.

**V₀ scan:** same doc — `tools.kzconv.scan_inner_potential` (ask `spacing`;
report uncertainty; user accept). Not a separate skill.

**Slit bend / FS correction:** same doc — `tools.analysis.fs_correction` /
`edge_flatness` (PyARPES: broadcast vs φ + quadratic). Not a separate skill.

**Moiré / mini-BZ:** `reference/bz-overlay.md` — `tools.moire` (+ `bz2d`).
Not a separate skill.

## See also

- `arpes-viewer-env.md` — interpreter / PYTHONPATH  
- `folder-manifest.md` — `list_entries` for Pass B peek  
- `degrid.md` — detector grid removal  
- `k-and-kz-conversion.md` — EF / slit bend / V₀ + k/kz convert  
- `bz-overlay.md` — BZ / moiré mini-BZ  
- `formats-and-axes.md` — PyARPES/MAESTRO notes (other backend)  
- Upstream README / CHANGELOG for loader and tool detail  
