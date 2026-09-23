# Example: self-energy from MDC fits

Follow `reference/self-energy.md`. Needs a **single-band** cut (prefer
k-converted).

```python
from arpes.analysis.self_energy import (
    fit_for_self_energy,
    to_self_energy,
    estimate_bare_band,
    quasiparticle_lifetime,
)

# kcut = convert_to_kspace(...)  # prefer momentum cut; EF aligned
# ROI: one clear band — ask if multi-peak

# Path C: reuse existing MDC broadcast `results` if present, else:
# se = fit_for_self_energy(kcut, method="mdc", bare_band="ransac_linear")
# # or: se = to_self_energy(results, bare_band="ransac_linear")

# se["self_energy"].real.plot(label="Re Σ")
# se["self_energy"].imag.plot(label="Im Σ")
# se["bare_band"].plot(label="bare band")

# Optional only if user asks:
# tau = quasiparticle_lifetime(se["self_energy"], se["bare_band"])
```

**Report:** path (reuse vs `fit_for_self_energy`), bare-band spec, ReΣ/ImΣ,
Lorentzian+affine; lifetime only if asked.
