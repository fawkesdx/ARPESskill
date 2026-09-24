# Example: Publication figure layout

Follow `reference/figure-layout.md`. User asked a journal multi-panel figure —
**not** a quick-report overview trio.

```python
from tools.figure import (
    Figure, Panel, PanelData, FigureStyle, JOURNAL_PRESETS,
)

# ASK: which journal width? or use named preset from JOURNAL_PRESETS
label, width_mm, font_pt = next(
    p for p in JOURNAL_PRESETS if "Nature, single" in p[0]
)
style = FigureStyle(
    width_mm=width_mm,
    font_pt=font_pt,
    shared_levels=True,
    edge_labels_only=True,
)

# panel_a / panel_b: Panel(data=PanelData(array=..., x=..., y=..., ...), ...)
fig = Figure(panels=[panel_a, panel_b], style=style)
fig.fit_grid(cols=2)
fig.letter_panels()

# Export via upstream painter/export → analysis/figures/<stem>_fig.pdf
# Optional: fig.save_style("analysis/figures/paper_style.json")
print(label, width_mm, font_pt, "shared_levels", style.shared_levels)
```

On `pyarpes` only: simple `matplotlib` GridSpec OK; for full presets → A/B/C/**D**.

**Report:** preset name, mm, font pt, shared clim/ranges, output path.
