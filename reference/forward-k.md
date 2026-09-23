# Forward k helpers (point / pair cuts)

**Gate:** user asks k-cut **through** an angle-space **point** or **pair**, or
forward-map one angle coord → k (plan a cut). Complements full-volume
`convert_to_kspace` (`k-and-kz-conversion.md`).

**Docs:** `arpes.utilities.conversion.forward`

Capabilities: `k_through_point`, `k_through_pair`, `k_coord_forward` —
`backend-capability-map.md`.

---

## Prerequisites

Same as analysis k: energy axis stated; EF align when claiming absolute k;
offsets / Γ policy from `k-and-kz-conversion.md`. Geometry / V₀ as needed.

Point / pair coords = **user** (or confirmed click) — **no invent**.

---

## Through angular point

```python
from arpes.utilities.conversion.forward import convert_through_angular_point
import numpy as np

# cut = convert_through_angular_point(
#     data,
#     coords={"phi": …, "theta": …},  # user angles; prefer eV in coords if present
#     cut_specification={"kx": np.linspace(-1, 1, 400)},
#     transverse_specification={"ky": np.linspace(-0.05, 0.05, 20)},
#     relative_coords=True,
# )
```

Echo `relative_coords`, cut / transverse grids. Package may attach
`highsymm_*` attrs — report.

---

## Through angular pair

```python
from arpes.utilities.conversion.forward import convert_through_angular_pair

# cut = convert_through_angular_pair(
#     data, first_point={…}, second_point={…},
#     cut_specification={"kx": np.linspace(0, 0, 400)},  # margin vs endpoints
#     transverse_specification={"ky": np.linspace(-0.05, 0.05, 20)},
#     relative_coords=True,
# )
```

`cut_specification` margins are **relative to the segment** when
`relative_coords=True` (docs). Stock path expects **ky** transverse — if
install asserts otherwise, quote error / ask.

---

## Single coordinate forward

```python
from arpes.utilities.conversion.forward import convert_coordinate_forward

# k_pt = convert_coordinate_forward(data, {"phi": …, "theta": …, "eV": …})
```

Uses volumetric “test charge” so result matches small-angle
`convert_to_kspace` — **state** that (exact Euler helpers differ). Prefer
passing **eV** in coords (else slow / warn). Expensive — one point at a time.

Also available: `convert_coordinates` / `convert_coordinates_to_kspace_forward`
for bulk coord maps — only if user asks; check dims support table in package.

---

## Cache

Keep useful cuts under `analysis/kspace/` with meta (points, grids, offsets,
EF) per k-doc.

---

## Hard rules

- No DIY rotation / k-path formulas when forward helpers import.  
- No invent high-sym angle points.  
- Forward cut ≠ Γ finder; offsets still k-doc.  
- Check installed signatures before claiming kwargs.

---

## Checklist

1. User points / pair stated; EF/offsets noted.  
2. Helper matches ask (point / pair / coord forward).  
3. Grids + `relative_coords` echoed; product saved if kept.  
4. Volumetric caveat stated for `convert_coordinate_forward`.
