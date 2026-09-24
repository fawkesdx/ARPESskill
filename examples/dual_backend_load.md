# Dual-backend load (Route B)

Same user ask — different backend by file sniff (override wins).

## MAESTRO / ALS FITS → `pyarpes`

```text
User: Load this MAESTRO cut and state axes.
```

Agent:

1. Sniff `.fits` (or prefer sibling FITS over MH1 `.h5`) → backend `pyarpes`.
2. Ensure Python 3.8 env (`pyarpes-env.md`).
3. `arpes.io.load_data(..., location="MAESTRO")` (or project preferred loader).
4. Report: `backend: pyarpes`, dims, units, energy convention.

## ANTARES `.nxs` → `arpes_viewer`

```text
User: Open this ANTARES NeXus file and list what's inside.
```

Agent:

1. Sniff `.nxs` / ANTARES → backend `arpes_viewer`.
2. Ensure ≥3.9 env + `PYTHONPATH` to `ARPES_viewer` (`arpes-viewer-env.md`).
3. Structure peek: `loader.registry.list_entries(path)` (folder Pass B).
4. Full load when asked: `loader.registry.load(path, entry=…)`.
5. Report: `backend: arpes_viewer`, loader name, `kind`, axes — no invent.

## User override

```text
User: Use PyARPES for this nxs anyway.
```

→ Honor override; state that sniff would have preferred `arpes_viewer`.
If load fails → A/B/C/**D** (`package-first.md`).

## Missing capability (D)

```text
User: Run PCA on this CASSIOPEE map.   # already loaded with arpes_viewer
```

→ `decomp_pca` Browser cell empty. **Stop.** Offer:

- **D** switch this stem/step to `pyarpes` (needs data on that stack — ask how),
- **B** map a project PCA helper,
- **C** new `analysis/` helper,
- **A** retry same backend (will still lack PCA).

Do **not** silently DIY sklearn or bridge `NxsScan` → xarray.

## See also

- `reference/arpes-viewer-backend.md`
- `reference/backend-capability-map.md`
- `reference/folder-manifest.md`
