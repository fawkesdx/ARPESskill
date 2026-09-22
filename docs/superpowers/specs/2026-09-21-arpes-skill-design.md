# ARPESskill — Design Spec

**Date:** 2026-09-21  
**Status:** Approved (2026-09-21)  
**Repo (planned):** `https://github.com/fawkesdx/ARPESskill` (public)

## 1. Purpose

ARPESskill is a **general LLM agent skill** for working with ARPES data. It teaches agents how to load and analyze photoemission data using the known typical axes of ARPES measurements, units, and physics assumptions — without inventing any of those.

It is intentionally **not tied to one analysis package** long-term. The skill is a **bridge**: detect what the user has, then drive that stack. **v1 implements the PyARPES path only** (plus xarray/h5py fallback for load/inspect). TensorSpec_GUI and other stacks are separate later work.

### What “data reduction” means here

In ARPES, **reduction** does **not** mean “compress the file.” It means turning a raw multidimensional scan into analysis products: energy/momentum cuts, EDC/MDC, Fermi-surface maps, fitted dispersions, k- and kz-converted volumes, etc.

## 2. Goals (v1) — PyARPES only

1. **Data literacy:** formats, dimension names, units, angle↔momentum / hv↔kz caveats.
2. **Core analysis workflow:** load → inspect → cut / FS / EDC / MDC → plot, with a safe-reduction checklist.
3. **Line analysis + fitting:** EDC and MDC peak fits with **Gaussian, Lorentzian, Voigt**; broadcast fits to produce **width vs E**, **width vs k**, **E vs k** (fitted dispersion) plots.
4. **Momentum conversion:** cuts and Fermi maps converted to **k-space** (`convert_to_kspace` / kx–ky); never treat angle as k silently.
5. **Photon-energy → kz:** Eph-dependent scans converted with stated **inner potential**; agent must surface V₀ assumptions.
6. **Failure-mode awareness:** angle-as-k, hν/kz mixups, silent Γ claims, bogus labels, fit without stating lineshape/background.
7. **Public, portable install:** Cursor, Claude Code, other skill-capable agents.

### Explicitly deferred (separate workstreams later)

- TensorSpec_GUI headless module bridge / linked XY ‖ dispersion viewer
- TensorSpec HTML/REST
- ARPESeed / ML warehouse
- Deep `peaks` / nanoARPES ROI UX / in-operando recipes
- Full many-body / self-energy publication pipelines (basic MDC→width is in; advanced Σ(ω) optional later)

### Success criteria

Primary smoke: **load typical ALS MAESTRO ARPES data with PyARPES and analyze via the LLM agent**, without inventing axes.

Must demonstrate (on real or tutorial data as available):

1. Axes + units stated before plots.
2. At least one **EDC or MDC** extracted and plotted.
3. At least one **peak fit** (Gaussian, Lorentzian, or Voigt) and one **broadcast/derived** plot (width vs E or k, or E vs k from fits).
4. At least one **cut or Fermi map** converted to **k-space** with conversion assumptions stated.
5. At least one **hv / Eph → kz** conversion path documented and runnable when hv-scan data exist (tutorial `photon_energy` OK if no MAESTRO hv scan on hand); **inner potential** stated.
6. Safe-reduction checklist followed or explicitly skipped with reason.
7. Failure modes avoided per `reference/failure-modes.md`.

## 3. Non-goals (v1)

- TensorSpec / TensorSpec_GUI / HTML bridge (beyond one-line future note)
- Linked XY spatial map ‖ dispersion viewer (use TensorSpec_GUI later)
- ARPESeed / training / DAQ / MATLAB
- Large MAESTRO files in git
- Requiring interactive QtTool/Bokeh as the agent path (prefer **scripted** PyARPES + matplotlib)

## 4. Approach

**Portable agent-skill pack:** thin `SKILL.md` + `reference/` + `examples/`.

| Situation | Prefer |
|-----------|--------|
| v1 analysis (fit, k, kz) | **PyARPES** |
| Load/inspect only, no PyARPES | **xarray + h5py/nexusformat** (no full fit/kz recipes) |

Agent always states which path it used. Fit + k + kz recipes assume PyARPES.

## 5. Architecture

### 5.1 Repo layout

