# Failure modes

Common agent mistakes in ARPES analysis and the correct behavior. Cross-check against
`SKILL.md` hard rules before reporting results.

| Failure | Correct |
|---------|---------|
| Plot angle axis labeled as k | Convert first with `convert_to_kspace`, or label axes in **degrees** (°) |
| hv scan plotted as kz without V₀ | Set or ask for `inner_potential`; state uncertainty if V₀ unknown |
| Swap binding ↔ kinetic | Check PyARPES convention (binding often ≤0 below EF); state which is used |
| Invent MAESTRO motor names | Read coords/attrs from file — never guess `phi`, `theta`, etc. |
| "Γ is at image center" | No — state method to find Γ (manual pick, fit, symmetry, model) |
| Fit without lineshape | Name Gaussian, Lorentzian, or Voigt (+ background if used) |
| Core fit without ROI / invent Doniach–Šunjić | Shirley + package peaks; ask if exotic model missing (`edc-mdc-fitting.md`) |
| Broadcast fit with no E vs k / width follow-up plots | Save default derived curves (`edc-mdc-fitting.md`) |
| Quote vF / m* without band model or k window | Linear/Quadratic on centers; state units + window; prefer k-space |
| Treat core-as-2D as valence EDC/MDC broadcast | Angle-integrate; core section first; no default k-convert |
| Use TensorSpec APIs in v1 | Defer; use PyARPES for load, reduce, fit, and k/kz |
| XY spatial overview = one random mid pixel only | Spatial set: \(I_R\) map, hot-spot, mean (`spatial-xy-scans.md`) |
| XY map with no stated spectroscopic ROI \(R\) | Echo default or user box (E ± φ/ψ); rebuild if \(R\) changes |
| Auto broadcast fit every XY pixel | Hot-spot kind analysis first; broadcast only if asked + token note |
| k/kz whole spatial hypercube by default | Reduce ROI / hot spot / spatial mean first |
| Treat hot spot as Γ or EF | Anti-claim; run EF/Γ workflows separately if needed |
| Treat polarization as ordinary intensity for fits/k | State channel; usually fit up/down or total I (`spin-arpes.md`) |
| Invent Sherman function / DIY P formula | Package `to_intensity_polarization`; **ask** if Sherman missing |
| Claim SARPES live-tested with no user file | No spin `example_data`; say untested until user provides data |
| Call ring `beam_current` sample transport I | Confirm meaning; ring ≠ sample (`in-operando-param-scans.md`) |
| Assume `volts` = gate / invent dose coverage math | Ask units/meaning; no DIY calibration formulas |
| Param series overview with no \(P\) meaning stated | Confirm \(P\); mid \(P^*\) or ask if stepped plateaus |
| Treat pump–probe `delay` as generic \(P\) only | Use `tr-arpes.md` (t0 + Δ maps), not only in-operando |
| Invent t0 or mix fs/ps without stating | attrs/`find_t0`/ask; echo units |
| ΔI without pre-t0 reference / buffer stated | `relative_change` / normalized; state t0 + buffer |
| DIY Σ from FWHM / invent k-dependent Σ | Package `to_self_energy` / `fit_for_self_energy`; k-independent only (`self-energy.md`) |
| Σ on multi-band without asking | Single-peak preflight; stop + ask |
| Quote lifetime / mfp in default Σ report | Ask first; state formula + units |
| Silent bare-band choice for ReΣ | Echo `ransac_linear` / `linear` / user |
| Replace intensity with curvature / claim peaks from MG | Both maps; state derived; fits elsewhere (`band-enhance.md`) |
| Enhance full 3D volume by default | Reduce to 2D cut first |
| DIY pocket centroid / silent multi-pocket | User center or `pocket_parameters` if one clear sheet (`fs-pocket.md`) |
| Pocket center = Γ without ask | Γ workflow separate; ask before offsets |
| Auto-deconvolve / invent PSF | Smooth ≠ deconvolve; PSF required (`smooth-deconvolve.md`) |
| Silent swap raw → smoothed for fits | Echo which array; opt-in |
| Launch QtTool as only path | Prefer scripted PyARPES + matplotlib; GUIs are optional |
| PyARPES missing → silent xarray fallback | **STOP**; discover/offer shared env; if declined → user-map then inspect-only |
| New `.venv-arpes` every project when shared exists | Reuse conda `arpes38` / `~/arpes-py38-venv` (`pyarpes-env.md`) |
| Call user functions without confirmed map | Propose map; wait (`backend-capability-map.md`) |
| New skill workflow without capability row | Same-change update to `backend-capability-map.md` |
| Install PyARPES without asking | Ask first; install only if the user says yes |
| `pip install arpes` on Python 3.9+ / default env | Refuse; shared 3.8 env (`reference/pyarpes-env.md`) |
| Bare `pip install arpes` hangs on PyQt / qmake | Use conda `pyqt=5` first, then `pip install arpes --no-deps` |
| Loader complains about **h5** / **fits** | Install **h5py** (HDF5 `.h5`) and **astropy** (FITS `.fits`) — not peak-fitting |
| Dump full arrays / whole beamtime into chat | Warn (token note); write scripts + files under `analysis/` instead |
| Cut overview = 1D line / Fermi or hv = single edge frame | Use `default-overview-plots.md`: cut=1; Fermi trio; hv/kz trio (isoenergy + photon-axis dispersion) |
| Silent custom loader when PyARPES fails | Stop; report error; ask before new code (`package-first.md`) |
| Only try MH1 `.h5` when sibling `.fits` exists | Prefer `.fits` + `load_data(..., location='MAESTRO')` first (`formats-and-axes.md`) |
| Blind `S.spectra[0]` / first spectrum var | Skip `*num*`; pick largest `spectrum-*` intensity image |
| Invent `rot90` / rename axes to match another format | Trust loaded coords; ask if display orientation is wrong |
| Trust log “EPH/Cut” over dims for overview kind | **Dims win**; log is comment only (`default-overview-plots.md`) |
| Report omits overview assumptions | Echo defaults + anti-claims (Γ / k / EF / kz) in report header |
| Mid pixel / mid ψ claimed as Γ or E=0 as calibrated EF | Anti-claims in `default-overview-plots.md` assumptions section |
| `convert_to_kspace` during quick-report trios | Quick = angle-space only; k/kz = analysis / user ask (`k-and-kz-conversion.md`) |
| Invent absolute KE matrix when EF-aligned `eV` + `hv` exist | Use PyARPES convention; WF only for EF calibration if needed |
| Γ claimed with no method / ignore user offset | Label provisional heuristic; **user offset wins**; persist in npz |
| Reuse stale k npz after Γ / V₀ / grid change | Recompute and overwrite (or version); meta must match |
| Skip energy-axis notice on load | Always state Ek / Eb / E−EF / ambiguous |
| Convert cut to k without PyARPES EF finder | Fit edge first; report EF_fit + meV from 0; shift EF→0 |
| Claimed E−EF/Eb but \|EF_fit\| > 50 meV, no note | Warn **possible charging**; still print deviation |
| Invent k formula or auto-Γ / FS-center finder | `convert_to_kspace` + `apply_offsets` only; Fermi: ask if no package path |
| Fermi map → k without EF finder | Same energy rules as cut (`k-and-kz-conversion.md`) |
| hv stack → kz without per-hv EF align | Backend path in `k-and-kz-conversion.md`: `pyarpes` angle-sum + `shift_by`; viewer `kz_map` → `process_kz_map` |
| Treat `tools.kzmap` prep as kz conversion | Prep ≠ Å⁻¹; still need V₀ + `kzconv` / `convert_to_kspace` |
| Mid-φ / single-pixel EDC as default hv EF fit | `pyarpes`: sum/mean over φ; viewer: ask/state **index box** (same indices all hv) |
| Norm viewer kz_map before align | Only after align+crop (`normalise_totals`) |
| Report a separate “kz-map skill” | One skill: k/kz conversion (viewer prep subsection) |
| Mean-only EF report for hv stack | Report **per-hv** EF_fit + meV from 0; plot EF_fit vs hv |
| Skip EF QC / post-shift then claim kz FS | Hard-stop on junk/pinned/stderr; verify ≈0 at low/mid/high hv |
| hv npz with only scalar `ef_fit_eV` | Require `ef_fit_per_hv` (+ optional plot path) |
| broadcast_model broken → mid-φ fallback | Loop **summed-φ** EDCs + `AffineBroadenedFD`; ask if still fails |
| Slit offset from high-hv soft X-ray slice only | Prefer **lowest-hv** slice after EF align |
| Invent photon-momentum / incidence angles | Use `beamline-geometry.md`; MAESTRO / ALBA **55°**; ANTARES **45°** + fixed H slit; ask; SLS postponed |
| Assume ANTARES slit rotatable / vertical | Fixed **horizontal**, not rotatable |
| Invent analyzer/beamline ΔE when tables missing | Package estimates or **ask** (`resolution.md`); no DIY pass-energy math |
| Apply MERLIN resolution tables to ANTARES/MAESTRO | Endstation-specific; report failure |
| Shirley default on valence / hull on core | Path B: core→Shirley; valence→hull (`backgrounds.md`) |
| Auto incoherent-above-EF on every cut | Only if asked; edge heuristic warned |
| Silent swap raw → bg-subtracted | Echo method; before/after |
| Invent a₀ / BZ for unnamed crystal | User cell or graphene/ws2/wse2→`wwe2` only (`bz-overlay.md`) |
| Claim data-on-3D-BZ / DIY hexagon | Package 2D `plot_data_to_bz` / `bz_plot` only; 3D data N/I |
| Silent missing `ase` for BZ | Report optional dep; ask install or user cell |
| DIY rebin / silent normalize before fits | Package `rebin` / `normalize_dim`; echo product (`axis-prep.md`) |
| Confuse axis symmetrize with gap EDC symmetrize | `symmetrize_axis` vs `gap.symmetrize` (`axis-prep.md`, `near-ef-gap.md`) |
| Invent polygon / silent full-frame mask | User vertices or boolean; echo; package `apply_mask` (`masks.md`) |
| Confuse spatial spectroscopic ROI with polygon mask | ROI = `spatial-xy-scans.md`; polygon = `masks.md` |
| DIY correlate / silent apply align offset | Package `align`; ask before apply (`align.md`) |
| Invent mosaic stitch from align | Offset only; no invent stitch (`align.md`) |
| DIY sklearn decomp / silent NMF on negatives | Package `*_along`; NMF non-neg warn (`decomposition.md`) |
| DIY waterfall / invent σ for ToF plots | Package stack / `plot_with_std` (`stack-plots.md`) |
| DIY k-path / invent angular high-sym for forward cut | Package `convert_through_angular_*` (`forward-k.md`) |
| Subtract CP−CM without null-ROI scale / invent null | Scale first; user ROI (`dichroism.md`) |
| Dichroism via SARPES polarization helpers | Different physics; use `dichroism.md` |
| Sequential / jet cmap for dichroism | Red+/blue− diverging; echo clim (`dichroism.md`) |
| Invent KE cube when `eV`+`hv` present | Use EF-aligned `eV` + `hv`; no invented matrix |
| Long swept “Cut” treated as valence only | Check core-as-2D heuristics; report image + angle-integrated EDC (`default-overview-plots.md`) |
| Valence k-conversion on suspected core-as-2D | Stop / ask; user must override science kind |
| Re-walk folder / paste full catalog every turn | Build `analysis/manifest.json`; recall later (`folder-manifest.md`) |
| Folder map uses full `load_data` / spectrum | Peek only (astropy/h5py or viewer `list_entries`); full load at overview/analysis (`folder-manifest.md`) |
| Force PyARPES on ANTARES `.nxs` without ask | Route B → `arpes_viewer` or ask (`arpes-viewer-backend.md`) |
| Force viewer on MAESTRO FITS without ask | Route B → `pyarpes` or ask |
| PCA / decomp on `arpes_viewer` stem silently DIY | Stop; offer **D** (switch to `pyarpes`) / B / C (`package-first.md`) |
| Silent `NxsScan` ↔ xarray bridge | Forbidden; ask **D** or user export |
| Install viewer deps into PyARPES 3.8 env | Separate env (`arpes-viewer-env.md`) |
| De-grid after k / FS bend / kz-align / smooth | Refuse; `not_pixel_locked` (`degrid.md`) — do first |
| DIY FFT / Wiener “degrid” | `tools.degrid` on `arpes_viewer` only; else A/B/C/**D** |
| Silent `degrid_cut_notch` without PE-loss warn | Warn; prefer map `[grid]` + `degrid_cut_with_grid` |
| De-grid on `pyarpes` stem without ask | Stop; offer **D** / B / C (`degrid.md`) |
| Ignore stale manifest after files change | Refresh rows when mtime/hash differs |
| Treat log “Cut” as kind without dims/heuristics | Dims + core-as-2D rules; log → `log_comment` only |
| Reimplement fit / k-conversion by hand | Use active-backend APIs; ask A/B/C/**D** if unavailable |
| Near-EF FD divide without resolution | Always convolve FD with resolution (`near-ef-gap.md`) |
| Symmetrize every EDC by default | Only for gap/pseudogap (or explicit ask); state p–h symmetry |
| DIY symmetrize / invent gap Δ fitter | `arpes.analysis.gap.symmetrize`; ask before custom Δ |
| Metal EF / gap workflow in quick report | User-asked cut analysis only (`near-ef-gap.md`) |

## Additional guidance

- **Angle vs momentum:** detector or manipulator angles are in degrees until
  `convert_to_kspace` produces k coordinates. See `reference/k-and-kz-conversion.md`.
- **Inner potential:** absolute kz from hv scans requires V₀ in
  `spectrum.attrs["inner_potential"]`. If unknown, report relative kz or ask one
  sharp question.
- **Γ (gamma point):** for **overview** plots, mid-frame ≠ Γ. For **k conversion**,
  use provisional heuristic labeled as such, or user offset (wins). Never claim
  Γ without method. See `reference/k-and-kz-conversion.md`.
- **k/kz:** analysis mode only; cache under `analysis/kspace/*.npz`. Quick
  report must not convert.
- **Folder inventory:** multi-file work starts with `analysis/manifest.json`
  via **peek** (`folder-manifest.md`); record `backend` per row; recall
  instead of re-cataloging; no full spectrum load for first map.
- **Fits:** every reported fit must name the lineshape and any background model. See
  `reference/edc-mdc-fitting.md`.
- **Self-energy:** single-band; package `to_self_energy` / `fit_for_self_energy`;
  state bare band; no default lifetime (`self-energy.md`).
- **Band enhance:** both curvature + min-gradient; not intensity; no EF/centers
  from these alone (`band-enhance.md`).
- **FS pocket:** one sheet; user or package center; not auto-Γ (`fs-pocket.md`).
- **Smooth / deconvolve:** gaussian for noise; RL only if asked + PSF
  (`smooth-deconvolve.md`).
- **Resolution:** package estimates; ask if tables missing (`resolution.md`).
- **Backgrounds:** Shirley core / hull valence / incoherent ask (`backgrounds.md`).
- **BZ overlay:** user cell wins; named library only; ase optional; no invent
  lattice; no 3D data-on-BZ (`bz-overlay.md`).
- **Axis prep:** package rebin/symmetrize/normalize/sort/condense; echo dims;
  no silent normalize (`axis-prep.md`).
- **Masks:** boolean or package polygon; GUI ask; no invent outline (`masks.md`).
- **Align:** package correlation offset; ask before apply; not stitch (`align.md`).
- **Decomposition:** package `*_along`; echo axes/n_components; NMF non-neg
  (`decomposition.md`).
- **Stack plots:** package helpers; no invent σ (`stack-plots.md`).
- **Forward k:** package through-point/pair / coord_forward; user points
  (`forward-k.md`).
- **Dichroism:** null-ROI scale then D+A; red+/blue−; not SARPES (`dichroism.md`).
- **Stack policy:** prefer PyARPES; if missing, offer venv then **user-map**
  (`backend-capability-map.md`); inspect-only last. TensorSpec deferred.
  New workflows must update the capability inventory (living list).

When in doubt, read the matching `reference/` file and ask the user one sharp question
rather than inventing axes, units, or physics assumptions.
