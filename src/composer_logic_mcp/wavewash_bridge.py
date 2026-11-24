"""Read-only bridge to WaveWash v0.2's public developer API."""
import math
from dataclasses import replace
from pathlib import Path

PROFILES = ("music_gen", "custom", "asr", "tts", "speaker_id")
METRICS = ("sample_rate", "channels", "duration_sec", "clipped_ratio",
           "dc_offset", "snr_db", "silence_ratio", "lufs",
           "crest_factor_db", "mono_sum_loss_db", "dropout_count",
           "spectral_rolloff_hz", "spectral_cliff_db_per_oct")


def prepare(profile_name):
    """Validate dependency and profile before touching any manifests."""
    if profile_name not in PROFILES:
        raise ValueError(f"Unsupported WaveWash profile: {profile_name}")
    try:
        import wavewash
    except ImportError as exc:
        raise RuntimeError(
            "Install WaveWash into this environment: python -m pip install 'wavewash>=0.2,<0.3'"
        ) from exc
    version = wavewash.__version__
    if not version.startswith("0.2."):
        raise RuntimeError(f"WaveWash 0.2.x required; installed {version}")
    return wavewash


def _finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if hasattr(value, "item"):
        return _finite(value.item())
    return value


def inspect_file(path, profile_name, wavewash_module):
    """Return an independent, non-destructive WaveWash QC verdict."""
    profile = replace(wavewash_module.PROFILES[profile_name])
    report = wavewash_module.analyze_file(Path(path), profile)
    metrics = {name: _finite(getattr(report, name, None)) for name in METRICS}
    return {
        "version": wavewash_module.__version__,
        "profile": profile_name,
        "passed": bool(report.passed),
        "issues": list(report.issues),
        "warnings": list(report.warnings),
        "metrics": metrics,
    }
