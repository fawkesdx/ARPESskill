# Example: temperature series (track, weight, λ, Debye–Waller)

Follow `reference/temperature-series.md`. Several cuts of one k-line at different
temperatures, k-converted, EF aligned per scan. All numbers are EXAMPLE values.

```python
import numpy as np, h5py
# 0. metadata per scan from the RAW header (field names are beamline-specific; MAESTRO MH1 shown): exposure = sweeps x frames
with h5py.File("scan_0001.h5") as f:
    d = {r[0].decode(): r[2].decode().strip() for r in f["Headers/DAQ_Swept"][()]}
    expo = int(float(d["SSsw0"])) * int(float(d["SSfr_0"]))        # validate with a same-T control pair
    # T: scan comment / log or a contact-thermometer channel; a saturating cryostat sensor is not the sample T
```

```python
# 1-2. PyARPES: same high-T sub-model (outer pair) at every T; shared width via lmfit expr, bounded centres
from arpes.fits.fit_models import VoigtModel, AffineBackgroundModel
from arpes.fits.utilities import broadcast_model
model = AffineBackgroundModel() + VoigtModel(prefix="OL_") + VoigtModel(prefix="OR_")
params = {"OL_center": {"value": -0.10, "min": -0.13, "max": -0.07},
          "OR_center": {"value": +0.10, "min": +0.07, "max": +0.13},
          "OL_gamma": {"value": 0.03, "min": 0.005, "max": 0.045},     # cap = WCAP x pass-A pair width at E_ref (example numbers)
          "OR_gamma": {"expr": "OL_gamma"}}                             # one width per pair
# res_T = broadcast_model(model, cut_T.sel(eV=slice(-0.15, 0)), "eV", params=params)
# widths_T = res_T.F.p("OL_gamma"); centers_T = res_T.F.p("OL_center")
```

Phase 2 (linear-constrained centres, shared |slope| per pair, X crossing from the
EF separation) has no package helper on either backend: state **user-map** and
keep the constrained fitter in `analysis/` (document δ, WCAP, E_ref, windows).

```python
# 3. weight per sweep x frame, FD-corrected, with the control pair and deep reference echoed
kB = 8.617e-5
def fd_broadened(E, T, dE=0.00506):
    from scipy.ndimage import gaussian_filter1d
    g = np.arange(-0.3, 0.3, 2e-4); f = 1 / (1 + np.exp(g / (kB * T)))
    return np.interp(E, g, gaussian_filter1d(f, (dE / 2.3548) / 2e-4))
# area_T = fitted Voigt area / expo_T / fd_broadened(E, T); report with FWHM and height per side
# control: two scans at the same T with different exposure -> area ratio must be 1.00
# deep reference: mean counts / expo in a window ~1 eV below E_F, small |k| -> flat to a few %
```

```python
# 4. linewidth vs T -> lambda(E) with ONE velocity
v = 1.6                                    # eV*A EXAMPLE: the stated velocity (e.g. phase-2 common slope)
# Gamma[T][E] = FWHM_k[T](E) * v  (eV)
# for each E: slope, G0 = lstsq(T, Gamma); lam = slope / (2*np.pi*kB)
# report lam(E) +- sigma for T <= 300 K and for the high-T-only range; flag E where the model changes
```

```python
# 5. Debye-Waller: ln I = ln I0 - <u2> |G|^2, |G| = photoelectron momentum (not the band k)
hv, phi, V0 = 80.0, 4.5, 12.0               # EXAMPLE values
G = 0.5123 * np.sqrt(hv - phi + V0)        # a few 1/A; propagate the V0 uncertainty
# I(T) = peak area (and height) of ONE feature with ONE model at every T, per sweep x frame, FD-corrected
# fit ln I vs T for T below the structural transition and without flux changes; echo deep-window and background controls
```

**Report:** metadata table (T source, exposure, crop); which model at which T;
cap-limited pairs; normalisation used and rejected; per-side area / FWHM /
height table; λ(E) with v and T range; DW slope, ⟨u²⟩(T), Θ_D with mass, excluded
scans; figures under `analysis/figures/`.
