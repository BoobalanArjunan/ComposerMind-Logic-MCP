"""Experimental native bounce for a prepared Logic project.

Requires a visible Tracks window, no open dialogs, and preconfigured WAV
bounce settings. Do not interact with the desktop during execution.
"""
import platform
import re
import subprocess
import time
import wave
from pathlib import Path
from threading import Lock

_lock = Lock()

def bounce(filename: str, output_dir: str, *, execute: bool = False) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", filename):
        raise ValueError("Use a simple filename without extension")
    folder = Path(output_dir).expanduser().resolve()
    target = folder / (filename + ".wav")
    if target.exists() or target.is_symlink():
        raise FileExistsError(str(target))
    if not execute:
        return {"executed": False, "verified": False, "path": str(target)}
    if platform.system() != "Darwin":
        raise RuntimeError("macOS required")
    import Quartz as Q
    from AppKit import NSWorkspace
    with _lock:
        folder.mkdir(parents=True, exist_ok=True)
        if any(folder.glob(filename + ".*")):
            raise FileExistsError(str(target))
        workspace = NSWorkspace.sharedWorkspace()
        def focus():
            app = workspace.frontmostApplication()
            if not app or app.localizedName() != "Logic Pro":
                raise RuntimeError("Logic lost focus; inspect UI before retry")
        def key(code, flags=0):
            focus()
            for pressed in (True, False):
                event = Q.CGEventCreateKeyboardEvent(None, code, pressed)
                Q.CGEventSetFlags(event, flags)
                Q.CGEventPost(Q.kCGHIDEventTap, event)
                time.sleep(.15)
        def paste(value):
            focus()
            subprocess.run(["/usr/bin/pbcopy"], input=value.encode(), check=True)
            time.sleep(.5)
            key(9, Q.kCGEventFlagMaskCommand)
            time.sleep(1)
        def activate():
            subprocess.run(["/usr/bin/open", "-a", "Logic Pro"], check=True)
            for _ in range(20):
                app = workspace.frontmostApplication()
                if app and app.localizedName() == "Logic Pro":
                    time.sleep(1)
                    focus()
                    return
                time.sleep(.5)
            raise RuntimeError("Cannot activate Logic")
        cmd = Q.kCGEventFlagMaskCommand
        activate()
        key(11, cmd)
        time.sleep(3)
        key(36)
        time.sleep(3)
        key(0, cmd)
        paste(filename)
        key(5, cmd | Q.kCGEventFlagMaskShift)
        time.sleep(2)
        key(0, cmd)
        paste(str(folder))
        time.sleep(2)
        key(36)
        time.sleep(2)
        if target.exists() or target.is_symlink():
            raise FileExistsError(str(target))
        key(36)
        previous = stable = 0
        for _ in range(90):
            time.sleep(1)
            if not target.is_file():
                continue
            size = target.stat().st_size
            stable = stable + 1 if size > 44 and size == previous else 0
            previous = size
            if stable >= 3:
                with wave.open(str(target), "rb") as audio:
                    rate = audio.getframerate()
                    channels = audio.getnchannels()
                    bits = audio.getsampwidth() * 8
                    frames = audio.getnframes()
                    if (rate, channels, bits) != (48000, 2, 24) or frames <= 0:
                        raise RuntimeError("Unexpected WAV format")
                    if len(audio.readframes(frames)) != frames * channels * 3:
                        raise RuntimeError("Truncated WAV")
                return {"executed": True, "verified": True, "path": str(target),
                        "sample_rate": rate, "channels": channels, "bit_depth": bits,
                        "duration_seconds": frames / rate, "size_bytes": size}
        raise RuntimeError("Render timed out; inspect Logic before retry")
