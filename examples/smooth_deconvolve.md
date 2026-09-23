# Example: smooth and deconvolution

Follow `reference/smooth-deconvolve.md`.

```python
from arpes.analysis.filters import gaussian_filter_arr, boxcar_filter_arr
from arpes.analysis.deconvolution import make_psf1d, deconvolve_rl, deconvolve_ice

# --- Smooth (default noise path) ---
# sm = gaussian_filter_arr(cut, sigma=0.05)  # state sigma / dims
# before/after plots under analysis/

# boxcar / savitzky_golay only if asked

# --- Deconvolve (separate ask; never auto) ---
# psf = make_psf1d(...)  # or user PSF — state width
# dec = deconvolve_rl(cut, ...)  # check installed signature
# warn: artifacts; not a fit

# If both: ask order (prefer RL on raw unless user wants light smooth first)
```

**Report:** track (smooth vs deconvolve), params, which array used downstream.
