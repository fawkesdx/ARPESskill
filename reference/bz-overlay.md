# Brillouin-zone overlay

**Gate:** user asks **BZ** / Brillouin zone / high-symmetry path overlay on an
FS or k-map. Not default overview.

Prefer **k-converted** data (`reference/k-and-kz-conversion.md`). Angle-space
overlay only if user insists — state limitation.

**Docs:** [Brillouin Zones](https://arpes.readthedocs.io/en/latest/brillouin-zones.html)
· `arpes.plotting.bz`

**Optional dep:** `ase` (Atomic Simulation Environment). If `import ase` fails →
say so; ask install into shared env (`pyarpes-env.md`) **or** proceed with
user-supplied cell only.
only (no `overplot_standard` / ASE vertices).

Capabilities: `bz_plot`, `bz_overplot_standard`, `bz_annotate_path`,
`bz_data_on_zone` — `backend-capability-map.md`.

---

## Cell policy (path C)

| Source | When |
|--------|------|
| **User** ASE `cell` / lattice vectors / high-sym path string | Always wins |
| **Package** `overplot_standard(name=…)` | Only if user names `graphene` / `ws2` / `wse2` |
| Else | **Ask** — do not invent a₀ / structure |

Package library keys (hex 2D): `graphene`, `ws2`, and **`wwe2`** (PyARPES typo
for WSe2 — pass `"wwe2"` when user says WSe2; **echo** the typo). Do **not**
invent other `name=` keys.

Echo `rotate=` / `repeat=` when used.

---

## Overlay on existing FS / k plot

```python
from arpes.plotting.bz import overplot_standard, bz_plot, annotate_special_paths
import numpy as np

# Named material (user said graphene / ws2 / wse2):
# bz = overplot_standard("ws2", repeat=([-2, 2], [-2, 2]), rotate=np.pi / 12)
# bz(plt.gca())

# User cell:
# bz_plot(cell=user_cell, ax=ax, paths=[], repeat=None, rotate=...)

# High-sym path (user string or ASE specials): G, K, M, Gn, G(0,1), …
# annotate_special_paths(ax, "GMKG", cell=user_cell)
```

Save figure under `analysis/`; state cell source + rotate/repeat.

---

## Data onto 2D BZ

Needs **k-space** (`data.S.is_kspace`). User or package cell required.

```python
from arpes.plotting.bz import plot_data_to_bz

# fig, ax = plot_data_to_bz(kdata, cell, bz_number=(0, 0), rotate=None)
```

**Hard:** `plot_data_to_bz3d` / data-on-3D-BZ → package `NotImplementedError`.
Do not claim 3D data-on-BZ. Cut plane schematic → `plot_plane_to_bz` only if
user asks and has 3D cell + ASE.

---

## Γ / offsets

BZ drawing ≠ finding Γ. Offsets still follow `k-and-kz-conversion.md`. Overlay
does not replace user / package Γ policy.

---

## Hard rules

- No invent lattice constants or crystal names beyond the three library keys.  
- No silent `ase` assume — report missing optional dep.  
- No DIY hexagon / polygon when package `bz_plot` / `overplot_standard` fits.  
- Prefer scripted matplotlib; `bz_tool` / `ktool(zone=…)` only if user wants GUI
  (**ask**).

---

## Checklist

1. User asked BZ / path; prefer k-converted map.  
2. Cell = user wins; else named graphene/ws2/wse2→`wwe2`; else ask.  
3. `ase` available or user cell only.  
4. Echo rotate/repeat; save plot; no 3D data-on-BZ claim.
