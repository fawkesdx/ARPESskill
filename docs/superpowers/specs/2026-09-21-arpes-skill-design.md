# ARPESskill — Design Spec

**Date:** 2026-09-21  
**Status:** Revised draft — awaiting user re-review  
**Repo (planned):** `https://github.com/fawkesdx/ARPESskill` (public)

## 1. Purpose

ARPESskill is a **general LLM agent skill** for working with ARPES data. It teaches agents how to load and analyze photoemission data using the known typical axes of ARPES measurements, units, and physics assumptions — without inventing any of those.

It is intentionally **not tied to one analysis package** long-term. The skill is a **bridge**: detect what the user has, then drive that stack. **v1 implements the PyARPES path only** (plus xarray/h5py fallback). TensorSpec_GUI and other stacks are separate later work — not mixed into this v1 delivery.

### What “data reduction” means here

In ARPES, **reduction** does **not** mean “compress the file.” It means turning a raw multidimensional scan into analysis products: energy/momentum cuts, EDC/MDC, Fermi-surface maps, spatial ROIs, etc. v1 covers the **light** end — load, lock axes, one or two standard cuts/plots — not full publication pipelines or heavy many-body fitting.

## 2. Goals (v1) — PyARPES only

1. **Data literacy (primary):** formats, dimension names, units, angle↔momentum caveats.
2. **Light analysis workflow (secondary):** load → inspect → cut → plot, with a safe-reduction checklist.
3. **Failure-mode awareness:** classic agent mistakes (angle-as-k, hν/kz mixups, silent Γ claims, bogus labels).
4. **PyARPES path:** concrete recipes for MAESTRO-style load and analyze via LLM.
5. **Public, portable install:** clone GitHub; load into Cursor, Claude Code, or other skill-capable agents.

### Explicitly deferred (separate workstreams later)

- TensorSpec_GUI headless module bridge
- TensorSpec HTML/REST
- ARPESeed / ML warehouse
- Deep `peaks` / nanoARPES / in-operando recipes

### Success criteria

Primary smoke: **load typical ALS MAESTRO ARPES data with PyARPES and analyze via the LLM agent** (jobs usually done in a GUI), without inventing axes.

Also:

1. State axes and units before any plot.
2. Produce at least one FS- or EDC-style product with labeled axes.
3. Follow (or explicitly skip with reason) the safe-reduction checklist.
4. Avoid failure modes listed in `reference/failure-modes.md`.

## 3. Non-goals (v1)

- Any TensorSpec / TensorSpec_GUI / HTML bridge code or required docs beyond a one-line “future work” note
- ARPESeed model download / inference
- Training pipelines or synthetic corpus generation
- Beamline DAQ / instrument control
- MATLAB control
- Required heavy fitting stacks
- Large MAESTRO files in git
- Full nanoARPES / in-operando depth

## 4. Approach

**Portable agent-skill pack:** thin `SKILL.md` + `reference/` + `examples/`.

| Situation | Prefer |
|-----------|--------|
| v1 default | **PyARPES** |
| PyARPES missing | **xarray + h5py/nexusformat** |

Agent always states which path it used.

## 5. Architecture

### 5.1 Repo layout

```
ARPESskill/
├── README.md
├── LICENSE                 # MIT
├── SKILL.md
├── reference/
│   ├── formats-and-axes.md
│   ├── safe-reduction.md
│   └── failure-modes.md
└── examples/
    └── maestro_pyarpes.md
```

### 5.2 File ownership

| File | Responsibility |
|------|----------------|
| `SKILL.md` | Triggers, hard rules, workflow, PyARPES-first bridge policy |
| `reference/formats-and-axes.md` | File types, dims, units, k-conversion; MAESTRO notes |
| `reference/safe-reduction.md` | Load → inspect → cut → plot checklist |
| `reference/failure-modes.md` | Anti-patterns |
| `examples/maestro_pyarpes.md` | Worked MAESTRO + PyARPES path (+ xarray fallback note) |
| `README.md` | Multi-host install + scope |

**Constraint:** `SKILL.md` ~100–200 lines; detail in `reference/`.

### 5.3 Agent workflow

1. Identify artifact (MAESTRO `.h5`, etc.).
2. Use PyARPES if available; else xarray/h5py; state which.
3. Lock coordinates (names + units).
4. Sanity print (shape, ranges).
5. Light reduce per `safe-reduction.md`.
6. Plot/report with labeled units; state assumptions.
7. If unsure → read `reference/`; one sharp question.

### 5.4 Hard rules

- Never invent axis names or units.
- Never treat detector angle as k without stating conversion assumptions.
- Never claim “Γ found” without method.
- Do not pull TensorSpec into v1 answers unless the user explicitly asks (then: say it is deferred / separate skill).
- Prefer existing project loaders before writing new ones.

### 5.5 Error handling

- Missing deps → suggest install; offer xarray fallback.
- Ambiguous axes → stop and ask.
- Corrupt/partial file → report readable parts only.

## 6. Trigger

Invoke for ARPES spectra, FS maps, EDC/MDC, MAESTRO/NeXus/HDF5/Igor, PyARPES, angle↔momentum.

## 7. Testing (v1)

- Manual MAESTRO smoke via **PyARPES** (user-provided path; not in git).
- Checklist vs hard rules.
- No CI package required for v1.

## 8. Distribution

- Public GitHub: `fawkesdx/ARPESskill`, `main`, MIT.
- Install: Cursor / Claude Code / generic agent skill dirs (README documents each).
- Tag `v1` when MAESTRO + PyARPES smoke passes.

## 9. Implementation order

1. Create public GitHub repo `fawkesdx/ARPESskill`.
2. Author `SKILL.md` + three reference files + `maestro_pyarpes.md` + README + LICENSE.
3. Local install smoke on at least one agent host.
4. Manual MAESTRO + PyARPES pass.
5. Tag `v1`.

TensorSpec_GUI bridge = **new design + plan later**, separate from this v1.

## 10. Decisions log

| Decision | Choice |
|----------|--------|
| Scope v1 | General skill, **PyARPES only** |
| TensorSpec_GUI | Deferred — separate workstream |
| HTML TensorSpec | Out |
| Content | Literacy + light reduction |
| Smoke | MAESTRO via PyARPES + LLM |
| Fallback | xarray + h5py |
| Shape | Thin SKILL.md + references |
| License / GitHub | MIT / `fawkesdx/ARPESskill` |

## 11. Clarifications

1. Purpose = general LLM skill; not Cursor-only.
2. “Reduce” = ARPES cuts/maps.
3. Package bridge long-term; **v1 = PyARPES path only**.
4. TensorSpec_GUI callable bridge = later, separate.
