"""Synthetic research baseline, independent of Logic Pro."""
import random
import math
from pathlib import Path
import tempfile
import wave
from .diversity import fingerprint
from .dataset import audit_wav

def benchmark(seed=42, budget=12, threshold=0.98):
    import numpy as np
    if not 2 <= budget <= 100:
        raise ValueError("Budget must be 2..100")
    if not 0 <= threshold <= 1:
        raise ValueError("Invalid threshold")
    def run(adaptive, root):
        rng = random.Random(seed)
        history, vectors, rows = [], [], []
        for i in range(budget):
            candidates = [tuple(rng.random() for _ in range(3)) for _ in range(16 if adaptive else 1)]
            p = max(candidates, key=lambda x: min((math.dist(x, h) for h in history), default=0))
            history.append(p)
            t = np.arange(96000) / 48000
            f = 110 * 8**p[0]
            y = (np.sin(2*np.pi*f*t) + p[1]*np.sin(4*np.pi*f*t)) * np.exp(-p[2]*5*t)
            y *= 0.5 / np.max(np.abs(y))
            pcm = (y * 8388607).astype(np.int32)
            stereo = np.repeat(pcm[:,None], 2, axis=1).astype("<i4")
            path = root / f"{i:04}.wav"
            with wave.open(str(path), "wb") as w:
                w.setparams((2,3,48000,0,"NONE","not compressed"))
                w.writeframes(stereo.view(np.uint8).reshape(-1,4)[:,:3].tobytes())
            qc = audit_wav(path)
            similarity = None
            if not qc["reasons"]:
                v = fingerprint(path)
                if vectors:
                    similarity = float(np.clip(np.max(np.asarray(vectors) @ v), -1, 1))
                vectors.append(v)
            rows.append({"parameters": list(p), "pcm_pass": not qc["reasons"],
                         "similarity": similarity, "near_duplicate": similarity is not None and similarity >= threshold})
        return {"attempts": budget, "pcm_passed": len(vectors),
                "near_duplicates": sum(r["near_duplicate"] for r in rows), "samples": rows}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        return {"seed": seed, "budget_per_arm": budget, "threshold": threshold,
                "renderer": "synthetic_harmonic_v1", "random": run(False, root),
                "adaptive": run(True, root)}
