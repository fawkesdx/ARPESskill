---
name: arpes
description: >
  Load and analyze ARPES photoemission data with correct axes, units,
  EDC/MDC extraction, Gaussian/Lorentzian/Voigt peak fitting, k-space
  conversion, photon-energy to kz conversion, near-EF gap/pseudogap,
  spatial XY / nanoARPES scans, Spin-ARPES (SARPES), in-operando parameter
  scans, time-resolved / pump–probe ARPES (delay, t0, ΔI), single-band
  self-energy (Σ), band enhance (curvature / minimum gradient), and Fermi-surface
  pocket analysis via PyARPES or a confirmed user-project capability map. Use
  when working with ARPES spectra, Fermi surfaces, EDC, MDC, spin-ARPES,
  trARPES, pump-probe, in-operando, dosing, gated devices, self-energy,
  curvature, minimum gradient, FS pocket, MAESTRO or NeXus/HDF5 ARPES files,
  angle-to-momentum conversion, hv/kz scans, spatial maps, nanoARPES,
  pseudogap, or PyARPES.
---

# ARPES

## When to use

User or task involves ARPES spectra, Fermi maps, EDC/MDC, peak fitting,
k or kz conversion, spatial XY / nanoARPES maps, Spin-ARPES / SARPES,
in-operando parameter scans (dose, gate, current, field, T), time-resolved /
pump–probe ARPES (trARPES), self-energy / Σ, band enhance (curvature /
minimum gradient), FS pocket, MAESTRO/NeXus/HDF5/Igor ARPES files, or PyARPES.

## What reduction means

In ARPES, **reduction** does not mean compress the file. It means turning a
raw multidimensional scan into analysis products: energy/momentum cuts,
EDC/MDC, Fermi-surface maps, fitted dispersions, k- and kz-converted
volumes, etc.

## Stack policy

1. Prefer **PyARPES** for analysis (fit, k, kz).
2. **At session start (and before any analysis):** check whether PyARPES
   imports **and** that the interpreter is **Python 3.8.x**.
   (`python -c "import arpes, sys; print(sys.version_info[:2])"`)
   PyARPES (`arpes` on PyPI) requires `>=3.8,<3.9` — not 3.9+.
3. **If PyARPES is missing or Python is not 3.8 — STOP and ask**
   (do not silently fall back; do not `pip install arpes` into the current env):
   - Explain: PyARPES needs a **dedicated Python 3.8 venv** so it does not
     break the user’s normal Python / other projects.
   - Ask: *Create a new `.venv-arpes` with Python 3.8 and install PyARPES there?*
   - Wait for yes/no.
   - If **yes**: follow `reference/pyarpes-env.md` (find `python3.8` →
     `python3.8 -m venv .venv-arpes` → `pip install arpes` in that venv →
     re-check import). If `python3.8` is missing, ask Homebrew vs conda
     (or a user-provided 3.8 path) before inventing installs.
   - If **no**: enter **user-map** path — search project → propose capability →
     callable map → **confirm** → use (`reference/backend-capability-map.md`).
     Only if no mappable `load_spectrum` (etc.) → ask for **xarray + h5py
     load/inspect only** (no fit / k / kz / gap). State path explicitly.
4. After PyARPES setup, run with `.venv-arpes/bin/python` (state that path).
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
  `reference/beamline-geometry.md` (MAESTRO 55°; ALBA LOREA 55° — ask; SLS soft
  X-ray postponed) + **ask** about photon momentum / incidence; npz must store
  `ef_fit_per_hv` (`reference/k-and-kz-conversion.md`).
- After k/kz conversion: save `analysis/kspace/*.npz` with required meta;
  prefer reload from cache when meta still matches.
- **Core-as-2D:** cut-shaped file with swept + deep/core clues (soft: span ≳10 eV
  or deepest ≳5 eV below EF) → suspect core level saved as 2D image; quick
  report = detector×energy **and** angle-integrated EDC; no default valence k
  (`reference/default-overview-plots.md`).
- **Folder first:** for multi-file folders, build/refresh `analysis/manifest.json`
  before deep analysis; later **recall** from it (`reference/folder-manifest.md`).

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

- Missing PyARPES / wrong Python — **ask to create `.venv-arpes` (Python 3.8)
  and install** (`reference/pyarpes-env.md`); if declined → user-map path
  (`backend-capability-map.md`); only then inspect-only xarray/h5py.
- Package load fails / feature missing — quote error; ask before custom code
  (`reference/package-first.md`).
- Ambiguous axes — stop and ask one sharp question.
- Ambiguous V₀ — ask or mark kz as relative/uncertain.
- Corrupt/partial file — report readable parts only.

## Workflow

1. If the user points at a **folder** / many files: build or refresh
   `analysis/manifest.json` (+ optional `manifest.md`) **first** — see
   `reference/folder-manifest.md`. Later turns **recall** from the manifest;
   do not re-walk the folder into chat.
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
18. Plot/report with labeled units; **list overview / conversion assumptions**.
19. Before expensive batch work — token note (`reference/token-usage.md`).

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
- `reference/k-and-kz-conversion.md` — analysis-mode k/kz + Γ + npz cache
- `reference/beamline-geometry.md` — MAESTRO / ALBA LOREA 55° defaults; SLS soft X-ray postponed
- `reference/failure-modes.md`
- `reference/pyarpes-env.md` — Python 3.8 dedicated venv + install
- `reference/token-usage.md` — when to warn about token cost
- `reference/default-overview-plots.md` — cut / Fermi trio / hv–kz trio + assumptions
- `reference/package-first.md` — use package APIs; ask before new code
- `reference/backend-capability-map.md` — capability IDs; PyARPES defaults; user-map; living list
- `reference/folder-manifest.md` — folder inventory before analysis; recall later

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
- `examples/backend_user_map.md`
- `examples/convert_k_kz.md`

## Requires (full analysis)

- **Python 3.8.x only** for PyARPES (`>=3.8,<3.9` on PyPI)
- Dedicated venv (recommended name: `.venv-arpes`) — see `reference/pyarpes-env.md`
- `pip install arpes` **inside that venv**
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
