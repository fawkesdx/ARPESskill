---
name: arpes
description: >
  Load and analyze ARPES photoemission data with correct axes, units,
  EDC/MDC extraction, Gaussian/Lorentzian/Voigt peak fitting, k-space
  conversion, photon-energy to kz conversion, near-EF gap/pseudogap,
  spatial XY / nanoARPES scans, Spin-ARPES (SARPES), in-operando parameter
  scans, time-resolved / pump–probe ARPES (delay, t0, ΔI), single-band
  self-energy (Σ), band enhance (curvature / minimum gradient), and Fermi-surface
  pocket analysis, smooth / deconvolution, experimental resolution estimates,
  background subtraction (Shirley / hull / incoherent), Brillouin-zone /
  high-symmetry path overlays, axis prep (rebin / symmetrize / normalize /
  sort / condense), data masks (boolean / polygon), correlation alignment
  of spectra, sklearn-style decomposition (PCA / NMF / ICA / factor analysis),
  specialized plots (stack / false-color / ToF±σ), forward k cuts through
  angular points/pairs, and CP/CM dichroism (null-ROI scale then diff/asym)
  via PyARPES or a confirmed user-project capability map. Use when working
  with ARPES spectra, Fermi surfaces, EDC, MDC, spin-ARPES, trARPES,
  pump-probe, in-operando, dosing, gated devices, self-energy, curvature,
  minimum gradient, FS pocket, smooth, deconvolution, resolution, background,
  Shirley, Brillouin zone, BZ overlay, rebin, symmetrize, normalize_dim, mask,
  polygon mask, align, register, shift spectra, PCA, NMF, ICA, stack plot,
  false color, ToF, forward k, convert_through_angular, dichroism, CP, CM,
  circular dichroism, ANTARES, MAESTRO or NeXus/HDF5 ARPES files,
  angle-to-momentum conversion, hv/kz scans, spatial maps, nanoARPES,
  pseudogap, or PyARPES.
---

# ARPES

## When to use

User or task involves ARPES spectra, Fermi maps, EDC/MDC, peak fitting,
k or kz conversion, spatial XY / nanoARPES maps, Spin-ARPES / SARPES,
in-operando parameter scans (dose, gate, current, field, T), time-resolved /
pump–probe ARPES (trARPES), self-energy / Σ, band enhance (curvature /
minimum gradient), FS pocket, smooth / deconvolution, resolution estimates,
background subtraction, BZ / high-symmetry path overlay, axis prep (rebin /
symmetrize / normalize), masks (boolean / polygon), spectrum alignment,
PCA/NMF/ICA decomposition, stack / false-color / ToF±σ plots, forward-k
point/pair cuts, CP/CM dichroism, MAESTRO/ANTARES/NeXus/HDF5/Igor ARPES
files, or PyARPES.

## What reduction means

In ARPES, **reduction** does not mean compress the file. It means turning a
raw multidimensional scan into analysis products: energy/momentum cuts,
EDC/MDC, Fermi-surface maps, fitted dispersions, k- and kz-converted
volumes, etc.

## Stack policy

1. Prefer **PyARPES** for analysis (fit, k, kz).
2. **At session start (and before any analysis):** discover a working PyARPES
   **3.8** interpreter — prefer **shared** env (`reference/pyarpes-env.md`):
   conda `arpes38` → `~/arpes-py38-venv` → legacy names → project `.venv-arpes`
   only if already present. Verify:
   `…/python -c "import arpes, sys; print(sys.executable, sys.version_info[:2])"`
   PyARPES requires `>=3.8,<3.9` — not 3.9+.
3. **If none / wrong Python — STOP and ask** (do not silently fall back; do not
   `pip install arpes` into the current env):
   - Explain: needs **dedicated Python 3.8**; prefer **one shared env** so
     projects reuse it (not a new install per folder).
   - Ask: *Reuse/create shared env — conda `arpes38` (Mac) or
     `~/arpes-py38-venv` — and install PyARPES?* (Project `.venv-arpes` only
     if you want isolation.)
   - Wait for yes/no.
   - If **yes**: follow `reference/pyarpes-env.md` (discover → create shared →
     install → re-check). If `python3.8` missing, ask Homebrew vs conda
     (or user 3.8 path) before inventing installs.
   - If **no**: **user-map** path (`reference/backend-capability-map.md`);
     only then xarray/h5py inspect-only. State path explicitly.
