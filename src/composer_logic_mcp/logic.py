"""Logic Pro inspection and narrowly scoped, opt-in macOS automation."""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path
from typing import Callable

LOGIC_BUNDLES = (
    Path("/Applications/Logic Pro.app"),
    Path("/Applications/Logic Pro X.app"),
)
APPLESCRIPT_TIMEOUT = 12


class LogicAutomationError(RuntimeError):
    """A Logic automation request failed safely."""


def _run_command(argv: list[str], timeout: int = APPLESCRIPT_TIMEOUT) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(argv, check=True, capture_output=True, text=True, timeout=timeout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as error:
        raise LogicAutomationError(f"Command failed: {error}") from error


def status(
    *,
    system: Callable[[], str] = platform.system,
    exists: Callable[[Path], bool] | None = None,
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]] = _run_command,
) -> dict[str, object]:
    """Read-only host inspection; no Logic activation or UI interaction."""
    if system() != "Darwin":
        return {"supported": False, "installed": False, "running": False, "reason": "macOS required"}
    check = exists or (lambda path: path.is_dir())
    installed = any(check(candidate) for candidate in LOGIC_BUNDLES)
    try:
        result = runner(["/usr/bin/osascript", "-e", 'application "Logic Pro" is running'])
        running = result.stdout.strip().lower() == "true"
    except LogicAutomationError as error:
        return {"supported": True, "installed": installed, "running": None, "reason": str(error)}
    return {"supported": True, "installed": installed, "running": running}


def transport(
    action: str,
    *,
    execute: bool = False,
    system: Callable[[], str] = platform.system,
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]] = _run_command,
) -> dict[str, object]:
    """Send only a play/stop toggle, after explicit execute=True.

    Logic's standard Space shortcut toggles play/stop. The requested action cannot
    be guaranteed without observing transport state; therefore we return a
    truthful toggle label, NOT a claim that playback reached a specific state.
    """
    if action not in {"toggle_playback"}:
        raise ValueError("Only 'toggle_playback' is supported; stop/play require state inspection first")
    if not execute:
        return {"executed": False, "action": action, "note": "Dry run. Set execute=True to send Space."}
    if system() != "Darwin":
        raise LogicAutomationError("Logic automation requires macOS")
    script = (
        'tell application "Logic Pro" to activate\n'
        'tell application "System Events" to key code 49\n'
    )
    runner(["/usr/bin/osascript", "-e", script])
    return {
        "executed": True,
        "action": "toggle_playback",
        "verified_state": None,
        "note": "Space sent. Transport state is not verified; keyboard mapping may vary.",
    }


def track_action(
    action: str,
    name: str = "",
    *,
    execute: bool = False,
    system: Callable[[], str] = platform.system,
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]] = _run_command,
) -> dict[str, object]:
    """Dispatch a validated Track menu command; UI outcome requires readback."""
    menus = {
        "create_audio": "New Audio Track",
        "create_instrument": "New Software Instrument Track",
        "rename": "Rename Track",
        "select": "Search and Select Track…",
    }
    if action not in menus:
        raise ValueError("Unsupported track action")
    named = action in {"rename", "select"}
    if named and (not name.strip() or len(name) > 200 or any(ord(c) < 32 or ord(c) > 126 for c in name)):
        raise ValueError("Use a nonempty printable ASCII track name of at most 200 characters")
    if not execute:
        return {"executed": False, "action": action, "name": name, "note": "Dry run"}
    if system() != "Darwin":
        raise LogicAutomationError("Logic automation requires macOS")
    script = (
        'on run argv\n'
        'tell application "System Events"\n'
        'tell process "Logic Pro"\n'
        'set frontmost to true\n'
        'delay 0.5\n'
        'if not (enabled of menu item (item 1 of argv) of menu "Track" of menu bar 1) then error "Track command disabled"\n'
        'click menu item (item 1 of argv) of menu "Track" of menu bar 1\n'
        'delay 0.5\n'
    )
    if named:
        script += 'keystroke (item 2 of argv)\ndelay 1\nkey code 36\n'
    script += 'delay 1\nend tell\nend tell\nend run\n'
    runner(["/usr/bin/osascript", "-e", script, "--", menus[action], name])
    return {"executed": True, "action": action, "name": name,
            "verified_state": None, "note": "Command dispatched; verify track state in Logic."}
