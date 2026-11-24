"""Use a locally compiled Vision probe; preserve the original classifier."""
import json
import os
import subprocess
from pathlib import Path
from .vision_state import classify

def inspect_screen():
    executable = Path(os.environ.get("COMPOSERMIND_VISION_BIN",
        str(Path.home() / ".cache/composermind/vision-core"))).expanduser()
    if not executable.is_file():
        raise RuntimeError("Compile VisionCore before using FastRender")
    result = subprocess.run([str(executable)], capture_output=True,
                            text=True, timeout=60, check=True)
    rows = json.loads(result.stdout)
    state = classify(rows)
    if state["state"] == "bounce_save":
        anchors = [r for r in rows if r["text"].strip().casefold() == "save as:" and r["confidence"] >= .7]
        if len(anchors) == 1:
            a = anchors[0]
            # Conservative heuristic: destination selector is below Save As,
            # not a matching folder in the file browser.
            candidates = [r for r in rows if r["confidence"] >= .7
                          and .025 <= r["y"] - a["y"] <= .075
                          and a["x"] <= r["x"] <= a["x"] + .25]
            if len(candidates) == 1:
                state["destination_name"] = candidates[0]["text"].strip().lstrip("• ").casefold()
    return state
