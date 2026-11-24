"""Read-only visual state detection; never sends UI events."""
import json
import subprocess
from pathlib import Path


def classify(rows):
    texts = [str(r.get("text", "")).strip().casefold() for r in rows
             if float(r.get("confidence", 0)) >= 0.7]
    titles = [t for t in texts if t.startswith(("bounce \"", "bounce “"))]
    if len(titles) == 1 and "save as:" in texts and "cancel" in texts and "bounce" in texts:
        return {"state": "bounce_save", "title": titles[0]}
    return {"state": "unknown"}


def inspect_screen():
    result = subprocess.run(
        ["/usr/bin/swift", str(Path(__file__).with_name("vision.swift"))],
        capture_output=True, text=True, timeout=60, check=True)
    return classify(json.loads(result.stdout))


if __name__ == "__main__":
    print(json.dumps(inspect_screen()))
