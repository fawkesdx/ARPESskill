# ARPESskill — Design Spec

**Date:** 2026-09-21  
**Status:** Revised draft — awaiting user re-review  
**Repo (planned):** `https://github.com/fawkesdx/ARPESskill` (public)  
**Related (out of scope for v1):** TensorSpec, ARPESeed — private bridge skill later

## 1. Purpose

ARPESskill is a **general LLM agent skill** for working with ARPES data. It teaches agents how to load and analyze photoemission data using the known typical axes of ARPES measurements, units, and physics assumptions — without inventing any of those.

It is intentionally **not tied to one analysis package**. The skill is a **bridge**: detect what the user already has (or can install), then drive that stack correctly. For v1 we start with **PyARPES** as the primary Python path (mature, common, good for conventional MAESTRO-style ARPES). If PyARPES is absent, fall back to **xarray + h5py/nexusformat**.

It is also **not** tied to TensorSpec or ARPESeed. Those integrations ship later as a separate private skill.

### What “data reduction” means here

In ARPES, **reduction** does **not** mean “compress the file.” It means turning a raw multidimensional scan into analysis products: energy/momentum cuts, EDC/MDC, Fermi-surface maps, spatial ROIs, etc. v1 covers only the **light** end of that — load, lock axes, one or two standard cuts/plots — not full publication pipelines or heavy many-body fitting.

## 2. Goals (v1)

1. **Data literacy (primary):** formats, dimension names, units, angle↔momentum caveats.
2. **Light analysis workflow (secondary):** load → inspect → cut → plot, with a safe-reduction checklist.
3. **Failure-mode awareness:** classic agent mistakes (angle-as-k, hν/kz mixups, silent Γ claims, bogus labels).
4. **Public, portable install:** clone GitHub; load into whatever agent host the user uses (see §8).

Later goals (not v1): spatial XY / nanoARPES depth, in-operando axes (gate/bias/time), richer package routing (e.g. `peaks`).

### Success criteria

Primary smoke test: **load typical ALS MAESTRO ARPES data and analyze it via the LLM agent** (same jobs usually done in a GUI), without inventing axes.

Also required:

1. State axes and units before any plot.
2. Produce at least one FS- or EDC-style product with labeled axes.
3. Follow (or explicitly skip with reason) the safe-reduction checklist.
4. Avoid failure modes listed in `reference/failure-modes.md`.

## 3. Non-goals (v1)

- TensorSpec / ARPESeed APIs, model download, or inference wrappers
- Training pipelines or synthetic corpus generation
- Beamline DAQ / instrument control
- MATLAB control (works for one lab, not general — out of public skill)
- Required dependency on heavy fitting stacks
- CI package, pip-installable Python library, or large example datasets checked into git
- Notebooks as a required deliverable (optional later)
- Full nanoARPES / in-operando workflows (documented as future; package pointers only)

## 4. Approach

**Portable agent-skill pack:** thin `SKILL.md` entry + `reference/` + `examples/`. Content is markdown knowledge and workflow; packaging targets multiple hosts.

Rationale: ships fast on GitHub; progressive disclosure; package-agnostic bridge; same files usable beyond a single IDE.

### Package strategy

| Situation | Prefer |
|-----------|--------|
| Conventional ARPES / MAESTRO (v1 default) | **PyARPES** |
| PyARPES missing | **xarray + h5py/nexusformat** |
| Spatially resolved XY / nanoARPES / large 4D (later) | **`peaks` (`peaks-arpes`)** — strong ROI / spatial / lazy 4D support |
| In-operando extra axes (gate, current, time) | Same stacks as xarray datasets; skill must treat extra dims as first-class later — not v1 depth |

v1 implements the PyARPES (+ xarray fallback) path well. `peaks` is named in docs as the better spatial/nano route when those dims appear; deep `peaks` recipes = post-v1.

## 5. Architecture

### 5.1 Repository layout

```
ARPESskill/
├── README.md                 # install for multiple agent hosts + scope
├── LICENSE                   # MIT
├── SKILL.md                  # thin entry: triggers, hard rules, workflow, pointers
├── reference/
│   ├── formats-and-axes.md   # include MAESTRO / NeXus notes
│   ├── safe-reduction.md
│   └── failure-modes.md
└── examples/
    └── maestro_load_and_analyze.md
```

### 5.2 File ownership

| File | Responsibility |
|------|----------------|
| `SKILL.md` | When to invoke; hard rules; ordered workflow; package-bridge policy; pointers |
| `reference/formats-and-axes.md` | File types, dim names, units, k-conversion; MAESTRO notes |
| `reference/safe-reduction.md` | Load → inspect → cut → plot checklist |
| `reference/failure-modes.md` | Anti-patterns agents invent |
| `examples/maestro_load_and_analyze.md` | Worked MAESTRO path: PyARPES + xarray fallback |
| `README.md` | Human install for Cursor, Claude Code, and generic agents |

