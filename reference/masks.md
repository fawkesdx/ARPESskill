# Masks (boolean + polygon)

**Gate:** user asks **mask** / keep-only region / polygon ROI / boolean select
before mean or fit. Not default overview.

**Docs:** `arpes.analysis.mask` · XPS notebook boolean `.where` pattern ·
optional `mask_tool` / `MaskTool`

Capabilities: `mask_boolean`, `mask_polygon`, `mask_apply` —
`backend-capability-map.md`.

**Related:** spectroscopic integration box for XY maps =
`spatial-xy-scans.md` (not the same as polygon mask — echo both).

---

## Boolean (preferred when numbers given)

Threshold / logical on a map or PCA component, then `.where` + reduce.

```python
# mask = pca0 > 500
# clean = spectrum.where(mask).mean(["x", "y"])
```

Echo condition (threshold, components, `&` / `|` / `~`). Save mask array or
defn under `analysis/` if reusable.

---

## Polygon → apply

User supplies vertices (coords in data units) or a saved mask dict.

```python
from arpes.analysis.mask import raw_poly_to_mask, apply_mask, apply_mask_to_coords

# mask_def = raw_poly_to_mask(poly)  # or dict with dims/polys
# # mask_def may include dims=, polys=, optional fermi=
# masked = apply_mask(data, mask_def, replace=np.nan, invert=False, radius=None)
```

Echo `invert` / `radius` / `replace`. If mask has `fermi`, package may clip
to ~EF+0.2 eV — **state** that.

`apply_mask_to_coords` for coordinate-broadcast masks — check install before
claiming kwargs.

---

## GUI (ask only)

`mask_tool` / `MaskTool` / Bokeh mask — **ask**; prefer scripted vertices or
boolean. Skill default = matplotlib + package apply.

---

## After mask

Reuse fit / mean / spatial / core recipes on masked product. Echo which
array downstream.

---

## Hard rules

- No invent polygon / threshold.  
- No silent full-frame keep.  
- No DIY shapely when `apply_mask` imports.  
- Spatial spectroscopic ROI ≠ polygon mask — name which.

---

## Checklist

1. User asked mask; boolean vs polygon stated.  
2. Condition / vertices / invert / radius echoed.  
3. Mask def saved if reusable; product named for later steps.  
4. GUI only if asked.
