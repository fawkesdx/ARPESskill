# Self-energy (Σ) from MDC / EDC fits

**Gate:** user asks for **self-energy**, **Σ(E)**, ReΣ/ImΣ, or quasiparticle
lifetime / mean free path from a **single-band** cut. Not a default overview
step.

**Prefer:** momentum-converted cut (`kp` / `kx` / …). Angle-space MDCs only if
user insists — state that Σ units / vF conversion are less trustworthy.

**Docs:** `arpes.analysis.self_energy` · MDC broadcast → linewidth + dispersion

Capabilities: `self_energy_fit`, `self_energy_from_mdc`, `estimate_bare_band`,
`qp_lifetime` — `backend-capability-map.md`.

---

## Preflight

1. **Single peak** in the ROI (one Lorentzian-like band). Multi-band / overlapping
   peaks → **stop and ask** (package helpers assume one peak-like component).  
2. Prefer **k-converted** intensity vs (`eV`, momentum).  
3. Prefer **MDC** path (`method="mdc"`): broadcast along `eV`. EDC path only if
   user asks (`method="edc"`).  
4. If session already has a **single-peak MDC broadcast** `ModelResult` array →
   reuse it (**path C**). Else run package fit (below).

---

## Path C (default)

| Situation | Action |
|-----------|--------|
| MDC broadcast results already in session | `to_self_energy(results, bare_band=…)` |
| No prior MDC fits | `fit_for_self_energy(data, method="mdc", bare_band=…)` |

`fit_for_self_energy` = `broadcast_model([LorentzianModel, AffineBackgroundModel], …)`
then `to_self_energy`. **Name** Lorentzian + affine every time.

Package supports **k-independent** Σ only (`k_independent=True`). Do **not** invent
k-dependent Σ.

---

## Bare band

Required for **ReΣ** (and for MDC → energy-unit ImΣ via Fermi velocity).

| Spec | When |
|------|------|
| **`ransac_linear`** (default) | Package default via `estimate_bare_band`; **state it** |
| `linear` | User asks ordinary linear fit (no RANSAC) |
| User E(k) | User supplies bare dispersion — use it; label *user* |

Never silently switch. Echo bare-band method in the report.

```python
from arpes.analysis.self_energy import (
    fit_for_self_energy,
    to_self_energy,
    estimate_bare_band,
    quasiparticle_lifetime,
)

# Prefer existing MDC broadcast `results` if present:
# se = to_self_energy(results, bare_band="ransac_linear")
# Else:
# se = fit_for_self_energy(kcut, method="mdc", bare_band="ransac_linear")
# se["self_energy"]  # complex: Re + i Im
# se["bare_band"]
```

Physics (package): ImΣ from Lorentzian **FWHM/2** (γ); on MDC fits, widths are
scaled by Fermi velocity into energy units. ReΣ = measured dispersion − bare band
(MDC form uses vF). State that resolution / lineshape bias Σ.

---

## Default report

Save under `analysis/`:

1. **ReΣ** vs energy (or fit axis)  
2. **ImΣ** vs same axis  
3. **Bare band** overlay on measured centers (or dispersion plot)  
4. Echo: path (reuse MDC vs `fit_for_self_energy`), bare-band spec, k vs angle,
   Lorentzian+affine

### Optional (ask first)

| Quantity | API | Note |
|----------|-----|------|
| Quasiparticle lifetime | `quasiparticle_lifetime(Σ, bare_band)` | From \|ImΣ\|; **state** formula / units |
| Mean free path | `local_fermi_velocity` × lifetime (package helper if present) | Meters; needs bare-band vF |

Do **not** quote lifetime / mfp in the default report unless the user asks.

---

## Package map

| Step | Prefer |
|------|--------|
| Fit + Σ | `fit_for_self_energy` |
| Σ from existing MDCs | `to_self_energy` |
| Bare band | `estimate_bare_band` / string spec / user array |
| Lifetime | `quasiparticle_lifetime` — ask first |

Upstream MDC broadcast alone: `edc-mdc-fitting.md` (`broadcast_model`).

---

## Do not

- DIY Σ from FWHM without package helpers when they import.  
- Claim k-dependent Σ (not implemented in stock PyARPES).  
- Multi-peak / multi-band without asking.  
- Default lifetime / mfp claims.  
- Bare FD / gap recipes here — use `near-ef-gap.md` for gap/pseudogap.  
- Invert vF / m\* band fits into Σ without this workflow.

---

## Checklist

1. Single-band ROI; k-space preferred; method mdc (or edc if asked).  
2. Path C: reuse MDC results **or** `fit_for_self_energy`.  
3. Bare band stated (`ransac_linear` / `linear` / user).  
4. ReΣ + ImΣ + bare-band plot saved; Lorentzian+affine named.  
5. Lifetime / mfp only if asked + assumptions stated.
