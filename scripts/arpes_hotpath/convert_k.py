"""In-plane k conversion. Package convert_to_kspace only. No k formula."""

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from arpes_hotpath.axes import axes_report
from arpes_hotpath.overview import classify_kind
from arpes_hotpath.policy import PolicyRefusal


def _zero_in_range(da, dim):
    """True when 0 lies inside the coord span. Nearest sample may sit off 0."""
    if dim not in da.coords:
        return False
    values = np.asarray(da.coords[dim].values, dtype=float)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return False
    return float(np.min(finite)) <= 0 <= float(np.max(finite))


def prepare_k(
    da,
    *,
    mode,
    gamma_method,
    offsets,
    energy_label,
    kind=None,
):
    """Gates only. Does not convert and does not write a dispersion formula."""
    if mode != "analysis":
        raise PolicyRefusal(
            "quick report stays angle-space. Pass --mode analysis to convert."
        )
    report = axes_report(da, source_path=None, backend=None)
    if report["angle_as_k"]:
        raise PolicyRefusal(
            "a dim is named like momentum without convert provenance. "
            "Refusing to relabel it as inverse angstrom."
        )
    if report.get("kspace_provenance"):
        raise PolicyRefusal("array already has kspace_provenance; not converting again")
    label = energy_label or report["energy"]["label"]
    if label == "ambiguous":
        raise PolicyRefusal("energy axis ambiguous; state Ek, Eb, or E-EF before convert")
    resolved_kind = kind or classify_kind(da)[0]
    if resolved_kind == "hv":
        raise PolicyRefusal(
            "hv stack is not this in-plane script. kz needs a stated V0 in the k/kz reference."
        )
    if resolved_kind == "core_level_2d":
        raise PolicyRefusal("suspected core-as-2D; no default valence k conversion")
    method = (gamma_method or "").strip()
    if not method:
        raise PolicyRefusal("gamma method required; not inventing a zone center")
    applied = None
    if resolved_kind == "fermi" and method != "user":
        raise PolicyRefusal("Fermi map needs user offsets. Provisional nearest-0 is for cuts.")
    if method == "user":
        if not offsets:
            raise PolicyRefusal("user gamma method needs an offsets object (degrees)")
        applied = "user"
    elif method == "loader_offsets":
        holder = getattr(da, "S", None)
        current = getattr(holder, "offsets", None) if holder is not None else None
        if not current:
            raise PolicyRefusal("loader_offsets requested but S.offsets is empty")
        offsets = dict(current)
        applied = "loader_offsets"
    elif method == "provisional:nearest-0":
        if resolved_kind != "cut":
            raise PolicyRefusal("provisional nearest-0 is only for a cut")
        from arpes_hotpath.overview import split_angles

        detector, _scan = split_angles(da)
        if detector is None or not _zero_in_range(da, detector):
            raise PolicyRefusal(
                "0° is not in the detector range. Pass user offsets; not inventing Gamma."
            )
        offsets = {}
        applied = "provisional:nearest-0"
    else:
        raise PolicyRefusal(
            "gamma_method must be user, loader_offsets, or provisional:nearest-0"
        )
    return {
        "energy_label": label,
        "kind": resolved_kind,
        "gamma_method": method,
        "offsets": offsets or {},
        "apply_offsets": applied == "user",
        "axes": report,
    }


def package_convert(da):
    try:
        from arpes.utilities.conversion.core import convert_to_kspace
    except ImportError:
        try:
            from arpes.utilities import convert_to_kspace
        except ImportError as exc:
            raise PolicyRefusal(
                f"convert_to_kspace import failed ({exc}). No hand-written k formula."
            ) from exc
    return convert_to_kspace(da)


def package_apply_offsets(da, offsets):
    holder = getattr(da, "S", None)
    apply = getattr(holder, "apply_offsets", None) if holder is not None else None
    if apply is None:
        raise PolicyRefusal(
            "no S.apply_offsets on this object. Refusing to rewrite angle coordinates by hand."
        )
    return apply(offsets)


def package_shift_ef(da, energy_dim, ef_fit_eV):
    if abs(ef_fit_eV) < 1e-4:
        return da
    holder = getattr(da, "S", None)
    shift = getattr(holder, "shift_by", None) if holder is not None else None
    if shift is None:
        raise PolicyRefusal(
            "EF is not at 0 and this object has no S.shift_by. "
            "Refusing a hand-rolled energy shift."
        )
    return shift({energy_dim: -float(ef_fit_eV)})


