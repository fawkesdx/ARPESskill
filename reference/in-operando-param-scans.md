# In-operando / external-parameter scans

**Gate:** a scan axis \(P\) that is an **external control** (dose, gate voltage,
sample current, magnetic field, temperature, …) — not the usual spectroscopic
or spatial dims.

**\(P\) is not:** `eV`, detector angle (`phi` / `pixel`), deflection
(`psi` / `Slit_Defl`), spatial `x`/`y`, photon energy `hv` when that dim is
the beamline mono energy (use hv/kz recipes), or pump–probe **`delay`** (use
`tr-arpes.md` for t0 / ΔI).

Package-first: load → discover coords → `sel`/`isel`/`sum`/`mean` along \(P\) →
**reuse** existing kind recipes. No invent K-coverage, \(R(V)\), or magnetometry
formulas — ask or user-map if specialty analysis is needed.

Capabilities: `param_scan_detect`, `param_overview`, `param_slice_reduce` —
`backend-capability-map.md`.

---

## Detect \(P\)

1. List dims with size >1.  
2. Subtract the “usual” set when present: `eV`, `phi`/`pixel`, `psi`/`Slit_Defl`,
   `x`/`y`/`z`, `hv` (as photon energy), spin channels.  
3. Remaining n>1 dims are **\(P\) candidates**.  
4. If the name is unclear (`LMOTOR*`, bare `volts`, custom FITS column) →
   **ask** the user: meaning + units (e.g. “K dose / s”, “\(V_\mathrm{gate}\)” ,
   “sample I / nA”, “B / T”).  
5. MAESTRO renames you may see (still confirm science meaning):
   - `S_Volts` → `volts` (not automatically “gate”)  
   - `RINGCURR` → `beam_current` (**ring** current ≠ sample transport I)  
6. Log text (“dosing”, “in-operando”) is comment only — **dims win**.

Multiple \(P\) dims (e.g. V and B): treat as a param hypercube; default overview
reduces or picks mid on the secondary \(P\) unless user states otherwise.

---

## Kind at each \(P\) (wrapper)

```text
classify spectroscopic kind (cut / E-line / Fermi / XY / hv / spin / …)
  → slice or reduce at P*
  → run EXISTING skill recipe for that kind
  → optional broadcast / stack along P (user-asked)
```

Same pattern as spatial XY: parameter axis wraps spectroscopy; it does not
replace it.

---

## Spectroscopic ROI \(R\) for “vs \(P\)” plots

Plots of intensity vs \(P\) need an integration **box** in spectroscopic dims
(same idea as the XY map ROI).

- User box wins (E ± φ/ψ bounds).  
- Default: near-EF window for valence; full/stated E for core — **echo \(R\)**.  
- Change \(R\) → rebuild I(\(P\)) curves.

---

## Default slice \(P^*\)

1. **Default:** mid index along \(P\).  
2. If the series looks **stepped / plateaus** (common in dosing) → **ask** which
   step or coordinate value to use for the detailed overview.  
3. User may request argmax of I(\(P\)) or an explicit value (e.g. “at 1.2 V”).

Anti-claim: \(P^*\) is not Γ or EF calibration.

---

## Quick report — param set

Save under `analysis/`; token note if many steps (`token-usage.md`).

| # | Plot | Rule |
|---|------|------|
| 1 | **I or EDC vs \(P\)** | Integrate over \(R\); label \(P\) with units |
| 2 | **Kind overview at \(P^*\)** | Cut / core / Fermi lite / … for that slice |
| 3 | **Optional stack** | Stack EDCs vs \(P\) or I(\(E,P\)) — ask/note if large |
| 4 | **Combos** | If also XY or hv: reduce first (`spatial-xy-scans.md` / hv rules); do not dump every hypercube slice |

Echo: \(P\) meaning, units, \(R\), \(P^*\) choice (mid / asked step / value).

Quick report: no full-cube k/kz.

---

## Analysis (user-asked)

- Fit / gap / k at one \(P\) or a stated \(P\) window.  
- `broadcast_model` along \(P\) → peak position vs dose, etc. — token note;
  test one step first.  
- Temperature series: same rules; PyARPES `temperature_dependence` example is
  the pattern, not a special case.  
- Specialty (monolayer calibration, four-probe \(R\), Hall) → package-first ask
  A/B/C or user-map; do not invent.

---

## Package map

| Step | Prefer |
|------|--------|
| Load | `load_data` / MAESTRO plugin; read real coord names |
| Slice / reduce | `sel` / `isel` / `sum` / `mean` |
| Stack plots | `arpes.plotting.stack_plot` helpers if useful |
| Fits vs \(P\) | `broadcast_model(..., "<P_dim>")` |

---

## Do not

- Call ring `beam_current` sample transport current.  
- Assume `volts` = gate without asking.  
- Invent coverage / magnetotransport formulas.  
- Skip kind classification (“it’s dosing so only plot vs dose”).  
- k-convert the entire \(P\) stack by default.

---

## Checklist

1. \(P\) dim(s) named + units/meaning confirmed if ambiguous.  
2. Spectroscopic kind stated; \(R\) and \(P^*\) echoed.  
3. Param-set PNGs saved.  
4. Deeper work uses matching kind reference at the chosen slice.  
5. Broadcast / specialty only if asked.
