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
    def run(mode, root):
        rng = random.Random(seed)
        history, vectors, rows = [], [], []
        for i in range(budget):
            candidates = [tuple(rng.random() for _ in range(3)) for _ in range(16 if mode != 'random' else 1)]
            def score(x):
                exploration = min((math.dist(x, h) for h in history), default=0)
                if mode != "feedback" or not rows:
                    return exploration
                weights = np.exp(-np.array([math.dist(x, h)**2 for h in history]) / 0.08)
                rewards = np.array([0.0 if not r["pcm_pass"] else
                                    1.0 if r["similarity"] is None else
                                    max(0.0, 1.0-r["similarity"]) for r in rows])
                predicted = float(weights @ rewards / max(weights.sum(), 1e-12))
                return exploration + 0.5 * predicted
            p = max(candidates, key=score)
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
                "renderer": "synthetic_harmonic_v1", "random": run("random", root),
                "adaptive": run("parameter", root),
                "feedback": run("feedback", root)}

def benchmark_suite(output_dir, seeds=range(10), budget=100, threshold=0.98):
    """Persist per-attempt results and descriptive statistics."""
    import csv
    import json
    import statistics
    root = Path(output_dir).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    seeds = list(seeds)
    if not seeds:
        raise ValueError("At least one seed required")
    results = [benchmark(seed, budget, threshold) for seed in seeds]
    summary = {}
    for mode in ("random", "adaptive", "feedback"):
        rates = [r[mode]["near_duplicates"]/budget for r in results]
        summary[mode] = {"mean_flag_rate": statistics.mean(rates),
                         "sd_flag_rate": statistics.stdev(rates) if len(rates)>1 else None}
    report = {"results": results, "summary": summary}
    (root/"benchmark.json").write_text(json.dumps(report, indent=2, allow_nan=False))
    with (root/"attempts.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["seed","strategy","attempt","frequency_param","harmonic_param","decay_param","pcm_pass","similarity","near_duplicate"])
        for r in results:
            for mode in summary:
                for i, row in enumerate(r[mode]["samples"]):
                    writer.writerow([r["seed"],mode,i,*row["parameters"],row["pcm_pass"],row["similarity"],row["near_duplicate"]])
    return summary
