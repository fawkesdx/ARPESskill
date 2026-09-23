# Backend capability map

Skill = **workflow + physics**. Backend = **capability ID → callable**.

**Default backend:** PyARPES (document every new step here first).  
**Alternate:** confirmed functions in the **user’s project** (after venv decline
or explicit “use my code”).  
**Future:** TensorSpec / others as extra columns — deferred.

---

## Living-list rule (hard)

When adding **any** new analysis workflow to this skill (discuss → approve →
implement):

1. Write the recipe from the **PyARPES perspective first** (`reference/*.md`).
2. In the **same change**, add/update row(s) in the [Capability inventory](#capability-inventory)
   below — fill **PyARPES default**; leave **User (session)** blank.
3. Point the new reference doc at the capability ID(s).
4. Do not ship a callable analysis step that has no inventory row.

Later users (or sessions) map their own replacements into the user column /
`analysis/backend_map.json` without redesigning the skill.

---

## Stack resolution order

1. Check `import arpes` + Python **3.8** (`pyarpes-env.md`).
2. If missing/wrong → **offer** `.venv-arpes` + install; wait for yes/no.
3. If user **declines** (or chooses project code) → **project map path**
   ([Discovery](#discovery--confirm)).
4. If neither PyARPES nor a confirmed `load_spectrum` (etc.) → **xarray/h5py
   inspect-only** only (`formats-and-axes.md`); no fit / k / kz / gap claims.
5. Always state active path: `pyarpes` | `user-map` | `inspect-only`.

Do **not** silently skip the venv offer. Do **not** call user code before confirm.

---

## Capability inventory

Update this table whenever workflows grow. IDs are stable; symbols may change
with PyARPES versions — check installed package before claiming exact names.

| ID | Meaning | PyARPES default | User (session) | Reference |
|----|---------|-----------------|----------------|-----------|
| `load_spectrum` | Open cut / map / hv stack | `arpes.io.load_data` (+ `location=`) / project loader if already preferred | | `formats-and-axes.md` |
| `state_axes` | Dims, units, energy convention | `.dims` / `.coords` / `.attrs` | | `formats-and-axes.md` |
| `folder_manifest` | Multi-file inventory | thin glue → `analysis/manifest.json` | | `folder-manifest.md` |
| `overview_plot` | Quick-report figures | matplotlib (+ package plot helpers if used); spatial → `spatial-xy-scans.md` set | | `default-overview-plots.md`, `spatial-xy-scans.md` |
| `spatial_overview` | XY map + hot spot + mean | `sum`/`mean`/`sel` + optional `arpes.plotting.spatial`; hot spot = argmax of \(I_R\) | | `spatial-xy-scans.md` |
| `spatial_roi_reduce` | Reduce x,y ROI → kind recipe | `sel` / `where` / mean over spatial dims | | `spatial-xy-scans.md` |
| `pca_spatial` | PCA along x,y (optional) | `arpes.analysis.decomposition.pca_along` — ask before large runs | | `spatial-xy-scans.md` |
| `fit_fermi_edge` | Metal / EF edge fit | `AffineBroadenedFD` / FD models + `guess_fit` / `broadcast_model`; **hv stacks:** angle-summed near-EF then vs `hv` + QC (`k-and-kz-conversion.md`) | | `k-and-kz-conversion.md`, `near-ef-gap.md` |
| `shift_energy` | Align EF → 0 | `G.shift_by` (hv: `shift_by(centers, shift_axis="eV", shift_coords=True)` + post-shift verify) | | `k-and-kz-conversion.md`, `near-ef-gap.md` |
| `extract_edc_mdc` | EDC / MDC extraction | `sel` / `isel` / package helpers | | `safe-reduction.md`, `edc-mdc-fitting.md` |
| `fit_peak` | Single-curve peak fit | `GaussianModel` / `LorentzianModel` / `VoigtModel` + `guess_fit` | | `edc-mdc-fitting.md` |
| `fit_core` | Core / XPS-style fit | Shirley + multi-peak package models | | `edc-mdc-fitting.md` |
| `broadcast_fit` | Fit along dim(s) | `arpes.fits.utilities.broadcast_model` | | `edc-mdc-fitting.md` |
| `band_vf_mstar` | vF / m* on E(k) | `LinearModel` / `QuadraticModel` on centers | | `edc-mdc-fitting.md` |
| `convert_k` | Angle → in-plane k | `convert_to_kspace` + `S.apply_offsets` | | `k-and-kz-conversion.md` |
| `convert_kz` | hv → kz | `convert_to_kspace` / kz path + stated V₀ | | `k-and-kz-conversion.md`, `beamline-geometry.md` |
| `fd_broadened` | Resolution-broadened FD | package gap helper if present (check install); else ask | | `near-ef-gap.md` |
| `symmetrize_edc` | Symmetrize about EF | `arpes.analysis.gap.symmetrize` | | `near-ef-gap.md` |
| `gap_delta_fit` | Quantify gap Δ | package models only; **ask** if missing | | `near-ef-gap.md` |
| `spin_detect` | Recognize SARPES channels | `up`/`down` or `intensity`+`polarization` / spin attrs | | `spin-arpes.md` |
| `spin_to_IP` | up/down ↔ I+P | `arpes.analysis.sarpes.to_intensity_polarization` / `to_up_down` | | `spin-arpes.md` |
| `spin_normalize_pc` | Match up/down photocurrent | `normalize_sarpes_photocurrent` — ask (alters counts) | | `spin-arpes.md` |
| `spin_plot` | Spin-EDC / polarized plots | `arpes.plotting.spin.*` | | `spin-arpes.md` |
| `param_scan_detect` | Find external \(P\) dims | Dims minus spectroscopic/spatial/`hv`; **ask** meaning/units if unclear | | `in-operando-param-scans.md` |
| `param_overview` | I vs \(P\) + slice at \(P^*\) | `sel`/`sum`/`mean`; mid \(P^*\) or ask if stepped | | `in-operando-param-scans.md` |
| `param_slice_reduce` | Reduce to one \(P\) → kind recipe | `sel` / `isel` along \(P\) | | `in-operando-param-scans.md` |
| `tr_detect` | Recognize pump–probe delay | `delay` dim / loader alias; confirm units | | `tr-arpes.md` |
| `tr_find_t0` | Resolve pump–probe t0 | user / attrs / `S.t0` / `find_t0` / ask | | `tr-arpes.md` |
| `tr_relative_change` | ΔI or ΔI/I vs delay | `relative_change` / `normalized_relative_change` | | `tr-arpes.md` |
| `tr_overview` | Delay-set quick report | I vs delay + slice at delay\* ≥ t0 + Δ map | | `tr-arpes.md` |
| `self_energy_fit` | Fit single-band cut → Σ | `fit_for_self_energy` (MDC Lorentzian+affine default) | | `self-energy.md` |
| `self_energy_from_mdc` | Σ from existing MDC broadcast | `to_self_energy` | | `self-energy.md` |
| `estimate_bare_band` | Bare E(k) for ReΣ / vF | `estimate_bare_band` (`ransac_linear` default) | | `self-energy.md` |
| `qp_lifetime` | Quasiparticle lifetime / mfp | `quasiparticle_lifetime` (+ vF×τ if asked) — **ask** before default report | | `self-energy.md` |
| `band_curvature` | Curvature band enhance | `arpes.analysis.derivative.curvature` | | `band-enhance.md` |
| `band_min_gradient` | Minimum-gradient enhance | `arpes.analysis.derivative.minimum_gradient` | | `band-enhance.md` |
| `band_derivative` | 1st/2nd deriv along axis | `d1_along_axis` / `d2_along_axis` / `dn_along_axis` — **ask** | | `band-enhance.md` |
| `pocket_params` | Pocket center / anisotropy | `pocket_parameters` (user center wins; else one clear pocket) | | `fs-pocket.md` |
| `pocket_curves` | Radial cuts around pocket | `curves_along_pocket` | | `fs-pocket.md` |
| `pocket_edcs` | EDCs around / along pocket ray | `edcs_along_pocket` / `radial_edcs_along_pocket` — **ask** | | `fs-pocket.md` |
| `smooth_gaussian` | Gaussian denoise | `gaussian_filter_arr` — state σ | | `smooth-deconvolve.md` |
| `smooth_other` | Boxcar / Savitzky–Golay | `boxcar_filter_arr` / `savitzky_golay` — **ask** | | `smooth-deconvolve.md` |
| `deconvolve_psf` | Build / accept PSF | `make_psf1d` or user PSF — required before RL/ICE | | `smooth-deconvolve.md` |
| `deconvolve_rl` | Richardson–Lucy / ICE | `deconvolve_rl` default; `deconvolve_ice` if asked — **never auto** | | `smooth-deconvolve.md` |

**User (session)** column: fill only after [confirm](#discovery--confirm). Not
committed into the skill repo for a specific user — persist in the **user
project** if needed.

---

## Discovery + confirm

When on the **user-map** path (or user asks to map their code while PyARPES
exists):

1. Search the project for loaders, EF/edge fits, k/kz convert, peak fit, gap /
   symmetrize, overview plotting.
2. Propose a filled map: `ID → module:callable` + one-line why each match.
3. **Wait for user confirm** (all or per-ID).
4. Optional: write confirmed map to the project’s
   `analysis/backend_map.json`, e.g.:

```json
{
  "backend": "user-map",
  "confirmed": true,
  "map": {
    "load_spectrum": "mypkg.io.load_arpes",
    "convert_k": "mypkg.kspace.to_k"
  }
}
```

5. Recall from that file on later turns; refresh if paths break.
6. Unmapped ID needed for the asked task → **ask** or skip with reason.
   Do not reimplement PyARPES under `analysis/` without package-first A/B/C.

---

## Reporting

Every analysis report states:

- Backend: `pyarpes` | `user-map` | `inspect-only`
- If `user-map`: which IDs were used (and that they were confirmed)
- Physics assumptions still required (EF, Γ, V₀, T, resolution, p–h, …) —
  backend choice does not waive them

---

## Do not

- Call unconfirmed user functions.  
- Treat xarray inspect-only as a full analysis backend.  
- Add a new skill workflow without updating this inventory (living-list rule).  
- Claim TensorSpec is wired — still deferred.  
- Assume user callable ≡ PyARPES scientifically without stating assumptions.