**Constraint:** `SKILL.md` stays short (~100–200 lines). Detail lives in `reference/`.

### 5.3 Package bridge (hard policy)

1. Detect what is available in the user’s environment / project.
2. Prefer PyARPES for v1 MAESTRO workflows when present.
3. Else xarray + h5py/nexusformat.
4. Always state which path was used.
5. Do not invent a new analysis framework; drive existing tools.

### 5.4 Agent workflow

1. Identify artifact (MAESTRO/NeXus/HDF5/Igor/array; existing loaders in the project).
2. Lock coordinates (axis names; units ° vs Å⁻¹, eV, hν; binding vs kinetic if relevant).
3. Sanity print (shape, ranges, one mid-cut summary — no silent assumptions).
4. Reduce (light cuts only) after steps 2–3; follow `safe-reduction.md`.
5. Plot/report with labeled units; state assumptions (e.g. Γ location unknown).
6. If unsure: read matching `reference/` file; ask one sharp question.

### 5.5 Hard rules

- Never invent axis names or units.
- Never treat detector angle as momentum without stating conversion and geometry/inner-potential assumptions.
- Never claim “Γ found” without stating method (manual / fit / model).
- Bridge to available packages; do not require a single global install.
- Do not pull TensorSpec/ARPESeed unless the user asks.
- Prefer inspecting existing project loaders before writing new ones.

### 5.6 Error handling

- Missing deps → suggest install; offer fallback path.
- Ambiguous axes → stop and ask.
- Corrupt/partial file → report what is readable; do not fabricate values.

## 6. Trigger (SKILL.md frontmatter intent)

Invoke when the task involves ARPES spectra, Fermi surfaces, EDC/MDC, photoemission maps, angle↔momentum conversion, MAESTRO/NeXus/HDF5/Igor ARPES files, PyARPES, or related analysis packages.

## 7. Testing (v1)

No CI package in v1.

- **Primary:** manual smoke on a typical MAESTRO dataset (user-provided path; not committed to git if large).
- Checklist review against hard rules in §5.5.
- Optional later (v1.1): CI / tiny synthetic fixtures / `peaks` spatial example.

## 8. Distribution & portability

**Content is host-agnostic** (markdown skill + references). The `SKILL.md` + folder layout follows the emerging **Agent Skills** convention used by Cursor and compatible with other skill-loading agents.

| Host | How users load it |
|------|-------------------|
| Cursor | Clone/symlink → `~/.cursor/skills/arpes/` (or project `.cursor/skills/`) |
| Claude Code | Install into that product’s skills directory (document exact path in README; same files) |
| Other LLM agents | Point the agent at the repo / paste `SKILL.md` + needed `reference/` into context, or use that host’s “custom instructions / skill” mechanism |

Public GitHub: `fawkesdx/ARPESskill`, branch `main`, MIT, tag `v1` when MAESTRO smoke passes.

Dual-track: private TensorSpec/ARPESeed bridge = separate skill later.

No model weights, large MAESTRO files, or Einstein hooks in this repo.

## 9. Implementation order (after this revision is approved)

1. Create public GitHub repo `fawkesdx/ARPESskill`.
2. Author `SKILL.md` + three reference files + MAESTRO example + multi-host README + LICENSE.
3. Local install smoke on at least one host (Cursor and/or Claude Code).
4. Manual MAESTRO load + analyze pass against success criteria.
5. Tag `v1` when criteria met.

## 10. Decisions log

| Decision | Choice |
|----------|--------|
| Scope | General ARPES LLM skill; package bridge, not package lock-in |
| Wording | No Cursor-only purpose; Cursor is one install target |
| Content focus | Data literacy + light data reduction (cuts/plots) |
| Primary smoke | Typical MAESTRO data via agent (not GUI) |
| Stack v1 | PyARPES preferred; xarray fallback |
| Spatial / operando | Document `peaks` as better later path; not v1 depth |
| MATLAB | Out of public general skill |
| Distribution | Public skill repo; portable markdown; multi-host README |
| Shape | Thin SKILL.md + references + examples |
| License | MIT |
| GitHub | `fawkesdx/ARPESskill` |

## 11. Clarifications (from review)

1. **Why “Cursor” before?** Only because the brainstorm started in Cursor. Purpose is general LLM agents; Cursor is one loader.
2. **“Lightly reduce”** = light ARPES data reduction (cuts/maps), not file compression.
3. **Package philosophy** = bridge to user’s tools; start PyARPES; `peaks` suggested for spatial/nano later.
4. **Other LLMs** = yes — same files; README documents install per host. Skill body is not Cursor API code.