4. After setup, run with that env’s **absolute** `…/bin/python` (state path).
5. Always state backend: `pyarpes` | `user-map` | `inspect-only`.
6. TensorSpec / TensorSpec_GUI: deferred named backend later (not wired).
7. **Living list:** every new skill workflow ships PyARPES-first docs **and**
   new/updated rows in `reference/backend-capability-map.md` in the same change.

## Hard rules

- Never invent axis names or units.
- Never treat detector angle as momentum without conversion + stated assumptions.
- Never hv→kz without stating inner potential V₀ (or that it is unknown).
- Never claim Γ found without method (manual / fit / model).
- Never report fits without naming lineshape (+ background if used).
- **Peak fitting:** backend models only (PyARPES or confirmed user-map; core →
  then EDC/MDC); ask before any new lineshape (`reference/edc-mdc-fitting.md`).
  After valence broadcast: default E vs k / width plots; linear or parabolic on
  E(k) → report vF / m* when asked by that workflow (prefer k-space).
- **Near-EF / gap / pseudogap (cuts, user-asked only):** metal-ref EF → shift
  sample; optional divide by **resolution-broadened** FD (state T + resolution);
  if gap/pseudogap → symmetrize EDC about E=0 (`arpes.analysis.gap.symmetrize`);
  state p–h symmetry; ask before inventing a Δ fitter
  (`reference/near-ef-gap.md`).
- **Spatial XY scans (`x` & `y` n>1):** follow `reference/spatial-xy-scans.md` —
  spectroscopic ROI \(R\) for the XY map (user box or stated default); hot spot =
  argmax of \(I_R\); quick-report spatial set; then **reuse** cut / core / Fermi /
  hv recipes at hot spot or ROI; pixel broadcast only if asked.
- **Spin-ARPES / SARPES:** if up/down or I+P channels exist →
  `reference/spin-arpes.md` (package `sarpes` + spin plots; ask Sherman;
  Spin-EDC and spin cuts; reuse fits on channels / total I).
  Photon **CP/CM dichroism** (not spin) → `reference/dichroism.md`.
- **In-operando / param scans:** external axis \(P\) (dose, gate V, sample I, B,
  T, …) → `reference/in-operando-param-scans.md` (confirm meaning/units; mid
  \(P^*\) or ask if stepped; reuse kind recipes; no invent coverage/transport math).
  Pump–probe **`delay`** → use `reference/tr-arpes.md` instead (t0 + Δ maps).
- **trARPES / pump–probe:** `delay` dim → `reference/tr-arpes.md` (t0; delay\*
  nearest ≥ t0; package `tarpes` relative change; reuse kind recipes at slice).
- **Self-energy / Σ (user-asked):** single-band cut → `reference/self-energy.md`
  (path C: reuse MDC broadcast if present, else `fit_for_self_energy`; bare band
  default `ransac_linear`; lifetime only if asked).
- **Band enhance (user-asked):** 2D cut → `reference/band-enhance.md` (both
  `curvature` + `minimum_gradient` side by side; not intensity; no centers/EF
  from these alone).
- **FS pocket (user-asked):** one closed sheet → `reference/fs-pocket.md`
  (center = user or `pocket_parameters` if clearly one pocket; curves; EDCs ask).
- **Smooth / deconvolve (user-asked):** `reference/smooth-deconvolve.md`
  (gaussian smooth = noise default; RL/ICE only on explicit ask + stated PSF).
- **Resolution (user-asked / FD needs width):** `reference/resolution.md`
  (package estimates; ask if endstation tables missing — no invent).
- **Backgrounds (user-asked):** `reference/backgrounds.md` (core→Shirley;
  valence→hull; above-EF incoherent only if asked).
- **BZ overlay (user-asked):** `reference/bz-overlay.md` (prefer k-space; user
  cell / path wins; `overplot_standard` only for graphene/ws2/wse2→`wwe2`; ase
  optional; no invent lattice; no 3D data-on-BZ).
