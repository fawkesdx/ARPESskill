# Publication figure layout

**Gate:** user asks **publication figure** / journal panel layout / Nature|PRB|Science
column width / multi-panel paper figure / figure composer. **Not** default
quick-report overviews (`default-overview-plots.md`) and **not** waterfall
stacks (`stack-plots.md`).

This is **layout / export**, not a physics analysis recipe. Do not list it as
a core ARPES “analysis skill” sibling to k/kz.

**Backend:** primarily `arpes_viewer` —
[ARPES-data-browser](https://github.com/DingPei1995/ARPES-data-browser)
`tools.figure` (+ `tools.export`; paint may use `ui.figure` — prefer headless
model). Env: `arpes-viewer-env.md`.

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

Use `tools.figure.JOURNAL_PRESETS` (label, width_mm, font_pt). Examples include
Nature single/double, APS/PRB, Science, Elsevier, slide — **read the tuple in
the installed package**; do not hardcode different mm from memory.

```python
from tools.figure import Figure, Panel, PanelData, FigureStyle, JOURNAL_PRESETS

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

## Rules

| Rule | Detail |
|------|--------|
| Not overview | Quick report stays `default-overview-plots.md` |
| Not stack recipe | Waterfall / false-color → `stack-plots.md` |
| Ask size | Journal preset or user mm — never silent random width |
| Shared scales | Echo `shared_levels` / `shared_ranges` |
| Edge labels | Default `edge_labels_only=True` — outer axes only |
| Save | `analysis/figures/`; path in report; no huge arrays in chat |
| Style reuse | `style_dict` / `save_style` when making a paper set |

---

## Checklist

1. User asked publication / journal layout (not default overview).  
2. Backend: viewer `tools.figure` or simple matplotlib; no DIY composer invent.  
3. Preset / width_mm / font_pt echoed.  
4. Shared clim/limits stated; panels lettered if multi.  
5. PNG/PDF under `analysis/figures/`.
