# Band enhance (curvature / minimum gradient)

**Gate:** user asks to **sharpen bands**, highlight dispersion, **curvature**,
**minimum gradient**, or derivative maps — **not** default overview.

**Input:** reduced **2D** cut (or stated ROI of a cut). Prefer intensity as
loaded/converted; do **not** auto-smooth unless user asks (see future
smooth/filter recipe).

**Docs:** `arpes.analysis.derivative` — `curvature`, `minimum_gradient`,
`dn_along_axis` / `d1_along_axis` / `d2_along_axis`

Capabilities: `band_curvature`, `band_min_gradient`, `band_derivative` —
`backend-capability-map.md`.

---

## Default (path C)

Run **both** and save **side-by-side** (or two panels) under `analysis/`:

1. `curvature(arr)`  
2. `minimum_gradient(arr)`

Echo every time:

- These are **derived maps**, not photoemission intensity.  
- Params if non-default (`alpha` / `directions` for curvature; `delta` for
  min-gradient). Package defaults OK if stated as “package default”.

```python
from arpes.analysis.derivative import curvature, minimum_gradient

# cut2d = ...  # 2D DataArray (e.g. eV × kp or eV × phi)
# c = curvature(cut2d)
# g = minimum_gradient(cut2d)
# side-by-side matplotlib: intensity | curvature | min-gradient (or curv | MG)
```

---

## Optional (ask)

| Ask | API |
|-----|-----|
| 1st / 2nd derivative along one axis | `d1_along_axis` / `d2_along_axis` / `dn_along_axis` |
| Tune curvature `alpha` / axes | pass `directions=`, `alpha=` — **state** values |
| Pre-smooth then enhance | only if user wants; do not invent kernel |

---

## Hard rules

- **No** peak centers, EF, Γ, vF, or Σ from curvature / MG alone.  
- Fits still `edc-mdc-fitting.md`; Σ still `self-energy.md`.  
- No full 3D / spatial / delay **volume** enhance by default — reduce to 2D
  first (token note if user insists on many slices).  
- Prefer package APIs; no invent Laplacian / Sobel DIY when imports work.

---

## Package map

| Step | Prefer |
|------|--------|
| Curvature | `arpes.analysis.derivative.curvature` |
| Min gradient | `arpes.analysis.derivative.minimum_gradient` |
| Axis derivatives | `d1_along_axis` / `d2_along_axis` / `dn_along_axis` |

---

## Do not

- Replace intensity overview with curvature only.  
- Claim “band found” without stating it is a visual enhance.  
- Auto-fit Lorentzians on curvature image.  
- Silent param changes (`alpha`, `delta`).

---

## Checklist

1. User asked enhance; 2D cut / ROI stated.  
2. Both curvature + min-gradient saved / shown.  
3. Stated: not intensity; params if non-default.  
4. No centers / EF / Σ claimed from these maps alone.
