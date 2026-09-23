# Axis preparation

**Gate:** user asks **rebin** / downsample / **symmetrize** about an axis /
**normalize** intensity along a dim / **sort** coords / **condense** empty
margins. Not default overview.

**Docs:** `arpes.analysis.general` · `arpes.preparation.axis_preparation` ·
[Data manipulation](https://arpes.readthedocs.io/en/latest/notebooks/data-manipulation-intermediate.html)

Capabilities: `rebin`, `symmetrize_axis`, `normalize_dim`, `sort_axis`,
`condense` — `backend-capability-map.md`.

**Not this doc:** bg subtract (`backgrounds.md`); FD divide / gap
(`near-ef-gap.md`); smooth / deconvolve (`smooth-deconvolve.md`); polygon
masks (deferred).

---

## Rebin

Downsample by integrating chunks (default). Exactly one of `shape=` or
`reduction=` (or dim kwargs). **`interpolate=True` not implemented** in
stock PyARPES — do not claim it.

```python
from arpes.analysis.general import rebin

# coarser = rebin(data, reduction={"phi": 2, "eV": 2})
# # or: rebin(data, shape={"phi": 200, "eV": 400})
```

Echo factors; save if used before fits / k.

---

## Symmetrize axis

Mirror + combine about an axis (package shifts so first coord → 0, then
flips). Prefer **after** EF→0 / stated Γ when symmetrizing `eV` or momentum.

```python
from arpes.analysis.general import symmetrize_axis

# sym = symmetrize_axis(cut, "phi")  # echo axis; optional flip_axes=
```

**Hard:** never invent a mirror plane or high-sym point. User/offsets still
rule Γ (`k-and-kz-conversion.md`). Gap **EDC** symmetrize about EF =
`gap.symmetrize` (`near-ef-gap.md`) — different helper.

---

## Normalize along dim(s)

Rescale so slices share average intensity along kept dim(s). Common for
laser-ARPES / matrix-element compare — **alters counts**.

```python
from arpes.preparation import normalize_dim
# from arpes.preparation.axis_preparation import normalize_total  # ask

# eq = normalize_dim(spectrum, "eV")           # equalize along eV
# eq = normalize_dim(spectrum, ["eV", "phi"])  # keep both
```

Echo dims. Do **not** silent-normalize before quantitative fits / Σ unless
user opts in. `normalize_total` (fixed total) only if asked.

≠ Shirley/hull bg; ≠ `normalize_by_fermi_distribution` (near-EF path).

---

## Sort axis

```python
from arpes.preparation import sort_axis

# ordered = sort_axis(data, "hv")  # or other scrambled motor
```

Use when coords are out of order after load/stitch.

---

## Condense

Clip to regions with substantial weight. Stock helper often trims `eV` to
`slice(None, 0.05)` — **state** that package default; ask if user wants a
different window.

```python
from arpes.analysis.general import condense

# clipped = condense(data)  # echo eV trim if applied
```

---

## Hard rules

- No DIY `reshape` / `np.mean` rebin when `rebin` imports.  
- No silent intensity reweight before fits — echo product used.  
- Symmetrize ≠ gap EDC symmetrize; normalize ≠ background.  
- Check installed signatures before claiming kwargs.

---

## Checklist

1. User asked a prep step; method matches table above.  
2. Dims / reduction / shape / normalize axes echoed.  
3. Before/after saved when intensity or grid changes.  
4. Downstream fits name which array (raw vs prep).
