# Publication figure layout

**Gate:** user asks **publication figure** / journal panel layout / Nature|PRB|Science
column width / multi-panel paper figure / figure composer. **Not** default
quick-report overviews (`default-overview-plots.md`) and **not** waterfall
stacks (`stack-plots.md`).

This is **layout / export**, not a physics analysis recipe. Do not list it as
a core ARPES “analysis skill” sibling to k/kz.

**Backend:** primarily `arpes_viewer` —
[ARPES-data-browser](https://github.com/DingPei1995/ARPES-data-browser)
`tools.output.figure` (+ `tools.output.export`, `tools.output.figfile`; the
painter is `ui.panels.figure` — prefer the headless model, paint offscreen).
Older checkouts have the same model at `tools.figure` — check which imports.
Env: `arpes-viewer-env.md`.

**Which panels to make** (notched cube, CEC series, stacked slices, k_z
evolution, data vs calculation, crystal + BZ, fitted trends) →
`figure-gallery.md`. This file is how to lay them out and save them.

**`pyarpes`:** simple multi-panel matplotlib / `GridSpec` OK. Do **not** invent
a full journal-composer clone; if user needs `JOURNAL_PRESETS` / shared style
JSON → A/B/C/**D** (`package-first.md`).

Capabilities: `figure_compose`, `figure_journal_preset` —
`backend-capability-map.md`.

---

## Model (headless)

| Piece | Role |
|-------|------|
| `FigureStyle` | Shared look: width mm, font pt, gaps, `shared_levels`, `shared_ranges`, `edge_labels_only` |
| `Figure` | Grid of `Panel`s + style; `fit_grid`, `letter_panels`, `common_levels` / `common_ranges` |
| `Panel` / `PanelData` | One image/curves + colormap, ranges, overlays, (a)(b) label |
| `JOURNAL_PRESETS` | Named journal column widths (mm) + default font pt |

Upstream units = **millimetres** (journal column). Echo preset name +
`width_mm` + `font_pt` in the report.

---

## Journal presets (cite package — do not invent)

Use `tools.output.figure.JOURNAL_PRESETS` (label, width_mm, font_pt). Examples include
Nature single/double, APS/PRB, Science, Elsevier, slide — **read the tuple in
the installed package**; do not hardcode different mm from memory.

```python
from tools.output.figure import Figure, Panel, PanelData, FigureStyle, JOURNAL_PRESETS

# Pick preset by user ask, or ask which journal width
label, width_mm, font_pt = JOURNAL_PRESETS[0]  # e.g. Nature single — verify index
style = FigureStyle(width_mm=width_mm, font_pt=font_pt,
                   shared_levels=True,   # comparable panels
                   shared_ranges=False,  # set True if same axes
                   edge_labels_only=True)
fig = Figure(panels=[...], style=style)
fig.fit_grid(cols=2)
fig.letter_panels()  # (a), (b), …
# Paint/export via upstream ui/export path — save under analysis/figures/
# Optional: fig.save_style(path) for reuse across paper figures
```

Fill each `Panel` with `PanelData` (array + x/y axes + labels). Prefer
**shared colour levels** when panels must be compared by eye; state when
shared vs per-panel.

---

## Free layout: frames, alignment, letters

A grid is fine for equal panels. A paper figure with mixed panels (a 3-D
view beside a row of maps, a curve plot beside cuts) is laid out by hand:
each `Panel.frame = (x, y, w, h)` in mm from the top left, then tidied.

```python
fig.panels[0].frame = (10, 8, 40, 40)
fig.panels[1].frame = (58, 9, 40, 38)
fig.align_panels([0, 1, 2], "top")        # left / right / top / bottom / hcenter / vcenter
fig.distribute_panels([3, 4, 5, 6], "x")  # equal gaps (3+ panels)
fig.match_size([0, 1, 2], "height")       # width / height / both, from the first
fig.letter_panels()                       # (a), (b), … in reading order
fig.panels[1].label_offset = (-4.0, 0.0)  # nudge one letter (mm), e.g. off a long y title
```

- `FigureStyle.panel_label_aligned = True` (default): letters of a row share
  one height, of a column one left edge, whatever each panel's titles are.
- Not every panel needs a letter: sub-panels of one result share one letter
  (clear the others' `label`, add `(i)`, `(ii)` as text notes).

## Colour bars, guides, error bars

| Want | Set |
|------|-----|
| Raw intensity bar | `colorbar=True`, `colorbar_ends="high-low"` (words, not counts) |
| Short bar under a panel | `colorbar_position="below"`, `colorbar_length=0.6` |
| Calculated / guide line | `Overlay(xs, ys, color, width_pt, style="dashed")` |
| Measured points ± σ | `Overlay(..., marker="o", marker_mm=1.1, line=False, y_errors=[…])` |
| Named k ticks | `x_tick_labels=[(0.0, "Γ"), (1.2, "M")]` |
| A gap in a curve | NaN in `ys` (drawn in pieces) |

Curves (fitted quantity vs parameter): `ui.viewers.curves.curve_panel(x,
[(label, y, colour)], x_label=…, y_label=…, name=…)` makes a plot panel; add
measured points as an `Overlay` with markers and error bars.

## Save: editable figure + data folder

```python
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PyQt5.QtWidgets import QApplication
app = QApplication.instance() or QApplication([])
from ui.panels.figure import FigurePainter, write_figure
from tools.output import figfile

write_figure(FigurePainter(fig), "analysis/figures/fig1.pdf", "pdf")   # or png / svg / tif
figfile.save("analysis/figures/fig1.afig", fig)            # re-opens in the composer
figfile.write_data_folder("analysis/figures/fig1.afig", fig)
# -> analysis/figures/data for fig1/<letter>/processed/ (panel data .nxs, lines.csv)
#    .../original/ (source files traced back through conversions), sources.txt
```

Recommend saving the `.afig` + data folder with every paper figure: a
referee question months later is answered from the folder, not from memory.
Set `PanelData.sources` (`figfile.source_record(path, entry=…)`) when a
panel is built from arrays so the original file is traced.

---

## House style (ask once per paper set, then reuse)

A journal preset fixes the column width and a default font size. It does **not**
fix the user's own drawing conventions, and users have strong ones. Before the
first paper figure of a set, ask for (or read from a stored `style_dict`) and
then apply to every panel:

| Item | Ask | Typical answers |
|------|-----|-----------------|
| Font family | "Which font?" | Arial, Helvetica, the journal's own |
| Size range | "Smallest and largest text allowed?" | Nature: 6 pt min, 12 pt max; tick labels ≈ 7, axis labels ≈ 8, letters ≈ 9 |
| Panel letters | "Letter format and position?" | `a.` (lowercase, period, no brackets, not bold, outside top-left) **or** `(a)` bold inside — never guess |
| Colour names | "Which colour means which band / temperature?" | keep the mapping across the whole paper |

Apply with `FigureStyle(font_pt=…)` on `arpes_viewer` (letters via
`letter_panels(fmt=…)` where the installed version supports it; otherwise clear
the auto letters and add text notes) or with matplotlib `rcParams`
(`font.family`, `font.size`, `mathtext.fontset = "custom"` so maths uses the
same face). Verify the font resolves (`font_manager.findfont`) and that **no**
text falls outside the size range — check the smallest annotation, not only the
axis labels. Save the answers in the set's `style_dict` so the next figure does
not ask again.

---

## Rules

| Rule | Detail |
|------|--------|
| Not overview | Quick report stays `default-overview-plots.md` |
| Not stack recipe | Waterfall / false-color → `stack-plots.md` |
| Ask size | Journal preset or user mm — never silent random width |
| House style | Font family, min/max pt, letter format from the user (or stored `style_dict`) — never the matplotlib defaults |
| Shared scales | Echo `shared_levels` / `shared_ranges` |
| Edge labels | Default `edge_labels_only=True` — outer axes only |
| Save | `analysis/figures/`; path in report; no huge arrays in chat |
| Style reuse | `style_dict` / `save_style` when making a paper set |
| Align, don't eyeball | `align_panels` / `distribute_panels` / `match_size`; letters aligned |
| Editable copy | `.afig` + `data for <stem>/` next to the PDF when on `arpes_viewer` |

---

## Checklist

1. User asked publication / journal layout (not default overview).  
2. Backend: viewer `tools.output.figure` or simple matplotlib; no DIY composer invent.  
3. Preset / width_mm / font_pt echoed; house style (font, size range, letter format) applied and echoed.  
4. Shared clim/limits stated; panels lettered if multi.  
5. PNG/PDF under `analysis/figures/` (+ `.afig` and data folder on viewer).  
6. Panel content chosen from `figure-gallery.md` when the user asks for a
   figure *type*.
