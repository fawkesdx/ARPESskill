"""Minimal MCP stdio (Content-Length). Enough for tools/list and tools/call."""

import json
import sys


def _read_message():
    headers = {}
    while True:
        line = sys.stdin.buffer.readline()
        if line == b"":
            return None
        if line in (b"\r\n", b"\n"):
            break
        key, value = line.decode("utf-8").split(":", 1)
        headers[key.strip().lower()] = value.strip()
    length = int(headers["content-length"])
    body = sys.stdin.buffer.read(length)
    return json.loads(body.decode("utf-8"))


def _write_message(payload):
    raw = json.dumps(payload).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(raw)}\r\n\r\n".encode("utf-8"))
    sys.stdout.buffer.write(raw)
    sys.stdout.buffer.flush()


def serve(server_name, version, tools):
    by_name = {tool["name"]: tool for tool in tools}
    while True:
        message = _read_message()
        if message is None:
            return 0
        method = message.get("method")
        msg_id = message.get("id")
        if msg_id is None:
            continue
        if method == "initialize":
            _write_message(
                {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": server_name, "version": version},
                    },
                }
            )
            continue
        if method == "ping":
            _write_message({"jsonrpc": "2.0", "id": msg_id, "result": {}})
            continue
        if method == "tools/list":
            listed = [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "inputSchema": tool["inputSchema"],
                }
                for tool in tools
            ]
            _write_message({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": listed}})
            continue
        if method == "tools/call":
            params = message.get("params") or {}
            name = params.get("name")
            arguments = params.get("arguments") or {}
            tool = by_name.get(name)
            if tool is None:
                _write_message(
                    {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": f"unknown tool {name}"}],
                            "isError": True,
                        },
                    }
                )
                continue
            try:
                result = tool["handler"](arguments)
                text = result if isinstance(result, str) else json.dumps(result)
                _write_message(
                    {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": text}],
                            "isError": False,
                        },
                    }
                )
            except Exception as exc:
                _write_message(
                    {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": str(exc)}],
                            "isError": True,
                        },
                    }
                )
            continue
        _write_message(
            {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"method not found: {method}"},
            }
        )
