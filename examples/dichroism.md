# Example: dichroism (CP / CM)

Follow `reference/dichroism.md`. Needs CP + CM spectra + user null ROI.

```python
import numpy as np

# cp, cm = load both channels (echo labels / files)
# Optional: align(cp, cm) if drifted — ask before apply

# Null ROI (user) — region expected ≈0 dichroism
# null = (cp.phi > a) & (cp.phi < b) & ...   # or .sel slices
# s = float(cp.where(null).mean() / cm.where(null).mean())
# cm_s = cm * s  # echo s

# D = cp - cm_s
# denom = cp + cm_s
# eps = ...  # echo
# A = D / denom.where(np.abs(denom) > eps)

# Plot both — red +, blue −; tweak clim for look; echo vmin/vmax
# vmax = float(np.nanpercentile(np.abs(D.values), 99))
# D.plot(cmap="RdBu_r", vmin=-vmax, vmax=vmax)
# A.plot(cmap="RdBu_r", vmin=-va, vmax=va)
```

**Report:** labels; null ROI; scale; D+A; clim/offset if adjusted.
