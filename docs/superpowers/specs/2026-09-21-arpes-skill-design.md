# ARPESskill — Design Spec

**Date:** 2026-09-21  
**Status:** Revised draft — awaiting user re-review  
**Repo (planned):** `https://github.com/fawkesdx/ARPESskill` (public)  
**Companion code (your lab):** TensorSpec branch `TensorSpec_GUI` — headless modules the skill can call  
**Not used for this bridge:** TensorSpec `HTML_einstein_app` / REST API

## 1. Purpose

ARPESskill is a **general LLM agent skill** for working with ARPES data. It teaches agents how to load and analyze photoemission data using the known typical axes of ARPES measurements, units, and physics assumptions — without inventing any of those.

It is intentionally **not tied to one analysis package**. The skill is a **bridge**: detect what the user already has, then drive that stack correctly.

**v1 stack order:**

1. **PyARPES** — primary portable path (any lab).
2. **TensorSpec_GUI modules** — when `tensorspec` from the `TensorSpec_GUI` branch is importable, the agent may call its **headless** loaders / data model / cut helpers (same code the GUI will use later). Not the Qt window; not the HTML web API.
3. **xarray + h5py/nexusformat** — fallback if neither stack is present.

ARPESeed / ML warehouse stay out of this skill.

### What “data reduction” means here

In ARPES, **reduction** does **not** mean “compress the file.” It means turning a raw multidimensional scan into analysis products: energy/momentum cuts, EDC/MDC, Fermi-surface maps, spatial ROIs, etc. v1 covers the **light** end — load, lock axes, one or two standard cuts/plots — not full publication pipelines or heavy many-body fitting.

## 2. Goals (v1)

1. **Data literacy (primary):** formats, dimension names, units, angle↔momentum caveats.
2. **Light analysis workflow (secondary):** load → inspect → cut → plot, with a safe-reduction checklist.
3. **Failure-mode awareness:** classic agent mistakes (angle-as-k, hν/kz mixups, silent Γ claims, bogus labels).
4. **Dual callable paths:** PyARPES recipes **and** TensorSpec_GUI module recipes (headless).
5. **Public, portable install:** clone GitHub; load into whatever agent host the user uses (see §8).

Later: richer spatial/`peaks` depth; angle→k conversion shared inside TensorSpec_GUI core so GUI + LLM share one implementation; in-operando dims.

### Success criteria

1. **Primary (portable):** load typical ALS MAESTRO data with **PyARPES** and analyze via LLM (GUI-replacement jobs), without inventing axes.
2. **Secondary (your lab):** same MAESTRO file loadable via **TensorSpec_GUI headless modules** (`MaestroLoader` / `ARPESLoader` → `TensorData`), with axes stated and one cut/profile produced — callable from the agent without opening the Qt GUI.
3. State axes and units before any plot; follow (or explicitly skip) safe-reduction checklist; avoid listed failure modes.

## 3. Non-goals (v1)

- TensorSpec **HTML** / Einstein REST (`HTML_einstein_app`) as the bridge target
- Launching or driving the Qt GUI as a required agent path (modules only; GUI consumes same modules later)
- ARPESeed model download / inference
- Training pipelines or synthetic corpus generation
- Beamline DAQ / instrument control
- MATLAB control
- Required dependency on heavy fitting stacks
- Large MAESTRO files checked into ARPESskill git
- Full nanoARPES / in-operando depth (pointers only)
- Merging TensorSpec into the public ARPESskill repo (bridge docs live here; TensorSpec code stays in TensorSpec)

## 4. Approach

**Portable agent-skill pack** in `ARPESskill` + **module work in TensorSpec_GUI** when gaps block headless LLM use.

| Layer | Where | Role |
|-------|--------|------|
| Skill docs | `ARPESskill` (public) | Literacy, workflow, how to call PyARPES **and** TensorSpec_GUI modules |
| General analysis | PyARPES (user env) | Default portable path |
| Lab stack | TensorSpec `TensorSpec_GUI` | Headless load / `TensorData` / cuts; later same functions for GUI viewer |
| Fallback | xarray + h5py | When neither stack installed |

### Package routing

| Situation | Prefer |
|-----------|--------|
| General / no TensorSpec | **PyARPES** |
| User has TensorSpec_GUI env and asks for it / MAESTRO via TensorSpec | **`tensorspec` headless modules** |
| Neither | **xarray + h5py/nexusformat** |
| Heavy spatial 4D later | Document **`peaks`**; optional post-v1 |

**Hard rule:** agent always states which path it used. Do not require TensorSpec for public users.

## 5. Architecture

### 5.1 ARPESskill repo layout

