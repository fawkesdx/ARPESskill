"""Load one file and print axis QC JSON. Does not plot and does not convert."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arpes_hotpath.axes import axes_report
from arpes_hotpath.jsonutil import jsonable
from arpes_hotpath.load import load_spectrum
from arpes_hotpath.policy import PolicyRefusal


def run(path, backend, allow_inspect=False, location=None):
    da, used, picked = load_spectrum(
        path, backend=backend, allow_inspect=allow_inspect, location=location
    )
    report = axes_report(da, source_path=path, backend=used, picked_variable=picked)
    report["momentum_note"] = (
        "angle or pixel is not inverse angstrom; report_momentum is false "
        "unless kspace_provenance is already on the array"
    )
    return jsonable(report)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Axis QC after load. No k conversion.")
    parser.add_argument("path")
    parser.add_argument("--backend", required=True, choices=["pyarpes", "arpes_viewer", "inspect-only"])
    parser.add_argument("--allow-inspect", action="store_true")
    parser.add_argument("--location", default=None)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args(argv)
    try:
        report = run(args.path, args.backend, args.allow_inspect, args.location)
    except PolicyRefusal as exc:
        print(json.dumps({"ok": False, "refusal": str(exc)}))
        return 2
    payload = {"ok": True, **report}
    text = json.dumps(payload)
    print(text)
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
