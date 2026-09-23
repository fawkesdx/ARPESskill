# Example: resolution estimates

Follow `reference/resolution.md`.

```python
from arpes.analysis.resolution import (
    total_resolution_estimate,
    thermal_broadening_estimate,
    analyzer_resolution_estimate,
    beamline_resolution_estimate,
)

# Thermal often works if S.temp present:
# dE_th = thermal_broadening_estimate(data, meV=True)

# Analyzer / beamline need endstation calibration tables (e.g. MERLIN).
# On ANTARES / MAESTRO these may raise — catch, ask user, do not invent.
# try:
#     dE_an = analyzer_resolution_estimate(data, meV=True)
#     dE_bl = beamline_resolution_estimate(data, meV=True)
#     dE = total_resolution_estimate(
#         data, include_thermal_broadening=True, meV=True
#     )
# except (KeyError, NotImplementedError, AttributeError) as e:
#     print("partial only:", e)

# ANTARES: fixed horizontal slit — see beamline-geometry.md
```

**Report:** parts + units; which failed; what entered FD/EF if used.
