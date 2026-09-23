# Background subtraction

**Gate:** user asks **subtract / remove background**. Not default overview.

Path **B** defaults:

| Context | Default method |
|---------|----------------|
| **Core / XPS-like** | **Shirley** — `remove_shirley_background` (`edc-mdc-fitting.md`) |
| **Valence cut / EDC** | **Convex hull** — `remove_background_hull` / `calculate_background_hull` |
| **Above-EF contamination** | `remove_incoherent_background` — **only if asked** |

**Docs:** `arpes.analysis.shirley` · `arpes.analysis.background` ·
`arpes.corrections.background`

Capabilities: `bg_shirley`, `bg_hull`, `bg_incoherent` —
`backend-capability-map.md`.

---

## Shirley (core)

Follow core section of `edc-mdc-fitting.md`. Echo on/off + ROI.

```python
from arpes.analysis.shirley import remove_shirley_background
# clean = remove_shirley_background(roi)
```

Do **not** default Shirley on valence dispersions.

---

## Convex hull (valence default)

1. Prefer 1D EDC or stated energy cut; for 2D, reduce or apply per documented
   package use — **state** what was subtracted.  
2. Optional `breakpoints=` to piece the hull — **echo** if used.  
3. Save **before / after** under `analysis/`.  
4. Fits after: name that hull bg was removed.

```python
from arpes.analysis.background import (
    calculate_background_hull,
    remove_background_hull,
)

# bkg = calculate_background_hull(edc)
# clean = remove_background_hull(edc)  # or edc - bkg
```

---

## Incoherent above EF (ask only)

Use when user cites 2nd-harmonic / ToF spill / counts **above EF**.

1. Energy axis should be EF-aligned or have a usable edge.  
2. Package uses `S.find_spectrum_energy_edges` heuristic — **state** that;
   warn if EF uncertain.  
3. `set_zero=True` (default) clamps negatives — echo.  
4. Never auto-run on every cut.

```python
from arpes.corrections.background import remove_incoherent_background
# clean = remove_incoherent_background(data, set_zero=True)
```

---

## Fit backgrounds (not subtraction)

Affine / constant under peaks = `AffineBackgroundModel` in the fit
(`edc-mdc-fitting.md`) — different from subtracting a spectrum-wide bg first.
Name both if used together.

---

## Hard rules

- No invent polynomial / spline bg when Shirley / hull / incoherent fit the ask.  
- No silent replace of the working array — echo which product downstream.  
- Shirley ≠ hull ≠ incoherent — pick by context table or **ask**.

---

## Checklist

1. Context = core / valence / above-EF stated.  
2. Method matches path B (or user override).  
3. Before/after saved; params (`breakpoints`, `set_zero`) echoed.  
4. Later fits name bg treatment.
