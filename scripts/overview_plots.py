"""Default overview PNGs. Angle space. Writes assumptions JSON. No k convert."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arpes_hotpath.jsonutil import jsonable
from arpes_hotpath.load import load_spectrum
from arpes_hotpath.overview import render_overview
from arpes_hotpath.policy import PolicyRefusal


def run(path, backend, out_dir, allow_inspect=False, location=None, notes=""):
    da, used, picked = load_spectrum(
        path, backend=backend, allow_inspect=allow_inspect, location=location
    )
    da.attrs["backend"] = used
    stem = Path(path).stem
    rendered = render_overview(da, stem=stem, out_dir=out_dir, notes=notes)
    rendered["backend"] = used
    rendered["picked_variable"] = picked
    rendered["path"] = str(path)
    out = Path(out_dir) / "overview" / f"{stem}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = jsonable(rendered)
    out.write_text(json.dumps({"ok": True, **payload}, indent=2) + "\n", encoding="utf-8")
    payload["overview_json"] = str(out)
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description="Angle-space default overview.")
    parser.add_argument("path")
    parser.add_argument("--backend", required=True, choices=["pyarpes", "arpes_viewer", "inspect-only"])
    parser.add_argument("--allow-inspect", action="store_true")
    parser.add_argument("--location", default=None)
    parser.add_argument("--out", required=True, help="Directory for figures/ and overview/")
    parser.add_argument("--notes", default="")
    args = parser.parse_args(argv)
    try:
        payload = run(
            args.path,
            args.backend,
            args.out,
            args.allow_inspect,
            args.location,
            args.notes,
        )
    except PolicyRefusal as exc:
        print(json.dumps({"ok": False, "refusal": str(exc)}))
        return 2
    summary = {
        "ok": True,
        "kind": payload["kind"],
        "plots": payload["plots"],
        "overview_json": payload["overview_json"],
        "energy": payload["axes"]["energy"],
        "angle_as_k": payload["axes"]["angle_as_k"],
        "report_momentum": payload["assumptions"]["momentum_reported"],
        "backend": payload["backend"],
    }
    print(json.dumps(jsonable(summary)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
