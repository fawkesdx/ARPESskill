# De-grid example (ANTARES / CASSIOPEE)

Requires `arpes_viewer` env + `PYTHONPATH` → `ARPES_viewer`
(`arpes-viewer-env.md`).

## Map

```text
User: Remove the MCP grid from this ANTARES map before I convert to k.
```

1. Backend already `arpes_viewer` (or Route B on `.nxs`).  
2. `why = not_pixel_locked(info)` → must be `None`.  
3. `degrid_map(cube)` → save under `analysis/`; optionally save `[grid]`.  
4. Report backend + pixel-lock OK. **Then** k only if user asks.

## Cut with saved grid

```text
User: De-grid this cut using the grid from Map80eV.
```

1. Load cut + `[grid]` pattern (same pass energy / lens).  
2. `degrid_cut_with_grid(frame, pattern)`.  
3. If no grid → ask before `degrid_cut_notch` and warn PE loss in grid bands.

## Wrong backend

```text
User: De-grid this MAESTRO FITS (pyarpes stem).
```

→ Stop. `degrid_*` N/A on PyARPES. Offer **D** (viewer stack / re-load) or
B/C — not DIY FFT.

## See also

- `reference/degrid.md`
- Upstream README “De-grid” section
