# k and kz conversion

Reference for converting angle-space ARPES data to **in-plane momentum** (k,
kx, ky) and **out-of-plane momentum** (kz). Also covers **when** to convert,
**hv-stack EF prep** (backend-specific APIs), and how to **cache** products
under `analysis/`.

**One skill** — not a separate “kz-map” skill. Same physics; package path
follows the **active backend** (`pyarpes` vs `arpes_viewer`).

**PyARPES docs:** [Converting to k-space](https://arpes.readthedocs.io/en/latest/notebooks/converting-to-kspace.html)

Requires completed load/inspect (`reference/safe-reduction.md`). Never label
axes as Å⁻¹ until `convert_to_kspace` has actually run.

## Modes (important)

| Mode | When | k / kz |
|------|------|--------|
| **Quick report** | Catalogs, first-look overview trios | **Off** — angle-space only (`default-overview-plots.md`) |
| **Analysis / requested report** | User asks for k, kz, momentum axes, or a report that includes conversion | **On** — this document |

If unclear: ask one sharp question. **Do not convert silently** during quick report.

## Energy axis notice (always — load & analysis)

On **every load**, state the energy axis kind to the user. Do **not** silently
relabel.

| Label | Meaning | Typical clues (not absolute) |
|-------|---------|------------------------------|
| **Ek** | Absolute kinetic (analyzer scale) | Range ≫ 0; attrs/units say kinetic |
| **Eb** | Binding (sign conventions vary) | Attrs say binding; may be positive-down |
| **E−EF** | EF-aligned (PyARPES default: ≤0 below EF) | `0` in range; negative below EF |
| **ambiguous** | Cannot tell | Say so; ask one sharp question |

Example line:  
`Energy axis: E−EF (claimed); range [−1.2, 0.05] eV`

## EF finder before cut → k (required)

Before `convert_to_kspace` on a **dispersion cut** (analysis mode):

1. **Always** run a PyARPES Fermi-edge fit — even if the axis is already labeled
   E−EF or Eb (charging / mono drift can move the edge off 0).
2. Use **only** package tools (e.g. `AffineBroadenedFD` via `broadcast_model`
   and/or a mid-cut EDC fit; then `G.shift_by` / documented energy correction).
   **Do not invent** a custom edge fitter or hand-rolled \(k=\ldots\) formulas.
3. Report **EF_fit** and **deviation from 0**:  
   `EF_fit = X eV → |X| = … meV from 0 eV`.
4. Shift so EF → 0, then convert.

| Loaded claim | After EF fit | Tell the user |
|--------------|--------------|---------------|
| **Ek** | Fit + shift to EF=0 | Was kinetic; EF calibrated with PyARPES edge fit (state EF_fit + deviation). **Do not** convert as raw Ek. |
| **E−EF** or **Eb**, \|EF_fit\| ≤ **50 meV** | Shift if needed | Print EF_fit and deviation from 0; no charging flag. |
| **E−EF** or **Eb**, \|EF_fit\| > **50 meV** | Shift to 0 for conversion | Print EF_fit + deviation; **possible sample charging** (or bad energy cal). Warning only — not a proven diagnosis. |

**Charging flag threshold:** `|EF_fit| > 50 meV` when the axis was claimed E−EF or Eb.
Always print the deviation regardless of threshold.

Do **not** invent a separate absolute-KE matrix when data already has EF-aligned
`eV` (after this step) and `hv` in attrs/coords. PyARPES `convert_to_kspace`
uses that spectral model.

| Situation | Action |
|-----------|--------|
| After EF→0 + `hv` present | Proceed to offsets + `convert_to_kspace` |
| EF fit fails / no clear edge | Stop; ask user (metal EF region? insulator?) |
| hv missing when conversion needs it | Stop; ask |
| hv missing on hv-stack (kz) | **Stop** — cannot do absolute kz |

**Work function:** for EF calibration from analyzer KE when needed — not a usual
extra argument to `convert_to_kspace` once EF is at 0.

## Slit bend / FS correction (before convert)

**Same skill step** — not a separate “FS bend” skill. PyARPES already documents
this as [Fermi edge corrections](https://arpes.readthedocs.io/en/latest/notebooks/fermi-edge-correction.html)
(“Correcting the curved Fermi edges” / straight slit).

### Uniform EF vs slit bend

| | Uniform EF align | Slit bend / FS correction |
|--|------------------|---------------------------|
| What | Whole frame off by one energy | Edge **bows vs detector angle** (φ / slit) |
| Typical cause | Mono / WF / charging | Straight-slit / analyzer optics along slit |
| Fix | One shift (or one per hv) | Shift **each angle column** so edge is flat vs φ |
| If skipped when bent | Edge not at 0 | Fake dispersion / fake **kz** bend after convert |

Mean-only `fd_center.mean()` → EF≈0 is **not** enough when `fd_center(φ)` still
curves. Check span of centers vs φ (or viewer `edge_flatness`); skill warn if
bend ≳ **~30 meV** across slit (viewer banner ≈ 0.03 eV) — convert still
allowed with warning.

**Not:** band-enhance `curvature` (`band-enhance.md`); not per-hv mono align.

**Order:** optional de-grid → **this** (if needed) → per-hv EF align on stacks →
Γ / V₀ → convert.

### `pyarpes`

```python
from arpes.fits.utilities import broadcast_model
from arpes.fits.fit_models import AffineBroadenedFD, QuadraticModel

# Slit frame: cut, or map.sum("theta") (deflector) — curvature is along analyzer φ
near = slit_frame.sel(eV=slice(-0.2, 0.1))  # adapt
results = broadcast_model(AffineBroadenedFD, near, "phi")
centers = results.F.p("fd_center")
bend_span = float(centers.max() - centers.min())  # report
# If bend_span small → mean shift OK; if large → smooth along φ:
quad = QuadraticModel().guess_fit(centers)
edge = quad.eval(x=full.phi)   # evaluate on the volume being corrected
corrected = full.G.shift_by(edge, "eV")
```

Package-first — no invent DIY poly outside this pattern / package models.

### `arpes_viewer`

- Check: `tools.kzconv.edge_flatness(cube, angle, energy)` → spread (eV).  
- Correct: `tools.analysis.fs_correction(values, angle_axis, energy_axis, coeffs, …)`
  — coeffs from a polynomial through a feature that should be flat (EF or band
  bottom); apply along slit; maps: fit on slit cut / θ-summed frame, apply to
  cube.  
- Do not invent coeffs; user picks / fit_feature path as upstream GUI does.

Report: backend, bend span, method (`quadratic_phi` / `fs_correction` / mean-only).

Capability: `fs_bend_correct` — `backend-capability-map.md`.

## Γ / zero momentum (policy)

Mechanism: `data.S.apply_offsets({...})` on present angle motors (`phi`,
`theta`, `psi`, …). **User-defined offset always wins.** Never claim “Γ found”
without naming method. Overview mid-detector / mid-scan ≠ Γ for k conversion.

### Cuts (dispersion)

1. Prefer existing `S.offsets` if already set by the loader — label *loader offsets*.
2. Else **provisional** nearest-0° / mid if 0 in range — label
   *provisional:nearest_zero* (not a PyARPES auto-Γ API).
3. User offset overrides; persist and recompute if changed.

### Fermi maps (stricter — package only + ask)

There is **no** general PyARPES `estimate_gamma_from_isoenergy`. Do **not** invent
centroid / argmax / symmetry scripts.

Order:

1. **User offset** if provided → `apply_offsets`; method `user`.
2. Else print existing **`S.offsets`** if present → method `loader_offsets`;
   ask whether to keep or replace.
3. Else, if the isoenergy is clearly a **single pocket**, may call
   **`arpes.analysis.pocket.pocket_parameters`** (package only) and propose its
   center as offsets — label *package:pocket_parameters*; **ask before applying**.
   Full pocket / radial-EDC workflow: `reference/fs-pocket.md` (separate from Γ).
   BZ overlay after k: `reference/bz-overlay.md` (does not replace Γ policy).
   Forward point/pair k-cuts: `reference/forward-k.md`.
4. Else offer interactive **`arpes.plotting.qt_ktool.ktool`** / `widgets.kspace_tool`
   if the user wants GUI — **ask first** (skill prefers scripted path).
5. Else **STOP and ask** for Γ / normal-emission angles (or a clickable point).
   Do not freestyle a center finder.

Any **new** center-finding code → ask A/B/C (`package-first.md`); do not write it
silently.

## Prerequisites

Before `convert_to_kspace` on a **cut or Fermi map**:

1. **Energy axis notice** (Ek / Eb / E−EF / ambiguous) — same for both.
2. **EF finder** → report EF_fit + deviation from 0 → shift EF→0;
   charging warning if claimed E−EF/Eb and `|EF_fit| > 50 meV`.
3. **Slit bend** — if edge bows vs detector φ, straighten
   ([above](#slit-bend--fs-correction-before-convert)); mean-only insufficient.
4. Identify which **angles** map to in-plane momentum — read `.coords`.
5. Set Γ offsets per [Γ policy](#γ--zero-momentum-policy) (Fermi = stricter).
6. State sample geometry in the report.
7. For kz: set or ask for **V₀** (`attrs["inner_potential"]`).

## In-plane k — cut

**Skip** this path if the file is **suspected core-as-2D**
(`reference/default-overview-plots.md`) unless the user overrides to valence.

```python
from arpes.fits.utilities import broadcast_model
from arpes.fits.fit_models import AffineBroadenedFD, QuadraticModel
from arpes.utilities.conversion import convert_to_kspace

# 1) State energy axis kind to user (Ek / Eb / E−EF / ambiguous)

# 2) EF finder (PyARPES only) — even if already labeled E−EF
near_ef = cut.sel(eV=slice(-0.15, 0.1))  # adjust window to data
results = broadcast_model(AffineBroadenedFD, near_ef, "phi")
centers = results.F.p("fd_center")
bend_span = float(centers.max() - centers.min())
# ALWAYS report: EF_fit summary + bend_span vs φ
# If claimed E−EF/Eb and |mean| > 0.05: warn possible charging
if bend_span > 0.03:  # ~30 meV — straighten along φ (see slit-bend section)
    edge = QuadraticModel().guess_fit(centers).eval(x=cut.phi)
    cut_ef = cut.G.shift_by(edge, "eV")
else:
    ef_fit = float(centers.mean())
    cut_ef = cut.G.shift_by(-ef_fit, "eV")  # uniform EF → 0

# 3) Provisional or user Γ offsets (no invent auto-Γ)
cut_ef.S.apply_offsets({"phi": phi0})  # keys = dims present
# gamma_method = "provisional:…" | "user"

# 4) Convert — package only
kdata = convert_to_kspace(cut_ef)  # or resolution= / kp=linspace(...)
```

## In-plane k — Fermi map

**Energy:** same as cut — axis notice + EF finder + EF_fit/deviation +
charging warn at 50 meV + shift EF→0; if edge bows vs φ, slit-bend straighten
first ([above](#slit-bend--fs-correction-before-convert)). Do **not** skip EF
because “it’s a map.”

**Center / Γ:** follow [Fermi maps (stricter)](#fermi-maps-stricter--package-only--ask)
— package offsets / optional `pocket_parameters` / optional `ktool` / **ask**.
No invent centroid code.

Convert the near-EF isoenergy (or stated window) and/or the volume as the task
requires. Finite energy window ≠ true FS if bands disperse strongly — echo that
caveat.

```python
from arpes.fits.utilities import broadcast_model
from arpes.fits.fit_models import AffineBroadenedFD
from arpes.utilities.conversion import convert_to_kspace
# optional, only if clearly a pocket and user agrees:
# from arpes.analysis.pocket import pocket_parameters

# 1) Energy axis notice (Ek / Eb / E−EF / ambiguous)
# 2) EF finder on a near-EF cut through the map (package only) — same as cut
#    e.g. mid-psi or angle-summed strip → AffineBroadenedFD → shift_by
# 3) Γ: user | S.offsets | ask about pocket_parameters | ask about ktool | STOP ask
#    fmap.S.apply_offsets({...})  # only after user/package path chosen
# 4) Isoenergy or .S.fermi_surface as appropriate
k_fs = convert_to_kspace(fs_slice)  # or full fmap after EF+offsets
# Report: energy axis, EF_fit + meV from 0, gamma_method, grid
```

## hv → kz (Eph stacks)

### Backend fork (same skill)

| Active backend | EF-align path | Then convert |
|----------------|---------------|--------------|
| `pyarpes` | Angle-summed near-EF + `broadcast_model` / `G.shift_by` ([below](#ef-align-across-hv--pyarpes)) | `convert_to_kspace` + stated V₀ |
| `arpes_viewer` + kind `kz_map` | User **index box** + `tools.kzmap.process_kz_map` ([below](#arpes_viewer--kz_map-prep-toolskzmap)) | `tools.kzconv.to_kz_cube` + stated V₀ |

Prep ≠ conversion. Aligned cube is still angle/E until `convert_kz` runs.
If wrong backend for the data → A/B/C/**D** (`package-first.md`).

Optional **de-grid** first when MCP/mesh present (`reference/degrid.md`) — before
kzmap align / k convert.

### Energy on hv stacks

Absolute **Ek differs per hv slice**. After a correct load you normally have:

- `eV` (or viewer energy axis) — shared energy coord (intended **Eb / E−EF**), and  
- `hv` — photon energy dim and/or attrs  

Do **not** invent a separate kinetic-energy cube when those exist. KE for
conversion is implied by **hv + EF-aligned energy**. If the load still looks like
raw analyzer KE with one grid for all hv → state that; align EF **per hv**
before kz.

Always give the energy-axis notice (Ek / Eb / E−EF / ambiguous).

### EF align across hv — `pyarpes`

Mono / undulator drift can move the edge differently at each hv. Use **package
APIs only** ([Fermi edge corrections](https://arpes.readthedocs.io/en/latest/notebooks/fermi-edge-correction.html)).

**Hard rule for PyARPES hv stacks:** fit an **angle-integrated** near-EF edge,
then broadcast on `hv`. Mid-φ / single-pixel EDC is **not** the default
(too noisy / biased). User may override to a stated φ window only if they ask.

#### 1. Edge ROI (required)

1. Near-EF energy strip (adapt window; state it — e.g. `eV=slice(-0.15, 0.1)`).
2. Integrate (sum/mean) over **detector angle** (`phi` / equivalent), or a
   **wide φ window** that covers the slit — not one mid-φ pixel.
3. Then `broadcast_model(AffineBroadenedFD, edge, "hv")` (or package equiv.).

```python
from arpes.fits.utilities import broadcast_model
from arpes.fits.fit_models import AffineBroadenedFD

# REQUIRED pattern: near-EF × angle-integrated, then fit vs hv
edge = hv_scan.sel(eV=slice(-0.15, 0.1)).sum("phi")  # or mean; real angle dim
results = broadcast_model(AffineBroadenedFD, edge, "hv")
centers = results.F.p("fd_center")  # DataArray vs hv — keep the full curve
```

#### 2. QC before convert (hard stop)

Before any shift / isoenergy / kz:

1. **Plot and store** `EF_fit` vs `hv` under `analysis/` (link path in report).
2. **Report every slice:** `EF_fit(hv)` and meV from 0 — **not** mean-only.
3. **Fail (stop and ask)** if any of:
   - ≥ **20%** of centers are exactly `0` (or identical float junk) when a real
     edge is expected
   - Centers clearly **pinned** to the ROI energy edge
   - ≥ **20%** centers still wild after scrub (`|EF| ≳ 250 meV` / MAD outliers) —
     package fit did not find a real edge on those slices
4. **Warn** (do not hard-stop solely on these) if:
   - Median fit **stderr** absurd vs ROI, or stderr NaN on many slices —
     `AffineBroadenedFD` often returns junk stderr even when `fd_center` is
     physical; gate on **centers**, not stderr alone
   - Many slices `|EF_fit| > 50 meV` (charging-scale; flag in products)
5. **Outlier scrub (allowed):** replace clear spike/wild `fd_center` points via
   interp from neighbors; document count; re-QC. Do **not** invent a custom
   edge model — only clean package centers.
6. **Optional soft checks:** metal-like contrast (I below EF ≫ I above EF);
   `fd_width` overflow → widen/narrow ROI or ask.

Do **not** proceed to `shift_by` / convert while QC fails.

#### 3. Package fallback (broadcast broken)

If `broadcast_model` fails or returns unusable objects (e.g. `np.object` mess):

- Loop **angle-summed** near-EF EDCs per hv with `AffineBroadenedFD().guess_fit`
  (still package model).
- Same QC on the collected centers.
- **Do not** silently fall back to mid-φ-only EDCs.

Do **not** invent a custom edge fitter. If package fit still fails → ask.

#### 4. Shift API (canonical)

```python
hv_ef = hv_scan.G.shift_by(
    centers, shift_axis="eV", shift_coords=True
)
```

Prefer this over hand-rolled per-slice concat. If manual concat is unavoidable,
apply the **same QC** and document why `shift_by` was not used.

#### 5. Post-shift verify (required before isoenergy / kz)

After align, build **angle-summed** EDCs at **low / mid / high** hv. Edge must
sit near **≈0** (skill default: \|edge\| ≲ **20 meV** on these checks).  
If not → **stop / ask**; do not trust isoenergy or kz maps.

Optional: re-fit a quick edge on those three check EDCs to confirm.

#### 6. Isoenergy / kz FS gate

Near-EF isoenergy maps and kz conversion run **only after** steps 1–5 pass.  
Otherwise label products **EF-misaligned / do not trust** and do not present
them as calibrated FS / kz.

Capabilities: `fit_fermi_edge`, `shift_energy` —
`reference/backend-capability-map.md`.

### `arpes_viewer` — kz_map prep (`tools.kzmap`)

**When:** active backend `arpes_viewer`; data kind `kz_map` (or clear hv stack
in viewer space); user asks EF align / “process kz map” / prep before kz
convert. **Not** a separate skill — same k/kz recipe, viewer API.

**Not:** substitute for V₀ or `tools.kzconv.to_kz_cube`. Prep puts EF→0 on a
common energy axis; Å⁻¹ still needs convert + stated V₀ (next subsections).

**Order:** optional de-grid (`degrid.md`) → this prep → slit/Γ → V₀ →
`to_kz_cube`.

#### ROI (required)

One **index** box, same detector channels every hv:

```text
index_region = ((angle_from, angle_to), (energy_from, energy_to))  # inclusive
```

Pick a metal-like edge region with points clearly above and below EF. State the
box in the report. Do **not** default to a single mid-angle pixel when a box is
expected — ask if missing.

Energy bounds are **indices into each spectrum’s energy axis** (axes may not
yet agree); that is why the box is index-locked, not a shared eV window.

#### Call (prefer one-shot)

```python
from tools.kzmap import process_kz_map

# cube: (hv, angle, E); energy: 1D axis matching cube[..., E]
result = process_kz_map(
    cube, energy, index_region,
    temperature=30.0,       # adapt; state it
    normalise=True,         # after align+crop; flux varies with hv
)
# result.cube, result.energy (EF=0), result.ef, result.ok, result.trimmed,
# result.normalised; result.spread; result.summary()
```

Prefer `process_kz_map` over calling `fit_levels` / `align` /
`normalise_totals` separately unless debugging. Package-first — no invent EF
fitter.

#### QC (map onto shared hard-stop spirit)

1. **Plot and store** `result.ef` vs hv under `analysis/`.
2. **Report** per-hv EF + `result.ok` (False = interpolated from neighbors).
3. **Fail / ask** if no edges fitted, spread absurd vs energy window, or too
   many non-ok / wild centers (same spirit as PyARPES ≥20% junk / pinned).
4. Echo `result.summary()` and `spread` (eV trimmed by misalignment).
5. **Post-align:** check low/mid/high hv EDCs sit near ≈0 before isoenergy /
   kz convert.

#### Optional intensity norm

`normalise=True` (default upstream) runs **after** align+crop only — totals
then cover the same E range. Norm before align biases by the misalignment
being fixed. State when used.

Capabilities: `fit_fermi_edge`, `shift_energy`, `kz_map_align` —
`reference/backend-capability-map.md`.

### Slit / Γ offset (after EF align)

Same family as **cut** Γ: `S.apply_offsets` — no invent center finder.

**Default skill rule:** determine the analyzer/slit offset on the **lowest-hv**
slice available (after EF align). Reason: photon-momentum push grows with hv
(soft X-ray). Apply that offset to the **whole** cube, then convert.

If lowest-hv slice is too noisy / no clear normal emission → ask user which
slice or which offset to use.

### V₀ and convert

1. Confirm `hv` present — **Stop** if missing.  
2. **Resolve V₀** — **ask or state source**; never silent (see sources table).  
   - `pyarpes`: `attrs["inner_potential"]`  
   - `arpes_viewer`: pass `inner_potential=` into `tools.kzconv.to_kz_cube`  
3. Soft X-ray / photon momentum — see below.  
4. Convert; prefer **periodicity** / BZ eye-check; absolute kz depends on V₀.

Same skill step — not a separate “V₀ scan” skill.

#### Sources (resolve before convert)

| Source | When | Report |
|--------|------|--------|
| User / literature | Preferred | Value + citation / “user stated” |
| Viewer `scan_inner_potential` | User asks scan / unknown V₀ on `kz_map` | `best` + `uncertainty()` + `spacing` used |
| Typical ~5–15 eV guess | Last resort only | Mark **uncertain / relative kz** — **never** silent 10 eV |

#### Viewer — `scan_inner_potential`

**Gate:** active `arpes_viewer`; EF-prepped (or aligned) hv / `kz_map` cube; user
asks V₀ scan / periodicity tune / “find inner potential.”

**Need:**

- `spacing` — repeat distance along surface normal (Å); often lattice `c` or
  `c/2`. **Ask** if unknown — do **not** invent. (Cleavage / interlayer
  candidates may later help; until then: user cell.)
- `work_function` (eV) — state source.
- Optional: trial grid (upstream default ≈ 2–30 eV, step 0.5),
  `binding_energy`, `kpar_halfwidth`, geometry offsets.

```python
from tools.kzconv import scan_inner_potential

scan = scan_inner_potential(
    photon_energy, angle, energy, cube,
    spacing=spacing_A,          # ASK — Å along normal
    work_function=work_function,
    # inner_potentials=np.arange(2.0, 30.5, 0.5),  # optional override
)
# scan.best (eV or None), scan.periods vs scan.inner_potentials,
# scan.target (= 2π/spacing), scan.uncertainty(), scan.sensitivity
```

**Honesty (upstream):** this is a **weak** measurement. Report
`uncertainty()` next to `best`. A short hv range may constrain V₀ only to a
few eV. **Settle** by eye — kz pattern vs BZ / zone boundaries — then **ask**
user accept / edit `best`. Do not treat the scalar alone as exact truth.

Then pass the **accepted** V₀ into `to_kz_cube`. Store in npz
`inner_potential` + assumptions (`v0_source=scan|user|lit`, spacing, uncertainty).

Capability: `scan_inner_potential` — `backend-capability-map.md`.

#### `pyarpes` — no invent scan loop

Prefer user / literature V₀ + visual periodicity vs hv. Do **not** invent a
DIY Fourier / period-vs-V₀ fitter. If user wants automated
`scan_inner_potential` on a PyARPES-only stem → A/B/C/**D** (D only if data can
live on viewer) or mark relative kz.

#### Convert after V₀ resolved

**`pyarpes`:**

```python
import numpy as np
from arpes.utilities.conversion import convert_to_kspace

hv_ef.attrs["inner_potential"] = V0  # eV — MUST state source
kz_data = convert_to_kspace(
    hv_ef,  # or .S.fermi_surface / appropriate reduction
    # kp=np.linspace(...), kz=np.linspace(...),  # or resolution=
)
```

**`arpes_viewer`:** after `process_kz_map` (or equivalent align) + V₀ resolve:

```python
from tools import kzconv

kz_axis, kpar_axis, e_out, out = kzconv.to_kz_cube(
    photon_energy, angle, energy, cube,
    inner_potential=V0,   # accepted value
    work_function=work_function,
    # …
)
```

Do not invent free-electron formulas outside package APIs.

Typical V₀ ~5–15 eV (material/surface-dependent). Do not silently assume 10 eV.

### Photon momentum (soft X-ray) — gap + beamline defaults

UV ARPES often **neglects** photon momentum. Soft X-ray (rough skill flag:
**hv ≳ 100 eV**, or user says soft X-ray) may need a correction and the
**photon incidence geometry**.

PyARPES tutorials document `convert_to_kspace` + **`inner_potential`**; they do
**not** document a simple public “photon momentum on + incidence angle” switch.
Treat full photon-momentum correction as a **known gap**:

1. Warn the user when hv is in soft X-ray / high-hv range.  
2. Load curated defaults from `reference/beamline-geometry.md` (**ALS MAESTRO**
   and **ALBA LOREA**: default incidence **55°**; **SOLEIL ANTARES**: **45°** +
   fixed horizontal slit — ask before use; **SLS** soft
   X-ray ARPES postponed / dark time).  
3. **Ask:** accept default geometry notes / edit numbers / ignore photon
   momentum for this run.
4. If a correction requires **new** code beyond package APIs → ask A/B/C
   (`package-first.md`); do not invent formulas silently.

### Pipeline summary

**`pyarpes`:**

```text
load hv stack → state energy axis (expect Eb / E−EF + hv)
  → optional de-grid; slit bend straighten if edge bows vs φ
  → near-EF × angle-summed edge → AffineBroadenedFD vs hv
  → QC: EF_fit(hv) plot + per-slice report; hard-stop if pinned/junk
  → G.shift_by(centers, shift_axis="eV", shift_coords=True)
  → post-shift: summed-φ EDC at low/mid/high hv ≈0 (≲20 meV)
  → slit/Γ offset from lowest-hv slice (cut-like; ask if unclear)
  → resolve V₀ (user/lit | mark relative — no DIY scan invent)
  → convert_to_kspace
  → soft X-ray? → beamline geometry default + ask (photon momentum)
  → analysis/kspace/<stem>_kz.npz (include ef_fit_per_hv)
```

**`arpes_viewer` (`kz_map`):**

```text
load kz_map → state energy axis
  → optional de-grid (pixel-locked; degrid.md)
  → slit bend: edge_flatness warn; fs_correction if bent
  → user index box → tools.kzmap.process_kz_map (fit / align / crop / optional norm)
  → QC: ef vs hv + ok mask + spread; post-align ≈0 checks
  → slit/Γ (ask if unclear)
  → resolve V₀ (user/lit | scan_inner_potential + ask accept | relative)
  → tools.kzconv.to_kz_cube
  → soft X-ray? → beamline geometry + ask
  → save products + ef_fit_per_hv under analysis/
```

## Output grid / resolution

- **Default:** PyARPES `resolution=` / auto bounds from angle range — reasonable sampling.
- **User override:** explicit `N` or `np.linspace` for `kp` / `kx` / `ky` / `kz`.
- Always state the grid in the report and in npz meta.

## Analysis cache (`analysis/kspace/*.npz`)

After a successful conversion (offsets / V₀ / energy locked), save under the
user’s project so later agents can reload products instead of raw files.

```text
analysis/kspace/<stem>_k.npz    # cut or FS → in-plane k
analysis/kspace/<stem>_kz.npz   # hv stack → kz (+ in-plane as present)
```

### Required npz keys

| Key | Content |
|-----|---------|
| `intensity` | Converted array |
| named axes | e.g. `eV`, `kp`, `kx`, `ky`, `kz` (1D) |
| `dims` | Ordered dim names (object/string array OK) |
| `source_path` | Original raw path |
| `offsets` | Angle offsets used (serialized dict) |
| `gamma_method` | `provisional:<name>` \| `user` \| … |
| `inner_potential` | float; omit or NaN if N/A |
| `hv` | scalar or array |
| `energy_convention` | short string (Ek / Eb / E−EF as claimed + after shift) |
| `ef_fit_eV` | Scalar summary OK for **cuts**; for **hv stacks** prefer mean/median of per-hv only as extra |
| `ef_fit_per_hv` | **Required for hv→kz stacks:** 1D array of EF_fit before shift (same length as `hv`) |
| `ef_deviation_meV` | Per-hv array and/or scalar summary (`|EF_fit| × 1000` from 0) |
| `ef_fit_plot_path` | Optional string path to EF_fit vs hv PNG under `analysis/` |
| `ef_qc_passed` | bool — QC + post-shift verify passed |
| `charging_warning` | bool / flag if claimed E−EF/Eb and \|EF_fit\| > 50 meV (any/many slices) |
| `grid_spec` | resolution / linspace description |
| `assumptions` | Free-text echo |
| `created_utc` | ISO timestamp |
| `skill_ref` | e.g. `arpes` + date |

For hv stacks, **scalar `ef_fit_eV` alone is not enough** — ship `ef_fit_per_hv`.

### Save / load sketch

```python
from pathlib import Path
import numpy as np

out = Path("analysis/kspace") / f"{stem}_k.npz"
out.parent.mkdir(parents=True, exist_ok=True)
np.savez_compressed(
    out,
    intensity=np.asarray(kdata.values),
    **{name: np.asarray(kdata.coords[name]) for name in kdata.dims},
    dims=np.array(kdata.dims),
    source_path=np.array(str(raw_path)),
    # serialize offsets / meta as JSON strings if needed
    gamma_method=np.array(gamma_method),
    energy_convention=np.array("EF-aligned binding-like"),
    grid_spec=np.array(grid_spec),
    assumptions=np.array(assumptions_text),
    created_utc=np.array(created_utc),
    skill_ref=np.array("arpes"),
)

# Reload: prefer npz when meta matches current offsets/V₀/grid (or user accepts cache)
# If user changes Γ / V₀ / grid → recompute and overwrite (or versioned name)
```

Quick report never requires npz. Prefer **read analysis npz** over raw when cache
is valid.

## Rules summary

Point/pair forward cuts (not full volume): `reference/forward-k.md`.

| Rule | Detail |
|------|--------|
| **No k in quick report** | Overviews stay angle-space |
| **State energy axis** | Ek / Eb / E−EF / ambiguous on every load |
| **EF finder before cut/Fermi → k** | Package edge fit; always report EF_fit + deviation from 0 |
| **Slit bend / FS correction** | Same skill: if edge bows vs φ, straighten (PyARPES quad+`shift_by` or viewer `fs_correction`); mean-only ≠ bend fix; not band-enhance curvature |
| **Charging warn** | Claimed E−EF/Eb and \|EF_fit\| > 50 meV |
| **Fermi Γ** | Package offsets / pocket_parameters / ktool / **ask** — no invent center |
| **EF align hv stacks** | **Same skill, backend path:** `pyarpes` = angle-summed near-EF + `broadcast_model` / `shift_by`; `arpes_viewer` `kz_map` = index box + `tools.kzmap.process_kz_map` — not a second skill |
| **Viewer prep ≠ convert** | `kzmap` align ≠ Å⁻¹; still need V₀ + `kzconv` / `convert_to_kspace` |
| **hv EF QC** | Plot EF_fit vs hv; per-slice report; hard-stop if ≥20% zero/junk, pinned, or absurd stderr |
| **hv shift** | Prefer `G.shift_by(...)` (`pyarpes`) or `process_kz_map` / `align` (`arpes_viewer`) |
| **Post-shift verify** | Summed-φ EDC at low/mid/high hv ≈0 (≲20 meV) before isoenergy/kz |
| **hv npz meta** | Require `ef_fit_per_hv` (+ optional plot path); scalar alone insufficient |
| **Slit offset for kz** | Prefer **lowest-hv** slice after EF align (cut-like offsets) |
| **Photon momentum** | Soft X-ray: warn + `beamline-geometry.md` defaults + **ask**; no invent |
| **State V₀** | Before absolute kz; ask / lit / viewer scan / mark relative — never silent |
| **V₀ scan** | Same skill step: `tools.kzconv.scan_inner_potential` on viewer; report uncertainty; user accept; ask `spacing` — not a second skill |
| **Prefer periodicity** | Cross-check bands vs hv / BZ when possible; scan alone is weak |
| **No fake Å⁻¹** | Until package convert runs (`convert_to_kspace` / `to_kz_cube`) |
| **State geometry + Γ method** | Named method; user offset wins |
| **User offset wins** | Overrides; update cache |
| **No invented KE matrix / k formulas / center finders** | Package APIs only; ask before new code |
| **Cache after convert** | `analysis/kspace/*.npz` with required meta |

## Common mistakes

See `reference/failure-modes.md`.
