"""Pass B manifest. Counts on stdout. Full catalog stays on disk."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arpes_hotpath.manifest import write_manifest
from arpes_hotpath.policy import PolicyRefusal


def main(argv=None):
    parser = argparse.ArgumentParser(description="Header-peek folder manifest.")
    parser.add_argument("data_root")
    parser.add_argument("--analysis", required=True, help="Directory for manifest.json")
    args = parser.parse_args(argv)
    try:
        root = Path(args.data_root)
        if not root.is_dir():
            raise PolicyRefusal(f"not a directory: {root}")
        payload = write_manifest(root, args.analysis)
    except PolicyRefusal as exc:
        print(json.dumps({"ok": False, "refusal": str(exc)}))
        return 2
    print(json.dumps({"ok": True, **payload}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
