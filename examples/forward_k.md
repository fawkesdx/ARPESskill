# Example: forward-k point / pair cuts

Follow `reference/forward-k.md`. Needs angle-space data + user points.

```python
import numpy as np
from arpes.utilities.conversion.forward import (
    convert_through_angular_point,
    convert_through_angular_pair,
    convert_coordinate_forward,
)

# Prefer EF-aligned data + stated offsets (k-and-kz-conversion.md)

# k_pt = convert_coordinate_forward(
#     data, {"phi": phi0, "theta": theta0, "eV": e0}
# )

# cut = convert_through_angular_point(
#     data,
#     coords={"phi": phi0, "theta": theta0, "eV": e0},
#     cut_specification={"kx": np.linspace(-1.5, 1.5, 400)},
#     transverse_specification={"ky": np.linspace(-0.05, 0.05, 21)},
#     relative_coords=True,
# )

# cut2 = convert_through_angular_pair(
#     data,
#     first_point={"phi": p1, "theta": t1},
#     second_point={"phi": p2, "theta": t2},
#     cut_specification={"kx": np.linspace(0, 0, 400)},
#     transverse_specification={"ky": np.linspace(-0.05, 0.05, 21)},
# )
```

**Report:** points; grids; relative_coords; volumetric caveat if coord_forward.
