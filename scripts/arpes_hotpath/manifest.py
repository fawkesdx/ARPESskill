"""Pass B folder manifest. Header / structure peek. No spectrum cubes."""

import json
from datetime import datetime, timezone
from pathlib import Path

import h5py
import numpy as np

from arpes_hotpath.jsonutil import jsonable

DATA_EXTS = frozenset(
    {".fits", ".fit", ".h5", ".hdf5", ".nxs", ".nc", ".krx", ".ibw", ".pxp"}
)
KIND_ENUM = frozenset(
    {"cut", "core_level_2d", "fermi", "hv", "xy", "unknown", "load_error"}
)


def _utc_from_mtime(path):
    stamp = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    return stamp.strftime("%Y-%m-%dT%H:%M:%SZ")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def collect_files(data_root):
    """One directory level. Prefer .fits over a sibling .h5/.hdf5."""
    root = Path(data_root)
    stems = {}
    for path in sorted(root.iterdir()):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext not in DATA_EXTS:
            continue
        slot = stems.setdefault(path.stem, {})
        slot[ext] = path
    rows = []
    for stem, slot in sorted(stems.items()):
        preferred = None
        for ext in (".fits", ".fit", ".nxs", ".nc", ".h5", ".hdf5", ".krx", ".ibw", ".pxp"):
            if ext in slot:
                preferred = slot[ext]
                break
        alt = None
        if preferred.suffix.lower() in (".fits", ".fit"):
            for ext in (".h5", ".hdf5"):
                if ext in slot and slot[ext] != preferred:
                    alt = slot[ext]
                    break
        elif preferred.suffix.lower() in (".h5", ".hdf5"):
            for ext in (".fits", ".fit"):
                if ext in slot:
                    alt = slot[ext]
                    break
        rows.append({"stem": stem, "path": preferred, "alt": alt})
    return rows


def _attr_map(obj, limit=30):
    out = {}
    for key in list(obj.attrs)[:limit]:
        out[str(key)] = jsonable(obj.attrs[key])
    return out


def _hv_from_mapping(mapping):
    if not mapping:
        return None
    for key, value in mapping.items():
        folded = str(key).casefold().replace(" ", "_")
        if folded in {"hv", "photon_energy", "photon_energy_ev", "beamline_energy"}:
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
    return None


def peek_h5(path):
    shapes = {}
    attrs = {}
    root_attrs = {}
    mh1 = False
    with h5py.File(path, "r") as handle:
        root_attrs = _attr_map(handle)
        mh1 = "Headers" in handle

        def visit(name, obj):
            if isinstance(obj, h5py.Dataset):
                shapes[name] = [int(n) for n in obj.shape]
                if obj.attrs:
                    attrs[name] = _attr_map(obj)

        handle.visititems(visit)
    dim_names = []
    for name, shape in shapes.items():
        leaf = name.split("/")[-1]
        if len(shape) == 1 and leaf:
            dim_names.append(leaf)
    hv = _hv_from_mapping(root_attrs)
    if hv is None:
        for group_attrs in attrs.values():
            hv = _hv_from_mapping(group_attrs)
            if hv is not None:
                break
    return {
        "peek_ok": True,
        "load_error": None,
        "shape": _largest_shape(shapes),
        "dims": dim_names or None,
        "hv_eV": hv,
        "mh1": mh1,
        "notes": "h5py shapes and attrs only; dataset values not read",
    }


def _largest_shape(shapes):
    if not shapes:
        return None
    return max(shapes.values(), key=lambda shape: int(np.prod(shape)) if shape else 0)


def peek_fits(path):
    try:
        from astropy.io import fits
    except ImportError:
        return {
            "peek_ok": False,
            "load_error": "astropy not installed; FITS data array not read",
            "shape": None,
            "dims": None,
            "hv_eV": None,
            "mh1": False,
            "notes": "header peek skipped",
        }
    header = fits.getheader(path, 0)
    shape = []
    naxis = int(header.get("NAXIS") or 0)
    for index in range(1, naxis + 1):
        if f"NAXIS{index}" in header:
            shape.append(int(header[f"NAXIS{index}"]))
    mapping = {key: header[key] for key in header if key not in {"COMMENT", "HISTORY"}}
    return {
        "peek_ok": True,
        "load_error": None,
        "shape": shape or None,
        "dims": None,
        "hv_eV": _hv_from_mapping(mapping),
        "mh1": False,
        "notes": "astropy getheader only; HDU data not read",
    }


def peek_file(path):
    ext = path.suffix.lower()
    if ext in {".fits", ".fit"}:
        return peek_fits(path)
    if ext in {".h5", ".hdf5", ".nxs", ".nc"}:
        try:
            return peek_h5(path)
        except Exception as exc:
            return {
                "peek_ok": False,
                "load_error": str(exc),
                "shape": None,
                "dims": None,
                "hv_eV": None,
                "mh1": False,
                "notes": "peek failed",
            }
    return {
        "peek_ok": False,
        "load_error": f"no header peek for {ext}",
        "shape": None,
        "dims": None,
        "hv_eV": None,
        "mh1": False,
        "notes": "size and extension only",
    }


