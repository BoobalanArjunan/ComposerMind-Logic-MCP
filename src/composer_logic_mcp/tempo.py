"""Native tempo bridge; writes require explicit opt-in."""
import json
import platform
import subprocess
from pathlib import Path


def tempo(bpm: int | None = None, *, execute: bool = False) -> dict:
    if bpm is not None and (type(bpm) is not int or not 40 <= bpm <= 240):
        raise ValueError("BPM must be an integer between 40 and 240")
    if bpm is not None and not execute:
        return {"executed": False, "target_bpm": bpm, "verified": False}
    if platform.system() != "Darwin":
        raise RuntimeError("Logic tempo control requires macOS")
    cmd = ["/usr/bin/swift", str(Path(__file__).with_name("tempo.swift"))]
    if bpm is not None:
        cmd.append(str(bpm))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Tempo bridge failed")
    data = json.loads(result.stdout)
    if bpm is not None and abs(data["bpm"] - bpm) >= 0.01:
        raise RuntimeError("Tempo readback differs from target")
    return {**data, "executed": bpm is not None, "verified": True}
