# Example: Debye–Waller test on a temperature series

Follow `reference/debye-waller.md` (inputs from `reference/temperature-series.md`).

```python
import numpy as np
from scipy.optimize import curve_fit
from scipy.integrate import quad
from scipy.ndimage import gaussian_filter1d
KB, HB2_AMU_KB = 8.617e-5, 48.51           # eV/K ; hbar^2/(amu kB) in A^2 K
HV, PHI, V0, V0E = 80.0, 4.5, 12.0, 4.0    # eV, EXAMPLE values: your photon energy, work function, inner potential +- uncertainty
M = {'A': 100.0, 'B': 50.0}                # amu, EXAMPLE: one entry per sublattice (element) in the initial state
NORM_FLOOR = 0.05
G = 0.5123 * np.sqrt(HV - PHI + V0); Ge = 0.5123 * 0.5 * V0E / np.sqrt(HV - PHI + V0)   # photoelectron momentum, 1/A

def fd(E, T, dE=0.00506):
    g = np.arange(-0.6, 0.6, 2e-4); f = 1 / (1 + np.exp(g / (KB * T)))
    return np.interp(E, g, gaussian_filter1d(f, (dE / 2.3548) / 2e-4))
lor = lambda x, c, w, h: h / (1 + (2 * (x - c) / w) ** 2)
mdc2 = lambda k, cL, wL, hL, cR, wR, hR, b0, b1: lor(k, cL, wL, hL) + lor(k, cR, wR, hR) + b0 + b1 * k
edc1 = lambda E, c, w, h, b0, b1: lor(E, c, w, h) + b0 + b1 * (E - c)
area = lambda w, h: np.pi * w * h / 2

# per scan: v (E x k) per sweep x frame; (A) the band present at every T, at E0 in its exclusive window; (B) one deep EDC peak; (C) deep window
# y = v[i-2:i+3].mean(0) / fd(E[i], T); sig = sqrt(max(y,1)/5)/sqrt(expo) + 0.02*y.max()
# p, C = curve_fit(mdc2, k, y, p0=..., sigma=sig, bounds=...); aL, aR = area(p[1], p[2]), area(p[4], p[5])
# edc = v[:, |k|<=k_win].mean(1); p, C = curve_fit(edc1, E[sel], edc[sel], ...); a = area(p[1], p[2])
# deep = v[(E>=E_deep_lo)&(E<=E_deep_hi)][:, |k|<=k_deep].mean()

def lnfit(T, A, Ae):
    """weighted ln I vs T; returns slope, sigma, intercept, chi2_r (covariance scaled by max(chi2_r, 1))"""
    y = np.log(A); s = np.sqrt((Ae / A) ** 2 + NORM_FLOOR ** 2)
    X = np.vstack([T, np.ones_like(T)]).T / s[:, None]; sol, *_ = np.linalg.lstsq(X, y / s, rcond=None)
    cov = np.linalg.inv(X.T @ X); chi2 = float((((y - X @ sol * s) / s) ** 2).sum() / max(len(T) - 2, 1)); cov *= max(chi2, 1.0)
    return sol[0], np.sqrt(cov[0, 0]), sol[1], chi2

def convert(slope, slope_e):
    du2 = -slope / G ** 2; du2e = np.hypot(slope_e / G ** 2, du2 * 2 * Ge / G)        # d<u^2>/dT, A^2/K
    thD = {el: (np.sqrt(3 * HB2_AMU_KB / (M[el] * du2)) if du2 > 0 else np.inf) for el in M}   # high-T Debye limit
    return du2, du2e, thD   # if du2 <= 2*du2e: report the 2-sigma lower bound on Theta_D instead

def u2_debye(T, thD, Mamu):
    I = quad(lambda x: x / np.expm1(x), 0, thD / T)[0]
    return 3 * HB2_AMU_KB / (Mamu * thD) * (0.25 + (T / thD) ** 2 * I)   # full Debye <u^2>(T) for the figure

# fit range: T below the structural transition and without flux change (deep reference flat); run lnfit for
# (A) areas per side and L+R, (A) heights, (B) area and height, (C) deep window, (D) MDC background;
# k-test: I(T_lo)/I(T_hi) vs k at fixed E against the flat DW line exp(2W(T_hi) - 2W(T_lo)).
```

**Report:** |G| (hν, φ, V₀ ± δ); kept / excluded temperatures; per-observable slope,
2W change, d⟨u²⟩/dT, Θ_D per mass or its 2σ bound, χ²ᵣ; area vs height verdict;
k-dependence verdict; caveats; offer the hν-pair experiment.
