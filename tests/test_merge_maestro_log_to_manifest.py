import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from merge_maestro_log_to_manifest import merge_maestro_log, parse_hv, stem_of


CSV_HEADERS = [
    "File Name",
    "Measurement Type",
    "Pre/Post Comments",
    "Photon Energy (eV)",
    "Polarization",
    "Cryostat A (K)",
    "Cryostat B (K)",
    "Cryostat C (K)",
    "Cryostat D (K)",
    "Manipulator Position",
    "Deflection Settings",
    "SMU 1 & 2 Settings",
    "Analyzer Settings",
    "Energy Resolution",
]


def _write_csv(path: Path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        w.writeheader()
        for row in rows:
            w.writerow({h: row.get(h, "N/A") for h in CSV_HEADERS})


def test_stem_of():
    assert stem_of("20260101_00001.fits") == "20260101_00001"
    assert stem_of("only.h5") == "only"


def test_parse_hv():
    assert parse_hv("91.5 eV") == 91.5
    assert parse_hv("N/A") is None
    assert parse_hv("") is None
    assert parse_hv("hv=1.2e2") == 120.0


def test_merge_prefers_fits_and_keeps_comment(tmp_path):
    stem = "20260101_00001"
    (tmp_path / f"{stem}.fits").write_bytes(b"x")
    (tmp_path / f"{stem}.h5").write_bytes(b"yy")
    _write_csv(
        tmp_path / "MAESTRO_Measurement_Log.csv",
        [
            {
                "File Name": f"{stem}.fits",
                "Measurement Type": "Cut",
                "Pre/Post Comments": "sample note",
                "Photon Energy (eV)": "91.5",
            }
        ],
    )
    manifest_path = merge_maestro_log(str(tmp_path))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert len(manifest["files"]) == 1
    entry = manifest["files"][0]
    assert entry["path"].endswith(".fits")
    assert entry["path_alt"].endswith(".h5")
    assert entry["ext"] == ".fits"
    assert entry["backend"] == "pyarpes"
    assert entry["kind"] == "unknown"
    assert entry["log_comment"] == "sample note"
    assert entry["maestro_log"]["meas_type_log"] == "Cut"
    assert entry["hv_eV"] == 91.5
    assert entry["kind"] != entry["maestro_log"]["meas_type_log"]


def test_merge_h5_only_when_no_fits(tmp_path):
    stem = "only"
    (tmp_path / f"{stem}.h5").write_bytes(b"h5data")
    _write_csv(
        tmp_path / "MAESTRO_Measurement_Log.csv",
        [{"File Name": f"{stem}.h5", "Measurement Type": "Fermi"}],
    )
    manifest_path = merge_maestro_log(str(tmp_path))
    entry = json.loads(manifest_path.read_text())["files"][0]
    assert entry["path"].endswith(".h5")
    assert entry["path_alt"] is None
    assert entry["kind"] == "unknown"


def test_merge_preserves_existing_real_kind(tmp_path):
    stem = "peeked"
    (tmp_path / f"{stem}.h5").write_bytes(b"z")
    analysis = tmp_path / "analysis"
    analysis.mkdir()
    (analysis / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "created_utc": "2026-01-01T00:00:00Z",
                "updated_utc": "2026-01-01T00:00:00Z",
                "data_root": str(tmp_path),
                "skill_ref": "arpes",
                "files": [
                    {
                        "stem": stem,
                        "path": str(tmp_path / f"{stem}.h5"),
                        "ext": ".h5",
                        "kind": "cut",
                        "backend": "pyarpes",
                        "preferred_loader": "x",
                        "size_bytes": 1,
                        "mtime_utc": "2026-01-01T00:00:00Z",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    _write_csv(
        tmp_path / "MAESTRO_Measurement_Log.csv",
        [{"File Name": f"{stem}.h5", "Measurement Type": "WrongLabel"}],
    )
    merge_maestro_log(str(tmp_path))
    entry = json.loads((analysis / "manifest.json").read_text())["files"][0]
    assert entry["kind"] == "cut"
    assert entry["maestro_log"]["meas_type_log"] == "WrongLabel"


def test_merge_preserves_existing_load_error_kind(tmp_path):
    stem = "badpeek"
    (tmp_path / f"{stem}.h5").write_bytes(b"z")
    analysis = tmp_path / "analysis"
    analysis.mkdir()
    (analysis / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "created_utc": "2026-01-01T00:00:00Z",
                "updated_utc": "2026-01-01T00:00:00Z",
                "data_root": str(tmp_path),
                "skill_ref": "arpes",
                "files": [
                    {
                        "stem": stem,
                        "path": str(tmp_path / f"{stem}.h5"),
                        "ext": ".h5",
                        "kind": "load_error",
                        "load_error": "peek failed",
                        "backend": "pyarpes",
                        "preferred_loader": "x",
                        "size_bytes": 1,
                        "mtime_utc": "2026-01-01T00:00:00Z",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    _write_csv(
        tmp_path / "MAESTRO_Measurement_Log.csv",
        [{"File Name": f"{stem}.h5", "Measurement Type": "Cut"}],
    )
    merge_maestro_log(str(tmp_path))
    entry = json.loads((analysis / "manifest.json").read_text())["files"][0]
    assert entry["kind"] == "load_error"
    assert entry.get("load_error") == "peek failed"


def test_merge_writes_manifest_md(tmp_path):
    (tmp_path / "a.h5").write_bytes(b"a")
    _write_csv(
        tmp_path / "MAESTRO_Measurement_Log.csv",
        [{"File Name": "a.h5", "Pre/Post Comments": "hi"}],
    )
    merge_maestro_log(str(tmp_path))
    md = (tmp_path / "analysis" / "manifest.md").read_text(encoding="utf-8")
    assert "| a |" in md
    assert "pyarpes" in md


def test_merge_missing_csv_raises(tmp_path):
    import pytest

    with pytest.raises(FileNotFoundError):
        merge_maestro_log(str(tmp_path))
