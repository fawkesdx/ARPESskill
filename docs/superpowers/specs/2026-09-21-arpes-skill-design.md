# ARPESskill — Design Spec

**Date:** 2026-09-21  
**Status:** Draft for user review  
**Repo (planned):** `https://github.com/fawkesdx/ARPESskill` (public)  
**Related (out of scope for v1):** TensorSpec, ARPESeed — private bridge skill later

## 1. Purpose

ARPESskill is a general Cursor/LLM agent skill for working with ARPES data. It teaches agents how to load, interpret, and lightly reduce photoemission data without inventing axes, units, or physics assumptions.

It is intentionally **not** tied to TensorSpec or ARPESeed. Those integrations ship later as a separate private skill.

## 2. Goals (v1)

1. **Data literacy (primary):** formats, dimension names, units, angle↔momentum caveats.
2. **Light analysis workflow (secondary):** load → inspect → cut → plot, with a safe-reduction checklist.
3. **Failure-mode awareness:** document classic agent mistakes (angle-as-k, hν/kz mixups, silent Γ claims, bogus labels).
4. **Public install:** clone GitHub → install into `~/.cursor/skills/arpes/`.

### Success criteria

With the skill installed, an agent can:

1. Load a common ARPES-like file (or `.npy` stack) without guessing axes.
2. State axes and units before any plot.
3. Produce one Fermi-surface or EDC-style plot with labeled axes.
4. Follow (or explicitly skip with reason) the safe-reduction checklist.
5. Avoid failure modes listed in `reference/failure-modes.md`.

## 3. Non-goals (v1)

- TensorSpec / ARPESeed APIs, model download, or inference wrappers
- Training pipelines or synthetic corpus generation
- Beamline DAQ / instrument control
- Required dependency on heavy fitting stacks
- CI package, pip-installable Python library, or large example datasets
- Notebooks as a required deliverable (optional later as v1.1)

## 4. Approach

**Cursor skill pack** (thin entry + reference files), not a monolith and not a Python package.

Rationale: matches Cursor progressive disclosure, stays editable, ships fast on GitHub, leaves room for a private TensorSpec bridge skill later without bloating the public skill.

## 5. Architecture

### 5.1 Repository layout

```
ARPESskill/
├── README.md
├── LICENSE                 # MIT
├── SKILL.md                # thin entry: triggers, hard rules, workflow, pointers
├── reference/
│   ├── formats-and-axes.md
│   ├── safe-reduction.md
│   └── failure-modes.md
└── examples/
    └── load_and_plot.md
```

### 5.2 File ownership

| File | Responsibility |
|------|----------------|
| `SKILL.md` | When to invoke; non-negotiable rules; ordered workflow; pointers into `reference/` |
| `reference/formats-and-axes.md` | File types, dim names, units, k-conversion caveats |
| `reference/safe-reduction.md` | Load → inspect → cut → plot checklist |
| `reference/failure-modes.md` | Anti-patterns agents invent |
| `examples/load_and_plot.md` | One worked path: PyARPES preferred, xarray fallback |
| `README.md` | Human install + scope; notes private bridge as out of scope |

**Constraint:** `SKILL.md` stays short (~100–200 lines). Detail lives in `reference/`. Agents load reference files only when needed.

### 5.3 Preferred analysis stack

1. **Prefer PyARPES** when available.
2. **Fallback:** xarray + h5py / nexusformat.
3. Agent must state which path it used.

### 5.4 Agent workflow

1. Identify artifact (file type / array shape / existing loader in the project).
2. Lock coordinates (axis names; units ° vs Å⁻¹, eV, hν; binding vs kinetic if relevant).
3. Sanity print (shape, ranges, one mid-cut summary — no silent assumptions).
4. Reduce only after steps 2–3; follow `safe-reduction.md`.
5. Plot/report with labeled units; state assumptions (e.g. Γ location unknown).
6. If unsure: read the matching `reference/` file; ask the user one sharp question.

### 5.5 Hard rules

- Never invent axis names or units.
- Never treat detector angle as momentum without stating conversion and geometry/inner-potential assumptions.
- Never claim “Γ found” without stating method (manual / fit / model).
- Prefer PyARPES; if missing, use xarray path and say so.
- Do not pull TensorSpec/ARPESeed into answers unless the user asks (that belongs to the future private bridge skill).
- Prefer inspecting existing project loaders before writing new ones.

### 5.6 Error handling

- Missing deps → suggest install; offer fallback path.
- Ambiguous axes → stop and ask.
- Corrupt/partial file → report what is readable; do not fabricate values.

## 6. Trigger (SKILL.md frontmatter intent)

Invoke when the task involves ARPES spectra, Fermi surfaces, EDC/MDC, photoemission maps, angle↔momentum conversion, NeXus/HDF5/Igor ARPES files, or PyARPES.

## 7. Testing (v1)

No CI package in v1.

- Manual smoke against 2–3 fixture descriptions in `examples/` (synthetic tiny arrays OK; real paths optional).
- Checklist review against hard rules in §5.5.
- Optional later (v1.1): CI / tiny helper scripts.

## 8. Distribution

- Public GitHub: `fawkesdx/ARPESskill`, default branch `main`.
- Install: clone → copy or symlink to `~/.cursor/skills/arpes/`.
- Tag `v1` after first usable skill content lands.
- Dual-track: private TensorSpec/ARPESeed bridge skill is a **separate** repo/skill, not this one.
- This repo must not contain model weights, large data, or Einstein deploy hooks.

## 9. Implementation order (after this spec is approved)

1. Create public GitHub repo `fawkesdx/ARPESskill`.
2. Author `SKILL.md` + three reference files + one example + README + LICENSE.
3. Local install smoke (`~/.cursor/skills/arpes`).
4. Manual checklist pass against success criteria.
5. Tag `v1` when criteria met.

Detailed task breakdown lives in the implementation plan (next step after user approves this spec).

## 10. Decisions log

| Decision | Choice |
|----------|--------|
| Scope | General ARPES skill first; not TensorSpec-specific |
| Content focus | Data literacy + light analysis workflow |
| Distribution | Public skill repo now; private bridge later |
| Stack | PyARPES preferred; xarray + h5py/nexusformat fallback |
| Done bar | Load + axes/units + plot + checklist + failure modes |
| Shape | Cursor skill pack (thin SKILL.md + references) |
| License | MIT |
| GitHub | `fawkesdx/ARPESskill` |
