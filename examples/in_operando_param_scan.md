# Example: in-operando parameter scan (along \(P\))

Follow `reference/in-operando-param-scans.md`. Replace dim name `P` with the real
coord (`volts`, `temperature`, dose motor, …) after confirming meaning + units.

```python
# data = load_data("PATH/TO/operando_scan", location="MAESTRO")
# dims e.g. (eV, phi, volts) or (eV, temperature) — discover from data.dims

# 1) Identify P candidates; ask if name unclear
# P_dim = "volts"  # example only

# 2) Spectroscopic ROI R for I vs P
# R = dict(eV=slice(-0.05, 0.02))  # near-EF example; user box wins
# along_P = data.sel(**R).sum("eV")  # may still have phi — sum/mean as stated
# if "phi" in along_P.dims:
#     along_P = along_P.mean("phi")
# along_P.plot()  # I vs P

# 3) P* = mid index; if stepped/plateau series → ask which step
# p_star = float(data.coords[P_dim].isel({P_dim: data.sizes[P_dim] // 2}))
# slice_p = data.sel({P_dim: p_star}, method="nearest")
# → run cut / core / Fermi overview on slice_p (existing recipes)

# 4) Optional: broadcast_model(..., P_dim) only if user asks (+ token note)
```

**Report:** \(P\) meaning/units, \(R\), \(P^*\) (mid vs user-picked step), kind recipe used.