```
ARPESskill/
├── README.md
├── LICENSE
├── SKILL.md
├── reference/
│   ├── formats-and-axes.md
│   ├── safe-reduction.md
│   ├── edc-mdc-fitting.md      # Voigt/Lorentz/Gauss, broadcast, width/E/k plots
│   ├── k-and-kz-conversion.md  # cut/FS → k; Eph → kz; V₀ rules
│   └── failure-modes.md
└── examples/
    ├── maestro_pyarpes.md      # load + inspect + light cuts
    ├── fit_edc_mdc.md          # fit + derived line plots
    └── convert_k_kz.md         # k-space + kz examples
```

### 5.2 File ownership

| File | Responsibility |
|------|----------------|
| `SKILL.md` | Triggers, hard rules, workflow, pointers |
| `formats-and-axes.md` | File types, dims, units, MAESTRO notes |
| `safe-reduction.md` | Load → inspect → cut/FS/EDC/MDC checklist |
| `edc-mdc-fitting.md` | Lineshapes, `broadcast_model`, width vs E/k, E vs k |
| `k-and-kz-conversion.md` | `convert_to_kspace`, kx–ky FS, hv→kz, inner potential |
| `failure-modes.md` | Anti-patterns (incl. fit + conversion) |
| `examples/*` | Worked scripted recipes |

**Constraint:** `SKILL.md` ~100–200 lines; detail in `reference/`.

### 5.3 Agent workflow

1. Identify artifact; prefer PyARPES for analysis goals.
2. Lock coordinates (names + units).
3. Sanity print (shape, ranges).
4. Reduce: cut / FS / EDC / MDC as needed.
5. If reporting momentum: convert to k (state geometry assumptions).
6. If hv-dependent: convert to kz (state V₀).
7. If line analysis: fit with named lineshape; broadcast if tracking; plot params vs E or k.
8. Plot/report with labeled units; state all assumptions.
9. If unsure → read matching `reference/`; one sharp question.

### 5.4 Hard rules

- Never invent axis names or units.
- Never treat detector angle as k without conversion + stated assumptions.
- Never convert hv→kz without stating **inner potential** (or that it is unknown / placeholder).
- Never claim “Γ found” without method.
- Never report fit results without lineshape (+ background if used).
- Do not pull TensorSpec into v1 unless user asks (deferred).
- Prefer scripted analysis over launching Qt GUI tools.
- Prefer existing project loaders before writing new ones.

### 5.5 Error handling

- Missing PyARPES → suggest install; limit to load/inspect via xarray if needed.
- Ambiguous axes → stop and ask.
- Ambiguous V₀ → ask or mark kz as relative/uncertain.
- Corrupt/partial file → report readable parts only.

## 6. Trigger

Invoke for ARPES spectra, FS maps, EDC/MDC, peak fitting, k-conversion, kz/hv scans, MAESTRO/NeXus/HDF5/Igor, PyARPES.

## 7. Testing (v1)

- MAESTRO smoke: load + axes + cut/EDC (user path; not in git).
- Fit smoke: one EDC/MDC fit + one broadcast/derived plot (MAESTRO or PyARPES tutorial data).
- k smoke: cut or FS → k-space.
- kz smoke: hv-scan → kz (tutorial `photon_energy` acceptable).
- Checklist vs hard rules.

## 8. Distribution

- Public GitHub: `fawkesdx/ARPESskill`, `main`, MIT.
- Multi-host install in README.
- Tag `v1` when success criteria met.

## 9. Implementation order

1. Create public GitHub repo.
2. Author `SKILL.md` + five reference files + three examples + README + LICENSE.
3. Local install smoke on one agent host.
4. Run smokes: MAESTRO load, fit, k, kz.
5. Tag `v1`.

TensorSpec_GUI / XY linked viewer = later separate design.

## 10. Decisions log

| Decision | Choice |
|----------|--------|
| Scope v1 | PyARPES: literacy + EDC/MDC/fit + k + kz |
| Spatial linked viewer | Deferred (TensorSpec_GUI) |
| Lineshapes | Gaussian, Lorentzian, Voigt |
| Fallback without PyARPES | Load/inspect only |
| Shape | Thin SKILL.md + references + examples |
| License / GitHub | MIT / `fawkesdx/ARPESskill` |

## 11. Clarifications

1. Purpose = general LLM skill; not Cursor-only.
2. “Reduce” = ARPES cuts/maps/fits/conversions.
3. v1 = PyARPES path only; TensorSpec_GUI later.
4. Expanded goals = **fit + k + kz**; XY side-by-side viewer still out.
