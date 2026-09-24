# Example: Core-level fit, then EDC/MDC (PyARPES)

**Goal:** Package-only fitting. Start with **core**, then valence **EDC/MDC**.
Follow `reference/edc-mdc-fitting.md` and `reference/package-first.md`.

## 0. Mode

Analysis / user-requested fitting — not quick-report overviews alone.
If the file is **core-as-2D**, angle-integrate before fitting.

## 1. Core level (first)

```python
from arpes.fits.fit_models import GaussianModel, AffineBackgroundModel
from arpes.analysis.shirley import remove_shirley_background

# core_2d: detector × eV (or already 1D)
# det = [d for d in core_2d.dims if d != "eV"][0]
# core_edc = core_2d.mean(det)  # angle-integrated

# Tutorial stand-in: use a 1D EDC-like curve from user data when available
# core_edc = ...

roi = core_edc.sel(eV=slice(e_lo, e_hi))  # MUST state window
clean = remove_shirley_background(roi)  # state if used

model = (
    AffineBackgroundModel()
    + GaussianModel(prefix="a_")
    + GaussianModel(prefix="b_")
)
result = model.guess_fit(
    clean - clean.min(),
    params={
        "a_center": {"value": c1},  # user/prior guess — do not invent element IDs
        "b_center": {"value": c2},
    },
)
print(result.fit_report())
# Report: Shirley on/off, lineshapes, centers, widths, amplitudes
```

Optional nano-XPS map broadcast: see PyARPES XPS notebook +
`broadcast_model(..., ["x","y"], params=result_to_hints(result))` — token note
if many pixels. **Ask** before inventing Doniach–Šunjić if not in package.

## 2. Valence EDC (single)

```python
from arpes.io import example_data
from arpes.fits.fit_models import LorentzianModel

cut = example_data.cut.spectrum
print(cut.dims, list(cut.coords))

non_eV = [d for d in cut.dims if d != "eV"][0]
edc = cut.isel({non_eV: cut.sizes[non_eV] // 2})
result = LorentzianModel().guess_fit(edc)
print(result.fit_report())
```

## 3. Broadcast MDC / EDC on a cut

```python
from arpes.fits.utilities import broadcast_model
from arpes.fits.fit_models import LorentzianModel, LinearModel, QuadraticModel

# Example: MDCs vs energy — use actual dim names
fit_results = broadcast_model(LorentzianModel, cut, "eV")
# centers = fit_results.F.p("center")   # inspect API for installed version
# widths  = fit_results.F.p(...)        # width param name depends on model

# Default plots (MDC path): E vs k, width vs k; also width vs E if useful
# Prefer k-space cut for vF / m*

# Second-stage band fit on centers — ask linear vs parabolic if unclear
# band = LinearModel().guess_fit(centers_near_EF)      # → vF from slope
# band = QuadraticModel().guess_fit(centers_near_bottom)  # → m* from curvature
# Report vF and/or m* with units + fit window; save PNGs under analysis/
```

**Agent narrative:** after broadcast, always draw the default follow-up curves;
then linear/parabolic on E(k) for vF/m* when appropriate; package models only.

## 4. Multi-band (N>1)

When a dispersion cut shows **several bands** (user asks multi-band **or** a
check MDC shows clear multiple peaks):

1. **Propose N** from a mid-cut MDC / overlay → **wait for user confirm** (never
   silent multi-peak broadcast).
2. Compose **N prefixed peaks** + background (package models only) →
   `broadcast_model` along `eV`.
3. Plot **per-prefix** E vs k (and width vs k); ask **linear vs parabolic per
   band** → report vF and/or m* with stated k window.
4. **Continuity / track identity:** package helper only — **N/A** in this repo
   unless a verified PyARPES / viewer symbol is mapped; **no DIY unswap** /
   nearest-center loop. If tracks may swap at crossings → handoff A/B/C/D or user
   re-label.
5. User stuck → spell **Multi-band handoff** (`reference/edc-mdc-fitting.md` §
   Multi-band dispersion + Multi-band handoff).

```python
from arpes.fits.fit_models import LorentzianModel, AffineBackgroundModel
from arpes.fits.utilities import broadcast_model

# After user confirmed N=2, labels a/b
model = (
    AffineBackgroundModel()
    + LorentzianModel(prefix="a_")
    + LorentzianModel(prefix="b_")
)
fit_results = broadcast_model(model, cut, "eV")
# centers_a = fit_results.F.p("a_center")  # per prefix — inspect install API
# centers_b = fit_results.F.p("b_center")
# Per band: LinearModel / QuadraticModel on centers → vF / m*
```

**Σ / self-energy:** single-band ROI only — not multi-band (`self-energy.md`).
