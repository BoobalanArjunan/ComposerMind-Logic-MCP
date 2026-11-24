"""Advisory acoustic similarity; does not modify audio or QC verdicts."""
import json
from pathlib import Path

def fingerprint(path):
    import librosa
    import numpy as np
    y, sr = librosa.load(path, sr=24000, mono=True)
    if not len(y) or not np.all(np.isfinite(y)) or not np.any(y):
        raise ValueError("Empty, silent or nonfinite audio")
    y = np.pad(y, (0, max(0, 2048-len(y))))
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64)
    mfcc = librosa.feature.mfcc(S=librosa.power_to_db(mel, ref=np.max), n_mfcc=13)[1:]
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    rms = librosa.feature.rms(y=y)[0]
    envelope = np.interp(np.linspace(0, len(rms)-1, 16), np.arange(len(rms)), rms)
    blocks = [np.r_[mfcc.mean(axis=1), mfcc.std(axis=1)],
              np.r_[centroid.mean(), centroid.std(), bandwidth.mean(), bandwidth.std()],
              chroma.mean(axis=1), envelope]
    blocks = [b / max(float(np.linalg.norm(b)), 1e-12) for b in blocks]
    vector = np.concatenate(blocks)
    return vector / max(float(np.linalg.norm(vector)), 1e-12)

def analyze_diversity(manifest_path, threshold=0.98):
    import numpy as np
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between zero and one")
    manifest = json.loads(Path(manifest_path).expanduser().read_text())
    rows = []
    vectors = []
    errors = []
    for sample in manifest["samples"]:
        if sample["status"] != "accepted":
            continue
        try:
            v = fingerprint(sample["path"])
        except Exception as exc:
            errors.append({"path": sample["path"], "error": str(exc)})
            continue
        row = {"path": sample["path"], "nearest_previous": None,
               "similarity": None, "potential_near_duplicate": False}
        if vectors:
            scores = np.asarray(vectors) @ v
            i = int(np.argmax(scores))
            score = float(np.clip(scores[i], -1, 1))
            row.update(nearest_previous=rows[i]["path"], similarity=score,
                       potential_near_duplicate=score >= threshold)
        rows.append(row)
        vectors.append(v)
    return {"engine": "acoustic_fingerprint_v1", "advisory": True,
            "threshold": threshold, "analyzed": len(rows),
            "potential_near_duplicates": sum(r["potential_near_duplicate"] for r in rows),
            "samples": rows, "errors": errors}
