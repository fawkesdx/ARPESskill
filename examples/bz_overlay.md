# Example: Brillouin-zone overlay

Follow `reference/bz-overlay.md`. Needs k-converted FS/map (user file) + cell
or named material. Moiré = same skill, two lattices.

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

## Moiré mini-BZ (`arpes_viewer` — same skill)

```python
from tools.moire import moire_bz, moire_reciprocal_vectors
from tools.bz2d import reciprocal_vectors_2d

# ASK user: a1,a2 / g vectors for each layer + twist — do not invent
# g1_top, g2_top = reciprocal_vectors_2d(a1_top, a2_top)
# g1_bot, g2_bot = ...
# gm1, gm2, polygon = moire_bz(g1_top, g2_top, g1_bot, g2_bot)
# Plot polygon on k_fs axes; report gm1, gm2 (or |gm|), twist
# Prefer moire_reciprocal_vectors over hex_moire_lattice_fast for new work
```

On `pyarpes`: no auto-moiré → A/B/C/**D** or user-supplied moiré cell into
`bz_plot`.

**Report:** cell source (user / graphene|ws2|wwe2); moiré inputs if used;
rotate/repeat; ase status; no Γ claim from overlay alone.
