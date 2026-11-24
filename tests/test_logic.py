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
        runner=lambda argv: completed("true\n"),
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


def test_status_mac_not_running():
    answer = status(system=lambda: "Darwin", exists=lambda path: True,
                    runner=lambda argv: completed("false\n"))
    assert answer["running"] is False


def test_status_uses_applescript():
    def run(argv):
        assert argv == ["/usr/bin/osascript", "-e", 'application "Logic Pro" is running']
        return completed("true\n")
    assert status(system=lambda: "Darwin", runner=run)["running"] is True


from composer_logic_mcp.logic import track_action


@pytest.mark.parametrize("action,name,menu", [
    ("create_audio", "", "New Audio Track"),
    ("create_instrument", "", "New Software Instrument Track"),
    ("rename", "Test-01", "Rename Track"),
    ("select", "Test-01", "Search and Select Track…"),
])
def test_track_dispatch(action, name, menu):
    commands = []
    def run(argv):
        commands.append(argv)
        return completed()
    assert not track_action(action, name, runner=run)["executed"]
    assert not commands
    result = track_action(action, name, execute=True, system=lambda: "Darwin", runner=run)
    assert result["executed"] and result["verified_state"] is None
    assert commands[0][-2:] == [menu, name]


def test_track_invalid_name():
    with pytest.raises(ValueError):
        track_action("rename", "")


def test_track_non_mac():
    with pytest.raises(LogicAutomationError):
        track_action("create_audio", execute=True, system=lambda: "Linux")


def test_track_invalid_action():
    with pytest.raises(ValueError):
        track_action("delete")
