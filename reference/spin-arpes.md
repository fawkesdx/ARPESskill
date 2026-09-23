# Spin-ARPES (SARPES)

**Gate:** data has spin channels — typically `up`/`down` DataArrays, or
`intensity` + `polarization`, or an explicit spin dim / attrs. If none → not
SARPES; use ordinary ARPES recipes.

**No bundled spin tutorial file** in PyARPES `example_data`. Recipes are
**package-documented**; live-test when the user supplies a file. Say so in the
report if untested on their beamline.

**Docs:** [Spin-ARPES](https://arpes.readthedocs.io/en/latest/spin-arpes.html) ·
API `arpes.analysis.sarpes` · `arpes.plotting.spin`

Capabilities: `spin_detect`, `spin_to_IP`, `spin_plot`, `spin_normalize_pc` —
`backend-capability-map.md`.

---

## Kinds (both supported)

| Kind | Typical shape | Default overview |
|------|----------------|------------------|
| **Spin-EDC** | Mostly 1D energy + spin channels | Up & down curves + polarization (package spin plots) |
| **Spin cut** | `eV` × angle (`phi` / …) + spin | Total intensity (or up+down) dispersion **and** polarization / difference map |

Dims win. Log “spin” alone is not enough without channels.

---

## Pipeline (package only)

```text
1. Detect spin representation (up/down vs I+P)
2. State energy convention; Sherman / photocurrent if used
3. Optional normalize_sarpes_photocurrent (ask/state)
4. to_intensity_polarization / to_up_down as needed
5. Package spin plots → analysis/
6. Deeper: reuse EDC/cut recipes per channel or on total I
7. k-convert only if angles present — usually on total intensity (state choice)
```

### 1–2. Detect + assumptions

- Prefer dataset with `up` and `down`, or `intensity` and `polarization`.
- **Sherman function:** if correcting polarization, use package path
  (`perform_sherman_correction=True` → `S.sherman_function`). If missing →
  **ask**; do not invent a Sherman value.
- Photocurrent up/down present → mention; normalize only with user OK /
  stated reason (`normalize_sarpes_photocurrent` destroys raw count integrity —
  say so).

### 3–5. Convert + plot

```python
from arpes.analysis.sarpes import (
    to_intensity_polarization,
    to_up_down,
    normalize_sarpes_photocurrent,
)
from arpes.plotting.spin import (
    spin_polarized_spectrum,
    spin_colored_spectrum,
    spin_difference_spectrum,
)

# Optional:
# data = normalize_sarpes_photocurrent(data)

ip = to_intensity_polarization(data)  # needs up, down
# or: ud = to_up_down(ip)             # needs intensity, polarization

spin_polarized_spectrum(data)   # up/down curves
# spin_colored_spectrum(data)   # I with P as color
# spin_difference_spectrum(data)
```

Save PNGs under `analysis/`. Prefer scripted plots; Qt only if user asks.

### 6. Kind reuse (analysis)

| Goal | Approach |
|------|----------|
| Peak / EDC fit | Fit **up** and **down** separately (or total I); name lineshape; compare centers/widths |
| Cut dispersion | Treat total I (or each channel) like a normal cut → `edc-mdc-fitting.md` |
| Polarization EDC | Plot P(E); do **not** feed raw P into intensity-only fitters without stating why |
| Near-EF / gap | Apply `near-ef-gap.md` to total I or per channel — state which; p–h + spin caveats |

### 7. Momentum

`convert_to_kspace` only with angle dims. Default: convert **total intensity**
(up+down or `intensity`). Converting one spin channel alone → **state**. Follow
`k-and-kz-conversion.md` EF/Γ rules on that spectrum.

---

## Quick report checklist

1. Spin kind: Spin-EDC vs Spin cut (dims).  
2. Representation: up/down or I+P.  
3. Sherman / photocurrent normalize: used or not (+ ask if needed).  
4. At least one package spin figure + total-I (or up+down) view for cuts.  
5. No invented polarization formula.

---

## Do not

- Invent Sherman function or custom \(P = (N_\uparrow - N_\downarrow)/\ldots\)
  when package helpers exist.  
- Treat polarization as ordinary photocurrent for fits/k without stating.  
- Claim beamline-tested without a user file.  
- Skip energy-axis / EF rules when doing k or gap work on spin data.

---

## Package map

| Step | Prefer |
|------|--------|
| up/down ↔ I+P | `to_intensity_polarization`, `to_up_down` |
| Photocurrent match | `normalize_sarpes_photocurrent` |
| Plots | `spin_polarized_spectrum`, `spin_colored_spectrum`, `spin_difference_spectrum` |
| Load | Endstation plugin if spin-ToF / spin location documented; else project loader / ask |
