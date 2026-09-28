"""MAESTRO measurement log: FITS-first File Name, H5-rich metadata."""
import argparse
import csv
import os
import sys

import h5py
import numpy as np


def clean_string(val):
    """Decodes bytes, strips literal quotes, and formats scientific numbers."""
    if isinstance(val, bytes):
        val = val.decode("utf-8", errors="ignore")

    val = str(val).strip()
    if val.startswith("'") and val.endswith("'"):
        val = val[1:-1]
    if val.startswith('"') and val.endswith('"'):
        val = val[1:-1]
    val = val.strip()

    try:
        f_val = float(val)
        if f_val.is_integer():
            return str(int(f_val))
        return f"{f_val:.5g}"
    except Exception:
        return val


def deep_clean(val):
    """Recursively drills into Numpy Structured Arrays to extract pure text."""
    if isinstance(val, (bytes, str)):
        return clean_string(val)
    if isinstance(val, (list, tuple, np.ndarray, np.void)):
        cleaned = [deep_clean(x) for x in val]
        return " | ".join(filter(None, cleaned))
    return clean_string(val)


def find_value(h_dict, exact_keys, partial_keys=None):
    """Hunts down the value and returns a labeled string."""
    if partial_keys is None:
        partial_keys = []

    for k in exact_keys:
        if k in h_dict:
            return f"{k.title()}: {h_dict[k]}"

    for pk in partial_keys:
        for k, v in h_dict.items():
            if pk in k:
                return f"{k.title()}: {v}"

    return "N/A"


def collect_stems(folder_path):
    """Return sorted unique stems that have .h5 and/or .fits/.fit."""
    stems = {}
    for name in os.listdir(folder_path):
        lower = name.lower()
        if not (
            lower.endswith(".h5")
            or lower.endswith(".fits")
            or lower.endswith(".fit")
        ):
            continue
        stem, ext = os.path.splitext(name)
        ext = ext.lower()
        if ext == ".fit":
            ext = ".fits"
        stems.setdefault(stem, {})[ext] = name
    return dict(sorted(stems.items()))


def preferred_file_name(ext_map):
    """CSV File Name: .fits first, else .h5."""
    if ".fits" in ext_map:
        return ext_map[".fits"]
    return ext_map[".h5"]


def h5_path_for_stem(folder_path, ext_map):
    if ".h5" not in ext_map:
        return None
    return os.path.join(folder_path, ext_map[".h5"])


def fits_only_row(file_name):
    """FITS-only stem: identity + N/A rich columns."""
    return [
        file_name,
        "unknown (fits-only)",
        "None",
        "N/A",
        "N/A",
        "N/A",
        "N/A",
        "N/A",
        "N/A",
        "N/A",
        "N/A",
        "N/A",
        "N/A",
        "N/A",
    ]


