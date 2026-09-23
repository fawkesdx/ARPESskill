# Spatial XY scans (3D–5D+, including hv)

**Gate:** when loaded data has **both** `x` and `y` (or equivalent stage
motors) with size >1 — a **spatial** scan. Subtype from other dims.

Package-first: PyARPES load + `sel`/`sum`/`mean`/`where` + existing kind
recipes. Optional GUI (`qt_tool` / `S.show`) only if the user asks.
Do **not** invent a TensorSpec-style linked viewer.

**Docs:** [Nano XPS example](https://arpes.readthedocs.io/en/latest/notebooks/full-analysis-xps.html) ·
[PyARPES spatial coords](https://arpes.readthedocs.io/en/latest/spectra.html) ·
`arpes.plotting.spatial`

Capabilities: `spatial_overview`, `spatial_roi_reduce`, `pca_spatial` (optional) —
`backend-capability-map.md`.

---

## Kind ladder (dims first)

| Kind | Typical dims | Spectroscopic content at each (x,y) |
|------|----------------|--------------------------------------|
| **XY–E** | `x,y,eV` | Energy line / XPS-like |
| **XY–ARPES** | `x,y,eV,φ` | Cut (dispersion) |
| **XY–map** | `x,y,eV,φ,ψ` (deflection / `Slit_Defl` / …) | Local Fermi map |
| **XY–hv** | `x,y,hv,eV` (± φ ± ψ) | Photon-energy dependent spatial scan |

Combos allowed (e.g. XY–hv–ARPES). Log text is comment only — **dims win**.
Use `S.is_spatial` when available as a hint; still print dims.

---

## Core idea: wrapper, not a new physics stack

```text
1. Build XY intensity map with spectroscopic ROI R (integration “box”)
2. Hot spot (x*,y*) = argmax of that map
3. Classify kind at (x*,y*) / ROI → run EXISTING skill recipes for that kind
4. Optional: broadcast fits → parameter maps on (x,y) — user-asked only
```

| Kind at point / ROI | Reuse | Map back to XY (if asked) |
|---------------------|--------|---------------------------|
| Cut | `edc-mdc-fitting.md`, cut overview | EDC/MDC centers, widths, amps vs (x,y) |
| E-line / core | Core section of `edc-mdc-fitting.md` | Peak position / width / amp maps |
| Fermi map | Fermi trio lite + EF rules (`default-overview-plots.md`, `k-and-kz-conversion.md`) | Isoenergy or derived maps — expensive; ask |
| hv stack | `k-and-kz-conversion.md` hv EF QC — on ROI or spatial mean, not whole cube by default | After reduce |

---

## Spectroscopic ROI R (the GUI “integration square”)

XY map intensity is **not** a mystery sum. It is integrate over a
**spectroscopic** ROI \(R\) (energy, and optional φ / ψ / hv), then plot vs x,y.

### Defaults (if user does not give a box)

| Situation | Default \(R\) |
|-----------|----------------|
| Valence / ARPES-like (φ or ψ present, or near-EF science) | Near-EF energy window — **state meV** (e.g. −50…+20 meV); integrate all φ/ψ unless stated |
| Core / XPS-like (XY–E, deep binding) | Full measured `eV` in file **or** stated core ROI — say which |
| User silent on φ/ψ | Integrate all detector / deflection angles |

### User override (preferred when they care)

Accept explicit bounds, e.g. “E −0.1…0 eV, φ −5°…5°”, or “core peak −35…−31 eV”.
Optional interactive mask/`qt_tool` **only if user asks** — full mask recipe:
`reference/masks.md` (boolean / polygon).

**Always echo \(R\)** in the report. Change \(R\) → **rebuild** XY map and
recompute hot spot (do not reuse an old argmax).

---

## Hot spot (x*, y*)

1. Form \(I_R(x,y)\) by integrating spectroscopic dims over \(R\).  
2. **(x*, y*) = argmax** of \(I_R\) (package `argmax` / numpy on the map).  
3. Report coordinates + intensity.  
4. If map is flat / empty / all-NaN → fall back to **mid indices**; **say so**.

Anti-claims: hot spot ≠ Γ; map energy window ≠ calibrated EF unless EF workflow ran.

---

## Quick report — spatial set (required PNGs)

Save under `analysis/`; token note if volume is huge (`token-usage.md`).

| # | Plot | Rule |
|---|------|------|
| 1 | **XY map** \(I_R(x,y)\) | State \(R\); label axes (µm or motor units from coords) |
| 2 | **At hot spot** | Spectrum / φ×E / local Fermi lite / mid-hv cut — whatever dims allow at (x*,y*) |
| 3 | **Spatial mean** | Mean over all x,y (or stated mask) of the same spectroscopic view |
| 4 | **Subtype extra** | **XY–map:** near-EF isoenergy at hot spot (state E). **XY–hv:** XY maps at low/mid/high hv **or** I(hv) at hot spot. **XY–E:** optional second E-window map only if user asks |

Echo overview assumptions + \(R\) + (x*,y*).

**Quick report stays angle/energy space** — no `convert_to_kspace` on the hypercube.

---

## Analysis mode (user-asked)

1. **Spatial ROI** (rectangle / mask in x,y) → reduce → treat as cut / map / hv / E-line.  
2. **Hot-spot first:** one full kind analysis (EDC/MDC, peak fit, Fermi lite, …).  
3. **Parameter maps:** `broadcast_model` on `["x","y"]` (or loop) only after a
   test curve; token note; save param XY figures.  
4. **PCA / NMF / ICA / factor analysis:** `reference/decomposition.md`
   (`pca_along` etc.) — ask before large decompositions.  
5. **k / kz / near-EF gap:** only on reduced ROI or spatial mean; follow those
   references; never silent full 5D/6D convert.

---

## Package map

| Step | Prefer |
|------|--------|
| Detect spatial | Dims; `S.is_spatial` hint |
| XY map / means | `sum` / `mean` / `sel` over stated dims |
| Spatial plots | `arpes.plotting.spatial` helpers if useful; else matplotlib |
| PCA / NMF / ICA / FA | `reference/decomposition.md` (`pca_along`, …) |
| Fits over XY | `broadcast_model` + models from `edc-mdc-fitting.md` |
| Interactive box | `qt_tool` / mask tools — **ask first** |

---

## Do not

- Full-sum XY map with **no** stated \(R\).  
- Auto-fit every pixel without user ask + token note.  
- Treat hot spot as Γ or EF calibration.  
- k/kz or hv-EF align on the entire spatial hypercube by default.  
- Launch Qt as the only overview path.  
- Invent TensorSpec / linked XY‖dispersion UI.

---

## Checklist before reporting

1. Dims listed; spatial subtype named (XY–E / ARPES / map / hv / combo).  
2. Spectroscopic ROI \(R\) stated (default or user).  
3. XY map + hot spot (x*,y*) + spatial mean (+ subtype extra) saved.  
4. Kind at hot spot / ROI identified; matching reference used for deeper analysis.  
5. Broadcast / PCA / k / gap only if asked (or clearly in scope); assumptions echoed.
