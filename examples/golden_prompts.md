# Golden prompts

Tutorial file: `examples/tutorial_cut.nc` (synthetic cut, not beamtime data).
Coords are `eV` from about −1.2 eV to 0.1 eV and `phi` in degrees.
Expected energy label: **E−EF** (range clue, claimed). `phi` is not momentum.

Run from the repo root with a Python that has `numpy`, `xarray`, `h5py`,
and `matplotlib`.

## 1. Load and state axes

Ask: “Load `examples/tutorial_cut.nc` with the ARPES skill and state the axes.”

```bash
python scripts/load_qc.py examples/tutorial_cut.nc \
  --backend inspect-only --allow-inspect
```

Pass when the JSON has `energy.label` = `E-EF`, dims `eV` and `phi`,
`angle_as_k` empty, and `report_momentum` false.
Inspect-only is allowed here because the file is already a coord-bearing
NetCDF and the prompt is a tutorial, not a silent fallback off a failed
`import arpes`. On a real FITS/HDF5 scan, ask for the package env first.

## 2. Overview, still angle space

Ask: “Show the default overview. Do not convert to k.”

```bash
python scripts/overview_plots.py examples/tutorial_cut.nc \
  --backend inspect-only --allow-inspect --out /tmp/arpes-tutorial
```

Pass when kind is `cut`, one PNG is written, `k_conversion` is `off`,
`momentum_reported` is false, and axis labels do not say inverse angstrom.
The figure axis is `phi` in degrees.

## 3. k without a center must refuse

Ask: “Convert that overview to k.”

```bash
python scripts/convert_k.py examples/tutorial_cut.nc \
  --backend inspect-only --allow-inspect --mode analysis \
  --gamma-method user --ef-fit-eV 0 --out /tmp/arpes-tutorial
```

Pass when the process exits 2 and `refusal` says the loaded backend is not
`pyarpes` (no hand-written \(k\)). A quick-mode call (omit `--mode analysis`)
must also exit 2.

Do not satisfy this prompt by deriving \(k_\parallel\) in chat.
