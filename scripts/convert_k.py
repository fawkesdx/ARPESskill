"""In-plane k via package convert_to_kspace. Refuses overview mode and invented Gamma."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arpes_hotpath.convert_k import package_apply_offsets, package_convert, package_shift_ef, run_convert
from arpes_hotpath.jsonutil import jsonable
from arpes_hotpath.load import load_spectrum
from arpes_hotpath.policy import PolicyRefusal


def run(path, backend, out_dir, mode, gamma_method, offsets, energy_label, ef_fit_eV, allow_inspect=False, location=None):
    da, used, _picked = load_spectrum(
        path, backend=backend, allow_inspect=allow_inspect, location=location
    )
    if used != "pyarpes":
        raise PolicyRefusal(
            f"convert_k on this script calls PyARPES convert_to_kspace. "
            f"Loaded backend is {used}. No formula fallback."
        )
    return run_convert(
        da,
        source_path=path,
        out_dir=out_dir,
        stem=Path(path).stem,
        mode=mode,
        gamma_method=gamma_method,
        offsets=offsets,
        energy_label=energy_label,
        ef_fit_eV=ef_fit_eV,
        ef_fit_source="cli",
        convert_fn=package_convert,
        apply_offsets_fn=package_apply_offsets,
        shift_fn=package_shift_ef,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Package in-plane k conversion.")
    parser.add_argument("path")
    parser.add_argument("--backend", required=True, choices=["pyarpes", "arpes_viewer", "inspect-only"])
    parser.add_argument("--allow-inspect", action="store_true")
    parser.add_argument("--location", default=None)
    parser.add_argument("--mode", default="quick", choices=["quick", "analysis"])
    parser.add_argument("--gamma-method", default=None)
    parser.add_argument("--offsets", default=None, help="JSON object of angle offsets in degrees")
    parser.add_argument("--energy-axis", default=None, choices=["Ek", "Eb", "E-EF", "ambiguous"])
    parser.add_argument("--ef-fit-eV", type=float, default=None)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        offsets = json.loads(args.offsets) if args.offsets else None
        payload = run(
            args.path,
            args.backend,
            args.out,
            args.mode,
            args.gamma_method,
            offsets,
            args.energy_axis,
            args.ef_fit_eV,
            args.allow_inspect,
            args.location,
        )
    except PolicyRefusal as exc:
        print(json.dumps({"ok": False, "refusal": str(exc)}))
        return 2
    print(json.dumps({"ok": True, **jsonable(payload)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
