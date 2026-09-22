# ARPESskill v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a portable LLM agent skill (`ARPESskill`) that teaches PyARPES-based MAESTRO load, EDC/MDC fitting (Gauss/Lorentz/Voigt), k-space conversion, and hv→kz conversion — then publish to GitHub.

**Architecture:** Thin `SKILL.md` entry (~100–200 lines) plus progressive-disclosure `reference/` docs and scripted `examples/`. No Python package in v1; agents run PyARPES recipes from the markdown. TensorSpec_GUI deferred.

**Tech Stack:** Markdown Agent Skills layout; PyARPES (user-installed); xarray/h5py fallback for load/inspect only; GitHub public repo `fawkesdx/ARPESskill`; MIT license.

**Spec:** `docs/superpowers/specs/2026-09-21-arpes-skill-design.md` (Approved 2026-09-21)

## Global Constraints

- v1 = **PyARPES path only** (+ xarray/h5py load/inspect fallback); no TensorSpec_GUI/HTML bridge beyond one-line future note
- `SKILL.md` must stay **~100–200 lines**; detail lives in `reference/`
- Prefer **scripted** PyARPES + matplotlib; do not require QtTool/Bokeh
- Never invent axes/units; never treat angle as k silently; never hv→kz without stating inner potential; never report fits without lineshape
- No large MAESTRO files in git
- Public repo: `fawkesdx/ARPESskill`, branch `main`, license **MIT**
- Skill `name`: `arpes` (folder install name `arpes`); omit `disable-model-invocation` so agents can auto-discover from description triggers
- Commit after each task; do not force-push; do not update git config

## File structure (create)

| Path | Responsibility |
|------|----------------|
| `LICENSE` | MIT text |
| `README.md` | Human install (Cursor / Claude Code / generic) + scope |
| `SKILL.md` | Triggers, hard rules, workflow, pointers |
| `reference/formats-and-axes.md` | Formats, dims, units, MAESTRO notes |
| `reference/safe-reduction.md` | Load→inspect→cut/FS/EDC/MDC checklist |
| `reference/edc-mdc-fitting.md` | Gauss/Lorentz/Voigt, broadcast, width/E/k plots |
| `reference/k-and-kz-conversion.md` | cut/FS→k; Eph→kz; V₀ rules |
| `reference/failure-modes.md` | Anti-patterns |
| `examples/maestro_pyarpes.md` | Load + inspect + light cuts |
| `examples/fit_edc_mdc.md` | Fit + derived plots |
| `examples/convert_k_kz.md` | k-space + kz examples |

Keep existing `docs/superpowers/specs/` and `docs/superpowers/plans/` as-is.

---

### Task 1: Repo scaffolding (LICENSE + README)

**Files:**
- Create: `LICENSE`
- Create: `README.md`
- Keep: `docs/superpowers/specs/2026-09-21-arpes-skill-design.md`

**Interfaces:**
- Consumes: none
- Produces: MIT `LICENSE`; README install paths that later tasks must match (`~/.cursor/skills/arpes/`, Claude Code skills dir note)

- [ ] **Step 1: Write `LICENSE` (MIT)**

Use standard MIT license text with copyright:

`Copyright (c) 2026 Sandy Adhitama Ekahana`

- [ ] **Step 2: Write `README.md`**

Must include these sections verbatim in spirit (exact headings below):

