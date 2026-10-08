"""Default overview figures. Angle space only. Kind from dims."""

import os

os.environ.setdefault("MPLBACKEND", "Agg")

from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np

from arpes_hotpath.axes import (
    DETECTOR_NAMES,
    ENERGY_NAMES,
    HV_NAMES,
    SCAN_NAMES,
    SPATIAL_NAMES,
    _fold,
    angle_as_k_flags,
    axes_report,
    classify_energy,
    find_dim,
    units_of,
)
from arpes_hotpath.policy import PolicyRefusal


def _sizes(da):
    return {dim: int(da.sizes[dim]) for dim in da.dims}


def _big(da, names):
    sizes = _sizes(da)
    return [dim for dim in da.dims if _fold(dim) in names and sizes[dim] > 1]


def plot_partner(da, energy_dim):
    """Detector dim, or the only other axis. Does not rename that axis."""
    detector, _scan = split_angles(da)
    if detector is not None:
        return detector
    others = [dim for dim in da.dims if dim != energy_dim and int(da.sizes[dim]) > 1]
    if len(others) == 1:
        return others[0]
    return None


def split_angles(da):
    """One angle axis is the detector (a cut). Two or more: detector + scan."""
    sizes = _sizes(da)
    names = SCAN_NAMES | DETECTOR_NAMES
    angles = [dim for dim in da.dims if _fold(dim) in names and sizes[dim] > 1]
    if not angles:
        return None, None
    if len(angles) == 1:
        return angles[0], None
    detectors = [dim for dim in angles if _fold(dim) in DETECTOR_NAMES]
    scans = [dim for dim in angles if _fold(dim) in SCAN_NAMES and dim not in detectors]
    detector = detectors[0] if detectors else None
    scan = scans[0] if scans else None
    if detector is None:
        detector = angles[0]
    if scan is None:
        scan = next(dim for dim in angles if dim != detector)
    return detector, scan


def _text_blob(da, notes):
    parts = [notes or ""]
    for key in ("scan_mode", "comment", "comments", "note"):
        if key in da.attrs:
            parts.append(str(da.attrs[key]))
    return " ".join(parts).casefold()


def core_as_2d(da, energy_dim, cut_shaped, notes):
    if not cut_shaped or energy_dim is None:
        return False, []
    energy = classify_energy(da, energy_dim)
    span = energy["range_eV"]
    wide = deep = False
    if span is not None:
        lo, hi = span
        wide = abs(hi - lo) >= 10
        deep = lo <= -5
    blob = _text_blob(da, notes)
    swept = "swept" in blob
    core_word = any(word in blob for word in ("core", "xps", "survey"))
    binding_like = energy["label"] in ("E-EF", "Eb")
    clues = []
    if swept and (core_word or (binding_like and (wide or deep))):
        clues.append("swept")
        if core_word:
            clues.append("core_word")
        if wide:
            clues.append("span_ge_10eV")
        if deep:
            clues.append("deepest_ge_5eV_below_0")
        return True, clues
    if binding_like and (wide or deep):
        if wide:
            clues.append("span_ge_10eV")
        if deep:
            clues.append("deepest_ge_5eV_below_0")
        return True, clues
    return False, []


def classify_kind(da, notes=""):
    """Dims win. Log text is not kind. Returns kind, confidence, clues."""
    energy = find_dim(da, ENERGY_NAMES)
    hv = _big(da, HV_NAMES)
    spatial = _big(da, SPATIAL_NAMES)
    if len(spatial) >= 2:
        return "xy", "high", ["x", "y"]
    if hv:
        return "hv", "high", ["hv"]
    detector, scan = split_angles(da)
    if scan is not None and energy is not None:
        return "fermi", "high", [scan, detector] if detector else [scan]
    sizes = _sizes(da)
    other_big = [
        dim
        for dim, size in sizes.items()
        if size > 1 and dim != energy and _fold(dim) not in HV_NAMES
    ]
    cut_shaped = energy is not None and scan is None and not hv and len(spatial) < 2
    # cut: energy plus at most one non-energy axis with n>1
    if cut_shaped and len(other_big) <= 1:
        flagged, clues = core_as_2d(da, energy, True, notes)
        if flagged:
            return "core_level_2d", "medium", clues
        return "cut", "high" if other_big else "medium", other_big
    return "unknown", "low", []


def axis_label(da, dim):
    units = units_of(da, dim) or "units unset"
    flags, _prov = angle_as_k_flags(da)
    marked = any(item["dim"] == dim for item in flags)
    suffix = "; not momentum" if marked else ""
    return f"{dim} ({units}){suffix}"


