# Example: background subtraction

Follow `reference/backgrounds.md`.

```python
from arpes.analysis.shirley import remove_shirley_background
from arpes.analysis.background import remove_background_hull, calculate_background_hull
from arpes.corrections.background import remove_incoherent_background

# Core → Shirley
# core_clean = remove_shirley_background(core_roi)

# Valence EDC → convex hull (default)
# edc_clean = remove_background_hull(edc)
# # optional: calculate_background_hull(edc, breakpoints=[...])

# Above-EF junk → only if asked
# cut_clean = remove_incoherent_background(cut, set_zero=True)
# # warn: uses find_spectrum_energy_edges heuristic

# Save before/after; echo method for later fits
```

**Report:** context + method; breakpoints / set_zero if used.
