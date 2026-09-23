# Decomposition (PCA / NMF / ICA / factor analysis)

**Gate:** user asks **PCA** / **NMF** / **ICA** / **factor analysis** /
sklearn-style decomposition of a map or hypercube. Not default overview.

**Docs:** `arpes.analysis.decomposition` · XPS notebook PCA pattern · optional
`pca_explorer` widget

Capabilities: `decomp_pca`, `decomp_nmf`, `decomp_ica`, `decomp_factor` —
`backend-capability-map.md`.

Spatial XY already mentions PCA — full recipe **here**; spatial doc links here.

---

## Choose method

| Ask | Call |
|-----|------|
| PCA (default explore) | `pca_along` |
| NMF / parts-based | `nmf_along` — **non-negative** data |
| ICA | `ica_along` |
| Factor analysis | `factor_analysis_along` |

Generic: `decomposition_along(..., decomposition_cls=…)`.

Echo **observation axes** (e.g. `["x","y"]`), `n_components`, `correlation=`
(StandardScaler) if used.

```python
from arpes.analysis.decomposition import (
    pca_along, nmf_along, ica_along, factor_analysis_along,
)

# transformed, model = pca_along(data, ["x", "y"], n_components=5)
# # dims often include "components"
```

---

## NMF note

NMF needs **non-negative** intensities. If negatives present → warn; clip /
`where` only if user agrees — do not silent abs().

---

## Report

1. Method + axes + n_components.  
2. Component maps / spectra sample (not every component in chat — token).  
3. Save under `analysis/`.  
4. `pca_explorer` / GUI — **ask** only.

Decomp components ≠ chemical peak IDs unless user interprets; fits still
`edc-mdc-fitting.md`. Mask with components → `masks.md`.

---

## Hard rules

- No DIY sklearn ravel when `*_along` imports.  
- Ask before large spatial/spectral cubes (`token-usage.md`).  
- No silent replace working spectrum with a component.  
- PCA in spatial overview stays optional — this doc for any decomp ask.

---

## Checklist

1. Method matches ask; axes + n_components echoed.  
2. NMF: non-negativity handled / warned.  
3. Products saved; GUI only if asked.  
4. Downstream mask/fit names which component if used.