def _nearest_zero_or_mid(da, dim):
    if dim not in da.coords:
        return int(da.sizes[dim]) // 2, "mid_index"
    values = np.asarray(da.coords[dim].values, dtype=float)
    if np.nanmin(values) <= 0 <= np.nanmax(values):
        return int(np.nanargmin(np.abs(values))), "nearest_0"
    return int(len(values) // 2), "mid_index"


def _mid(da, dim):
    return int(da.sizes[dim]) // 2


def isoenergy_pick(da, energy_dim):
    if energy_dim not in da.coords:
        index = _mid(da, energy_dim)
        return None, index, "mid_index", None
    values = np.asarray(da.coords[energy_dim].values, dtype=float)
    lo, hi = float(np.nanmin(values)), float(np.nanmax(values))
    if lo <= 0 <= hi:
        half = 0.025 if (0 - 0.025) >= lo and (0 + 0.025) <= hi else None
        return 0.0, int(np.nanargmin(np.abs(values))), "zero_in_range", half
    energy = hi - 0.25 * (hi - lo)
    return energy, int(np.nanargmin(np.abs(values - energy))), "quarter_from_top", None


def _fix(da, dim, index):
    out = da.isel({dim: index})
    if dim in da.coords:
        try:
            value = float(np.asarray(da.coords[dim].values)[index])
        except (TypeError, ValueError, IndexError):
            value = None
    else:
        value = None
    return out, value


def _plot(da, xdim, ydim, path, title):
    sl = da.transpose(ydim, xdim)
    x = (
        np.asarray(sl.coords[xdim].values, dtype=float)
        if xdim in sl.coords
        else np.arange(sl.sizes[xdim])
    )
    y = (
        np.asarray(sl.coords[ydim].values, dtype=float)
        if ydim in sl.coords
        else np.arange(sl.sizes[ydim])
    )
    fig, ax = plt.subplots(figsize=(4.6, 3.6))
    values = np.asarray(sl.values, dtype=float)
    if values.size == 0 or np.all(values == 0) or np.all(~np.isfinite(values)):
        ax.text(0.5, 0.5, "empty DAQ", ha="center", va="center", transform=ax.transAxes)
    else:
        ax.pcolormesh(x, y, values, shading="auto")
    ax.set_xlabel(axis_label(sl, xdim))
    ax.set_ylabel(axis_label(sl, ydim))
    ax.set_title(title, fontsize=8)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=100)
    plt.close(fig)


def _ensure_2d(da, keep):
    cur = da
    fixed = []
    for dim in list(cur.dims):
        if dim in keep:
            continue
        index = _mid(cur, dim)
        cur, value = _fix(cur, dim, index)
        fixed.append({"dim": dim, "index": index, "value": value, "how": "mid_index"})
    if cur.ndim != 2:
        raise PolicyRefusal(
            f"overview could not reduce to 2D (left dims {list(cur.dims)}); not inventing a slice"
        )
    return cur, fixed


def _assumptions(kind, clues, energy, extra):
    base = {
        "kind": kind,
        "kind_clues": clues,
        "kind_from": "dims",
        "log_text_is_kind": False,
        "k_conversion": "off",
        "momentum_reported": False,
        "energy_axis": energy,
        "energy_recalibrated": False,
        "gamma_claimed": False,
        "ef_calibrated": False,
        "absolute_kz": False,
        "anti_claims": [
            "mid deflection / mid detector is not Gamma",
            "pixel or angle is not inverse angstrom",
            "E≈0 is not a calibrated EF",
            "hv trio is not absolute kz",
        ],
    }
    base.update(extra)
    return base


