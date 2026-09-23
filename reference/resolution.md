# Experimental resolution estimates

**Gate:** user asks resolution / broadening budget, soft X-ray / near-EF needs
a stated width, or FD / EF fits need σ — **not** default overview.

**Docs:** `arpes.analysis.resolution` —
`total_resolution_estimate`, `thermal_broadening_estimate`,
`analyzer_resolution_estimate`, `beamline_resolution_estimate`

Capabilities: `resolution_total`, `resolution_parts` —
`backend-capability-map.md`.

---

## Package reality

- **`total_resolution_estimate`**: quadrature sum of beamline + analyzer
  (+ optional thermal).  
- **Thermal:** from `S.temp` via `thermal_broadening_estimate` — works when T
  is on the data.  
- **Analyzer / beamline tables:** stock PyARPES calibrations are **endstation-
  specific** (notably MERLIN / BL403). Other endstations (MAESTRO, ANTARES, …)
  often **KeyError** / `NotImplementedError` — **do not invent** pass-energy
  formulas. State failure; **ask** user widths or skip that part.

ANTARES: slit is **horizontal, fixed** (`beamline-geometry.md`) — do not assume
rotatable slit settings in resolution discussion.

---

## Recipe

1. Try package helpers; catch missing endstation tables.  
2. Report a **table** of what succeeded:

| Part | API | If missing |
|------|-----|------------|
| Thermal | `thermal_broadening_estimate` | Ask T or skip |
| Analyzer | `analyzer_resolution_estimate` | Ask / skip — no invent |
| Beamline | `beamline_resolution_estimate` | Ask / skip — no invent |
| Total | `total_resolution_estimate` | Only if parts available, or report partial |

3. State units (**eV** vs **meV** — package `meV=` flag).  
4. If used for FD / EF / near-EF (`near-ef-gap.md`): echo which estimate (or
   user σ) entered the fit.  
5. Optional: `include_thermal_broadening=True` on total — **state** on/off.

```python
from arpes.analysis.resolution import (
    total_resolution_estimate,
    thermal_broadening_estimate,
    analyzer_resolution_estimate,
    beamline_resolution_estimate,
)

# Prefer meV=True for readable numbers; state units
# try:
#     dE_th = thermal_broadening_estimate(data, meV=True)
#     dE_an = analyzer_resolution_estimate(data, meV=True)  # may fail
#     dE_bl = beamline_resolution_estimate(data, meV=True)  # may fail
#     dE = total_resolution_estimate(data, include_thermal_broadening=True, meV=True)
# except (KeyError, NotImplementedError, AttributeError) as e:
#     # report which part failed; ask user or use thermal-only
```

---

## Default report

- Parts obtained + total (or partial).  
- Endstation / whether tables existed.  
- Link to geometry slit notes when relevant (e.g. ANTARES fixed horizontal).  
- No silent overwrite of a user-stated resolution.

---

## Do not

- Invent analyzer radius / slit / pass-energy math when package fails.  
- Claim MERLIN tables apply to ANTARES / MAESTRO.  
- Skip stating units.  
- Treat estimate as measured Fermi-edge width without saying so.

---

## Checklist

1. User asked or workflow needs a width.  
2. Tried package; failures stated per part.  
3. Units + thermal-in-total on/off echoed.  
4. Downstream FD/EF uses stated source (estimate vs user).