def save_k_npz(kdata, path, *, meta):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    dims = list(kdata.dims)
    payload = {
        "intensity": np.asarray(kdata.values),
        "dims": np.array(dims),
    }
    for name in dims:
        if name in kdata.coords:
            payload[name] = np.asarray(kdata.coords[name].values)
    payload.update(
        {
            "source_path": np.array(meta["source_path"]),
            "offsets": np.array(json.dumps(meta["offsets"])),
            "gamma_method": np.array(meta["gamma_method"]),
            "inner_potential": np.array(np.nan),
            "hv": np.array(meta.get("hv", np.nan)),
            "energy_convention": np.array(meta["energy_convention"]),
            "ef_fit_eV": np.array(meta["ef_fit_eV"]),
            "ef_fit_per_hv": np.asarray(meta.get("ef_fit_per_hv", np.array([]))),
            "ef_deviation_meV": np.array(meta["ef_deviation_meV"]),
            "ef_qc_passed": np.array(bool(meta["ef_qc_passed"])),
            "charging_warning": np.array(bool(meta["charging_warning"])),
            "grid_spec": np.array(meta.get("grid_spec") or "package default"),
            "assumptions": np.array(meta["assumptions"]),
            "created_utc": np.array(meta["created_utc"]),
            "skill_ref": np.array("arpes"),
            "kspace_provenance": np.array("convert_to_kspace"),
        }
    )
    np.savez_compressed(path, **payload)
    return str(path)


def run_convert(
    da,
    *,
    source_path,
    out_dir,
    stem,
    mode,
    gamma_method,
    offsets,
    energy_label,
    ef_fit_eV,
    ef_fit_source,
    convert_fn,
    apply_offsets_fn,
    shift_fn,
):
    plan = prepare_k(
        da,
        mode=mode,
        gamma_method=gamma_method,
        offsets=offsets,
        energy_label=energy_label,
    )
    if ef_fit_eV is None:
        raise PolicyRefusal(
            "ef_fit_eV is required from a package Fermi-edge fit. This script does not invent one."
        )
    ef_fit_eV = float(ef_fit_eV)
    deviation = abs(ef_fit_eV) * 1000.0
    charging = plan["energy_label"] in {"E-EF", "Eb"} and deviation > 50
    energy_dim = plan["axes"]["energy"]["dim"]
    current = da
    shifted = False
    if abs(ef_fit_eV) >= 1e-4:
        if shift_fn is None:
            raise PolicyRefusal("shift_fn missing; refusing convert while EF is away from 0")
        current = shift_fn(current, energy_dim, ef_fit_eV)
        shifted = True
    if plan["apply_offsets"]:
        if apply_offsets_fn is None:
            raise PolicyRefusal("apply_offsets_fn missing")
        current = apply_offsets_fn(current, plan["offsets"])
    if convert_fn is None:
        raise PolicyRefusal("convert_fn missing")
    kdata = convert_fn(current)
    if not hasattr(kdata, "dims") or not hasattr(kdata, "values"):
        raise PolicyRefusal("convert_to_kspace did not return an array with dims")
    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    assumptions = (
        f"in-plane only; gamma_method={plan['gamma_method']}; "
        f"energy={plan['energy_label']}; ef_fit_source={ef_fit_source}; "
        "no kz; no hand-written k formula; "
        + (
            "package shift_by(energy=-EF_fit); post-shift edge refit not run"
            if shifted
            else "EF_fit already within 0.1 meV of 0; no shift"
        )
    )
    meta = {
        "source_path": str(source_path),
        "offsets": plan["offsets"],
        "gamma_method": plan["gamma_method"],
        "hv": np.nan,
        "energy_convention": plan["energy_label"],
        "ef_fit_eV": ef_fit_eV,
        "ef_fit_per_hv": np.array([]),
        "ef_deviation_meV": deviation,
        "ef_qc_passed": not shifted,
        "charging_warning": charging,
        "grid_spec": "package default",
        "assumptions": assumptions,
        "created_utc": created,
    }
    out = Path(out_dir) / "kspace" / f"{stem}_k.npz"
    saved = save_k_npz(kdata, out, meta=meta)
    return {
        "npz": saved,
        "dims": list(kdata.dims),
        "gamma_method": plan["gamma_method"],
        "offsets": plan["offsets"],
        "energy_convention": plan["energy_label"],
        "ef_fit_eV": ef_fit_eV,
        "ef_fit_source": ef_fit_source,
        "ef_deviation_meV": deviation,
        "ef_qc_passed": meta["ef_qc_passed"],
        "charging_warning": charging,
        "kind": plan["kind"],
        "assumptions": assumptions,
        "kspace_provenance": "convert_to_kspace",
    }