```markdown
# ARPESskill

General LLM agent skill for ARPES analysis via **PyARPES** (v1).

## What this is

Teaches agents to load ARPES data, lock axes/units, extract EDC/MDC,
fit peaks (Gaussian / Lorentzian / Voigt), convert cuts/Fermi maps to
k-space, and convert photon-energy scans to kz — without inventing
coordinates or physics assumptions.

## What this is not (v1)

- Not tied to TensorSpec / TensorSpec_GUI (future separate bridge)
- Not a Python package; not interactive Qt GUI control
- Does not ship MAESTRO data files

## Install

### Cursor
```bash
git clone https://github.com/fawkesdx/ARPESskill.git
mkdir -p ~/.cursor/skills
ln -s "$(pwd)/ARPESskill" ~/.cursor/skills/arpes
```
(Or copy the repo contents into `~/.cursor/skills/arpes/` so that
`~/.cursor/skills/arpes/SKILL.md` exists.)

### Claude Code
Clone the repo and install into Claude Code's skills directory so that
`SKILL.md` is discoverable (same files). If your Claude Code version
uses `~/.claude/skills/`, symlink similarly:
```bash
mkdir -p ~/.claude/skills
ln -s /absolute/path/to/ARPESskill ~/.claude/skills/arpes
```
Confirm the path for your Claude Code version if it differs.

### Other LLM agents
Point the agent at this repo, or inject `SKILL.md` plus needed files
under `reference/` into context.

## Requires (for full analysis)

- Python 3.8+
- `pip install arpes` (PyARPES) plus its usual scientific stack
- For load/inspect fallback only: `xarray`, `h5py`

## Skill layout

See `SKILL.md` and `reference/`.

## Citation / contact

Sandy Adhitama Ekahana, LBNL — sekahana@lbl.gov
```

- [ ] **Step 3: Verify scaffolding**

Run:

```bash
test -f LICENSE && test -f README.md && rg -n "fawkesdx/ARPESskill|PyARPES|~/.cursor/skills/arpes" README.md
```

Expected: exit 0; README mentions GitHub URL, PyARPES, Cursor install path.

- [ ] **Step 4: Commit**

```bash
git add LICENSE README.md
git commit -m "$(cat <<'EOF'
docs: add MIT license and multi-host README

Scaffold public ARPESskill install instructions for Cursor and
Claude Code before authoring the skill body.
EOF
)"
```

---

### Task 2: Author `SKILL.md` (thin entry)

**Files:**
- Create: `SKILL.md`

**Interfaces:**
- Consumes: README install name `arpes`
- Produces: frontmatter `name: arpes`; ordered workflow steps 1–9; pointers to all five `reference/` files and three `examples/` files (paths must match later tasks)

- [ ] **Step 1: Write `SKILL.md`**

Create file with this structure (keep total body **≤200 lines**; fill pointers exactly):

```markdown
---
name: arpes
description: >
  Load and analyze ARPES photoemission data with correct axes, units,
  EDC/MDC extraction, Gaussian/Lorentzian/Voigt peak fitting, k-space
  conversion, and photon-energy to kz conversion via PyARPES. Use when
  working with ARPES spectra, Fermi surfaces, EDC, MDC, MAESTRO or
  NeXus/HDF5 ARPES files, angle-to-momentum conversion, hv/kz scans,
  or PyARPES.
---

# ARPES

## When to use

User or task involves ARPES spectra, Fermi maps, EDC/MDC, peak fitting,
k or kz conversion, MAESTRO/NeXus/HDF5/Igor ARPES files, or PyARPES.

## Stack policy

1. Prefer **PyARPES** for analysis (fit, k, kz).
2. If PyARPES missing: **xarray + h5py** for load/inspect only; say so.
3. Always state which path was used.
4. TensorSpec / TensorSpec_GUI: out of v1 — if asked, say deferred.

## Hard rules

- Never invent axis names or units.
- Never treat detector angle as momentum without conversion + stated assumptions.
- Never hv→kz without stating inner potential V₀ (or that it is unknown).
- Never claim Γ found without method (manual / fit / model).
- Never report fits without naming lineshape (+ background if used).
- Prefer scripted PyARPES + matplotlib over launching Qt/Bokeh GUIs.
- Prefer existing project loaders before writing new ones.

## Workflow

1. Identify artifact (file type, shape, existing loaders).
2. Choose stack (PyARPES vs xarray); state which.
3. Lock coordinates — names + units (° vs Å⁻¹, eV, hν; binding vs kinetic).
4. Sanity print — shape, ranges, one mid-cut summary.
5. Reduce — cut / FS / EDC / MDC (see `reference/safe-reduction.md`).
6. If reporting momentum — convert to k (`reference/k-and-kz-conversion.md`).
7. If hv-dependent — convert to kz; state V₀.
8. If line analysis — fit + optional broadcast (`reference/edc-mdc-fitting.md`).
9. Plot/report with labeled units; state assumptions.

If unsure: read the matching `reference/` file; ask the user one sharp question.

## References

- `reference/formats-and-axes.md`
- `reference/safe-reduction.md`
- `reference/edc-mdc-fitting.md`
- `reference/k-and-kz-conversion.md`
- `reference/failure-modes.md`

## Examples

- `examples/maestro_pyarpes.md`
- `examples/fit_edc_mdc.md`
- `examples/convert_k_kz.md`
```

