# Example: Log a MAESTRO folder + Pass A manifest

**Goal:** User asks to log beamtime metadata; agent writes CSV in the data
folder and merges into `analysis/manifest.json` without loading spectra or
pasting the catalog into chat. See `reference/maestro-measurement-log.md`.

## User message

> Log the maestro data in `/Volumes/MAESTROdata/uARPES/2026/2026_06/MySession`

## Agent steps

1. **Resolve** the folder (flat leaf dir with `.fits`/`.h5` scans).
2. **CSV freshness:** if `MAESTRO_Measurement_Log.csv` is newer than all data
   files and user did not say refresh → skip logger; else run:

   ```bash
   python scripts/maestro_measurement_log.py "/Volumes/MAESTROdata/uARPES/2026/2026_06/MySession"
   ```

3. **Pass A merge:**

   ```bash
   python scripts/merge_maestro_log_to_manifest.py "/Volumes/MAESTROdata/uARPES/2026/2026_06/MySession"
   ```

4. **Chat reply (short):**

   - 42 stems logged; Measurement Type mix: 18 Cut, 12 Fermi Map, … (optional)
   - CSV: `…/MySession/MAESTRO_Measurement_Log.csv`
   - Manifest: `…/MySession/analysis/manifest.json` (Pass A; `kind=unknown`)

5. **Do not** run Pass B peek, overview plots, or graphify unless the user asks
   next.

## Notes

- FITS sibling present → CSV **File Name** is `.fits`; cryo/SMU/comments still
  from sibling `.h5` when available.
- CSV **Measurement Type** is **not** manifest `kind` — dims / Pass B decide
  `kind` later (`reference/folder-manifest.md`).
