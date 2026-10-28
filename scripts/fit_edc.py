"""One EDC, one package lineshape. Params JSON only — not the curve values."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arpes_hotpath.fit_edc import extract_edc, fit_edc_curve
from arpes_hotpath.jsonutil import jsonable
from arpes_hotpath.load import load_spectrum
from arpes_hotpath.policy import PolicyRefusal


def run(path, backend, lineshape, out_dir, allow_inspect=False, location=None, at=None, background="none"):
    da, used, picked = load_spectrum(
        path, backend=backend, allow_inspect=allow_inspect, location=location
    )
    extracted = extract_edc(da, at=at)
    fit = fit_edc_curve(extracted["curve"], lineshape=lineshape, background=background, n_peaks=1)
    stem = Path(path).stem
    out = Path(out_dir) / "fits" / f"{stem}_edc.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ok": True,
        "backend": used,
        "picked_variable": picked,
        "path": str(path),
        "energy_dim": extracted["energy_dim"],
        "n": extracted["n"],
        "min": extracted["min"],
        "max": extracted["max"],
        "mean": extracted["mean"],
        "fit": fit,
    }
    out.write_text(json.dumps(jsonable(payload), indent=2) + "\n", encoding="utf-8")
    payload["fit_json"] = str(out)
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description="Single EDC peak fit via PyARPES models.")
    parser.add_argument("path")
    parser.add_argument("--backend", required=True, choices=["pyarpes", "arpes_viewer", "inspect-only"])
    parser.add_argument("--allow-inspect", action="store_true")
    parser.add_argument("--location", default=None)
    parser.add_argument("--lineshape", required=True)
    parser.add_argument("--background", default="none")
    parser.add_argument("--at", default=None, help='JSON object of dim to value, e.g. {"phi": 0}')
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        at = json.loads(args.at) if args.at else None
        payload = run(
            args.path,
            args.backend,
            args.lineshape,
            args.out,
            args.allow_inspect,
            args.location,
            at,
            args.background,
        )
    except PolicyRefusal as exc:
        print(json.dumps({"ok": False, "refusal": str(exc)}))
        return 2
    print(
        json.dumps(
            {
                "ok": True,
                "fit_json": payload["fit_json"],
                "lineshape": payload["fit"]["lineshape"],
                "background": payload["fit"]["background"],
                "params": payload["fit"]["params"],
                "backend": payload["backend"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
