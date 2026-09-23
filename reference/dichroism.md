# Dichroism (CP / CM pattern)

**Gate:** user asks **dichroism** / CD / CP−CM / circular (or linear) pol
difference. Not default overview.

**Not a PyARPES module** — pattern on load + xarray + existing helpers
(`masks.md`, `align.md`, `axis-prep.md`). ≠ SARPES
(`spin-arpes.md` / `to_intensity_polarization`).

Capabilities: `dichro_load`, `dichro_null_scale`, `dichro_diff`, `dichro_asym`,
`dichro_plot` — `backend-capability-map.md`.

---

## Load CP + CM

1. Resolve **CP** and **CM** (or RCP/LCP, σ+/σ−, C+/C− — echo labels used).  
   Separate files, two data_vars, or pol dim — state which.  
2. Same spectroscopic dims/coords. If drifted → `align` first (`align.md`);
   ask before permanent shifts.  
3. EF / k claims still follow `k-and-kz-conversion.md` if working in k.

---

## Null-ROI scale (required before subtract)

Region expected **≈0 dichroism** (user box / mask). **Ask if missing** — never
invent.

Default metric: **mean** intensity in null ROI (use **sum** only if user says).

```python
# null = user ROI → boolean / .sel slice (echo bounds)
# s = float(cp.where(null).mean() / cm.where(null).mean())
# cm_scaled = cm * s   # or scale cp — echo which side
```

Echo scale factor + which array scaled. If null mean ~0 → stop / ask.

This is **not** `normalize_dim` (global along an axis).

---

## Products (path C — both)

```python
# D = cp_scaled - cm_scaled          # or cp - cm_scaled
# denom = cp_scaled + cm_scaled
# A = D / denom.where(abs(denom) > eps)   # mask / floor tiny denom — echo eps
```

Report **both** difference `D` and asymmetry `A`. Save under `analysis/` with
null ROI def + scale.

---

## Plot (diverging red / blue)

1. Diverging colormap: **red = positive**, **blue = negative**, zero near white.  
   Prefer `RdBu_r` (or equiv.) with limits **symmetric about 0** by default.  
2. User / agent may **tweak clim or color offset** so zero looks right and
   contrast is readable — **echo** `vmin`/`vmax` (and any offset). Not silent.  
3. Show D and A (or ask which first if token-tight). Mark null ROI on a side
   panel if useful.  
4. Scripted PNG under `analysis/` — prefer matplotlib over GUI.

```python
# import matplotlib.pyplot as plt
# vmax = float(np.nanpercentile(np.abs(D), 99))  # or user clim
# D.plot(cmap="RdBu_r", vmin=-vmax, vmax=vmax, center=0)  # xarray/matplotlib
```

---

## Hard rules

- No invent CP/CM pairing or null ROI.  
- Scale null ROI **before** subtract; echo factor.  
- Both D and A (path C).  
- No claim `arpes.dichroism.*` exists.  
- Not spin polarization helpers.

---

## Checklist

1. CP + CM identified; labels echoed.  
2. Null ROI user-stated; scale factor reported.  
3. D and A computed; tiny-denom handled.  
4. Plots: red+/blue−; clim/offset echoed if tweaked.
