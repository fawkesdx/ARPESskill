# Example: masks

Follow `reference/masks.md`.

```python
import numpy as np
from arpes.analysis.mask import raw_poly_to_mask, apply_mask

# Boolean (user threshold / PCA component)
# mask = (pca.isel(components=0) > 500)
# region = spectrum.where(mask).mean(["x", "y"])

# Polygon (user vertices in data units)
# mask_def = raw_poly_to_mask([(kx0, ky0), (kx1, ky1), ...])  # or full dict
# masked = apply_mask(k_fs, mask_def, replace=np.nan, invert=False)

# Echo invert/radius; save mask def under analysis/ if reuse
# GUI mask_tool only if asked
```

**Report:** boolean vs polygon; condition/vertices; product name for fits.
