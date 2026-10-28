"""MCP catalogs and one stdio round-trip. No package physics."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _frame(payload):
    raw = json.dumps(payload).encode("utf-8")
    return f"Content-Length: {len(raw)}\r\n\r\n".encode("utf-8") + raw


def _read_frame(stream):
    headers = {}
    while True:
        line = stream.readline()
        if line in (b"\r\n", b"\n"):
            break
        key, value = line.decode().split(":", 1)
        headers[key.strip().lower()] = value.strip()
    length = int(headers["content-length"])
    return json.loads(stream.read(length).decode())


def test_arpes_tool_catalog_matches_capability_ids():
    proc = subprocess.run(
        [sys.executable, "-m", "mcp_arpes", "--list-tools"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    tools = json.loads(proc.stdout)
    assert 8 <= len(tools) <= 12
    ids = {tool["capability_id"] for tool in tools}
    assert {
        "state_axes",
        "load_spectrum",
        "folder_manifest",
        "overview_plot",
        "fit_peak",
        "convert_k",
    } <= ids


def test_arpes_stdio_lists_tools():
    proc = subprocess.Popen(
        [sys.executable, "-m", "mcp_arpes"],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    proc.stdin.write(
        _frame(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}},
            }
        )
    )
    proc.stdin.write(_frame({"jsonrpc": "2.0", "method": "notifications/initialized"}))
    proc.stdin.write(_frame({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}))
    proc.stdin.close()
    first = _read_frame(proc.stdout)
    second = _read_frame(proc.stdout)
    proc.wait(timeout=10)
    assert first["id"] == 1
    assert first["result"]["serverInfo"]["name"] == "arpes"
    names = [tool["name"] for tool in second["result"]["tools"]]
    assert "state_axes" in names
    assert "convert_k" in names


def test_clio_catalog():
    proc = subprocess.run(
        [sys.executable, "-m", "mcp_clio_hdf5", "--list-tools"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    names = {tool["name"] for tool in json.loads(proc.stdout)}
    assert names == {"hdf5_list", "hdf5_attrs", "hdf5_partial"}
