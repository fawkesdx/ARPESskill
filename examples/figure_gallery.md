# Example: Paper figure from archetypes

Follow `reference/figure-gallery.md` (what to show) and
`reference/figure-layout.md` (layout, save). Backend `arpes_viewer`. User asked
for "a figure showing how the band crossing evolves along k_z, with the
calculation" — data: a k-map at the Γ plane, an hv scan converted to k_z
(V₀ stated), a band calculation (`_hr.dat` / `.bxsf`).

**Agent proposes** (one line each, user picks):

1. J + E + D + F + I — structure/BZ, k_z map, cuts stacked along k_z, cuts with
   calculated guides, fitted crossing energy vs k_z (full 3-D story).
2. E + F — k_z map and a row of cuts with guides (compact, one row).
3. F + H + I — one cut with guides, its MDC stack, crossing vs k_z.

```python
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PyQt5.QtWidgets import QApplication
app = QApplication.instance() or QApplication([])

import numpy as np
from tools.output.figure import Figure, FigureStyle, Overlay, JOURNAL_PRESETS
from tools.output import figfile
from tools.crystal import bandfiles, bands
from tools.spectra.dispersion import line_crossing
from ui.panels.figure import FigurePainter, write_figure, panel_from_dataset
from ui.viewers.curves import curve_panel

model = bandfiles.read(calc_path)                     # ASK: which file; E_F from file or user
# Z / shift fitted on one cut's measured band points (state both in the report)
align = bands.fit_alignment(k_points, energies, calculated)

panels = []
for cut, kz in zip(cuts, kz_values):                  # cuts already in k (state V0)
    p = panel_from_dataset(cut)
    k = cut_k_axis(cut)                               # the cut's own k axis
    for b in guide_bands:                             # bands to guide, by character
        e = bands.follow_band(model, k_points_on(k, kz), start, b, diabatic=True)
        p.overlays.append(Overlay(xs=list(k), ys=list(align.apply(e)),
                                  color="#ffffff", width_pt=0.7, style="dashed",
                                  name=f"calc band {b}"))
    p.title = f"k_z = {kz:.2f}"
    panels.append(p)

# (I) crossing energy per cut, with σ from the two fitted branches
pts = [line_crossing(left[i], right[i]) for i in range(len(cuts))]   # (k, E, k_err, E_err)
trend = curve_panel(kz_dense, [("calculation", calc_crossing, "#d62728")],
                    x_label="k_z (π/c)", y_label="E_c - E_F (eV)", name="E_c")
trend.overlays.append(Overlay(xs=list(kz_values), ys=[p[1] for p in pts],
                              y_errors=[p[3] for p in pts],
                              color="#1f4e9c", marker="o", marker_mm=1.1, line=False,
                              name="measured"))
panels.append(trend)

label, width_mm, font_pt = next(p for p in JOURNAL_PRESETS if "double" in p[0])
fig = Figure(panels=panels, style=FigureStyle(width_mm=width_mm, font_pt=font_pt,
                                              shared_levels=True))
for i, p in enumerate(fig.panels):                    # one row, then tidy
    p.frame = (10 + 36 * i, 8, 32, 40)
row = list(range(len(fig.panels)))
fig.align_panels(row, "top"); fig.match_size(row, "height")
fig.distribute_panels(row, "x")
fig.letter_panels()

write_figure(FigurePainter(fig), "analysis/figures/kz_crossing.pdf", "pdf")
figfile.save("analysis/figures/kz_crossing.afig", fig)
figfile.write_data_folder("analysis/figures/kz_crossing.afig", fig)
```

Names such as `cut_k_axis`, `k_points_on`, `left` / `right` (the two fitted
branches per cut) stand for the user's own data — **ask**, do not invent. `left` / `right` are
straight-line (`order=1`) fits from `tools.spectra.dispersion.fit_dispersion`.

**Report:** archetypes chosen; preset / mm / font; V₀; Z and shift; which
bands are guides and that they are calculated; clim shared or not; output
paths (PDF, `.afig`, data folder).

On `pyarpes` only: same panels with matplotlib (`GridSpec`, dashed `plot`
for guides, `errorbar` for I); no `.afig` — save the arrays next to the PDF.
