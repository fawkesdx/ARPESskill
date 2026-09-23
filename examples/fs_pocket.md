# Example: Fermi-surface pocket

Follow `reference/fs-pocket.md`. Needs a map with one clear closed pocket.

```python
from arpes.analysis.pocket import (
    pocket_parameters,
    curves_along_pocket,
    edcs_along_pocket,
    radial_edcs_along_pocket,
)

# fmap = ...  # 2D FS / kx-ky (± eV); prefer angle space if pocket small
# Confirm one closed pocket — ask if multi

# Center B: user coords win; else pocket_parameters if clearly one pocket
# params = pocket_parameters(fmap)
# center = params["center"]  # or user dict

# slices, angles = curves_along_pocket(fmap, **center)
# # plot a few slices; echo eV window

# Optional if asked:
# edcs = edcs_along_pocket(fmap, **center)
# radial = radial_edcs_along_pocket(fmap, angle=0.0, **center)
```

**Report:** center method (user / package), eV window, angle vs k; EDCs only if
asked; pocket center ≠ Γ unless Γ workflow says so.