def render_overview(da, *, stem, out_dir, notes=""):
    out_dir = Path(out_dir)
    fig_dir = out_dir / "figures"
    kind, confidence, clues = classify_kind(da, notes=notes)
    report = axes_report(da, source_path=None, backend=da.attrs.get("backend"))
    energy_dim = find_dim(da, ENERGY_NAMES)
    if report["angle_as_k"]:
        # Still plot, but labels refuse momentum. Record the flag.
        pass
    plots = []
    fixed = []
    if kind == "cut":
        if energy_dim is None:
            raise PolicyRefusal("cut overview needs an energy dim from coords")
        detector = plot_partner(da, energy_dim)
        if detector is None:
            raise PolicyRefusal("cut overview needs a detector/angle dim; not inventing one")
        image, extra_fixed = _ensure_2d(da, {energy_dim, detector})
        fixed.extend(extra_fixed)
        path = fig_dir / f"{stem}_cut.png"
        _plot(image, detector, energy_dim, path, f"{stem} detector × energy (angle space)")
        plots.append(str(path))
    elif kind == "core_level_2d":
        detector = plot_partner(da, energy_dim)
        if energy_dim is None or detector is None:
            raise PolicyRefusal("core-as-2D overview needs energy and detector dims")
        image, extra_fixed = _ensure_2d(da, {energy_dim, detector})
        fixed.extend(extra_fixed)
        path = fig_dir / f"{stem}_core_image.png"
        _plot(image, detector, energy_dim, path, f"{stem} detector × energy (suspected core)")
        plots.append(str(path))
        edc = image.mean(detector)
        fig, ax = plt.subplots(figsize=(4.6, 3.2))
        x = np.asarray(edc.coords[energy_dim].values, dtype=float) if energy_dim in edc.coords else np.arange(edc.sizes[energy_dim])
        ax.plot(x, np.asarray(edc.values, dtype=float))
        ax.set_xlabel(axis_label(image, energy_dim))
        ax.set_ylabel("mean intensity (arb.)")
        ax.set_title(f"{stem} angle-integrated EDC", fontsize=8)
        fig.tight_layout()
        edc_path = fig_dir / f"{stem}_core_edc.png"
        edc_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(edc_path, dpi=100)
        plt.close(fig)
        plots.append(str(edc_path))
    elif kind in ("fermi", "hv"):
        if energy_dim is None:
            raise PolicyRefusal(f"{kind} overview needs an energy dim")
        detector, scan = split_angles(da)
        hv_dims = _big(da, HV_NAMES)
        scan_dim = hv_dims[0] if kind == "hv" else scan
        if detector is None or scan_dim is None:
            raise PolicyRefusal(f"{kind} overview missing detector or scan dim")
        if kind == "hv":
            scan_index = _mid(da, scan_dim)
            scan_how = "mid_hv"
            scan_value = None
            if scan_dim in da.coords:
                scan_value = float(np.asarray(da.coords[scan_dim].values)[scan_index])
            slice1, _ = _fix(da, scan_dim, scan_index)
        else:
            scan_index, scan_how = _nearest_zero_or_mid(da, scan_dim)
            slice1, scan_value = _fix(da, scan_dim, scan_index)
        fixed.append(
            {"dim": scan_dim, "index": scan_index, "value": scan_value, "how": scan_how, "plot": 1}
        )
        image1, extra = _ensure_2d(slice1, {energy_dim, detector})
        fixed.extend(extra)
        e0, e_index, e_how, half = isoenergy_pick(da, energy_dim)
        if half:
            window = da.sel({energy_dim: slice(e0 - half, e0 + half)})
            if energy_dim in window.dims and window.sizes.get(energy_dim, 0) > 0:
                slice2 = window.mean(energy_dim)
            else:
                slice2, _ = _fix(da, energy_dim, e_index)
                half = None
                e_how = "nearest"
        else:
            slice2, _ = _fix(da, energy_dim, e_index)
        fixed.append(
            {
                "dim": energy_dim,
                "index": e_index,
                "value": e0,
                "how": e_how,
                "half_width_eV": half,
                "plot": 2,
            }
        )
        image2, extra = _ensure_2d(slice2, {scan_dim, detector})
        fixed.extend(extra)
        det_index = _mid(da, detector)
        slice3, det_value = _fix(da, detector, det_index)
        fixed.append(
            {
                "dim": detector,
                "index": det_index,
                "value": det_value,
                "how": "mid_detector",
                "plot": 3,
            }
        )
        image3, extra = _ensure_2d(slice3, {energy_dim, scan_dim})
        fixed.extend(extra)
        tag = "hv" if kind == "hv" else "fermi"
        specs = (
            (image1, detector, energy_dim, f"{stem}_{tag}_dispersion.png", "dispersion, energy vertical"),
            (image2, detector, scan_dim, f"{stem}_{tag}_isoenergy.png", f"isoenergy E={e0} ({e_how})"),
            (image3, scan_dim, energy_dim, f"{stem}_{tag}_perp.png", "perpendicular, energy vertical"),
        )
        for image, xdim, ydim, name, title in specs:
            path = fig_dir / name
            _plot(image, xdim, ydim, path, f"{stem} {title} (angle space)")
            plots.append(str(path))
    elif kind == "xy":
        xs = _big(da, SPATIAL_NAMES)
        cur = da
        summed = []
        for dim in list(da.dims):
            if dim in xs:
                continue
            cur = cur.sum(dim)
            summed.append(dim)
        if cur.ndim != 2:
            raise PolicyRefusal("xy overview did not reduce to x,y")
        ydim, xdim = xs[1], xs[0]
        if _fold(xdim) == "y":
            xdim, ydim = ydim, xdim
        path = fig_dir / f"{stem}_xy_sum.png"
        _plot(cur, xdim, ydim, path, f"{stem} XY sum (ROI not set; not Gamma)")
        plots.append(str(path))
        fixed.append({"summed_dims": summed, "how": "sum_all_nonspatial", "roi": None})
    else:
        raise PolicyRefusal(
            "overview kind unknown from dims; not guessing a plot. Load and state axes, then ask."
        )
    assumptions = _assumptions(
        kind,
        clues,
        report["energy"],
        {
            "kind_confidence": confidence,
            "fixed": fixed,
            "plots": plots,
            "angle_as_k": report["angle_as_k"],
            "empty_daq": report["empty_daq"],
            "spatial_roi": None if kind != "xy" else "unset; sum of non-spatial dims",
            "hot_spot_is_gamma": False,
            "axis_labels": {dim: axis_label(da, dim) for dim in da.dims},
        },
    )
    return {"kind": kind, "plots": plots, "assumptions": assumptions, "axes": report}
