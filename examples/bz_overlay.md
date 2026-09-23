# Example: Brillouin-zone overlay

Follow `reference/bz-overlay.md`. Needs k-converted FS/map (user file) + cell
or named material.

```python
import numpy as np
import matplotlib.pyplot as plt
from arpes.plotting.bz import (
    overplot_standard,
    bz_plot,
    annotate_special_paths,
    plot_data_to_bz,
)

# Assume k_fs already convert_to_kspace + EF-aligned
# k_fs.S.plot()

# User named WS2 → package library
# bz = overplot_standard("ws2", repeat=([-2, 2], [-2, 2]), rotate=0)
# bz(plt.gca())

# User said WSe2 → package key is typo "wwe2" (echo that)
# overplot_standard("wwe2")(plt.gca())

# User ASE cell + path
# bz_plot(cell=user_cell, ax=plt.gca(), paths=[], hide_ax=False, set_equal_aspect=True)
# annotate_special_paths(plt.gca(), "GMKG", cell=user_cell)

# Data onto 2D BZ (k-space required; not 3D)
# fig, ax = plot_data_to_bz(k_fs, user_cell, bz_number=(0, 0))
```

**Report:** cell source (user / graphene|ws2|wwe2); rotate/repeat; ase status;
no Γ claim from overlay alone.
