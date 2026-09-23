# Time-resolved ARPES (trARPES / pump–probe)

**Gate:** data has a **`delay`** dimension (pump–probe delay) with size >1, or
clear loader aliases that map to `delay`. Without delay → not trARPES; use other
recipes (including generic in-operando only if the axis is *not* pump–probe).

**Relation to in-operando:** delay is like an external param axis, but **t0** and
equilibrium-subtraction / relative-change maps are special — use this reference,
not only `in-operando-param-scans.md`.

**Docs:** [Ultrafast-ARPES](https://arpes.readthedocs.io/en/latest/tr-arpes.html) ·
`arpes.analysis.tarpes` · delay colorbars in `arpes.plotting.utils`

Capabilities: `tr_detect`, `tr_find_t0`, `tr_relative_change`, `tr_overview` —
`backend-capability-map.md`.

PyARPES docs note more examples “to come”; check installed symbols before
claiming plot helpers in `arpes.plotting.tarpes`.

---

## Detect

1. Coord/dim named `delay` (n>1), or endstation rename (e.g. “Delay Stage” →
   `delay` on some laser loaders).  
2. Note pump metadata if present: `pump_fluence`, `pump_power`, pump wavelength /
   polarization attrs.  
3. **Units:** pump–probe delays are often **picoseconds** in PyARPES conventions;
   attrs may say fs. **State units**; **ask** if ambiguous.  
4. Synchrotron / MAESTRO files: only trARPES if delay (or equivalent) is actually
   in the array — do not assume.

---

## t0 (required before dynamics claims)

Resolve in order:

1. User-stated t0  
2. `attrs["t0"]` / `S.t0` if present  
3. Package `arpes.analysis.tarpes.find_t0`  
4. **Ask**

Echo **t0 value + method** every time. Never invent.

---

## Spectroscopic ROI \(R\)

For I vs delay and Δ maps, state the energy (and angle) integration box:

- Near EF and/or **above EF** for excited carriers — say which.  
- User box wins. Change \(R\) → rebuild curves/maps.

---

## Default delay\* (overview slice)

1. Prefer **nearest delay ≥ t0** (first point at/after pump arrival on the grid).  
2. If that is unclear, **nearest delay to t0**.  
3. If t0 still unknown after step 4 above → use **mid delay** and state
   “t0 unresolved”.

Anti-claim: delay\* ≠ Γ / EF calibration.

---

## Quick report — delay set

Save under `analysis/`; token note if many delays.

| # | Plot | Rule |
|---|------|------|
| 1 | **I or EDC vs delay** | Integrate over \(R\); mark t0 if known |
| 2 | **Kind overview at delay\*** | Cut / EDC (or map lite) at delay\* |
| 3 | **Δ spectrum / map** | `relative_change` **or** `normalized_relative_change` — state which + pre-t0 `buffer` |
| 4 | Optional | Stack EDCs vs delay; delay colorbar utilities if useful |

```python
from arpes.analysis.tarpes import find_t0, relative_change, normalized_relative_change

# t0 = data.S.t0 or find_t0(data) or user
# delta = relative_change(data, t0=t0, buffer=0.3)  # buffer in delay units
# or: normalized_relative_change(data, t0=t0, buffer=0.3)
```

Echo: units, t0 method, \(R\), delay\*, which Δ recipe.

Quick report: no full delay-cube k-conversion.

---

## Analysis (user-asked)

| Goal | Approach |
|------|----------|
| Equilibrium reference | Mean (or sel) **before** t0 − buffer |
| Excited-state EDC/cut | Slice at delay\* or stated delay; reuse `edc-mdc-fitting.md` / cut overview |
| Dynamics fit | After t0: package decay / exp models — **name model**; ask if unclear |
| Gap / near-EF | `near-ef-gap.md` on chosen delay or equilibrium — state which |
| k-convert | One delay (or equilibrium) first; follow `k-and-kz-conversion.md` |

Do **not** invent coherent-phonon / full microscopic pump–probe models unless
package path exists and user chooses A/B/C.

---

## Package map

| Step | Prefer |
|------|--------|
| t0 | attrs / `S.t0` / `find_t0` / ask |
| ΔI | `relative_change` |
| ΔI/I | `normalized_relative_change` |
| Delay display | `delay_colorbar` / `delay_colormap` if useful |
| Load | Laser endstation plugins with delay rename; else project loader / ask |

---

## Do not

- Treat delay as generic \(P\) only (skip t0 / Δ maps).  
- Mix fs and ps without stating.  
- Claim MAESTRO fs trARPES without a delay dim.  
- k-convert entire delay stack by default.  
- Invent t0 or Sherman-like constants.

---

## Checklist

1. `delay` present; units stated.  
2. t0 + method echoed (or explicitly unresolved).  
3. \(R\), delay\*, Δ recipe stated; PNGs saved.  
4. Kind reuse at delay\* / equilibrium for deeper work.  
5. Decay / k / gap only with stated method or ask.