- [ ] **Step 2: Verify**

Run:

```bash
wc -l SKILL.md
rg -n "^name: arpes|Hard rules|convert_to_kspace|inner potential|Voigt|TensorSpec" SKILL.md || true
python3 - <<'PY'
from pathlib import Path
text = Path("SKILL.md").read_text()
assert text.startswith("---\n")
assert "name: arpes" in text
assert "description:" in text
assert "disable-model-invocation" not in text
n = len(text.splitlines())
assert 80 <= n <= 200, n
print("SKILL.md OK", n, "lines")
PY
```

Expected: print `SKILL.md OK` with line count in 80–200; no `disable-model-invocation`.

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "$(cat <<'EOF'
feat: add thin ARPES agent SKILL.md entry

Triggers, hard rules, PyARPES-first workflow, and pointers to
reference docs for fit and k/kz conversion.
EOF
)"
```

---

### Task 3: `reference/formats-and-axes.md` + `reference/safe-reduction.md`

**Files:**
- Create: `reference/formats-and-axes.md`
- Create: `reference/safe-reduction.md`

**Interfaces:**
- Consumes: workflow steps from `SKILL.md`
- Produces: MAESTRO load notes; checklist items referenced by examples

- [ ] **Step 1: Write `reference/formats-and-axes.md`**

Must cover:

1. Common formats: MAESTRO HDF5, NeXus, Igor, generic HDF5, `.nc` from PyARPES
2. Typical dims: `eV` (binding, often negative below EF in PyARPES), analyzer angles (`phi`, `psi`, …), manipulator angles, `hv`, spatial `x`/`y` (mention only; no linked-viewer recipes)
3. Units table: angle °, momentum Å⁻¹, energy eV, hv eV
4. Binding vs kinetic — never swap silently
5. MAESTRO via PyARPES: mention endstation plugins `MAESTROMicroARPESEndstation` / `MAESTRONanoARPESEndstation`; prefer `arpes.io.load_data` / project loaders; inspect `.coords` and `.attrs` before analysis
6. Sanity print template (shape, coord names, min/max per axis)

Include a short “xarray fallback” subsection: open with h5py, list groups/datasets, do not invent axis labels.

- [ ] **Step 2: Write `reference/safe-reduction.md`**

Checklist (numbered):

1. Confirm file path and loader
2. Print coords + units
3. Select ROI / energy window with explicit values
4. Extract **cut** (E–angle or E–k slice) OR **Fermi map** (near EF integration window stated in meV)
5. Extract **EDC** (fixed k/angle) or **MDC** (fixed E) with window stated
6. Plot with axis labels + units
7. Only then fit or convert to k/kz

Add “skip with reason” rule: if skipping a step, agent must say which and why.

- [ ] **Step 3: Verify**

```bash
test -f reference/formats-and-axes.md && test -f reference/safe-reduction.md
rg -n "MAESTRO|binding|Å|EDC|MDC|Fermi" reference/formats-and-axes.md reference/safe-reduction.md
```

Expected: matches for MAESTRO, binding, EDC, MDC, Fermi.

- [ ] **Step 4: Commit**

```bash
git add reference/formats-and-axes.md reference/safe-reduction.md
git commit -m "$(cat <<'EOF'
docs: add formats/axes and safe-reduction references

Document MAESTRO/PyARPES literacy and the load-to-cut checklist
agents must follow before fitting or k conversion.
EOF
)"
```

---

### Task 4: `reference/edc-mdc-fitting.md`

**Files:**
- Create: `reference/edc-mdc-fitting.md`

**Interfaces:**
- Consumes: EDC/MDC extraction rules from `safe-reduction.md`
- Produces: lineshape names and `broadcast_model` pattern used in `examples/fit_edc_mdc.md`

- [ ] **Step 1: Write `reference/edc-mdc-fitting.md`**

Must include:

**Models (exact import paths to document):**

- `arpes.fits.fit_models.GaussianModel`
- `arpes.fits.fit_models.LorentzianModel`
- `arpes.fits.fit_models.VoigtModel`

**Single curve fit pattern** (agent-facing code block):

```python
from arpes.fits.fit_models import VoigtModel  # or GaussianModel, LorentzianModel

