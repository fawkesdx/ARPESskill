# Temperature series (T-dependent cuts): tracking, weight, linewidth → λ, Debye–Waller

**Gate:** user has **several cuts of the same k-line at different temperatures**
(or any external parameter where the *lineshape* changes, not only the position) and
asks what changes with T: band splitting / onset, spectral-weight transfer,
linewidth vs T (electron–phonon λ), Debye–Waller. Single-cut fits stay in
`edc-mdc-fitting.md`; a T axis that only moves peaks is `in-operando-param-scans.md`;
single-band Σ(E) at one T is `self-energy.md`.

Capabilities: `tdep_metadata`, `tdep_common_model`, `tdep_constrained_track`,
`tdep_normalize`, `tdep_weight_test`, `tdep_onset_metric`, `linewidth_vs_T_lambda`,
`debye_waller_fit` — `backend-capability-map.md`.

This workflow was built on a MAESTRO near-Γ series (30–500 K, eight scans); the
numbers below are examples of what to check, not defaults to copy.

---

## 0. Metadata first (hard)

Before any fit across temperatures, build one table per scan and **echo it**:

| Field | Where it really is | Why |
|-------|--------------------|-----|
| Sample T | Scan **comment** / log, contact thermometer (`contacts_A`-type 0D channel), raw Fermi-edge width as a cross-check | The `Temperature.Sample` sensor can saturate or read the cold tip; labels from the sensor were wrong above ~135 K and at base T |
| Exposure | Raw header **sweeps × frames** (MAESTRO: `Headers/DAQ_Swept` `SSsw0` × `SSfr_0`; `0D_Data/*_num_sw_actual`) | Counts scale exactly with sweeps×frames; the comment "2 min" is **not** the exposure (wrong by ~1.7×) |
| hv, PE, slit, step, polarisation, ring current, spot | Headers | Must be constant; a flux / spot change (e.g. the highest-T scan) invalidates intensity comparison |
| Crop | k- and E-window containing **every** peak at **every** T | A band whose k_F moves out of the crop at high T breaks the series (re-crop everything, then redo all fits) |

Store it in `analysis/manifest.json` (`folder-manifest.md`).
No fit across T is reported with sensor temperatures or comment times.

---

## 1. One model at every T — or say which model where

- If the peak count N changes with T (fine structure appears on cooling), fit
  **(a)** the full N-band model where it is resolvable and **(b)** the high-T
  sub-model (e.g. the outer pair only) **on the same crop at every T**.
  Compare across T only within (b), or state explicitly when (a) at low T is
  compared with (b) at high T.
- Propose N from a mid-cut MDC and wait (`edc-mdc-fitting.md` multi-band flow).
  Lineshape named every time (Voigt with the instrument Gaussian from the file
  metadata; `resolution.md`).
- **Onset metric:** reduced χ² of the high-T sub-model vs E and vs T (median over
  near-EF and deep windows). A smooth rise on cooling with no step means no
  transition between the measured temperatures; a step locates it.

---

## 2. Constrained multi-band tracking (phase 1 → phase 2)

Free multi-peak broadcasts along E swap tracks and run widths away where peaks
overlap. The two-phase rule used here (user-map; see § Package map):

**Phase 1 — free centres, capped widths (two passes)**
1. Seeds: hand-placed (E, k) anchors per band, PCHIP-interpolated; centres may
   move ± 1.5 × seed width (the package rule).
2. Pass A: widths free → read each **pair's** FWHM at one reference energy
   (e.g. −9 meV).
3. Pass B (kept): **one Lorentzian width per left/right pair**, bounded
   `FWHM ≤ WCAP × (pass-A pair width at E_ref)`, WCAP = 1.5. Report which pairs
   sit on the cap (those widths are lower bounds).
4. Innermost pair: active only within its energy range (e.g. −27 meV..EF).

**Phase 2 — linear-constrained centres**
1. Straight line per branch from the phase-1 centres over a stated trusted
   window; **one shared |slope| per pair**: left `k = −A·E + b_L`, right
   `k = +A·E + b_R` (same |v| both sides). If the band velocity is assumed
   T-independent, fit **one A per pair jointly to all low-T scans**
   (`common_slopes`) and keep only the intercepts per scan.
2. Crossing pairs (X shape): place the crossing from the phase-1 **separation at
   EF**: `E* = −Δk_F / (2A)`, `k* = midpoint`; narrow the centre window near the
   crossing (taper) so the two tracks cannot swap.
3. Centres bounded to ± δ around their line (δ ≈ 0.006 Å⁻¹ here; halve it if
   the user says the window is too wide); widths as in phase 1 pass B.
4. Output per scan: centres ± σ, widths ± σ (full numeric Jacobian), areas,
   χ², flags for cap-limited pairs. Save `analysis/mdc_fit_<phase>_<scan>.npz`.

Never report a track that crosses its own line window as a dispersion; say
"constrained" in every figure caption.

---

## 3. Intensity across T: normalisation and the weight test

Question type: "does the high-T peak break into the low-T fine structure?" or
"is the low-T extra peak new weight?"

1. **Normalise per sweep × frame** from the headers. Validate with a
   **control pair** (two scans at the same T with different exposure → ratio
   must be 1.00 ± few %).
