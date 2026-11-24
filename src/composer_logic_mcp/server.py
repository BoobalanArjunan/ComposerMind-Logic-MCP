"""MCP stdio entrypoint."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .logic import status, transport

mcp = FastMCP("ComposerMind Logic Pro MCP")


@mcp.tool()
def logic_status() -> dict[str, object]:
    """Check macOS, Logic installation and process status without changing the DAW."""
    return status()


@mcp.tool()
def logic_transport(action: str = "toggle_playback", execute: bool = False) -> dict[str, object]:
    """Dry-run by default. Explicit opt-in sends the Space playback toggle to Logic.

    Supports only action='toggle_playback'. This does not read back transport state.
    Do not assume the action has started or stopped playback.
    """
    return transport(action, execute=execute)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
