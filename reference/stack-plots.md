# Stack / false-color / ToF±σ plots

**Gate:** user asks **stack** / waterfall / flat colored stack / **false-color**
RGB / ToF **±σ** error plot. Not default overview trio
(`default-overview-plots.md`).

**Docs:** [Stack plots](https://arpes.readthedocs.io/en/latest/stack-plots.html)
· `arpes.plotting.stack_plot` · `arpes.plotting.false_color` ·
`arpes.plotting.tof`

Capabilities: `plot_stack`, `plot_flat_stack`, `plot_false_color`,
`plot_tof_std` — `backend-capability-map.md`.

---

## Offset stack (waterfall)

```python
from arpes.plotting.stack_plot import stack_dispersion_plot

# fig, ax = stack_dispersion_plot(
#     image_2d, stack_axis="temperature", scale_factor=…, max_stacks=100
# )
```

Needs **2D** image-like data. Echo `stack_axis`, `scale_factor`,
`use_constant_correction` / `zero_offset` / `uniform` if used. Package may
**rebin** when stacks > `max_stacks` — state that.

---

## Flat stack (color, no offset)

Better for lineshape / gap compare:

```python
from arpes.plotting.stack_plot import flat_stack_plot

# fig, ax = flat_stack_plot(image_2d, stack_axis="temperature", cbarmap=…)
```

Echo stack axis + colorbar mapping.

Optional: `offset_scatter_plot` when Dataset has `var` + `var_std` — ask if
user wants scatter+error style.

---

## False color

```python
from arpes.plotting.false_color import false_color_plot

# false_color_plot(...)  # check install signature; state R/G/B channel map
```

Only if asked. Echo which arrays → RGB.

---

## ToF / count ±σ

When data carry statistical errors (`*_std` or package ToF attrs):

```python
from arpes.plotting.tof import plot_with_std, scatter_with_std

# plot_with_std(data, …)   # fill-between ±σ
# scatter_with_std(data, …)
```

If no error channel → say so; do **not** invent σ from intensity.

---

## Prep before plot

Normalize / subtract / rebin first via `axis-prep.md` / `backgrounds.md` if
user wants — echo prep; plot is presentation only.

Save PNG under `analysis/`.

---

## Hard rules

- No DIY waterfall / fill_between when package helpers import.  
- Stack plot ≠ reduction product for fits (still use raw/prep arrays).  
- No invent σ / RGB mapping.

---

## Checklist

1. Plot kind matches ask (offset / flat / false-color / ±σ).  
2. `stack_axis` + scale/cbar/channels echoed.  
3. PNG saved; prep named if any.  
4. Missing σ → report, don’t invent.
