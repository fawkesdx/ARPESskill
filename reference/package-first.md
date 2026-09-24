# Package-first policy (do not invent loaders)

This skill drives **existing callables** on the **active backend**: **PyARPES**
(`pyarpes`), **ARPES-data-browser** (`arpes_viewer` — `loader`/`tools`), or a
**confirmed user-map** (`backend-capability-map.md`). It is not a license to
rewrite ARPES infrastructure in `analysis/`.

## Order of preference

1. **Active package backend** public API — PyARPES (`load_data`,
   `convert_to_kspace`, fit models, …) **or** viewer (`loader.registry.load`,
   `tools.*`) per Route B / override (`arpes-viewer-backend.md`).
2. **Confirmed user-map** — project functions mapped to capability IDs after
   search + user confirm (`backend-capability-map.md`). Optional persist:
   project `analysis/backend_map.json`.
3. **Already in the user’s project** — import and call existing
   loaders/scripts when they are the better path (do not duplicate).
4. **Thin glue only** — short scripts that *call* those APIs and save plots under
   `analysis/` (orchestration, not a new library).
5. **New custom loader / reimplementation** — **only after asking the user**
   (option **C** below).

When adding a **new skill workflow**, document PyARPES first, fill Browser
defaults when applicable, and **update the capability inventory** in the same
change (living-list rule).

## Before writing new code

**STOP and ask** if you are about to:

- Write a new HDF5/FITS/NeXus loader instead of the active backend’s loader
- Reimplement k-conversion, EDC/MDC extract, or peak fitting by hand
- Invent **Doniach–Šunjić** or other XPS lineshapes not in the active backend
- Invent a **Fermi-surface / Γ center finder** instead of package offsets /
  user input / pocket helpers / GUI handoff
- Invent **photon-momentum** or beamline **incidence** formulas / angles not in
  `beamline-geometry.md` or user/staff input
- Invent **symmetrize**, bare-FD divide, or a **gap/Δ fitter** instead of
  package helpers (`near-ef-gap.md`)
- Copy large chunks of package logic into `analysis/`
- Bypass the active backend because the first entry point failed
- Silently convert **`NxsScan` ↔ xarray** between backends

Ask in this shape (feature missing / incomplete on **active** backend):

> Active backend `[pyarpes|arpes_viewer]` failed or lacks this capability:
> [exact error / missing ID]. I can (A) retry another official entry on the
> **same** backend, (B) **map helpers already in your project** to capability
> IDs (`backend-capability-map.md`), (C) write a **new** custom helper under
> `analysis/` (not ideal), or (D) **switch backend** for this stem/step (e.g.
> PCA on `pyarpes` when on `arpes_viewer`). Which do you want?

If the user already declined the shared env for that backend, prefer proposing
**(B)** (or **D** when the other package has the callable) before inspect-only.

Do **not** start (C) until the user clearly chooses it.  
Do **not** call (B) mappings until the user confirms the proposed map.  
Do **not** switch backends (**D**) or bridge data models until the user
clearly chooses it.

## Allowed without asking

- Small analysis scripts that **import** package functions and write figures/reports
- One-off `sel` / `isel` / plot after a successful package load
- Sanity prints of `.dims` / `.coords` / `.attrs`

## Not allowed silently

| Bad habit | Correct |
|-----------|---------|
| Custom `maestro_*.py` loader without asking | Report plugin failure; ask A/B/C/**D** |
| Hand-rolled Voigt fit when package peaks exist | Use active-backend fit models |
| DIY angle→k with ad-hoc formulas | Use mapped `convert_k`; state assumptions |
| Silent `NxsScan` ↔ xarray bridge | Forbidden; ask **D** or user export |
| DIY FS center / Γ from invent centroid code | Offsets / user / pocket helpers / GUI / **ask** |
| DIY symmetrize / bare FD / custom gap Δ | `gap.symmetrize` + resolution-broadened FD; ask if missing |
| DIY Σ from linewidth / invent k-dependent Σ | `to_self_energy` / `fit_for_self_energy`; k-independent only |
| DIY Laplacian / Sobel “sharpen” | Package `curvature` + `minimum_gradient` (`band-enhance.md`) |
| DIY pocket centroid / ellipse / kF | `pocket_parameters` / `curves_along_pocket` (`fs-pocket.md`) |
| DIY Wiener / invent PSF / silent RL | `gaussian_filter_arr` or `deconvolve_rl` + stated PSF (`smooth-deconvolve.md`) |
| DIY pass-energy / invent ΔE tables | `resolution.md` package helpers or **ask** |
| DIY polynomial bg / wrong Shirley on valence | Shirley / hull / incoherent per `backgrounds.md` |
| DIY hexagon / invent lattice for BZ | `bz_plot` / `overplot_standard` / user cell (`bz-overlay.md`) |
| DIY reshape rebin / silent intensity normalize | `rebin` / `normalize_dim` (`axis-prep.md`) |
| DIY shapely / invent mask polygon | `apply_mask` / `.where` (`masks.md`) |
| DIY np.correlate align / invent stitch | `align` / `align1d` / `align2d` (`align.md`) |
| DIY sklearn PCA/NMF unwrap | `pca_along` / `nmf_along` / … (`decomposition.md`) |
| DIY waterfall / invent ToF σ | `stack_dispersion_plot` / `plot_with_std` (`stack-plots.md`) |
| Full `load_data` for every file when mapping a folder | Header peek first (`folder-manifest.md`); spectrum load later |
| DIY dichroism without null-ROI scale | Pattern in `dichroism.md` (not a package module) |
| Call user project code without confirm | Propose capability map; wait (`backend-capability-map.md`) |
| New workflow with no capability row | Living-list: update inventory same change |
| “PyARPES can’t do MH1” → immediately rewrite | Document limitation; ask before new loader |

## MAESTRO decision tree

1. Look for a **`.fits`** (or `.fit`) for the scan. If present →
   `load_data(path, location="MAESTRO")` (or micro/nano location if known).
2. Pick the main spectrum variable carefully (largest `spectrum*`; skip
   `*_num_*` / monitor-like names) — see `formats-and-axes.md`.
3. If only **MH1 `.h5`** exists (or FITS load fails): quote the error; try
   another official `location=` / plugin entry if documented.
4. Check whether the **user’s project** already has an MH1 / custom helper —
   **use that** before writing anything new.
5. If still stuck → **ask** A/B/C/**D** above. Do not silently invent an MH1 loader
   or bridge to another backend without asking.
   or invent `rot90` / axis renames to “fix” the plot.

## After user approves custom code

- Keep it **minimal**, under the user’s analysis folder.
- Document that it is a **workaround**, not a replacement for the skill’s
  package path.
- Still never invent axis names/units — read from file metadata.
