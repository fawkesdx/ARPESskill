# Example: time-resolved ARPES (delay / t0 / Δ)

Follow `reference/tr-arpes.md`. Needs a dataset with a `delay` dim (user file —
no dedicated spin/tr tutorial cube required in `example_data`).

```python
from arpes.analysis.tarpes import find_t0, relative_change, normalized_relative_change

# data = load_data("PATH/TO/tr_arpes", location="...")  # must include delay
# Confirm delay units (often ps)

# t0: user → attrs/S.t0 → find_t0 → ask
# t0 = getattr(data.S, "t0", None) or data.attrs.get("t0") or find_t0(data)

# Spectroscopic ROI R for I vs delay (near-EF and/or above EF — state which)
# along_delay = data.sel(eV=slice(0.0, 0.5)).sum("eV")  # example above-EF
# if "phi" in along_delay.dims:
#     along_delay = along_delay.mean("phi")
# along_delay.plot()  # mark t0

# delay* = nearest delay >= t0 (or nearest to t0)
# delays = along_delay.coords["delay"]
# delay_star = float(delays.sel(delay=t0, method="backfill"))  # or nearest
# slice_t = data.sel(delay=delay_star, method="nearest")
# → cut/EDC overview on slice_t

# delta = relative_change(data, t0=t0, buffer=0.3)
# # or normalized_relative_change(...)
# delta.sel(delay=delay_star, method="nearest").plot()
```

**Report:** delay units, t0 + method, \(R\), delay\*, Δ = relative vs normalized.
