# Debye–Waller test — Implementation record

**Goal:** add the Debye–Waller routine used on a temperature series (a question raised by a
one-step-theory collaboration, Oct 2026) as its own reference recipe, replacing the short
§ 5 of `temperature-series.md` with a pointer.

**Content:** |G| = photoelectron momentum with V₀ propagated; one lineshape model at every T;
observables A (band present at every T, several energies), B (one deep EDC feature), C (deep window
control), D (MDC background); area vs height; 5 % normalisation floor; weighted ln-fit with scaled
covariance; ⟨u²⟩ and Θ_D per sublattice mass (2σ bound when the slope is zero); full Debye ⟨u²⟩(T)
for the figure; k-dependence test; excluded temperatures; the hν-pair discriminator.

## File map

| Action | Path |
|--------|------|
| Add | `reference/debye-waller.md`, `examples/debye_waller.md` |
| Modify | `reference/temperature-series.md` (§ 5 → pointer), `reference/backend-capability-map.md` (`debye_waller_fit` row), `SKILL.md`, `README.md`, `reference/failure-modes.md` |

Docs only; no scripts; nothing duplicated from `temperature-series.md` § 0/§ 3 (inputs) or `near-ef-gap.md` (FD).