def _backend_for(path, peek, alt):
    ext = path.suffix.lower()
    if ext in {".fits", ".fit"}:
        return "pyarpes", "arpes.io.load_data"
    if ext in {".nxs", ".krx"}:
        return "arpes_viewer", "loader.registry.load"
    if peek.get("mh1") or (alt is not None and peek_file(alt).get("mh1")):
        return "pyarpes", "arpes.io.load_data"
    if ext in {".h5", ".hdf5"} and peek.get("mh1"):
        return "pyarpes", "arpes.io.load_data"
    return None, None


def _kind_from_peek(peek):
    """Provisional only. Measurement-type strings are not kind."""
    dims = [str(name).casefold() for name in (peek.get("dims") or [])]
    if "x" in dims and "y" in dims:
        return "xy", "low", ["peek_dim_names"]
    if any(name in dims for name in ("hv", "photon_energy")):
        return "hv", "low", ["peek_dim_names"]
    if "ev" in dims or "eV".casefold() in dims:
        if any(name in dims for name in ("psi", "theta", "beta")):
            return "fermi", "low", ["peek_dim_names"]
        if any(name in dims for name in ("phi", "pixel")):
            return "cut", "low", ["peek_dim_names"]
    return "unknown", "low", []


def build_manifest(data_root, *, existing=None):
    root = Path(data_root)
    previous = {}
    if existing and isinstance(existing.get("files"), list):
        for row in existing["files"]:
            previous[row.get("stem")] = row
    files = []
    for item in collect_files(root):
        path = item["path"]
        alt = item["alt"]
        peek = peek_file(path)
        if alt is not None and path.suffix.lower() in {".fits", ".fit"}:
            alt_peek = peek_file(alt)
            if alt_peek.get("hv_eV") is not None and peek.get("hv_eV") is None:
                peek["hv_eV"] = alt_peek["hv_eV"]
            peek["mh1"] = bool(peek.get("mh1") or alt_peek.get("mh1"))
        backend, loader = _backend_for(path, peek, alt)
        if backend == "pyarpes" and peek.get("mh1"):
            loader = "arpes.io.load_data location=MAESTRO"
        kind, confidence, clues = _kind_from_peek(peek)
        prior = previous.get(item["stem"]) or {}
        if kind == "unknown" and prior.get("kind") not in (None, "unknown", "load_error"):
            kind = prior["kind"]
            confidence = prior.get("kind_confidence") or confidence
            clues = list(prior.get("kind_clues") or clues) + ["kept_prior_kind"]
        if peek.get("peek_ok") is False and kind == "unknown":
            pass
        entry = {
            "stem": item["stem"],
            "path": str(path),
            "path_alt": None if alt is None else str(alt),
            "ext": path.suffix.lower(),
            "preferred_loader": loader,
            "backend": backend,
            "loader": "MAESTRO" if peek.get("mh1") else None,
            "size_bytes": path.stat().st_size,
            "mtime_utc": _utc_from_mtime(path),
            "kind": kind if kind in KIND_ENUM else "unknown",
            "kind_confidence": confidence,
            "kind_clues": clues,
            "shape": peek.get("shape"),
            "dims": peek.get("dims"),
            "hv_eV": peek.get("hv_eV"),
            "energy_span_eV": None,
            "energy_axis": None,
            "peek_ok": peek.get("peek_ok"),
            "load_ok": peek.get("peek_ok"),
            "load_error": peek.get("load_error"),
            "overview_paths": list(prior.get("overview_paths") or []),
            "product_paths": list(prior.get("product_paths") or []),
            "notes": peek.get("notes"),
        }
        if prior.get("log_comment") is not None:
            entry["log_comment"] = prior["log_comment"]
        if prior.get("maestro_log") is not None:
            entry["maestro_log"] = prior["maestro_log"]
        files.append(entry)
    created = (existing or {}).get("created_utc") or _now()
    return {
        "schema_version": 1,
        "created_utc": created,
        "updated_utc": _now(),
        "data_root": str(root),
        "skill_ref": "arpes",
        "files": files,
    }


def manifest_markdown(manifest):
    lines = [
        "# Folder manifest",
        "",
        f"data_root: `{manifest['data_root']}`",
        "",
        "Peek is provisional. Measurement-log text is not `kind`.",
        "",
        "| stem | backend | kind | hv | shape | peek_ok |",
        "|------|---------|------|----|-------|---------|",
    ]
    for row in manifest["files"]:
        lines.append(
            "| {stem} | {backend} | {kind} | {hv} | {shape} | {peek} |".format(
                stem=row["stem"],
                backend=row.get("backend") or "ask",
                kind=row["kind"],
                hv="" if row.get("hv_eV") is None else row["hv_eV"],
                shape=row.get("shape"),
                peek=row.get("peek_ok"),
            )
        )
    lines.append("")
    return "\n".join(lines)


def write_manifest(data_root, analysis_dir):
    analysis = Path(analysis_dir)
    analysis.mkdir(parents=True, exist_ok=True)
    json_path = analysis / "manifest.json"
    existing = None
    if json_path.is_file():
        existing = json.loads(json_path.read_text(encoding="utf-8"))
    manifest = build_manifest(data_root, existing=existing)
    json_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    md_path = analysis / "manifest.md"
    md_path.write_text(manifest_markdown(manifest), encoding="utf-8")
    counts = {}
    for row in manifest["files"]:
        counts[row["kind"]] = counts.get(row["kind"], 0) + 1
    return {
        "manifest": str(json_path),
        "markdown": str(md_path),
        "n_files": len(manifest["files"]),
        "counts_by_kind": counts,
    }
