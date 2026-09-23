# Example: axis preparation

Follow `reference/axis-prep.md`.

```python
from arpes.analysis.general import rebin, symmetrize_axis, condense
from arpes.preparation import normalize_dim, sort_axis

# Rebin (integration chunks; not interpolate)
# coarse = rebin(cut, reduction={"phi": 2, "eV": 2})

# Symmetrize about an axis (echo; prefer EF/Γ-aligned first)
# sym = symmetrize_axis(cut, "phi")

# Equalize intensity along kept dim(s) — alters counts
# eq = normalize_dim(cut, "eV")

# Sort scrambled motor
# ordered = sort_axis(stack, "hv")

# Condense (package may trim eV → ~+50 meV — echo)
# clipped = condense(map2d)
```

**Report:** which prep; dims/factors; raw vs prep for later fits.
