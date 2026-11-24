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
    return classify(json.loads(result.stdout))
