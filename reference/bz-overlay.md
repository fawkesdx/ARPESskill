# Brillouin-zone overlay

**Gate:** user asks **BZ** / Brillouin zone / high-symmetry path / **moiré** /
mini-BZ overlay on an FS or k-map. Not default overview.

Prefer **k-converted** data (`reference/k-and-kz-conversion.md`). Angle-space
overlay only if user insists — state limitation.

**Docs:** [Brillouin Zones](https://arpes.readthedocs.io/en/latest/brillouin-zones.html)
· `arpes.plotting.bz` · viewer `tools.moire` / `tools.bz2d` (moiré)

**Optional dep:** `ase` (Atomic Simulation Environment). If `import ase` fails →
say so; ask install into shared env (`pyarpes-env.md`) **or** proceed with
user-supplied cell only (no `overplot_standard` / ASE vertices).

Capabilities: `bz_plot`, `bz_overplot_standard`, `bz_annotate_path`,
`bz_data_on_zone`, `bz_moire` — `backend-capability-map.md`.

**One skill** — moiré is a subsection here, not a separate skill.

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

## Moiré / mini-BZ (bilayer)

**Gate:** user asks **moiré BZ** / mini-BZ / twisted bilayer / two-lattice BZ.
Same BZ-overlay skill.

**Backend:** primarily `arpes_viewer` — `tools.moire` + `tools.bz2d`.  
**`pyarpes`:** no auto-moiré API in the skill map → **stop**; offer A/B/C/**D**
(D if data can live on viewer) **or** user-supplied moiré cell into
`bz_plot` / overlay. Do **not** invent twist formulas.

### Inputs (ask — never invent)

| Need | Examples |
|------|----------|
| Layer 1 & 2 | Real-space a (Å) + angles, or reciprocal `g1,g2` each |
| Relative twist / orientation | Degrees; or absolute rotations per layer |
| Lattice type (if hex fast path) | Two hexagonal same-family layers |

### APIs (`arpes_viewer`)

Prefer the **general** path:

```python
from tools.moire import moire_reciprocal_vectors, moire_bz, hex_moire_lattice_fast
from tools.bz2d import reciprocal_vectors_2d

# From user real-space vectors → reciprocal, then:
# gm1, gm2, polygon = moire_bz(g1_top, g2_top, g1_bot, g2_bot, search=1)
# Overlay polygon on k-map (matplotlib); echo gm1, gm2
```

| API | When |
|-----|------|
| `moire_reciprocal_vectors` / `moire_bz` | Default — any 2D lattice types / mismatch |
| `hex_moire_lattice_fast(a_top, a_bot, twist_deg)` | Optional hex–hex fast path only |

**Hex fast-path fences (upstream):**

- Exact for twist in **[0, 30]°** (hex fold: θ ↔ 60−θ); past 30° fold or use general method.  
- Equal-a branch tested; **unequal-a** less verified — prefer `moire_reciprocal_vectors` for new work.  
- Zero twist + equal a → no moiré (raise / ask).

Do **not** invent magic-angle graphene numbers. Echo `a_moire` / `gm` / twist in report.

Overlay on **k-converted** FS/map like a single BZ. Still not a Γ finder.

Capability: `bz_moire` — `backend-capability-map.md`.

---

## Γ / offsets

BZ drawing ≠ finding Γ. Offsets still follow `k-and-kz-conversion.md`. Overlay
does not replace user / package Γ policy.

---

## Hard rules

- No invent lattice constants or crystal names beyond the three library keys.  
- No invent moiré twist / a₀ — ask both layers.  
- No silent `ase` assume — report missing optional dep.  
- No DIY hexagon / polygon / moiré G when package APIs fit.  
- Prefer scripted matplotlib; `bz_tool` / `ktool(zone=…)` only if user wants GUI
  (**ask**).  
- No separate “moiré skill” in user-facing lists.

---

## Checklist

1. User asked BZ / path / moiré; prefer k-converted map.  
2. Single cell = user wins; else named graphene/ws2/wse2→`wwe2`; else ask.  
3. Moiré = two lattices + twist from user; `moire_bz` / general vectors preferred.  
4. `ase` available or user cell only (single-lattice PyARPES path).  
5. Echo rotate/repeat / gm / twist; save plot; no 3D data-on-BZ claim.
