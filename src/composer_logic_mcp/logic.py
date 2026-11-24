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
        result = runner(["/usr/bin/pgrep", "-fl", r"/Logic Pro(?: X)?\\.app/Contents/MacOS/Logic Pro"])
        running = bool(result.stdout.strip())
    except LogicAutomationError:
        running = False
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
