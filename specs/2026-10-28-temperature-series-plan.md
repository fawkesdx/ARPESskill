# Temperature-series workflow — Implementation record

**Goal:** add the T-dependent cut routine (metadata-first, one model per T, constrained
multi-band tracking, exposure-validated weight test, linewidth → λ, Debye–Waller) as a
reference recipe; keep single-cut fitting, Σ(E) and in-operando scans where they are.

**Origin:** VTe₂ near-Γ MAESTRO series (30–500 K), analysed Oct 2026; numbers in the
recipe are examples from that series.

**Not duplicated:** multi-band propose-N / handoff (`edc-mdc-fitting.md`), Σ(E) at one T
(`self-energy.md`), FD division (`near-ef-gap.md`), external-axis slicing
(`in-operando-param-scans.md`), MAESTRO log / manifest (`maestro-measurement-log.md`,
`folder-manifest.md`).

## File map

| Action | Path |
|--------|------|
| Add | `reference/temperature-series.md` |
| Add | `examples/temperature_series.md` |
| Modify | `reference/backend-capability-map.md` (rows `tdep_*`, `linewidth_vs_T_lambda`, `debye_waller_fit`) |
| Modify | `SKILL.md` (description keywords, hard-rule pointer) |
| Modify | `README.md` (table row) |
| Modify | `reference/failure-modes.md` (rows) |
| Modify | `reference/in-operando-param-scans.md` (pointer when lineshape changes with T) |

## Constraints kept

- Docs only; no new scripts. Constrained fitter = user-map (state it); package helpers named where they exist.
- No invented physics: formulas for λ and DW written out with their assumptions.