2. **Deep reference**: a window far below EF with no T-dependent band
   (e.g. −1.2..−1.0 eV, |k| small) must be constant per sweep×frame to a few %
   (3 % here). If it is not, the flux/spot changed — do not compare absolute
   weights for that scan (the 500 K scan: 3.5× drop).
3. **Fermi-function correction**: divide by FD(T) ⊗ Gaussian(ΔE from metadata)
   (`near-ef-gap.md` style); state T and ΔE; do not trust the corrected values
   within ~5 meV of EF.
4. Compare **areas** (not heights) of the same band; also report height and
   FWHM — a peak that keeps its area but broadens 40 % looks "weaker".
5. **Matrix elements:** (i) left/right asymmetry of the k-integrated weight vs T —
   if it is T-independent (0.68–0.70 at 30, 80, 300 K here) the geometry factor
   cancels in per-side T ratios; (ii) **fixed-k EDC weight ratios** between
   temperatures are |M(k)|²-robust (same k, hv, geometry); (iii) relative |M|² of
   *different* bands cannot be removed with one polarisation — say so before
   adding band areas.
6. Model-free cross-check: k-integrated weight per side (bg from the outer k
   window) per sweep×frame, FD-corrected.

Report as a table: per T, per side: area, FWHM, height, centre; the control-pair
ratio; the deep-reference constancy; the normalisation used (and the ones
rejected).

---

## 4. Linewidth vs T → electron–phonon λ, and the MFL check

Model (high-T limit of the Eliashberg form): `Γ(E, T) = Γ₀(E) + 2π λ k_B T`,
so `λ(E) = (dΓ/dT) / (2π k_B)`.

1. Use the **same model at every T** for the width (the high-T sub-model); the
   fine-structure decomposition contaminates widths near EF, so expect λ(E) to
   blow up there and say it.
2. Convert the MDC FWHM (Å⁻¹) to an energy width with **one** stated velocity
   `v` (e.g. the phase-2 common slope, 1/A) at all E and T; k-space cut only.
3. Fit Γ vs T linearly at each E on a grid; report λ(E) ± σ for two T ranges
   (all T ≤ T_max, and high-T-only where one model holds) and Γ₀(E).
4. Exclude temperatures beyond a structural transition or with a flux change.
5. **Marginal-Fermi-liquid check** (ask before claiming): MFL needs
   Γ ∝ max(|E|, k_B T) at *every* E; if λ(E) is flat only below some |E| and
   Γ₀(E) grows with |E| the way a Fermi liquid / impurity term does, do not call
   it MFL. Eliashberg saturation above ~Θ_D/… is a slope decrease at high T.
6. Lifetime / Σ(E) at one T stays in `self-energy.md`; this section is the
   **T-derivative** only.

---

## 5. Debye–Waller test (user-asked)

Full routine in `debye-waller.md`: `ln I(T) = ln I₀ − ⟨u²⟩(T)|G|²` with **|G| =
photoelectron momentum** (not the band k), one lineshape model at every T, area
*and* height of one feature, deep-window and background controls, excluded
temperatures (structural transition, flux change), Θ_D per sublattice mass or its
2σ bound, and the k-dependence test. Weight transfer found in § 3 can mimic or
mask the decay; say which range is clean. The clean discriminator is a
photon-energy pair at two temperatures (2W ∝ E_kin).

---

## Package map

| Step | PyARPES | ARPES-data-browser | Note |
|------|---------|--------------------|------|
| Metadata | `load_data` attrs + raw header peek (astropy/h5py) | `loader` + `tools.system` | sweeps×frames, comment T |
| N-band track | `broadcast_model` with prefixed models; `params=` `min`/`max`, `expr` for shared widths / slopes | `tools.peaks.fit_series` (`Band`, `Seed`, `share_width`) | Centre window independent of seed width + width cap: **not** in either package → user-map constrained fitter (state it) |
| Lines / slopes | `estimate_bare_band('linear')` per branch; joint slope by lstsq (user-map) | `tools.dispersion.fit_dispersion` | shared |slope| per pair, common across T if assumed |
| FD correction | `arpes.analysis.gap` / FD helper | `tools.fermi.fermi_function` | ⊗ Gaussian(ΔE) |
| λ, DW fits | numpy lstsq / `curve_fit` on the fit products | same | document formulas; no package helper |

---

## Do not

- Compare intensities normalised by comment time, or by a sensor temperature.
- Compare areas from a six-band fit at low T with a two-band fit at high T
  without saying so.
- Report widths at the cap as physical.
- Claim λ from energies where the decomposition is unstable; claim MFL from
  one energy.
- Use the in-plane k as |G| in a Debye–Waller fit, or include scans beyond a
  structural transition.

## Checklist

1. Metadata table echoed (T source, sweeps×frames, constant optics, crop).
2. Model per T stated; high-T sub-model at every T; onset χ² vs T.
3. Phase 1 (cap rule) → phase 2 (shared slopes, X crossing, δ window); caps flagged.
4. Normalisation validated (control pair = 1, deep reference flat); FD-corrected areas + widths + heights per side.
5. Matrix-element checks: L/R asymmetry vs T, fixed-k ratios.
6. λ(E) with v stated, two T ranges; MFL only if Γ ∝ max(|E|, k_B T) everywhere.
7. DW: |G| = photoelectron momentum, one model, controls, excluded T, Θ_D with mass.
