# ARPESskill

General LLM agent skill for ARPES analysis via **PyARPES**.

**Repo:** https://github.com/fawkesdx/ARPESskill

## What it does

Teaches Cursor / Claude / other agents to reduce ARPES data **without inventing
axes or physics**:

| Step | Skill behavior |
|------|----------------|
| Load | Prefer PyARPES (`load_data` / endstations); FITS-first for MAESTRO |
| Overview | Cut / Fermi / hv trios with stated assumptions |
| Fit | Core then EDC/MDC (Gaussian / Lorentzian / Voigt); package models only |
| k / kz | EF finder + QC; `convert_to_kspace`; hv EF = angle-summed edge + per-hv QC |
| Near-EF | Metal EF, resolution-broadened FD, symmetrize (gap/pseudogap) when asked |
| Spatial XY | ROI-integrated map, hot-spot kind reuse (cut / core / Fermi / hv), optional param maps |
| Spin-ARPES | Up/down or I+P; package spin plots; Sherman ask; Spin-EDC + spin cuts |
| In-operando | External \(P\) (dose/V/I/B/T); mid \(P^*\) or ask if stepped; reuse kind recipes |
| trARPES | `delay`; t0; delay\* ≥ t0; package ΔI / ΔI/I; reuse kind at slice |
| Self-energy | Single-band MDC → Σ (reuse fits or `fit_for_self_energy`); bare band; lifetime ask |
| Band enhance | Curvature + min-gradient side by side (not intensity) |
| Backend | Default PyARPES; optional confirmed map to **your** project functions |

## 60-second try

1. Install skill (below) + PyARPES in a **Python 3.8** venv (agent will ask).
2. Open Cursor chat in a folder with an ARPES file (or PyARPES tutorial data).
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

- **Python 3.8.x** only (PyARPES: `>=3.8,<3.9`)
- Dedicated venv (e.g. `.venv-arpes`) + `pip install arpes` inside it  
  See `reference/pyarpes-env.md` — agent asks before creating it
- Load/inspect fallback only: `xarray`, `h5py`

## What this is not

- Not a replacement for PyARPES — it **drives** PyARPES (or your mapped code)
- Not TensorSpec / Qt GUI control
- Does not ship beamtime data files

## Related tools

- [PyARPES](https://arpes.readthedocs.io) / [GitHub mirror](https://github.com/chstan/arpes)
- Beamline notes in-skill: MAESTRO, ALBA LOREA (incidence defaults); more welcome via PR

## Skill layout

- `SKILL.md` — entry + hard rules  
- `reference/` — workflows  
- `examples/` — short recipes  
- `LICENSE` · `README.md`

## Citation / contact

Sandy Adhitia Ekahana