- **Axis prep (user-asked):** `reference/axis-prep.md` (rebin / symmetrize_axis /
  normalize_dim / sort_axis / condense — echo dims; no silent normalize before
  fits).
- **Masks (user-asked):** `reference/masks.md` (boolean `.where` or package
  polygon `apply_mask`; GUI ask only; echo condition/vertices).
- **Align (user-asked):** `reference/align.md` (correlation `align` → unitful
  offset; ask before apply; not stitch).
- **Decomposition (user-asked):** `reference/decomposition.md` (PCA / NMF / ICA /
  factor analysis via `*_along`; echo axes + n_components; NMF non-neg).
- **Stack / false-color / ToF±σ (user-asked):** `reference/stack-plots.md`
  (package plot helpers; no invent σ).
- Prefer scripted **calls to the active backend** (PyARPES or confirmed user-map)
  + matplotlib over launching Qt/Bokeh GUIs.
- **Package-first:** use PyARPES / confirmed user-map callables / existing
  project APIs; do **not** write a new loader or reimplement package features
  without asking (see `reference/package-first.md`,
  `reference/backend-capability-map.md`).
- Prefer existing project loaders before writing new ones — and **ask** before
  any new loader.
- **Capability map living list:** when inserting a new analysis workflow, add
  PyARPES-default row(s) to `reference/backend-capability-map.md` in the same
  change so later sessions can map user replacements.
- **Never skip the PyARPES / Python 3.8 venv question** when `import arpes`
  fails or `sys.version_info` is not `(3, 8)`.
- **Never `pip install arpes` into Python 3.9+** or into the user’s default env
  without asking first.
- **Never silently fall back** to xarray/h5py without the user declining the
  dedicated venv (or explicitly choosing inspect-only).
- **Warn before high-token steps** (see `reference/token-usage.md`) — inform,
  do not discourage; offer a lighter path when useful.
- **Fermi map / hv–kz reports:** include the **overview trio** — see
  `reference/default-overview-plots.md`.
- **Echo overview assumptions** in reports (kind from dims; center slices;
  no silent EF recal; anti-claims on Γ / k / EF / kz) — see
  `reference/default-overview-plots.md` § Default overview assumptions.
- **No k/kz in quick report** — overview trios stay angle-space; convert only
  in analysis / when user asks (`reference/k-and-kz-conversion.md`).
- **State energy axis** on load (Ek / Eb / E−EF / ambiguous).
- **Before cut or Fermi map → k:** PyARPES EF finder; always report EF_fit +
  deviation from 0 eV; charging warn if claimed E−EF/Eb and `|EF_fit| > 50 meV`;
  then shift EF→0. Package `convert_to_kspace` only — no invent formulas.
- **Γ for k conversion:** user offset wins. Cuts may use labeled provisional
  nearest-0°. **Fermi maps:** package `S.offsets` / optional `pocket_parameters`
  / optional `ktool` only — else **ask**; never invent a center finder
  (`reference/k-and-kz-conversion.md`).
- **hv → kz:** EF-align **per hv** on an **angle-integrated** near-EF edge
  (do not use mid-φ as default); QC + plot EF_fit vs hv; per-slice report; post-shift
  verify ≈0; slit offset from **lowest-hv** slice; state V₀; soft X-ray →
  `reference/beamline-geometry.md` (MAESTRO 55°; ALBA LOREA 55°; SOLEIL ANTARES
  **45°** + fixed horizontal slit — ask; SLS soft X-ray postponed) + **ask**
  about photon momentum / incidence; npz must store
  `ef_fit_per_hv` (`reference/k-and-kz-conversion.md`).
- After k/kz conversion: save `analysis/kspace/*.npz` with required meta;
  prefer reload from cache when meta still matches.
- **Forward k cuts (user-asked):** point/pair through angle → k-cut via
  `reference/forward-k.md` (complements full-volume convert).
- **Dichroism (user-asked):** `reference/dichroism.md` (CP+CM; null-ROI scale
  then D and A; red+/blue− plots; clim tweak OK if echoed).
