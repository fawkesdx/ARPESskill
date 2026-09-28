"""Merge MAESTRO_Measurement_Log.csv into analysis/manifest.json (Pass A)."""
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def stem_of(filename: str) -> str:
    return Path(filename).stem


def parse_hv(cell: str):
    if not cell or cell == "N/A":
        return None
    m = re.search(r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", cell)
    return float(m.group(1)) if m else None


def _real_kind(kind) -> bool:
    return kind not in (None, "unknown", "load_error")


def merge_maestro_log(data_root: str, analysis_root: Optional[str] = None) -> Path:
    data_root = Path(data_root).resolve()
    csv_path = data_root / "MAESTRO_Measurement_Log.csv"
    if not csv_path.is_file():
        raise FileNotFoundError(csv_path)
    analysis_root = (
        Path(analysis_root).resolve() if analysis_root else (data_root / "analysis")
    )
    analysis_root.mkdir(parents=True, exist_ok=True)
    manifest_path = analysis_root / "manifest.json"

    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        by_stem = {e["stem"]: e for e in manifest.get("files", [])}
    else:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        manifest = {
            "schema_version": 1,
            "created_utc": now,
            "updated_utc": now,
            "data_root": str(data_root),
            "skill_ref": "arpes",
            "files": [],
        }
        by_stem = {}

    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fname = row["File Name"]
            st = stem_of(fname)
            fits = data_root / f"{st}.fits"
            fit = data_root / f"{st}.fit"
            h5 = data_root / f"{st}.h5"
            if fits.is_file():
                path, path_alt, ext = str(fits), (str(h5) if h5.is_file() else None), ".fits"
            elif fit.is_file():
                path, path_alt, ext = str(fit), (str(h5) if h5.is_file() else None), ".fits"
            elif h5.is_file():
                path, path_alt, ext = str(h5), None, ".h5"
            else:
                path, path_alt, ext = (
                    str(data_root / fname),
                    None,
                    Path(fname).suffix.lower() or ".h5",
                )

            p = Path(path)
            prior = by_stem.get(st, {})
            entry = dict(prior)
            entry.update(
                {
                    "stem": st,
                    "path": path,
                    "path_alt": path_alt,
                    "ext": ext,
                    "preferred_loader": "arpes.io.load_data location=MAESTRO",
                    "backend": "pyarpes",
                    "loader": "MAESTRO",
                    "size_bytes": p.stat().st_size
                    if p.is_file()
                    else entry.get("size_bytes", 0),
                    "mtime_utc": datetime.fromtimestamp(
                        p.stat().st_mtime, timezone.utc
                    ).strftime("%Y-%m-%dT%H:%M:%SZ")
                    if p.is_file()
                    else entry.get("mtime_utc", ""),
                    "log_comment": row.get("Pre/Post Comments") or None,
                    "maestro_log": {
                        "meas_type_log": row.get("Measurement Type"),
                        "photon_energy": row.get("Photon Energy (eV)"),
                        "polarization": row.get("Polarization"),
                        "cryostat_A_K": row.get("Cryostat A (K)"),
                        "cryostat_B_K": row.get("Cryostat B (K)"),
                        "cryostat_C_K": row.get("Cryostat C (K)"),
                        "cryostat_D_K": row.get("Cryostat D (K)"),
                        "manipulator": row.get("Manipulator Position"),
                        "deflection": row.get("Deflection Settings"),
                        "smu": row.get("SMU 1 & 2 Settings"),
                        "analyzer": row.get("Analyzer Settings"),
                        "energy_resolution": row.get("Energy Resolution"),
                    },
                    "hv_eV": parse_hv(row.get("Photon Energy (eV)", "")),
                }
            )
            if _real_kind(prior.get("kind")):
                entry["kind"] = prior["kind"]
            else:
                entry["kind"] = "unknown"
            by_stem[st] = entry

    manifest["files"] = [by_stem[k] for k in sorted(by_stem)]
    manifest["updated_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest["data_root"] = str(data_root)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    md = analysis_root / "manifest.md"
    lines = ["| stem | backend | kind | hv | comment |", "|---|---|---|---|---|"]
    for e in manifest["files"]:
        c = (e.get("log_comment") or "")[:60].replace("|", "/")
        lines.append(
            f"| {e['stem']} | {e.get('backend', '')} | {e.get('kind', '')} | "
            f"{e.get('hv_eV', '')} | {c} |"
        )
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: merge_maestro_log_to_manifest.py <data_folder> [analysis_folder]")
        sys.exit(1)
    data = sys.argv[1]
    analysis = sys.argv[2] if len(sys.argv) > 2 else None
    print(merge_maestro_log(data, analysis))
