import csv
import sys
from pathlib import Path

import h5py
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from maestro_measurement_log import extract_maestro_metadata


def _write_minimal_mh1(path: Path, comment="hello note"):
    """MH1 rows indexed as row[0]=short key, row[2]=value, row[3]=description."""
    with h5py.File(path, "w") as f:
        dt = np.dtype(
            [
                ("short_key", "S64"),
                ("unused", "S8"),
                ("value", "S64"),
                ("description", "S64"),
            ]
        )
        rows = np.array(
            [
                (b"Beamline Energy", b"", b"91.5", b""),
                (b"EPU Polarization", b"", b"0", b""),
                (b"Pass Energy", b"", b"20", b""),
                (b"Lens Mode Name", b"", b"Angular30", b""),
                (b"Low Level Scan Mode Name", b"", b"Cut", b""),
            ],
            dtype=dt,
        )
        g = f.create_group("Headers")
        g.create_dataset("Beamline", data=rows)
        f.create_group("Comments").create_dataset(
            "PreScan", data=np.bytes_(comment)
        )
        d0 = f.create_group("0D_Data")
        d0.create_dataset("Cryostat_A", data=np.array([8.5]))
        d0.create_dataset("Cryostat_B", data=np.array([80.0]))
        d0.create_dataset("Cryostat_C", data=np.array([240.0]))
        d0.create_dataset("Cryostat_D", data=np.array([7.0]))


def test_fits_preferred_file_name_reads_sibling_h5(tmp_path):
    stem = "20260101_00001"
    _write_minimal_mh1(tmp_path / f"{stem}.h5")
    (tmp_path / f"{stem}.fits").write_bytes(b"")
    out = extract_maestro_metadata(str(tmp_path))
    assert Path(out).name == "MAESTRO_Measurement_Log.csv"
    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["File Name"] == f"{stem}.fits"
    assert "91.5" in rows[0]["Photon Energy (eV)"]
    assert "hello note" in rows[0]["Pre/Post Comments"] or rows[0][
        "Pre/Post Comments"
    ] != "None"


def test_h5_only_stem(tmp_path):
    _write_minimal_mh1(tmp_path / "only.h5")
    extract_maestro_metadata(str(tmp_path))
    with open(
        tmp_path / "MAESTRO_Measurement_Log.csv", newline="", encoding="utf-8"
    ) as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["File Name"] == "only.h5"