- **Core-as-2D:** cut-shaped file with swept + deep/core clues (soft: span ≳10 eV
  or deepest ≳5 eV below EF) → suspect core level saved as 2D image; quick
  report = detector×energy **and** angle-integrated EDC; no default valence k
  (`reference/default-overview-plots.md`).
- **Folder first:** for multi-file folders, build/refresh `analysis/manifest.json`
  with **header-only peek** (astropy/h5py — not full `load_data`); later
  **recall** from it (`reference/folder-manifest.md`).

## Package-first (important)

Default = **call code that already exists** (PyARPES, or **confirmed** user-map
callables, or the project). If a path fails or is missing a feature, **tell the
user** and ask before writing a new custom loader/implementation. Details:
`reference/package-first.md`, `reference/backend-capability-map.md`.

## Token awareness

Before steps that will burn a lot of context (full-folder catalogs, pasting
arrays, broadcast fits over whole maps, many figures in-chat), give a short
**Token note** and offer a cheaper option (script → `analysis/`, summarize in
chat). Details: `reference/token-usage.md`.

## Error handling

- Missing PyARPES / wrong Python — **ask shared env** (conda `arpes38` or
  `~/arpes-py38-venv`; project `.venv-arpes` only if requested) —
  `reference/pyarpes-env.md`; if declined → user-map path
  (`backend-capability-map.md`); only then inspect-only xarray/h5py.
- Package load fails / feature missing — quote error; ask before custom code
  (`reference/package-first.md`).
- Ambiguous axes — stop and ask one sharp question.
- Ambiguous V₀ — ask or mark kz as relative/uncertain.
- Corrupt/partial file — report readable parts only.

## Workflow

1. If the user points at a **folder** / many files: build or refresh
   `analysis/manifest.json` (+ optional `manifest.md`) **first** — listing +
   **header-only peek** (`folder-manifest.md`). Do **not** full-load every
   spectrum. Later turns **recall** from the manifest; do not re-walk the
   folder into chat.
2. Identify artifact (file type, shape, **existing** package/project loaders);
   prefer rows from the manifest when present.
3. Check PyARPES + Python 3.8; if missing/wrong, ask for dedicated venv
   (see Stack policy / `reference/pyarpes-env.md`). If declined → propose
   user capability map (`backend-capability-map.md`) before inspect-only.
4. Try package load/analysis first (`reference/package-first.md`). For
   MAESTRO: prefer sibling **`.fits`** + `location='MAESTRO'` before MH1
   `.h5`; pick main spectrum carefully (`formats-and-axes.md`). If load
   fails or needs new code — **ask** before a custom loader.
5. Lock coordinates — names + units (° vs Å⁻¹, eV, hν; binding vs kinetic).
6. Sanity print — shape, ranges, one mid-cut summary.
7. Reduce — cut / FS / EDC / MDC (see `reference/safe-reduction.md`).
8. **Quick report:** stop at angle-space overviews
   (`default-overview-plots.md`). **Do not** convert to k/kz here.
   If spatial (`x`,`y` n>1) → `spatial-xy-scans.md` set. Update manifest
   `overview_paths` when PNGs are written.
9. **Analysis / user-requested momentum:** convert to k / kz
   (`reference/k-and-kz-conversion.md`) — state energy axis; EF finder +
   report EF_fit/deviation (charging warn if >50 meV on E−EF/Eb); for **hv
   stacks**: angle-summed edge + per-hv QC + post-shift verify + `ef_fit_per_hv`
   in npz; Γ per cut vs Fermi rules; stated V₀ for kz; save
   `analysis/kspace/*.npz`; link `product_paths` on the manifest row.
   Spatial hypercubes: reduce ROI / hot spot first (`spatial-xy-scans.md`).
10. If line / core analysis — fit (`reference/edc-mdc-fitting.md`: **core first**,
   then EDC/MDC; package models only). At a spatial hot spot / ROI, pick the
   recipe that matches the spectroscopic kind.
11. If user asks near-EF / metal EF / FD / **gap** / **pseudogap** on a cut —
    `reference/near-ef-gap.md` (metal fit → shift; optional resolution-broadened
    FD divide; symmetrize when gap/pseudogap).
