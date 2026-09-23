# Fermi-surface pocket analysis

**Gate:** user asks **pocket** / closed FS sheet / radial EDCs around a pocket /
pocket center or anisotropy. Not default overview.

**Input:** 2D Fermi map or kx–ky (± `eV`) with a **clear single closed** contour.
Package note: small pockets often clearer in **angle space** before k-convert —
prefer that unless already converted and user wants k.

**Docs:** `arpes.analysis.pocket` — `pocket_parameters`, `curves_along_pocket`,
`edcs_along_pocket`, `radial_edcs_along_pocket`

Capabilities: `pocket_params`, `pocket_curves`, `pocket_edcs` —
`backend-capability-map.md`.

---

## Preflight

1. Confirm **one** closed pocket. Multi-pocket, open arc, or unclear → **ask**.  
2. State energy window near EF (user box wins; else package-ish default e.g.
   `eV` ≈ −0.03…+0.05 — **echo**).  
3. Angle vs k space: say which.

---

## Center (path B)

| Source | When |
|--------|------|
| **User coords** | Always win if given |
| **`pocket_parameters` center** | Clearly **one** pocket; label *package:pocket_parameters* |
| **Ask** | Ambiguous / multi-sheet |

Never invent DIY centroid / ellipse. For **Γ offsets** on Fermi maps, still
follow `k-and-kz-conversion.md` (ask before applying pocket center as Γ).

```python
from arpes.analysis.pocket import (
    pocket_parameters,
    curves_along_pocket,
    edcs_along_pocket,
    radial_edcs_along_pocket,
)

# params = pocket_parameters(fmap)  # center, locations, pca, …
# center = params["center"]  # or user {phi:…, beta:…} / {kx:…, ky:…}
```

---

## Default report

Save under `analysis/`:

1. Echo center + method (user / package).  
2. If `pocket_parameters` used: center, optional PCA principal vectors / locations.  
3. Sample **curves along pocket** (`curves_along_pocket`) — plot a few radial
   cuts or summary figure.  
4. Near-EF window stated.

### Optional (ask)

| Goal | API |
|------|-----|
| EDCs around pocket | `edcs_along_pocket` |
| Radial EDCs along one angle from center | `radial_edcs_along_pocket` (+ center kwargs) |
| kF along rays | package MDC path inside pocket helpers — **name** method |

Reuse `edc-mdc-fitting.md` on extracted curves if user wants peaks.

---

## Package map

| Step | Prefer |
|------|--------|
| Center / anisotropy | `pocket_parameters` |
| Radial cuts | `curves_along_pocket` |
| EDCs | `edcs_along_pocket` / `radial_edcs_along_pocket` |

---

## Do not

- Auto-run pocket analysis on every Fermi overview.  
- Treat pocket center as Γ without Γ workflow / user OK.  
- DIY kF / ellipse when package APIs exist.  
- Multi-pocket without asking which sheet.

---

## Checklist

1. One closed pocket (or user picked which).  
2. Center = user or package (stated); else asked.  
3. Energy window + angle/k space echoed.  
4. Default: params + sample curves; EDCs only if asked.  
5. No silent Γ claim from pocket center.
