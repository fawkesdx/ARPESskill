"""stdio MCP: HDF5 attrs and partial reads."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "mcp_clio_hdf5"))

from arpes_hotpath.stdio_mcp import serve
from tools import TOOL_SPECS


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--list-tools" in argv:
        print(json.dumps([{"name": tool["name"], "description": tool["description"]} for tool in TOOL_SPECS]))
        return 0
    return serve("clio-hdf5", "0.2.0", TOOL_SPECS)


if __name__ == "__main__":
    raise SystemExit(main())