12. If spin channels present / user asks SARPES — `reference/spin-arpes.md`.
13. If external param axis \(P\) (dose / V / I / B / T / …) —
    `reference/in-operando-param-scans.md` (not pump–probe delay).
14. If `delay` dim / trARPES — `reference/tr-arpes.md`.
15. If user asks self-energy / Σ / QP lifetime on a single-band cut —
    `reference/self-energy.md`.
16. If user asks band enhance / curvature / min-gradient —
    `reference/band-enhance.md` (both maps).
17. If user asks FS pocket / radial EDCs around a sheet —
    `reference/fs-pocket.md`.
18. If user asks smooth / denoise / deconvolve —
    `reference/smooth-deconvolve.md`.
19. If user asks resolution / broadening budget (or FD needs σ) —
    `reference/resolution.md`.
20. If user asks background subtraction —
    `reference/backgrounds.md`.
21. If user asks BZ / Brillouin / high-sym path overlay —
    `reference/bz-overlay.md` (after k if possible).
22. If user asks rebin / symmetrize / normalize_dim / sort / condense —
    `reference/axis-prep.md`.
23. If user asks mask / polygon ROI / boolean keep-region —
    `reference/masks.md`.
24. If user asks align / register / spectral shift between datasets —
    `reference/align.md`.
25. If user asks PCA / NMF / ICA / factor analysis —
    `reference/decomposition.md`.
26. If user asks stack / waterfall / false-color / ToF±σ plot —
    `reference/stack-plots.md`.
27. If user asks k-cut through angle point/pair or forward coord → k —
    `reference/forward-k.md`.
28. If user asks dichroism / CP−CM / CD —
    `reference/dichroism.md`.
29. Plot/report with labeled units; **list overview / conversion assumptions**.
30. Before expensive batch work — token note (`reference/token-usage.md`).

If unsure: read the matching `reference/` file; ask the user one sharp question.

## References

- `reference/formats-and-axes.md`
- `reference/safe-reduction.md`
- `reference/edc-mdc-fitting.md` — peak fitting: core, then EDC/MDC (PyARPES only)
- `reference/near-ef-gap.md` — metal EF, resolution-broadened FD divide, symmetrize (gap/pseudogap)
- `reference/spatial-xy-scans.md` — XY / nano spatial scans (ROI map, hot spot, kind reuse)
- `reference/spin-arpes.md` — Spin-ARPES / SARPES (EDC + cuts; package sarpes/plots)
- `reference/in-operando-param-scans.md` — dose / gate / I / B / T param scans
- `reference/tr-arpes.md` — time-resolved / pump–probe (delay, t0, ΔI)
- `reference/self-energy.md` — single-band Σ from MDC (path C; bare band; optional lifetime)
- `reference/band-enhance.md` — curvature + minimum gradient (both; not intensity)
- `reference/fs-pocket.md` — FS pocket center / curves / EDCs (path B center)
- `reference/smooth-deconvolve.md` — gaussian smooth; RL/ICE deconvolve (ask + PSF)
- `reference/resolution.md` — total / thermal / analyzer / beamline ΔE estimates
- `reference/backgrounds.md` — Shirley (core) / hull (valence) / incoherent (ask)
- `reference/bz-overlay.md` — BZ / high-sym path (path C cell; ase optional)
- `reference/axis-prep.md` — rebin / symmetrize / normalize_dim / sort / condense
- `reference/masks.md` — boolean / polygon masks (`apply_mask`)
- `reference/align.md` — correlation align offset (ask before apply)
- `reference/decomposition.md` — PCA / NMF / ICA / factor analysis
- `reference/stack-plots.md` — stack / flat stack / false-color / ToF±σ
- `reference/forward-k.md` — k-cut through angular point/pair; coord forward
- `reference/dichroism.md` — CP/CM null-ROI scale; diff + asym; red/blue plot
- `reference/k-and-kz-conversion.md` — analysis-mode k/kz + Γ + npz cache
- `reference/beamline-geometry.md` — MAESTRO / ALBA LOREA 55°; SOLEIL ANTARES 45° + fixed H slit; SLS postponed
- `reference/failure-modes.md`
- `reference/pyarpes-env.md` — shared Python 3.8 env (conda / home venv) + install
- `reference/token-usage.md` — when to warn about token cost
- `reference/default-overview-plots.md` — cut / Fermi trio / hv–kz trio + assumptions
- `reference/package-first.md` — use package APIs; ask before new code
- `reference/backend-capability-map.md` — capability IDs; PyARPES defaults; user-map; living list
- `reference/folder-manifest.md` — folder inventory; header peek then recall

