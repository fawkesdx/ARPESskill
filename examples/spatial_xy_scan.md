# Example: spatial XY scan overview + kind reuse

Follow `reference/spatial-xy-scans.md`. Uses PyARPES tutorial `nano_xps` when no
user file (XY–E). For XY–ARPES / XY–map / XY–hv, same pattern with more dims.

```python
from arpes.io import example_data  # or load_data(path, location="MAESTRO")
import numpy as np
from pathlib import Path

data = example_data.nano_xps.spectrum  # dims often x, y, eV
# State dims + spatial subtype (XY–E / XY–ARPES / XY–map / XY–hv)

# Spectroscopic ROI R — user box wins; else default (near-EF or full E)
R_eV = slice(-36, -31)  # example core window; valence: near 0 eV
spec_r = data.sel(eV=R_eV)
# If φ/ψ present: also sel/sum those per user box or integrate all

xy_map = spec_r.sum("eV")  # I_R(x,y) — echo R in report
# Hot spot = argmax
flat = np.asarray(xy_map.values)
iy, ix = np.unravel_index(np.nanargmax(flat), flat.shape)
# Map indices → coords (adapt dim order to data!)
# x_star, y_star = float(xy_map.coords["x"][ix]), float(xy_map.coords["y"][iy])

# Quick report PNGs under analysis/:
# 1) xy_map.S.plot()
# 2) spectrum at hot spot
# 3) data.mean(["x","y"])  # or mean over R
# 4) subtype extra if XY–map / XY–hv

# Kind reuse at hot spot (XY–E → core fit; if cut dims → EDC/MDC; etc.)
# from arpes.fits.fit_models import GaussianModel
# curve = data.sel(x=x_star, y=y_star, method="nearest").sel(eV=R_eV)
# GaussianModel().guess_fit(curve)

# Broadcast over XY only if user asks (+ token note):
# broadcast_model(..., masked, ["x", "y"], params=...)
```

**Report must include:** subtype, \(R\), (x*,y*), which kind recipe ran, and that
hot spot ≠ Γ.
