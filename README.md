# ARPESskill

General LLM agent skill for ARPES analysis. **Adapts to different user
routines**: PyARPES and/or [ARPES-data-browser](https://github.com/DingPei1995/ARPES-data-browser),
folder triage vs single-file work, scripted analysis or GUI on ask — without
inventing axes or physics.

**Repo:** https://github.com/fawkesdx/ARPESskill

## What it does

Teaches Cursor / Claude / other agents to reduce ARPES data **without inventing
axes or physics**:

| Step | Skill behavior |
|------|----------------|
| Load | Route by file/beamline: MAESTRO/ALS FITS → PyARPES; ANTARES/CASSIOPEE → ARPES-data-browser; override OK |
| Overview | Cut / Fermi / hv trios with stated assumptions |
| Fit | Core then EDC/MDC (Gaussian / Lorentzian / Voigt); mapped package models |
| k / kz | EF + slit-bend if needed; mapped convert; hv EF = backend path; V₀ = user/lit/scan/relative |
| Near-EF | Metal EF, resolution-broadened FD, symmetrize (gap/pseudogap) when asked |
| Spatial XY | ROI-integrated map, hot-spot kind reuse (cut / core / Fermi / hv), optional param maps |
| Spin-ARPES | Up/down or I+P; package spin plots; Sherman ask; Spin-EDC and spin cuts |
| In-operando | External \(P\) (dose/V/I/B/T); mid \(P^*\) or ask if stepped; reuse kind recipes |
| trARPES | `delay`; t0; delay\* ≥ t0; package ΔI / ΔI/I; reuse kind at slice |
| Self-energy | Single-band MDC → Σ (reuse fits or `fit_for_self_energy`); bare band; lifetime ask |
| Band enhance | Curvature + min-gradient side by side (not intensity) |
| FS pocket | One closed sheet; center = user or `pocket_parameters`; curves; EDCs ask |
| Smooth / deconvolve | Gaussian smooth for noise; RL/ICE only if asked + PSF |
| Resolution | Package ΔE estimates; ask if endstation tables missing |
| Backgrounds | Core→Shirley; valence→hull; above-EF incoherent ask |
| BZ overlay | Prefer k-space; user cell wins; graphene/ws2/wse2; optional moiré (viewer); ase optional |
| Axis prep | Rebin / symmetrize / normalize_dim / sort / condense (user-asked) |
| Masks | Boolean `.where` or polygon `apply_mask`; GUI ask only |
| Align | Correlation offset (`align`); ask before apply; not stitch |
| Decomposition | PCA / NMF / ICA / factor analysis (`*_along` on PyARPES); ask before large cubes |
| Stack plots | Offset / flat stack; false-color; ToF±σ if errors exist |
| Forward k | Point/pair angular → k-cut; `convert_coordinate_forward` |
| Dichroism | CP+CM; null-ROI scale; diff + asym; red+/blue− clim tweak |
| De-grid | MCP/mesh via viewer `tools.degrid`; pixel-locked; **before** k |
| Pub figure | Journal mm presets / multi-panel (`tools.figure`); user-asked layout |
| Backend | `pyarpes` \| `arpes_viewer` \| confirmed **user-map**; missing fn → ask A/B/C/D |

## 60-second try

1. Install skill (below) + a backend env (agent will ask): PyARPES **3.8** and/or
   ARPES-data-browser **≥3.9**.
2. Open Cursor chat in a folder with an ARPES file (or tutorial data).
3. Ask: *“Load this spectrum with the ARPES skill; state axes; show the default overview.”*

Demo GIF / screenshots: coming soon under `examples/demo/` (load → overview → k).

## Install

### Cursor
```bash
git clone https://github.com/fawkesdx/ARPESskill.git
mkdir -p ~/.cursor/skills
ln -s "$(pwd)/ARPESskill" ~/.cursor/skills/arpes
```
(Or copy the repo so `~/.cursor/skills/arpes/SKILL.md` exists.)

### Claude Code
```bash
mkdir -p ~/.claude/skills
ln -s /absolute/path/to/ARPESskill ~/.claude/skills/arpes
```
Confirm the skills path for your Claude Code version if it differs.

### Other LLM agents
Point the agent at this repo, or inject `SKILL.md` plus needed files under
`reference/` into context.

## Requires (full analysis)

- **PyARPES path:** Python **3.8.x** + shared env — `reference/pyarpes-env.md`
- **ARPES-data-browser path:** Python **≥3.9** + clone on `PYTHONPATH` —
  `reference/arpes-viewer-env.md` (separate env; do not mix with 3.8)
- Load/inspect fallback only: `xarray`, `h5py`

## What this is not

- Not a replacement for PyARPES or ARPES-data-browser — it **drives** them
  (or your mapped code)
- Not the first ARPES agent skill (see related tools)
- Not TensorSpec control
- Does not ship beamtime data files

## Related tools

- [PyARPES](https://arpes.readthedocs.io) / [GitHub mirror](https://github.com/chstan/arpes)
- [ARPES-data-browser](https://github.com/DingPei1995/ARPES-data-browser) (SOLEIL ANTARES / CASSIOPEE)
- [ERLabPy `arpes-analysis` skill](https://github.com/kmnhan/erlabpy/tree/main/skills/arpes-analysis) — related agent skill on ERLabPy
- Beamline notes in-skill: MAESTRO, ALBA LOREA (55°); SOLEIL ANTARES (45°, fixed
  horizontal slit); more welcome via PR

## Skill layout

- `SKILL.md` — entry + hard rules  
- `reference/` — workflows  
- `examples/` — short recipes  
- `LICENSE` · `README.md`

## Citation / contact

Sandy Adhitia Ekahana
