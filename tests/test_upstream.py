import asyncio
import json
import sys
import pytest
from composer_logic_mcp.upstream import configuration, upstream

def test_dry_run():
    result = asyncio.run(upstream("rosa", "logic_plugins", {"action": "set"}))
    assert result["executed"] is False

def test_unknown_backend():
    with pytest.raises(ValueError):
        configuration("unknown")

def test_config(tmp_path, monkeypatch):
    path = tmp_path / "backends.json"
    path.write_text(json.dumps({"rosa": {"command": sys.executable, "args": ["-m", "logic_mcp"]}}))
    monkeypatch.setenv("COMPOSERMIND_BACKENDS", str(path))
    assert configuration("rosa").args == ["-m", "logic_mcp"]

def test_relative_command(tmp_path, monkeypatch):
    path = tmp_path / "backends.json"
    path.write_text(json.dumps({"rosa": {"command": "python"}}))
    monkeypatch.setenv("COMPOSERMIND_BACKENDS", str(path))
    with pytest.raises(ValueError):
        configuration("rosa")


def test_rubenknol_config(tmp_path, monkeypatch):
    path = tmp_path / "backends.json"
    path.write_text(json.dumps({"rubenknol": {"command": sys.executable, "args": ["worker.py"]}}))
    monkeypatch.setenv("COMPOSERMIND_BACKENDS", str(path))
    assert configuration("rubenknol").args == ["worker.py"]
