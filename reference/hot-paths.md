# Hot paths

Policy stays in `SKILL.md`. For these five steps, run the script (or the
`mcp_arpes` tool that calls it). Do not write a replacement loader, fitter,
or \(k\) formula.

| Capability | CLI | MCP tool |
|------------|-----|----------|
| `load_spectrum`, `state_axes` | `scripts/load_qc.py` | `state_axes`, `load_spectrum` |
| `overview_plot` | `scripts/overview_plots.py` | `overview_plot` |
| `fit_peak` (one curve) | `scripts/fit_edc.py` | `fit_peak` |
| `convert_k` (in-plane only) | `scripts/convert_k.py` | `convert_k` |
| `folder_manifest`, `folder_header_peek` | `scripts/folder_manifest.py` | `folder_manifest`, `folder_header_peek` |

Exit code **2** is a policy refusal. Quote `refusal` and stop. Do not retry
with hand-written physics.

## Load + axes

```bash
python scripts/load_qc.py PATH --backend pyarpes --location MAESTRO
python scripts/load_qc.py PATH.nc --backend inspect-only --allow-inspect
```

`--allow-inspect` only after the user declines the package env.
`.nc` inspect reads coords already stored in the file. HDF5/FITS cubes are
not given invented axis names here.

The JSON states `energy.label` (`Ek`, `Eb`, `E-EF`, or `ambiguous`) and
`angle_as_k`. `report_momentum` stays false unless the array already carries
`kspace_provenance`. A dim named `kx` with degree units is **not** Å⁻¹.

## Overview

```bash
python scripts/overview_plots.py PATH --backend inspect-only --allow-inspect --out analysis
```

Angle space only. Fermi and hv scans write three PNGs. Suspected core-as-2D
writes the image and an angle-integrated EDC. Assumptions JSON:
`analysis/overview/<stem>.json`. No `convert_to_kspace`.

## One EDC fit

```bash
python scripts/fit_edc.py PATH --backend pyarpes --lineshape lorentzian --out analysis
```

Lineshape is `gaussian`, `lorentzian`, or `voigt`. Background `none` or
`affine` (package `AffineBackgroundModel`). One peak. N>1 is a refusal —
propose N and confirm, then the multi-band recipe, not this script.
Missing PyARPES is a refusal. No scipy lineshape lives in the script.

## In-plane k

```bash
python scripts/convert_k.py PATH --backend pyarpes --mode analysis \
  --gamma-method user --offsets '{"phi": 0.1}' \
  --energy-axis E-EF --ef-fit-eV 0.012 --out analysis
```

- `--mode quick` (the default) refuses. Overview does not convert.
- `--ef-fit-eV` must come from a package Fermi-edge fit. The script does not
  fit the edge and does not contain a \(k\) formula.
- Fermi maps need `--gamma-method user` and offsets.
- `provisional:nearest-0` is only a cut whose detector span includes 0°.
- hv→kz is out of this script (needs stated V₀).
- Shift of a non-zero EF uses PyARPES `S.shift_by`. No numeric coord rewrite.
- Output: `analysis/kspace/<stem>_k.npz` with `kspace_provenance=convert_to_kspace`.

## Folder manifest

```bash
python scripts/folder_manifest.py DATA_ROOT --analysis analysis
```

Pass B peek. FITS headers need astropy; without it the FITS row is
`peek_ok: false` and the data array is not read. MH1 `.h5` uses h5py shapes
and attrs. Measurement Type is not `kind`. Chat should report
`counts_by_kind` only.

## MCP

`python -m mcp_arpes --list-tools` prints the catalog (8–12 tools).
`python -m mcp_arpes` speaks MCP stdio. `mcp.json` launches `./bin/arpes-mcp`.

`mcp_clio_hdf5` is a side server: `hdf5_list`, `hdf5_attrs`, `hdf5_partial`
(4096-element cap). It is not a reduction backend and not a logbook.

## Not here

- hv→kz, V₀, multi-band broadcast, spin, trARPES, and the rest of `reference/`
- peaks-arpes callables (map note only in `backend-capability-map.md`)
- A logbook / HDF5-header Q&A skill (later sibling, not these recipes)
