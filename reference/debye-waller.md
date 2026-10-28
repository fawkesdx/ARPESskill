# Debye–Waller test on a temperature series

**Gate:** user (or a theorist they relay) asks whether **thermal Debye–Waller (DW)
suppression** of the coherent direct-transition intensity explains the temperature
smearing of a cut, or asks for `⟨u²⟩(T)` / an effective Debye temperature from
ARPES. Upstream: the temperature-series workflow (`temperature-series.md`:
metadata, exposure, one model per T). Capability: `debye_waller_fit`.

The routine below was built for a MAESTRO near-Γ series (30–500 K, eight scans,
hv 81.85 eV); the numbers are examples of what to check, not defaults.

---

## Physics to state before fitting

- Coherent intensity: `I(T) = I₀ · exp(−2W(T))`, `2W = ⟨u²⟩(T) · |G|²`, plus a
  k-averaged, DOS-like incoherent part that grows as the coherent part falls.
- **|G| is the photoelectron momentum** at the emission geometry, not the in-plane
  band momentum: near normal emission `|G| ≈ k_f = 0.5123·√(hν − φ + V₀)` Å⁻¹
  (≈ 4.8 Å⁻¹ at 82 eV). With the band k (~0.1 Å⁻¹) 2W would be < 10⁻³ at any T.
  State φ and V₀ (± uncertainty; V₀ from `k-and-kz-conversion.md` rules — never a
  silent guess) and propagate `δ|G| = 0.5123·δV₀ / (2√(hν−φ+V₀))`.
- A DW factor is **uniform in in-plane k and E** and conserves nothing locally: it
  cannot shift k_F, change a velocity or create a new band. A **lifetime** effect
  broadens peaks and keeps their area. This is what the test separates.
- Debye model for the figure and for Θ_D:
  `⟨u²⟩(T) = 3ħ²/(M k_B Θ_D) · [¼ + (T/Θ_D)² ∫₀^{Θ_D/T} x/(eˣ−1) dx]`;
  high-T limit `⟨u²⟩ ≈ 3ħ² T /(M k_B Θ_D²)` → `Θ_D = √(3ħ²/(M k_B · d⟨u²⟩/dT))`
  with `ħ²/(amu·k_B) = 48.51 Å²·K`. The DW factor is atom-resolved: quote Θ_D for
  **each** sublattice mass that contributes to the initial state (e.g. Te and V).

---

## Inputs (from `temperature-series.md` § 0 and § 3)

- Cuts of the same k-line at every T, EF aligned; T from scan comment / contact
  thermometer; **exposure = sweeps × frames** from the raw headers.
- Per sweep×frame, divided by the resolution-broadened Fermi function (state T, ΔE).
- A **normalisation floor** (≈ 5 %) added in quadrature to every point (the deep
  reference is constant to ~3 %; without the floor the χ² is meaningless).
- **Exclude** scans with a flux / spot change (deep reference drops) and
  temperatures beyond a **structural transition** of the material (plot them, say
  they are excluded).

---

## Observables — one lineshape model at every T

| | model | why |
|---|---|---|
| **(A)** MDC peaks of the band that exists at every T, at several energies in a window where **only** that band is present (e.g. the outer pair at −90..−120 meV) | 2 Lorentzians + linear bg, bounded centres/widths | area per side and L+R; mean over the energies |
| **(B)** one sharp **EDC** feature far from E_F and from any T-dependent new band (e.g. the band-crossing peak at −0.22 eV, \|k\| ≤ 0.05) | Lorentzian + linear bg over a stated window | the cleanest single coherent feature |
| **(C)** deep window (e.g. −1.3..−0.9 eV, \|k\| ≤ 0.2) | window mean | DW-insensitive by the sum rule → flux / normalisation **control**; must be flat |
| **(D)** the MDC background level under (A) | from the fit | DW predicts a k-independent background that **rises** as peaks lose weight — but a broadening tail does the same, so (D) is ambiguous on its own |

Report **area and height separately** for (A) and (B). Area decay = weight loss
(DW-like); height decay with constant area = broadening (lifetime).

Error per point: Poisson on the counts ÷ √exposure, a few % of the maximum, the
fit covariance for areas (`σ_A = A·√((σ_w/w)² + (σ_h/h)²)`), then the floor.

---

## Fit

1. Weighted linear least squares of `ln I` vs T over the kept range:
   `ln I = ln I₀ + s·T`, `σ_lnI = √((σ_I/I)² + floor²)`; scale the covariance by
   max(χ²ᵣ, 1).
2. Convert: `d⟨u²⟩/dT = −s / |G|²` (error from σ_s and δ|G|),
   `2W(T_hi) − 2W(T_lo) = −s·(T_hi − T_lo)`, `⟨u²⟩(T_hi) − ⟨u²⟩(T_lo)`.
3. `Θ_D` per mass from the high-T limit; when the slope is consistent with zero,
   give the **2σ lower bound** on Θ_D (upper bound on the loss) instead of a value.
4. Do the same fit for (C) and (D); (C) must give s ≈ 0.
5. **k-dependence test:** `I(T_lo)/I(T_hi)` at the same k and E across the cut. A
   pure DW factor is a flat line at `exp(2W(T_hi) − 2W(T_lo))`; strong k / E
   dependence means band reconstruction, which DW cannot produce.

---

## Figure (one page)

(a) the MDC with fits at every T; (b) the EDC with fits; (c) `ln I(T)/I(T_lo)` for
A-area, B-area, C, D and a height, with the fit lines **and** the Debye prediction
for two or three Θ_D at the stated |G|; (d) per-side areas vs T at each energy;
(e) the k-dependence ratio with the pure-DW line; (f) apparent `⟨u²⟩(T) − ⟨u²⟩(T_lo)`
from the areas against the Debye curves.

---

## Report

- |G| with φ, V₀ ± δ; fit range and the excluded scans with the reason.
- Table per observable: slope ± σ (10⁻³/K), `2W` change, `d⟨u²⟩/dT`, `⟨u²⟩` change,
  Θ_D per mass (or 2σ bound), χ²ᵣ; per-temperature values in a log.
- The headline in words: whether the **areas** decay, the 2σ upper limit on
  coherent loss, the Θ_D bound; whether the **heights** fall through broadening;
  what the k-dependence shows; what the background does and why it is ambiguous.
- Caveats: few temperatures; nominal base T; V₀ assumed (enters ⟨u²⟩ quadratically);
  weight transfer / matrix elements can mimic or mask the decay (`temperature-series.md`
  § 3); Θ_D needs a per-sublattice reference from diffraction or specific heat.
- The decisive experiment: a **photon-energy pair at two temperatures** —
  2W ∝ E_kin, lifetime broadening is not. Offer it.

---

## Package map

| Step | PyARPES | ARPES-data-browser | Note |
|------|---------|--------------------|------|
| FD correction | FD helper / `arpes.analysis.gap` | `tools.fermi.fermi_function` | ⊗ Gaussian(ΔE) |
| Peak fits (A)(B) | `broadcast_model` / `LorentzianModel` + affine, or `curve_fit` on the extracted curve | `tools.peaks.fit_line` | one model at every T |
| ln-fit, Debye ⟨u²⟩, Θ_D | numpy lstsq, `scipy.integrate.quad` | same | no package helper; formulas above |

## Do not

- Use the in-plane k as |G|; silently assume V₀.
- Fit heights and call the decay DW without checking the areas and widths.
- Include a scan whose deep reference moved, or a temperature past a structural
  transition.
- Quote Θ_D for one mass as "the" Debye temperature of a compound.
- Claim DW explains smearing that is k- or E-dependent.
