"""Renderer-independent PCM dataset audit. Never modifies source audio."""
import hashlib
import json
import math
import tempfile
import wave
from pathlib import Path

from .wavewash_bridge import prepare, inspect_file

def audit_wav(path):
    path = Path(path)
    digest = hashlib.sha256()
    peak = total = count = clipped = 0
    with wave.open(str(path), "rb") as w:
        rate, channels, width, frames = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
        if width not in (2, 3, 4) or frames <= 0:
            raise ValueError("Expected nonempty 16/24/32-bit integer PCM")
        scale = 1 << (width * 8 - 1)
        digest.update(f"{rate}:{channels}:{width}:".encode())
        remaining = frames
        while remaining:
            n = min(remaining, 8192)
            raw = w.readframes(n)
            if len(raw) != n * channels * width:
                raise ValueError("Truncated PCM")
            digest.update(raw)
            for i in range(0, len(raw), width):
                v = int.from_bytes(raw[i:i+width], "little", signed=True)
                peak = max(peak, abs(v))
                total += (v / scale) ** 2
                clipped += int(v in (-scale, scale-1))
                count += 1
            remaining -= n
    rms = math.sqrt(total / count)
    reasons = []
    if (rate, channels, width) != (48000, 2, 3):
        reasons.append("format_mismatch")
    if rms < 10 ** (-60 / 20):
        reasons.append("low_rms")
    if clipped:
        reasons.append("full_scale_samples")
    return {"sample_rate": rate, "channels": channels, "bit_depth": width*8,
            "duration_seconds": frames/rate, "pcm_sha256": digest.hexdigest(),
            "peak_dbfs": 20*math.log10(peak/scale) if peak else None,
            "rms_dbfs": 20*math.log10(rms) if rms else None,
            "full_scale_samples": clipped, "reasons": reasons}

def audit_dataset(source_dir, manifest_path, wavewash_profile=None):
    source = Path(source_dir).expanduser().resolve()
    manifest = Path(manifest_path).expanduser().resolve()
    if not source.is_dir():
        raise ValueError("Source directory missing")
    if manifest.suffix.lower() != ".json":
        raise ValueError("Manifest must be JSON")
    ww = prepare(wavewash_profile) if wavewash_profile else None
    rows, seen = [], set()
    for path in sorted(source.iterdir()):
        if not path.is_file() or path.suffix.lower() != ".wav":
            continue
        row = {"path": str(path), "status": "rejected"}
        try:
            row.update(audit_wav(path))
            if not row["reasons"]:
                if row["pcm_sha256"] in seen:
                    row["reasons"].append("exact_pcm_duplicate")
                else:
                    seen.add(row["pcm_sha256"])
                    if ww is not None:
                        try:
                            row["wavewash"] = inspect_file(path, wavewash_profile, ww)
                            if not row["wavewash"]["passed"]:
                                row["reasons"].append("wavewash_rejected")
                        except Exception as exc:
                            row["wavewash"] = {"profile": wavewash_profile, "error": str(exc)}
                            row["reasons"].append("wavewash_error")
                    if not row["reasons"]:
                        row["status"] = "accepted"
        except (OSError, ValueError, EOFError, wave.Error) as exc:
            row["reasons"] = ["invalid_wav"]
            row["error"] = str(exc)
        rows.append(row)
    result = {"schema_version": 1,
              "qa_engine": "native_pcm_v1+wavewash_0.2" if ww else "native_pcm_v1",
              "wavewash_profile": wavewash_profile if ww else None,
              "source": str(source), "total": len(rows),
              "accepted": sum(r["status"] == "accepted" for r in rows),
              "samples": rows}
    result["rejected"] = result["total"] - result["accepted"]
    manifest.parent.mkdir(parents=True, exist_ok=True)
    # Atomic snapshot; reruns rebuild deterministically from source files.
    with tempfile.NamedTemporaryFile(mode="w", dir=manifest.parent, delete=False, encoding="utf-8") as f:
        tmp = Path(f.name)
        json.dump(result, f, indent=2, allow_nan=False)
    try:
        tmp.replace(manifest)
    finally:
        tmp.unlink(missing_ok=True)
    return result