def build_row_from_h5(f, file_name):
    """Build a 14-column row from open MH1 H5; file_name is CSV column 0."""
    h_dict = {}
    if "Headers" in f:
        for group_name in f["Headers"].keys():
            if (
                "offset" in group_name.lower()
                or "physical" in group_name.lower()
                or "old" in group_name.lower()
            ):
                continue

            dataset = f["Headers"][group_name]
            if isinstance(dataset, h5py.Dataset):
                for row in dataset:
                    try:
                        if len(row) >= 3:
                            short_key = clean_string(row[0]).lower()
                            val = clean_string(row[2])
                            desc_key = (
                                clean_string(row[3]).lower() if len(row) >= 4 else ""
                            )
                            if desc_key:
                                h_dict[desc_key] = val
                            if short_key:
                                h_dict[short_key] = val
                    except Exception:
                        pass

    raw_comments = []
    if "Comments" in f:
        for c_key in f["Comments"].keys():
            try:
                raw_comments.append(deep_clean(f["Comments"][c_key][()]))
            except Exception:
                pass

    header_comments = [
        v for k, v in h_dict.items() if "comment" in k or "notebook" in k
    ]
    all_comments = " | ".join(set(raw_comments + header_comments))
    if not all_comments:
        all_comments = "None"

    meas_type = "Cut (1D Dispersion)"
    scan_info = h_dict.get("low level scan mode name", "")
    d0_keys = (
        [k.lower() for k in list(f["0D_Data"].keys())] if "0D_Data" in f else []
    )

    has_spat = any(k in d0_keys for k in ["x", "y", "sample x", "sample y"])
    has_ang = any(
        k in d0_keys for k in ["deflection", "slit defl", "manipulator theta"]
    )

    if "xy scan fine" in scan_info.lower():
        meas_type = "XY Scan Fine (Piezo)"
    elif "xy scan" in scan_info.lower() or has_spat:
        meas_type = "XY Spatial Map"
    elif "fermi" in scan_info.lower() or has_ang:
        meas_type = "3D Fermi Map (Angle Sweep)"

    photon_e = find_value(
        h_dict,
        ["beamline energy", "mono energy", "epu energy", "bl_e", "mono_e"],
    )
    polarization = find_value(
        h_dict, ["epu polarization", "polarization", "epu_pol"]
    )

    cryo_temps = {
        "Cryostat_A": "N/A",
        "Cryostat_B": "N/A",
        "Cryostat_C": "N/A",
        "Cryostat_D": "N/A",
    }

    if "0D_Data" in f:
        try:
            d0_keys_list = list(f["0D_Data"].keys())
            for sensor in cryo_temps.keys():
                if sensor in d0_keys_list:
                    try:
                        raw_data = f["0D_Data"][sensor][()]
                        arr = np.atleast_1d(raw_data)
                        if np.issubdtype(arr.dtype, np.number):
                            arr_float = arr.astype(float)
                            valid_data = arr_float[
                                ~np.isnan(arr_float)
                                & (arr_float > 0.1)
                                & (arr_float < 1000)
                            ]
                            if valid_data.size > 0:
                                cryo_temps[sensor] = f"{np.mean(valid_data):.2f}"
                    except Exception:
                        pass
        except Exception:
            pass

    for sensor in cryo_temps.keys():
        if cryo_temps[sensor] == "N/A":
            s_key1 = sensor.lower()
            s_key2 = sensor.lower().replace("_", " ")
            if s_key1 in h_dict:
                cryo_temps[sensor] = h_dict[s_key1]
            elif s_key2 in h_dict:
                cryo_temps[sensor] = h_dict[s_key2]

    manip_data = [
        f"{k.title()}: {v}"
        for k, v in h_dict.items()
        if k.startswith("sample-") or k.startswith("manipulator ")
    ]
    manipulator = " | ".join(manip_data) if manip_data else "N/A"

    defl_data = [f"{k.title()}: {v}" for k, v in h_dict.items() if "defl" in k]
    defl_str = " | ".join(defl_data) if defl_data else "N/A"

    smu_data = [
        f"{k.title()}: {v}"
        for k, v in h_dict.items()
        if "smu" in k or "kthley" in k
    ]
    smu_str = " | ".join(smu_data) if smu_data else "N/A"

    pass_e = find_value(h_dict, ["pass energy", "epass"], ["pass"])
    center_e = find_value(
        h_dict,
        ["center energy", "kinetic energy", "ke_center", "energy"],
        ["kinetic energy", "center energy"],
    )
    lens = find_value(h_dict, ["lens mode", "lensmode", "lens mode name"], ["lens"])
    acq = find_value(h_dict, ["acquisition mode", "acq mode", "acqmode"], ["acq"])

    if acq == "N/A" and "Headers" in f:
        folder_names = [k.lower() for k in f["Headers"].keys()]
        if "daq_swept" in folder_names:
            acq = "Inferred From Folder: Swept"
        elif "daq_fixed" in folder_names:
            acq = "Inferred From Folder: Fixed"

    analyzer = f"{center_e} | {pass_e} | {lens} | {acq}"

    energy_res = find_value(
        h_dict, ["energy resolution", "energyresolution", "e_resolu"]
    )

    row_data = [
        file_name,
        meas_type,
        all_comments,
        photon_e,
        polarization,
        cryo_temps["Cryostat_A"],
        cryo_temps["Cryostat_B"],
        cryo_temps["Cryostat_C"],
        cryo_temps["Cryostat_D"],
        manipulator,
        defl_str,
        smu_str,
        analyzer,
        energy_res,
    ]

    return row_data, meas_type


def extract_maestro_metadata(folder_path, verbose=False):
    csv_file_path = os.path.join(folder_path, "MAESTRO_Measurement_Log.csv")

    headers = [
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

    stems = collect_stems(folder_path)
    if not stems:
        print(f"❌ No .h5 or .fits files found in {folder_path}")
        return None

    n = len(stems)
    print(f"📂 Found {n} file stem(s). Extracting and parsing headers...")

    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)

        for i, (stem, ext_map) in enumerate(stems.items(), start=1):
            file_name = preferred_file_name(ext_map)
            h5_path = h5_path_for_stem(folder_path, ext_map)

            if h5_path is None:
                writer.writerow(fits_only_row(file_name))
                if verbose:
                    print(f"✅ Logged: {file_name} (fits-only)")
                elif i % 25 == 0:
                    print(f"… processed {i}/{n}")
                continue

            row_data = None
            meas_type = ""
            try:
                with h5py.File(h5_path, "r") as f:
                    row_data, meas_type = build_row_from_h5(f, file_name)
            except Exception as e:
                if row_data is not None and "Bad file descriptor" in str(e):
                    pass
                else:
                    print(f"❌ Failed to parse {file_name}: {e}")
                    writer.writerow([file_name, "ERROR", str(e)] + [""] * 11)
                    continue

            if row_data:
                writer.writerow(row_data)
                if verbose:
                    print(f"✅ Logged: {file_name} ({meas_type})")
                elif i % 25 == 0:
                    print(f"… processed {i}/{n}")

    print(f"\n🎉 Done! Log file saved successfully at:\n{csv_file_path}")
    return csv_file_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="MAESTRO measurement log CSV")
    parser.add_argument(
        "folder",
        nargs="?",
        help="Path to MAESTRO data folder",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print one line per file logged",
    )
    args = parser.parse_args(argv)

    if args.folder:
        target = args.folder.strip().strip("'\"")
    else:
        target = input("Paste the path to your MAESTRO data folder: ").strip().strip(
            "'\""
        )

    target = target.replace("\\ ", " ").replace("\\(", "(").replace("\\)", ")")

    if not os.path.isdir(target):
        print(f"Error: not a directory: {target}")
        sys.exit(1)

    result = extract_maestro_metadata(target, verbose=args.verbose)
    if result is None:
        sys.exit(1)


if __name__ == "__main__":
    main()
