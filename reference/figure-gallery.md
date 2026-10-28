# Publication figure gallery (ARPES archetypes)

**Gate:** user asks for a **paper figure** of a given kind ("make a figure like
…", "3-D cube", "stacked constant-energy maps", "data vs DFT", "k_z evolution",
"crystal + BZ panel", "MDC stack with guides", "plot the fitted crossing vs
k_z"), or asks *how ARPES results are usually shown*. Layout, page width,
letters and export → `figure-layout.md`. Waterfall-only plots →
`stack-plots.md`. **Not** the quick-report overview
(`default-overview-plots.md`).

Material-agnostic: every archetype below is described by the **data it needs**
and the **physics it shows**, never by a compound. Do not suggest a figure the
data cannot support (e.g. no k_z panel without an hv scan and a stated V₀).

**Backend:** `arpes_viewer`
([ARPES-data-browser](https://github.com/DingPei1995/ARPES-data-browser)) has
headless builders for most panels (`tools.processing.volume`,
`tools.crystal.*`, `tools.spectra.dispersion`) and a composer model
(`tools.output.figure`) that writes PNG / PDF and a re-editable `.afig` with a
per-panel data folder. 3-D scenes and the crystal render need its Qt painter
(offscreen OK) — **GUI only if the user asks**. `pyarpes`: matplotlib
equivalents noted per archetype; if a panel needs a capability the backend
lacks → A/B/C/**D** (`package-first.md`).

Capabilities: `figure_gallery`, `plot_notched_cube`, `plot_stacked_slices`,
`plot_calc_overlay`, `plot_crystal_bz`, `band_crossing_fit` —
`backend-capability-map.md`.

---

## How to use this file

1. Ask (or infer from the request) **what the figure must show**: Fermi
   surface topology, a dispersion, its k_z dependence, agreement with a
   calculation, a quantitative trend.
2. Offer **2–3 archetypes** from the table that show it with the data in
   hand; say which data each needs. Let the user choose — do not build all.
3. Build each panel from the **active backend** (package-first), then lay out
   per `figure-layout.md`. Echo every number that changes the picture
   (energy window, integration width, clim, Z / shift, V₀).

---

## Archetypes

| # | Archetype | Shows | Needs |
|---|-----------|-------|-------|
| A | Overview: FS map + high-symmetry cuts | topology + where the cuts are | k-map (or angle map + stated Γ), cuts |
| B | Notched cube ("3-D box") | one CEC + two dispersions in one picture | 3-D cube (kx, ky, E) |
| C | CEC series (row of maps at several E) | how pockets grow / shrink with E | k-map |
| D | Stacked slices in 3-D | evolution along E or k_z as layers | k-map or k_z map |
| E | k_z evolution | 3-D character / periodicity along k_z | hv scan + V₀ |
| F | Data vs calculation | agreement, renormalisation | cut / map + band calculation |
| G | Raw + band-enhanced side by side | weak / flat features | cut (`band-enhance.md`) |
| H | EDC / MDC stack with guides | line shapes, peaks behind a dispersion | cut |
| I | Fitted quantity vs parameter | the quantitative result | fits with errors |
| J | Crystal structure + BZ schematic | geometry: termination, path, k_z planes | structure (CIF / cell) |
| K | Dichroism / spin maps | orbital / spin texture | CP/CM or spin channels (`dichroism.md`, `spin-arpes.md`) |
| L | Parameter series (T, dose, gate, delay) | changes with an external knob | series (`temperature-series.md`, `in-operando-param-scans.md`, `tr-arpes.md`) |

Common combinations in the literature:

- **Topology figure:** J (structure) + A or B + C (± calc row under C).
- **Band-evolution figure:** B or D + C, with the energies of C marked on B/D.
- **3-D (k_z) figure:** J (BZ with the measured planes) + E (k_z map, BZ edges)
  + D (cuts stacked along k_z) + F (cuts with calculated guides) + I (fitted
  feature vs k_z with the calculated curve).
- **Many-body figure:** F + H + I (Σ, width, v_F vs E) — see `self-energy.md`.

---

## A — Overview: FS map + high-symmetry cuts

- Map at E_F (state integration window, e.g. ±10 meV), BZ boundary dashed
  (`bz-overlay.md`), the cut positions as lines on the map, labelled to match
  the cut panels.
- Cuts in E − E_F vs k; same colormap as the map; high-symmetry points as
  named ticks on the k axis (`Panel.x_tick_labels = [(k, "Γ"), …]`).
- matplotlib: `GridSpec`, map `pcolormesh`, `axvline` / `plot` for cut lines.

## B — Notched cube

- `tools.processing.volume.notched_box(values, axes, notch=(x, y, z),
  corner=(±1, ±1, ±1))` → faces; painted by the viewer's 3-D view
  (`ui.panels.volume`) → `To figure composer` / `Panel` kind `scene3d`.
- Notch at the feature of interest (e.g. kx = ky = 0, down to the lowest E);
  state crop ranges; colormap reversed (dark = high) is a common print choice.
- Colour bar for raw intensity: ends **High / Low**, not counts
  (`Panel.colorbar_ends = "high-low"`).
- matplotlib: `plot_surface` on three faces with `facecolors` from the cube —
  acceptable; no fake shading.

## C — CEC series

- Same k ranges, same aspect, **shared clim** or per-panel clim *stated*.
- Energies chosen to show a change (e.g. E_F and 3–4 steps below); write
  `E − E_F = …` in each title.
- Optional second row: calculated contours at the **same** energies after
  the same Z / shift (`tools.crystal.bands.contours`); colour by orbital
  weight only if the calculation provides it — say which orbital.

## D — Stacked slices in 3-D

- `tools.processing.volume.stack_faces(values, axes, axis, positions,
  width=…)` — each layer averaged over `width` (state it).
- Separate the layers enough that none hides another (viewer *Spread* /
  z-aspect; oblique view ~40–45° azimuth, 10–15° elevation); transparent low
  values so lower layers show.
- Optional curve through the layers (a pocket centre, a crossing point) — only
  from measured or fitted points; say which.

## E — k_z evolution

- k_z map (E_F, k∥ vs k_z) with BZ boundaries and Γ / Z labels; V₀ stated
  (`k-and-kz-conversion.md`) — never silent.
- Cuts at selected k_z: either a row of panels (all same ranges) or stacked
  along k_z (archetype D with `axis = k_z`).
- Mark the k_z of each cut on the k_z map.

## F — Data vs calculation

Three accepted styles — offer them:

1. **Overlay:** calculated bands as thin lines (dashed or solid, one colour)
   over the cut / map.
2. **Split panel:** left half data, right half calculation (mirrored about Γ),
   same axes.
3. **Side by side:** data panel, calculation panel (bands or simulated
   spectral function), identical ranges.

Rules: calculation along the **same k path and k_z** as the data (an hv cut
is a curved k_z surface — `tools.crystal.bands.bands_along_cut(…, hv=…,
inner_potential=…)`); any **renormalisation Z and energy shift** fitted
(`tools.crystal.bands.fit_alignment`) or chosen must be stated in the
caption; never shift bands panel by panel without saying so.

Guide lines along a specific band through crossings: follow the band by
character, not by energy order (`tools.crystal.bands.follow_band(model,
k_points, start, band, diabatic=True)`) — otherwise the guide jumps at every
crossing.

## G — Raw + band-enhanced

Raw intensity next to curvature / second derivative with the **same** ranges;
never the enhanced map alone for quantitative claims (`band-enhance.md`).

## H — EDC / MDC stack with guides

- Offset waterfall over a stated window and binning; dense enough to read the
  dispersion (often 30–50 curves); highlight E_F or the curve at a feature.
- Guides: fitted peak positions as markers, or calculated bands evaluated at
  each curve's energy, dashed. Say which.
- Mark on the parent cut the window the stack covers (a dashed box).

## I — Fitted quantity vs parameter

- Points **with error bars** from the fits (`edc-mdc-fitting.md`), not joined
  unless the line means something; model / calculation as a line in one
  colour. Axis label with the quantity and unit (`E_c − E_F (eV)`,
  `v_F (eV Å)`, `Γ (meV)`).
- Two straight branches meeting at a crossing (a cone fitted as two sides, or
  any two bands): `tools.spectra.dispersion.line_crossing(first, second)`
  gives the crossing with its propagated error — report it with σ.

## J — Crystal structure + BZ schematic

- Structure from CIF (`tools.crystal.structure.read_cif`); viewer render:
  glossy / translucent atoms, thin grey bonds, lattice constants on the cell
  edges, cleavage plane if termination matters. No element key when the
  caption names the atoms.
- BZ (`tools.crystal.bz3d`): k axes as arrows, high-symmetry labels offset
  from their dots (or placed at an equivalent point that is not crowded),
  the measured path in colour, measured CECs painted on the planes they were
  measured on (Γ plane, zone top) — the clearest way to show *where* in 3-D
  the data come from.
- matplotlib / ASE fallback: `ase.visualize.plot.plot_atoms` for the cell; BZ via
  `arpes.plotting.bz` (no data-on-plane) → say so.

---

## Rules

| Rule | Detail |
|------|--------|
| Data first | Archetype must match available data; ask before simulating anything |
| State windows | Integration width, binning, energy of every CEC / slice |
| Scales | Shared vs per-panel clim echoed; same ranges for compared panels |
| Calculation honesty | Z, shift, k_z / V₀ used, orbital weight shown — all in the report |
| Guides | Say whether a guide is fitted, calculated, or a by-eye line |
| No silent enhancement | Smoothing / derivative / symmetrisation named in the report |
| 3-D views | Angles + crop echoed; 3-D panel exported as picture, its arrays kept |
| Reproducible | Save the editable figure + its data folder (`figure-layout.md` § Save) |
| Generic | No material-specific defaults; labels from the user's data |

---

## Checklist

1. What must the figure show? Offer 2–3 archetypes that fit the data.  
2. Build panels with the active backend; echo windows, clim, Z / shift, V₀.  
3. Guides / overlays labelled as fitted / calculated.  
4. Lay out per `figure-layout.md` (preset, align, letters, colour bars).  
5. Save PNG / PDF **and** the editable figure + data folder under
   `analysis/figures/`.