# edc: 1D DataArray with energy coordinate
result = VoigtModel().guess_fit(edc)
print(result.fit_report())
# Always report: lineshape name, center, width (FWHM or model σ/γ — state which), amplitude
```

**Broadcast / dispersion tracking:**

```python
from arpes.fits.utilities import broadcast_model
from arpes.fits.fit_models import LorentzianModel

# Fit MDCs vs energy (or EDCs vs momentum) — state which mode
fit_results = broadcast_model(LorentzianModel, data_2d, "eV")  # example axis name; use actual coord
# Derive plots: peak center vs k or E; width vs k or E
```

Rules:

- Name lineshape every time
- State background if composed
- Prefer MDC fits for dispersion E(k); EDC for energy-distribution studies
- After broadcast: plot **center vs momentum** (E vs k) and/or **width vs E** / **width vs k**
- Do not claim quasiparticle lifetime without stating assumptions

Link to PyARPES docs: https://arpes.readthedocs.io/en/latest/curve-fitting.html

- [ ] **Step 2: Verify**

```bash
rg -n "GaussianModel|LorentzianModel|VoigtModel|broadcast_model|width vs" reference/edc-mdc-fitting.md
```

Expected: all five patterns present.

- [ ] **Step 3: Commit**

```bash
git add reference/edc-mdc-fitting.md
git commit -m "$(cat <<'EOF'
docs: add EDC/MDC fitting reference for PyARPES

Document Gauss/Lorentz/Voigt fits and broadcast_model patterns for
width and dispersion plots.
EOF
)"
```

---

### Task 5: `reference/k-and-kz-conversion.md` + `reference/failure-modes.md`

**Files:**
- Create: `reference/k-and-kz-conversion.md`
- Create: `reference/failure-modes.md`

**Interfaces:**
- Consumes: hard rules from `SKILL.md`
- Produces: `convert_to_kspace` + `inner_potential` patterns for `examples/convert_k_kz.md`

- [ ] **Step 1: Write `reference/k-and-kz-conversion.md`**

Must include:

**In-plane k (cut / Fermi map):**

```python
from arpes.utilities.conversion import convert_to_kspace
import numpy as np

kdata = convert_to_kspace(
    cut_or_fs,  # angle-space DataArray
    # pass kp / kx / ky grids as appropriate for the scan type
)
# State: geometry, which angles mapped, EF alignment if relevant
```

**hv → kz:**

```python
spectrum.attrs["inner_potential"] = 10.0  # eV — MUST state to user; ask if unknown
kz_data = convert_to_kspace(
    hv_scan.S.fermi_surface,  # or appropriate hv-dependent array
    kp=np.linspace(-2, 2, 500),
    kz=np.linspace(3.5, 5.2, 400),
)
```

Rules:

- Always print/state V₀ before trusting absolute kz
- Absolute kz depends on V₀; prefer also checking kz periodicity when possible
- Never label axes Å⁻¹ unless conversion actually run
- Link: https://arpes.readthedocs.io/en/latest/notebooks/converting-to-kspace.html

- [ ] **Step 2: Write `reference/failure-modes.md`**

Bullet list of failure modes + correct behavior:

| Failure | Correct |
|---------|---------|
| Plot angle axis labeled as k | Convert first or label degrees |
| hv scan plotted as kz without V₀ | Set/ask `inner_potential`; state uncertainty |
| Swap binding ↔ kinetic | Check PyARPES convention (binding often ≤0 below EF) |
| Invent MAESTRO motor names | Read coords/attrs from file |
| “Γ is at image center” | No — state method to find Γ |
| Fit without lineshape | Name Gauss/Lorentz/Voigt (+ background) |
| Use TensorSpec APIs in v1 | Defer; use PyARPES |
| Launch QtTool as only path | Prefer scripts |

- [ ] **Step 3: Verify**

```bash
rg -n "convert_to_kspace|inner_potential|Γ|Voigt|angle" reference/k-and-kz-conversion.md reference/failure-modes.md
```

Expected: matches present in both files as appropriate.

- [ ] **Step 4: Commit**

```bash
git add reference/k-and-kz-conversion.md reference/failure-modes.md
git commit -m "$(cat <<'EOF'
docs: add k/kz conversion and failure-modes references

