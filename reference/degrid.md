# De-grid (detector MCP / mesh)

**Gate:** user asks **de-grid** / MCP grid / detector mesh / hexagonal grid /
Scienta mesh. Not default overview.

**Backend:** `arpes_viewer` only — [ARPES-data-browser](https://github.com/DingPei1995/ARPES-data-browser)
`tools.degrid` (`arpes-viewer-env.md`, `arpes-viewer-backend.md`).  
If active backend is `pyarpes` → **stop**; offer A/B/C/**D** (`package-first.md`).
Prefer **D** only if data can live on the viewer stack; do not invent a DIY FFT.

Capabilities: `degrid_pixel_lock`, `degrid_map`, `degrid_cut` —
`backend-capability-map.md`.

---

## What it is

Periodic **multiplicative** pattern locked to detector pixels:

- ANTARES / CASSIOPEE MBS MCP — hexagonal, ~5 px  
- CASSIOPEE Scienta — square mesh, ~11 px  

A **map is its own reference** (grid stays put; photoemission moves). Upstream
defaults are tested; do **not** invent Advanced parameters unless the user
sets them.

---

## Hard refuse — pixel-locked only

**Do de-grid first**, on data still on detector pixels.

Before calling degrid, check `tools.degrid.not_pixel_locked(info)` (or
equivalent metadata). If it returns a reason → **refuse** and quote it.

Typical blockers (non-exhaustive):

- Already k-converted / kz→k resampled  
- Fermi-surface bend correction / kz align  
- Smooth, derivative, curvature, background, symmetrise  
- Cut arithmetic product  
- Already de-gridded  

```python
from tools.degrid import not_pixel_locked

why = not_pixel_locked(scan.info)  # or dataset info dict
if why:
    raise SystemExit(f"refuse de-grid: {why}")
```

Never silent-degrid after k “to clean up.”

---

## Map / kz_map

```python
from tools.degrid import degrid_map

# cube = intensity array still on detector axes (check upstream shape order)
result = degrid_map(cube, settings=None, progress=None)
# Save de-gridded product under analysis/; optionally list/save [grid] pattern
# for later cuts (same lens mode + pass energy).
```

Echo: backend `arpes_viewer`, defaults used, whether `[grid]` pattern saved.
Progress bar / token note OK for large maps (~minute-scale upstream).

---

## Cut

1. **Prefer** `degrid_cut_with_grid(frame, pattern, …)` using a `[grid]` from a
   map taken with the **same** lens mode / pass energy.  
2. **Else** `degrid_cut_notch(frame, …)` — **warn explicitly**: removes grid
   *and* photoemission in those Fourier regions; power &lt; 1 means over-kill.

```python
from tools.degrid import degrid_cut_with_grid, degrid_cut_notch

# with_grid = degrid_cut_with_grid(frame, pattern)
# or notch = degrid_cut_notch(frame)  # warn user in report
```

---

## Products / report

- De-gridded array / viewer dataset under `analysis/` (or session list).  
- Optional grid pattern artifact for cuts.  
- Report: pixel-lock check OK; map vs cut; with-grid vs notch; backend.  
- Do not claim quantitative k until after later convert (still angle-space).

---

## Checklist

1. User asked de-grid?  
2. Backend `arpes_viewer` (+ env)? Else A/B/C/**D**.  
3. `not_pixel_locked` is None?  
4. Map → `degrid_map`; cut → with-grid or notch+warn.  
5. Products saved; assumptions echoed.  

## Do not

- DIY Fourier / Wiener “degrid” when `tools.degrid` exists.  
- De-grid after k / FS / kz-align / heavy process.  
- Silent notch without warning.  
- Install viewer deps into PyARPES 3.8 env.  
