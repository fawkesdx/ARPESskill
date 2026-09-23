# Example: stack / false-color / ToF±σ plots

Follow `reference/stack-plots.md`. Needs 2D image-like data (user file).

```python
from arpes.plotting.stack_plot import stack_dispersion_plot, flat_stack_plot
from arpes.plotting.false_color import false_color_plot
from arpes.plotting.tof import plot_with_std, scatter_with_std

# Offset waterfall
# fig, ax = stack_dispersion_plot(cut2d, stack_axis="phi", scale_factor=None)

# Flat colored stack (lineshape compare)
# fig, ax = flat_stack_plot(cut2d, stack_axis="temperature")

# False color — only if asked; echo RGB mapping
# false_color_plot(...)

# ToF ±σ — only if *_std / errors exist
# plot_with_std(ds, ...)
# scatter_with_std(ds, ...)

# Save PNG under analysis/; echo stack_axis / prep
```

**Report:** plot kind; stack_axis; scale/cbar; σ present?