## Examples

- `examples/maestro_pyarpes.md`
- `examples/fit_edc_mdc.md`
- `examples/near_ef_gap.md`
- `examples/spatial_xy_scan.md`
- `examples/spin_arpes.md`
- `examples/in_operando_param_scan.md`
- `examples/tr_arpes.md`
- `examples/self_energy.md`
- `examples/band_enhance.md`
- `examples/fs_pocket.md`
- `examples/smooth_deconvolve.md`
- `examples/resolution.md`
- `examples/backgrounds.md`
- `examples/bz_overlay.md`
- `examples/axis_prep.md`
- `examples/masks.md`
- `examples/align.md`
- `examples/decomposition.md`
- `examples/stack_plots.md`
- `examples/forward_k.md`
- `examples/dichroism.md`
- `examples/backend_user_map.md`
- `examples/convert_k_kz.md`

## Requires (full analysis)

- **Python 3.8.x only** for PyARPES (`>=3.8,<3.9` on PyPI)
- Dedicated **shared** Python 3.8 env (conda `arpes38` or `~/arpes-py38-venv`;
  project `.venv-arpes` only if asked) — see `reference/pyarpes-env.md`
- `pip install arpes` **inside that env**
- For load/inspect fallback only: `xarray`, `h5py` (any modern Python OK)

## Key PyARPES paths

See `reference/` for recipes. Common entry points:

- Load: `arpes.io.load_data` or project loaders
- k-space: `convert_to_kspace` + `S.apply_offsets` (analysis mode; state Γ method)
- kz: hv scans with stated `inner_potential` V₀; cache under `analysis/kspace/`
- Fit: core (Shirley + multi-peak) then EDC/MDC; `broadcast_model` for maps /
  dispersion parameter plots
- Near-EF / gap: metal `AffineBroadenedFD` → shift; optional broadened FD divide;
  `arpes.analysis.gap.symmetrize` for gap/pseudogap (`near-ef-gap.md`)
- Self-energy: `fit_for_self_energy` / `to_self_energy` (`self-energy.md`)
- Band enhance: `curvature` + `minimum_gradient` (`band-enhance.md`)
- FS pocket: `pocket_parameters` / `curves_along_pocket` (`fs-pocket.md`)
- Smooth / deconvolve: `gaussian_filter_arr`; `deconvolve_rl` + PSF if asked
  (`smooth-deconvolve.md`)
- Resolution: `total_resolution_estimate` / parts (`resolution.md`)
- Backgrounds: Shirley / hull / incoherent (`backgrounds.md`)
- BZ overlay: `overplot_standard` / `bz_plot` / `annotate_special_paths` /
  `plot_data_to_bz` (`bz-overlay.md`)
- Axis prep: `rebin` / `symmetrize_axis` / `normalize_dim` / `sort_axis` /
  `condense` (`axis-prep.md`)
- Masks: `.where` / `apply_mask` (`masks.md`)
- Align: `align` / `align1d` / `align2d` (`align.md`)
- Decomposition: `pca_along` / `nmf_along` / `ica_along` /
  `factor_analysis_along` (`decomposition.md`)
- Stack / ToF plots: `stack_dispersion_plot` / `flat_stack_plot` /
  `false_color_plot` / `plot_with_std` (`stack-plots.md`)
- Forward k: `convert_through_angular_point` / `pair` /
  `convert_coordinate_forward` (`forward-k.md`)
- Dichroism: CP/CM null-ROI scale → D and A; `RdBu_r` (`dichroism.md`)
