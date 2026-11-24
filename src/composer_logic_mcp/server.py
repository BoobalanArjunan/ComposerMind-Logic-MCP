"""MCP stdio entrypoint."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .logic import status, transport, track_action
from .tempo import tempo
from .native_render import bounce
from .upstream import upstream
from .dataset import audit_dataset

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



@mcp.tool()
def logic_create_audio_track(execute: bool = False) -> dict[str, object]:
    """Create an audio track in the active test project; dry-run by default."""
    return track_action("create_audio", execute=execute)


@mcp.tool()
def logic_create_instrument_track(execute: bool = False) -> dict[str, object]:
    """Create a software instrument track; dry-run by default."""
    return track_action("create_instrument", execute=execute)


@mcp.tool()
def logic_rename_track(name: str, execute: bool = False) -> dict[str, object]:
    """Rename the selected track; requires explicit execution and visual verification."""
    return track_action("rename", name, execute=execute)


@mcp.tool()
def logic_select_track(name: str, execute: bool = False) -> dict[str, object]:
    """Search for a track by name; use unique names and verify selection."""
    return track_action("select", name, execute=execute)


@mcp.tool()
def logic_get_tempo() -> dict:
    """Read the active Logic project tempo; may activate Logic."""
    return tempo()


@mcp.tool()
def logic_set_tempo(bpm: int, execute: bool = False) -> dict:
    """Set integer BPM (40–240) with readback; dry-run by default."""
    return tempo(bpm, execute=execute)


@mcp.tool()
async def logic_backend_tools(backend: str) -> dict:
    """Discover tools from an explicitly configured upstream backend."""
    return await upstream(backend)

@mcp.tool()
async def logic_backend_call(backend: str, tool: str, arguments: dict, execute: bool = False) -> dict:
    """Invoke an upstream tool with explicit opt-in. Inspect its result; no automatic fallback."""
    return await upstream(backend, tool, arguments, execute)

@mcp.tool()
def logic_bounce_audio(filename: str, output_dir: str, execute: bool = False) -> dict:
    """Experimental UI bounce. Requires prepared WAV settings, active Tracks window,
    no open dialogs, exclusive desktop use. Changes clipboard. Dry-run by default.
    """
    return bounce(filename, output_dir, execute=execute)


@mcp.tool()
def logic_dataset_audit(source_dir: str, manifest_path: str) -> dict:
    """Audit existing WAV files and write a JSON manifest without opening Logic."""
    result = audit_dataset(source_dir, manifest_path)
    return {k: v for k, v in result.items() if k != "samples"}


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
