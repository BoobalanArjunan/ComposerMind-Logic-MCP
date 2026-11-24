import json
from types import SimpleNamespace
import pytest
from composer_logic_mcp import tempo as module

def test_dry_run():
    assert module.tempo(140)["executed"] is False

@pytest.mark.parametrize("bpm", [39, 241, 120.5, True])
def test_invalid(bpm):
    with pytest.raises(ValueError):
        module.tempo(bpm, execute=True)

def test_verified_write(monkeypatch):
    monkeypatch.setattr(module.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k:
        SimpleNamespace(returncode=0, stdout=json.dumps({"bpm": 140}), stderr=""))
    assert module.tempo(140, execute=True)["verified"]

def test_wrong_readback(monkeypatch):
    monkeypatch.setattr(module.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k:
        SimpleNamespace(returncode=0, stdout='{"bpm": 121}', stderr=""))
    with pytest.raises(RuntimeError):
        module.tempo(140, execute=True)
