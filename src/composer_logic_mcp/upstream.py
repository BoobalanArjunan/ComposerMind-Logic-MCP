"""Compose independently installed upstream MCP servers over stdio.

No upstream code is vendored. One backend session at a time; no automatic
fallback after a write. The caller must inspect the backend's own readback.
"""
import os
import json
import asyncio
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BACKENDS = ("rosa", "monglong", "logician", "rubenknol")
ALIASES = {"cm_plugincore": "rosa", "cm_studiocore": "monglong",
           "cm_rendercore": "logician", "cm_midicore": "rubenknol"}

def configuration(backend):
    backend = ALIASES.get(backend, backend)
    if backend not in BACKENDS:
        raise ValueError("Unknown backend")
    path = Path(os.environ.get("COMPOSERMIND_BACKENDS", "~/.config/composermind/backends.json")).expanduser()
    config = json.loads(path.read_text())[backend]
    command = Path(config["command"]).expanduser()
    if not command.is_absolute() or not command.is_file():
        raise ValueError("Backend executable must be an existing absolute path")
    args = config.get("args", [])
    if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        raise ValueError("Invalid backend arguments")
    return StdioServerParameters(command=str(command), args=args)

async def upstream(backend, tool=None, arguments=None, execute=False):
    if tool is not None and not execute:
        return {"executed": False, "backend": backend, "tool": tool, "arguments": arguments or {}}
    params = configuration(backend)
    async with asyncio.timeout(180):
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                tools = (await session.list_tools()).tools
                if tool is None:
                    return {"backend": backend, "tools": [t.model_dump(mode="json") for t in tools]}
                if tool not in {t.name for t in tools}:
                    raise ValueError("Tool is not advertised by backend")
                result = await session.call_tool(tool, arguments or {})
                return {"executed": True, "backend": backend, "verified": False,
                        "result": result.model_dump(mode="json")}
