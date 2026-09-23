# Dataset alignment (correlation offset)

**Gate:** user asks **align** / register / find **shift** between two comparable
spectra (charging, work-function drift, compare cuts). Not default overview.

**Docs:** `arpes.analysis.align` (`align` / `align1d` / `align2d`)

Capabilities: `align_offset`, `align_apply` — `backend-capability-map.md`.

**Not this doc:** EF chemical-potential fit (`near-ef-gap.md` /
`k-and-kz-conversion.md`); Γ offsets; mosaic stitch/merge (no stock stitch —
do not invent).

---

## Measure offset

1. Same ndim: **1D** or **2D** arrays with comparable coords/range.  
2. Prefer `align(a, b, subpixel=True)` — returns **unitful** offset of `b`
   relative to `a`. Echo dims + `subpixel`.  
3. Report offsets in coordinate units.

```python
from arpes.analysis.align import align, align1d, align2d

# offset = align(ref, moving, subpixel=True)
# # 1D → scalar; 2D → (Δdim0, Δdim1) matching a.dims order
```

---

## Apply offset (ask before permanent)

1. Show measured Δ; **ask** before writing into working offsets / saved npz.  
2. Apply with package shift helpers when available (`G.shift_by`,
   `shift_coords`, or documented coordinate shift) — **echo** which.  
3. Re-plot overlay before/after under `analysis/`.

Do not silent-mutate loader offsets.

---

## Hard rules

- No DIY `np.correlate` / FFT register when `align` imports.  
- No invent multi-file stitch / blend.  
- Align ≠ EF finder ≠ Γ policy.  
- Check install signature (note: some builds have fragile `len(a.dims == 1)` —
  if `align` errors, call `align1d` / `align2d` explicitly).

---

## Checklist

1. User asked align; ref vs moving named.  
2. Offset reported (units); subpixel echoed.  
3. Apply only after ask (or user already said apply).  
4. Before/after overlay saved when applied.
