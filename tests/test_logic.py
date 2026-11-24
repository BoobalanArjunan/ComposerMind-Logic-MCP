"""Unit tests that do not require Logic Pro or macOS."""

import subprocess

import pytest

from composer_logic_mcp.logic import LogicAutomationError, status, transport


def completed(stdout: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["fake"], 0, stdout, "")


def test_status_non_mac_does_not_call_runner():
    def never(_):
        raise AssertionError("Unexpected command execution")

    assert status(system=lambda: "Linux", runner=never) == {
        "supported": False, "installed": False, "running": False, "reason": "macOS required"
    }


def test_status_mac_installed_running():
    answer = status(
        system=lambda: "Darwin",
        exists=lambda path: path.name == "Logic Pro.app",
        runner=lambda argv: completed("123 /Applications/Logic Pro.app/Contents/MacOS/Logic Pro"),
    )
    assert answer["installed"] is True
    assert answer["running"] is True


def test_transport_defaults_to_dry_run():
    assert transport("toggle_playback", system=lambda: "Darwin")["executed"] is False


def test_transport_rejects_unsupported_action():
    with pytest.raises(ValueError):
        transport("record", execute=True, system=lambda: "Darwin")


def test_transport_rejects_non_mac():
    with pytest.raises(LogicAutomationError):
        transport("toggle_playback", execute=True, system=lambda: "Linux")


def test_transport_executes_explicit_toggle():
    commands = []

    def run(argv):
        commands.append(argv)
        return completed()

    response = transport("toggle_playback", execute=True, system=lambda: "Darwin", runner=run)
    assert response["executed"] is True
    assert response["verified_state"] is None
    assert commands[0][:2] == ["/usr/bin/osascript", "-e"]
