"""Experimental selected-note transposition; use a disposable project copy."""
import time
import platform

def transpose_octave(*, execute=False):
    if not execute:
        return {"executed": False, "verified": False}
    if platform.system() != "Darwin":
        raise RuntimeError("macOS required")
    import Quartz as Q
    from AppKit import NSWorkspace
    app = NSWorkspace.sharedWorkspace().frontmostApplication()
    if not app or app.localizedName() != "Logic Pro":
        raise RuntimeError("Logic must be foreground with MIDI notes selected")
    for pressed in (True, False):
        event = Q.CGEventCreateKeyboardEvent(None, 126, pressed)
        Q.CGEventSetFlags(event, Q.kCGEventFlagMaskAlternate | Q.kCGEventFlagMaskShift)
        Q.CGEventPost(Q.kCGHIDEventTap, event)
        time.sleep(.15)
    return {"executed": True, "verified": False, "requested_semitones": 12}

def verify_octave(before, after):
    import librosa
    import numpy as np
    def pitch(path):
        y, sr = librosa.load(str(path), sr=22050, mono=True)
        f, voiced, _ = librosa.pyin(y, fmin=65, fmax=1800, sr=sr)
        valid = f[voiced & np.isfinite(f)]
        if len(valid) < 5:
            raise RuntimeError("Insufficient voiced pitch frames")
        return float(np.median(valid))
    a, b = pitch(before), pitch(after)
    shift = float(12 * np.log2(b/a))
    return {"before_hz": a, "after_hz": b, "measured_semitones": shift,
            "verified": abs(shift-12) <= .5}
