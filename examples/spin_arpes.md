# Example: Spin-ARPES (package recipes)

Follow `reference/spin-arpes.md`. **No** PyARPES `example_data` spin file —
replace `data` with a user load (`load_data` / project loader).

```python
from arpes.io import load_data
from arpes.analysis.sarpes import to_intensity_polarization
from arpes.plotting.spin import (
    spin_polarized_spectrum,
    spin_colored_spectrum,
    spin_difference_spectrum,
)

# data = load_data("PATH/TO/spin_file", location="...")  # user path
# Expect data_vars including up/down OR intensity/polarization

# Optional photocurrent normalize — ask first (alters counts)
# from arpes.analysis.sarpes import normalize_sarpes_photocurrent
# data = normalize_sarpes_photocurrent(data)

# Sherman: only if attrs/S.sherman_function known — else ask
ip = to_intensity_polarization(data)  # or perform_sherman_correction=True

# Spin-EDC or reduced EDC:
# spin_polarized_spectrum(data)   # or ip / channel selection
# spin_colored_spectrum(data)

# Spin cut: also plot total intensity dispersion (up+down or ip.intensity)
# difference / polarization map as dims allow:
# spin_difference_spectrum(data)

# Deeper: fit up and down EDCs separately (edc-mdc-fitting.md)
# k-convert: usually on total intensity if angles present
```

**Report:** spin kind, Sherman/normalize flags, which channel used for fits/k,
and that recipes were not live-validated without user data.
