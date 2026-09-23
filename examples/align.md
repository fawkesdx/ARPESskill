# Example: correlation align

Follow `reference/align.md`.

```python
from arpes.analysis.align import align, align1d, align2d

# ref, moving = two comparable 1D EDCs or 2D maps (same dims)
# offset = align(ref, moving, subpixel=True)
# # or: align1d(...) / align2d(...) if generic align fails

# Report unitful offset; ask before applying permanent shifts
# moved = moving.G.shift_by(...)  # check installed shift API; echo
```

**Report:** ref vs moving; Δ (units); applied? yes/no.