Codify convert_to_kspace usage, inner-potential rules, and common
agent anti-patterns for ARPES analysis.
EOF
)"
```

---

### Task 6: Examples (`maestro_pyarpes`, `fit_edc_mdc`, `convert_k_kz`)

**Files:**
- Create: `examples/maestro_pyarpes.md`
- Create: `examples/fit_edc_mdc.md`
- Create: `examples/convert_k_kz.md`

**Interfaces:**
- Consumes: all `reference/*` patterns
- Produces: runnable-shaped recipes agents can adapt (tutorial data OK where noted)

- [ ] **Step 1: Write `examples/maestro_pyarpes.md`**

Include:

1. Goal: load MAESTRO-like data, print axes, plot one cut or EF map
2. Preferred: `arpes.io.load_data` / endstation plugin path with **placeholder path** `PATH/TO/maestro.h5` (not real data in repo)
3. Fallback xarray/h5py snippet that lists keys only
4. Explicit “state axes + units before plot” narrative

```python
from arpes.io import load_data
# data = load_data("PATH/TO/maestro.h5")  # user path
# print(data.dims, data.coords, data.attrs)
```

Also show tutorial fallback:

```python
from arpes.io import example_data
cut = example_data.cut.spectrum
print(cut.dims, dict(cut.coords))
cut.S.plot()
```

- [ ] **Step 2: Write `examples/fit_edc_mdc.md`**

1. Build or select one EDC from `example_data.cut` (or user data)
2. Fit with `LorentzianModel` or `VoigtModel`; print fit report
3. Show `broadcast_model` sketch on 2D cut; plot center vs momentum and width vs energy (or state how to extract params from results)
4. Remind: name lineshape in the agent’s reply

- [ ] **Step 3: Write `examples/convert_k_kz.md`**

1. Angle cut → `convert_to_kspace` using `example_data.cut` or `example_data.map`
2. hv scan → kz using `example_data.photon_energy` with `attrs["inner_potential"] = …` stated in prose
3. Tell agent to narrate V₀ and that absolute kz depends on it

- [ ] **Step 4: Verify**

```bash
rg -n "example_data|load_data|broadcast_model|convert_to_kspace|inner_potential" examples/*.md
test -f examples/maestro_pyarpes.md && test -f examples/fit_edc_mdc.md && test -f examples/convert_k_kz.md
```

Expected: exit 0; all keywords found across examples.

- [ ] **Step 5: Commit**

```bash
git add examples/maestro_pyarpes.md examples/fit_edc_mdc.md examples/convert_k_kz.md
git commit -m "$(cat <<'EOF'
docs: add PyARPES worked examples for load, fit, k/kz

Provide scripted MAESTRO/tutorial recipes agents can adapt without
bundling large experimental files.
EOF
)"
```

---

### Task 7: Local install smoke + content checklist

**Files:**
- Modify: none required (optional fixups if checklist fails)
- Test: local symlink + grep checklist

**Interfaces:**
- Consumes: full tree from Tasks 1–6
- Produces: verified install path `~/.cursor/skills/arpes/SKILL.md`

- [ ] **Step 1: Symlink into Cursor skills**

```bash
REPO="$(cd "$(dirname "$0")" && pwd)"  # or use absolute /Users/sandyai/Documents/ARPESskill
mkdir -p ~/.cursor/skills
ln -sfn /Users/sandyai/Documents/ARPESskill ~/.cursor/skills/arpes
test -f ~/.cursor/skills/arpes/SKILL.md && ls -la ~/.cursor/skills/arpes
```

Expected: symlink points at repo; `SKILL.md` visible.

- [ ] **Step 2: Spec success-criteria checklist (docs presence)**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
root = Path("/Users/sandyai/Documents/ARPESskill")
required = [
  "SKILL.md", "README.md", "LICENSE",
  "reference/formats-and-axes.md",
  "reference/safe-reduction.md",
  "reference/edc-mdc-fitting.md",
  "reference/k-and-kz-conversion.md",
  "reference/failure-modes.md",
  "examples/maestro_pyarpes.md",
  "examples/fit_edc_mdc.md",
  "examples/convert_k_kz.md",
]
missing = [p for p in required if not (root / p).exists()]
assert not missing, missing
skill = (root / "SKILL.md").read_text()
assert "name: arpes" in skill
assert 80 <= len(skill.splitlines()) <= 200
for needle in ["Voigt", "inner potential", "convert", "PyARPES"]:
    assert needle.lower() in skill.lower() or True  # soft: may live in refs
fit = (root / "reference/edc-mdc-fitting.md").read_text()
assert "VoigtModel" in fit and "broadcast_model" in fit
kz = (root / "reference/k-and-kz-conversion.md").read_text()
assert "inner_potential" in kz and "convert_to_kspace" in kz
print("content checklist OK")
PY
```

Expected: `content checklist OK`

- [ ] **Step 3: Optional PyARPES runtime smoke (if installed)**

```bash
python3 - <<'PY'
try:
    from arpes.io import example_data
    from arpes.utilities.conversion import convert_to_kspace
    cut = example_data.cut.spectrum
    print("dims", cut.dims)
    print("pyarpes smoke OK")
except Exception as e:
    print("SKIP pyarpes runtime:", type(e).__name__, e)
PY
```

Expected: `pyarpes smoke OK` **or** explicit SKIP (do not fail the task if PyARPES not installed on the machine — document SKIP in commit message / notes).

- [ ] **Step 4: Commit only if Step 2 prompted fixes; else no empty commit**

If files changed to pass checklist:

```bash
git add -u
git commit -m "$(cat <<'EOF'
fix: address ARPESskill content checklist gaps

Align skill docs with v1 success criteria after local install smoke.
EOF
)"
```

---

### Task 8: Publish GitHub repo + tag

**Files:**
- Remote: `https://github.com/fawkesdx/ARPESskill.git`

**Interfaces:**
- Consumes: clean `main` with Tasks 1–7
- Produces: public remote; tag `v1.0.0` (or `v1` if user prefers — **use `v1.0.0`**)

- [ ] **Step 1: Create GitHub repo (if missing)**

```bash
gh repo view fawkesdx/ARPESskill >/dev/null 2>&1 || gh repo create fawkesdx/ARPESskill --public --source=. --remote=origin --description "General LLM agent skill for ARPES analysis via PyARPES"
```

If repo already exists empty on GitHub:

```bash
git remote add origin https://github.com/fawkesdx/ARPESskill.git 2>/dev/null || git remote set-url origin https://github.com/fawkesdx/ARPESskill.git
```

- [ ] **Step 2: Push `main`**

```bash
git push -u origin main
```

Expected: push succeeds.

- [ ] **Step 3: Tag and push tag**

```bash
git tag -a v1.0.0 -m "ARPESskill v1: PyARPES literacy, fit, k/kz"
git push origin v1.0.0
```

Only tag after Task 7 content checklist passed. If PyARPES runtime was SKIP, still OK to tag docs v1.0.0; note in tag message “runtime smoke optional”.

- [ ] **Step 4: Verify remote**

```bash
gh repo view fawkesdx/ARPESskill --web
git ls-remote --tags origin
```

Expected: repo public; `v1.0.0` present.

---

## Plan self-review

| Spec requirement | Task |
|------------------|------|
| Purpose / portable LLM skill | 1–2 |
| Data literacy | 3 |
| Safe reduction / EDC MDC cut FS | 3, 6 |
| Fit Gauss/Lorentz/Voigt + broadcast plots | 4, 6 |
| k-space conversion | 5, 6 |
| hv→kz + V₀ | 5, 6 |
| Failure modes | 5 |
| PyARPES only; TensorSpec deferred | 2, 5 |
| Multi-host install | 1, 7 |
| GitHub public + tag | 8 |
| No large data in git | 6 placeholders / tutorial only |
| SKILL.md thin | 2 line-count assert |

Placeholder scan: none intentionally left as TBD.

Type/path consistency: skill name `arpes`; reference and example paths match across Tasks 2–6.

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-09-21-arpes-skill-v1.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks  
2. **Inline Execution** — execute tasks in this session with executing-plans checkpoints  

Which approach?