```
ARPESskill/
├── README.md
├── LICENSE
├── SKILL.md
├── reference/
│   ├── formats-and-axes.md
│   ├── safe-reduction.md
│   ├── failure-modes.md
│   └── tensorspec-gui-bridge.md   # how to import/call TensorSpec_GUI modules
└── examples/
    ├── maestro_pyarpes.md
    └── maestro_tensorspec_gui.md
```

### 5.2 TensorSpec_GUI work (companion, same effort track)

Today GUI branch already has: `MaestroLoader`, `ARPESLoader`, `TensorData`, viewer panel (Qt).

Likely gaps for LLM:

- Thin **headless** helpers (load path → `TensorData`; slice/profile → arrays/plots) so agent does not import PySide6 UI
- Angle→k **conversion** in shared core (you called this out) — implement in TensorSpec_GUI codebase so GUI + skill both call it later
- Document public function names the skill should use

Code lives in `/Users/sandyai/Documents/GitHub/TensorSpec` on `TensorSpec_GUI`. ARPESskill only documents and examples the call sites.

**Not in scope:** porting or depending on `HTML_einstein_app` routers.

### 5.3 Package bridge policy

1. Detect env: `import arpes` / `import tensorspec` / raw h5py.
2. Default portable analysis → PyARPES.
3. If user wants TensorSpec path or project clearly TensorSpec-based → headless TensorSpec_GUI modules.
4. Else xarray fallback.
5. Never invent a third framework; never invent axes.

### 5.4 Agent workflow

1. Identify artifact (MAESTRO `.h5`, etc.).
2. Choose stack (PyARPES vs TensorSpec_GUI vs fallback); say which.
3. Lock coordinates (names + units).
4. Sanity print (shape, ranges).
5. Light reduce (cuts/profiles) per `safe-reduction.md`.
6. Plot/report with labeled units; state assumptions.
7. If unsure → read `reference/`; one sharp question.

### 5.5 Hard rules

- Never invent axis names or units.
- Never treat detector angle as k without stating conversion assumptions.
- Never claim “Γ found” without method.
- Prefer headless TensorSpec modules over launching the GUI.
- Do not use HTML/Einstein REST for this bridge.
- Prefer existing project loaders before writing new ones.

### 5.6 Error handling

- Missing deps → suggest install; offer other path (PyARPES ↔ TensorSpec ↔ xarray).
- Ambiguous axes → stop and ask.
- Corrupt/partial file → report readable parts only.

## 6. Trigger

Invoke for ARPES spectra, FS maps, EDC/MDC, MAESTRO/NeXus/HDF5, PyARPES, TensorSpec ARPES load/view/reduce, angle↔momentum.

## 7. Testing (v1)

1. MAESTRO smoke via **PyARPES** (required for public skill).
2. Same file smoke via **TensorSpec_GUI headless** modules (required for dual-path claim).
3. Checklist vs hard rules.
4. No large data in git.

## 8. Distribution

- Public: `fawkesdx/ARPESskill` — portable markdown skill; TensorSpec optional.
- Install notes: Cursor, Claude Code, generic agents.
- TensorSpec_GUI remains its own repo/branch; users who want path 2 need that env on `PYTHONPATH` / install.
- MIT on ARPESskill.

## 9. Implementation order

1. Land ARPESskill docs: literacy + PyARPES MAESTRO example + SKILL.md.
2. In TensorSpec_GUI: expose/finish headless load + cut helpers (and conversion stubs/impl as needed) without Qt.
3. Add `tensorspec-gui-bridge.md` + `maestro_tensorspec_gui.md` example to ARPESskill.
4. Dual smoke on one MAESTRO file (PyARPES + TensorSpec_GUI).
5. Publish GitHub + tag when both smokes pass (or tag `v0.1` after PyARPES-only if TensorSpec helpers slip — prefer both for “B”).

## 10. Decisions log

| Decision | Choice |
|----------|--------|
| Scope | General skill + optional TensorSpec_GUI module bridge |
| TensorSpec target | **`TensorSpec_GUI` headless modules**, not HTML/REST |
| Order | PyARPES first, then ensure TensorSpec_GUI callable |
| Viewer | Reuse TensorSpec data model/helpers; GUI later shares same core |
| Conversion | Build in TensorSpec_GUI core when needed; skill calls it |
| Spatial | PyARPES already has XY; `peaks` later for heavy 4D |
| MATLAB | Out |
| License / GitHub | MIT / `fawkesdx/ARPESskill` |

## 11. Clarifications

1. Purpose = general LLM skill; Cursor only one host.
2. “Reduce” = ARPES cuts/maps, not file size.
3. Package bridge = detect and drive user tools.
4. Track B = PyARPES + TensorSpec_GUI modules (not HTML).
5. “Call TensorSpec_GUI” = **import Python modules**, not click the desktop app.
