# Smooth and deconvolution

**Gate:** user asks **smooth** / denoise / filter **or** **deconvolve** /
Richardson–Lucy / ICE / PSF. Not default overview.

Two tracks (path **C**):

| Ask | Default |
|-----|---------|
| Noise / “clean up” / smooth | **Smooth** — `gaussian_filter_arr` |
| Deconvolution / RL / recover resolution | **Deconvolve** — separate; never auto |

**Docs:** `arpes.analysis.filters` · `arpes.analysis.savitzky_golay` ·
`arpes.analysis.deconvolution`

Capabilities: `smooth_gaussian`, `smooth_other`, `deconvolve_rl`,
`deconvolve_psf` — `backend-capability-map.md`.

---

## Smooth (default noise path)

1. Prefer `gaussian_filter_arr(arr, …)` — **state σ** (coordinate-aware; say
   which dims if relevant).  
2. **Boxcar** (`boxcar_filter_arr`) or **Savitzky–Golay** only if user asks.  
3. Save **before / after** under `analysis/`.  
4. Downstream fits / Σ / enhance: use smoothed array **only if user opts in** —
   else keep raw; echo which.

```python
from arpes.analysis.filters import gaussian_filter_arr, boxcar_filter_arr
# from arpes.analysis.savitzky_golay import savitzky_golay

# sm = gaussian_filter_arr(cut, sigma=…)  # state sigma
```

---

## Deconvolve (separate ask — never auto)

1. **Stop** if user only said “smooth” — do not jump to deconvolution.  
2. Require stated **PSF** / resolution: `make_psf1d(...)` or user-supplied PSF.
   No invent kernel from thin air.  
3. Default method: **`deconvolve_rl`** (Richardson–Lucy). **ICE**
   (`deconvolve_ice`) only if asked.  
4. **Warn:** artifacts / ringing / over-sharpen; result is **not** a peak fit
   and not “true” intensity.  
5. Save raw vs deconvolved; state n_iter / PSF params if exposed.

```python
from arpes.analysis.deconvolution import make_psf1d, deconvolve_rl, deconvolve_ice

# psf = make_psf1d(...)  # or user PSF — state width / shape
# dec = deconvolve_rl(data, ...)  # check installed signature before calling
```

---

## If user wants both

**Ask order.** Typical: deconvolve on **raw** (or very light smooth only if
agreed). Do not chain heavy smooth → RL silently.

Pre-smooth before band enhance: see `band-enhance.md` — link here; still ask.

---

## Package map

| Step | Prefer |
|------|--------|
| Gaussian smooth | `gaussian_filter_arr` |
| Boxcar / SG | `boxcar_filter_arr` / `savitzky_golay` — ask |
| PSF | `make_psf1d` / user |
| RL | `deconvolve_rl` |
| ICE | `deconvolve_ice` — ask |

Check installed call signatures before claiming kwargs.

---

## Do not

- Auto-deconvolve on load or overview.  
- Invent PSF / resolution width.  
- Silent replace of analysis array with smoothed/deconvolved.  
- Claim recovered “true” band width or Σ from RL alone.  
- DIY Wiener / Lucy outside package when APIs import.

---

## Checklist

1. Smooth vs deconvolve distinguished; deconvolve never from “smooth” alone.  
2. Smooth: method + σ (or window) stated; before/after saved.  
3. Deconvolve: PSF + method (RL/ICE) stated; artifact warn.  
4. Downstream product (raw / smooth / dec) echoed.
