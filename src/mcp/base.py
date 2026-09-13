"""Base JSON-RPC 2.0 Model Context Protocol (MCP) stdio microservice server."""

import asyncio
import json
import sys
from typing import Any, Callable, Coroutine


class MCPServerBase:
    """Lightweight, non-blocking stdio JSON-RPC 2.0 MCP server."""

    def __init__(self, server_name: str, version: str = "1.0.0"):
        self.server_name = server_name
        self.version = version
        self.tools: dict[str, dict[str, Any]] = {}
        self.handlers: dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: Callable[..., Coroutine[Any, Any, Any]],
    ) -> None:
        """Register an executable MCP tool definition and async handler."""
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema,
        }
        self.handlers[name] = handler

    async def dispatch(self, request: dict[str, Any]) -> dict[str, Any] | None:
        """Process a single JSON-RPC 2.0 message."""
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": self.server_name, "version": self.version},
                },
            }

        if method in ("ping", "notifications/initialized"):
            return {"jsonrpc": "2.0", "id": req_id, "result": {}} if req_id is not None else None

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": list(self.tools.values())},
            }

        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name not in self.handlers:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
                }

            try:
                result = await self.handlers[tool_name](**arguments)
                text_content = json.dumps(result, ensure_ascii=False) if isinstance(result, (dict, list)) else str(result)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": text_content}]},
                }
            except Exception as ex:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32603, "message": f"Tool execution failed: {ex}"},
                }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method '{method}' not implemented"},
        }

    async def run_stdio(self) -> None:
        """Run the persistent stdio JSON-RPC loop reading lines from stdin."""
        loop = asyncio.get_running_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        while not reader.at_eof():
            line = await reader.readline()
            if not line:
                break
            raw_str = line.decode("utf-8").strip()
            if not raw_str:
                continue
            try:
                req_obj = json.loads(raw_str)
                resp_obj = await self.dispatch(req_obj)
                if resp_obj is not None:
                    sys.stdout.write(json.dumps(resp_obj) + "\n")
                    sys.stdout.flush()
            except json.JSONDecodeError:
                err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()

    def run_cli(self) -> None:
        """Entrypoint supporting diagnostic --test-ping and interactive stdio."""
        if "--test-ping" in sys.argv:
            res = asyncio.run(self.dispatch({"jsonrpc": "2.0", "id": 1, "method": "ping"}))
            print(f"[OK] {self.server_name} v{self.version} responded to ping: {json.dumps(res)}")
            sys.exit(0)
        asyncio.run(self.run_stdio())


__all__ = ["MCPServerBase"]
