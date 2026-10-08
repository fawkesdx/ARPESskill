"""Single-curve EDC fit. Package lineshapes only. No broadcast, no new models."""

from arpes_hotpath.axes import ENERGY_NAMES, find_dim
from arpes_hotpath.policy import PolicyRefusal

LINESHAPES = {
    "gaussian": "GaussianModel",
    "lorentzian": "LorentzianModel",
    "voigt": "VoigtModel",
}


def extract_edc(da, *, at=None):
    energy = find_dim(da, ENERGY_NAMES)
    if energy is None:
        raise PolicyRefusal("no energy dim; not inventing an EDC axis")
    cur = da
    picked = []
    for dim, value in (at or {}).items():
        if dim not in cur.dims and dim not in cur.coords:
            raise PolicyRefusal(f"dim {dim} not on the array")
        cur = cur.sel({dim: value}, method="nearest")
        picked.append(dim)
    for dim in list(cur.dims):
        if dim == energy:
            continue
        cur = cur.mean(dim)
    if cur.ndim != 1 or energy not in cur.dims:
        raise PolicyRefusal("EDC extract did not yield a 1D energy curve")
    values = cur.values
    finite = values[values == values]
    return {
        "curve": cur,
        "energy_dim": energy,
        "n": int(cur.sizes[energy]),
        "min": None if finite.size == 0 else float(finite.min()),
        "max": None if finite.size == 0 else float(finite.max()),
        "mean": None if finite.size == 0 else float(finite.mean()),
        "integrated_dims": [dim for dim in da.dims if dim != energy and dim not in picked],
        "selected": at or {},
    }


def _params(result):
    params = getattr(result, "params", None)
    if params is None:
        raise PolicyRefusal("package fit returned no params")
    out = {}
    for name in params:
        item = params[name]
        value = getattr(item, "value", None)
        stderr = getattr(item, "stderr", None)
        out[str(name)] = {
            "value": None if value is None else float(value),
            "stderr": None if stderr is None else float(stderr),
        }
    return out


def fit_edc_curve(curve, *, lineshape, background="none", n_peaks=1, guess_fit=None, models=None):
    if n_peaks != 1:
        raise PolicyRefusal(
            "this script fits one peak. Propose N and confirm before multi-band; no silent N."
        )
    key = (lineshape or "").casefold()
    if key not in LINESHAPES:
        raise PolicyRefusal("lineshape must be gaussian, lorentzian, or voigt")
    bg = (background or "none").casefold()
    if bg not in {"none", "affine"}:
        raise PolicyRefusal("background must be none or affine (package AffineBackgroundModel)")
    if models is None or guess_fit is None:
        try:
            from arpes.fits import fit_models as models
            from arpes.fits.utilities import guess_fit
        except ImportError as exc:
            raise PolicyRefusal(
                f"PyARPES fit models unavailable ({exc}). "
                "No scipy/lmfit lineshape written here."
            ) from exc
    model_cls = getattr(models, LINESHAPES[key])
    if bg == "affine":
        if not hasattr(models, "AffineBackgroundModel"):
            raise PolicyRefusal("AffineBackgroundModel missing; ask before a new background")
        model = model_cls() + models.AffineBackgroundModel()
        result = guess_fit(model, curve)
    else:
        result = guess_fit(model_cls, curve)
    return {
        "lineshape": key,
        "background": bg,
        "n_peaks": 1,
        "model": LINESHAPES[key],
        "params": _params(result),
        "engine": "arpes.fits",
    }
