# CM DatasetCore + WaveWash 0.2

This integration uses the **public, read-only Python developer API**
`from wavewash import PROFILES, analyze_file`, not undocumented CLI flags.

## Setup

```bash
git pull origin feat/logic-mcp-prototype
python -m pip install -e ".[dev,wavewash]"
wavewash doctor
python -m pytest -q
```

## Audit existing prepared renders

```bash
PYTHONPATH="$PWD/src" python - <<'PY'
from pathlib import Path
from composer_logic_mcp.server import logic_dataset_audit
root = Path.home() / "ComposerMind-Datasets/Logic-MVP"
print(logic_dataset_audit(
    source_dir=str(root / "automated"),
    manifest_path=str(root / "metadata/dataset_manifest_wavewash.json"),
    wavewash_profile="music_gen"
))
PY
```

Original WAVs remain unchanged. The generated JSON contains native PCM facts
and optional `wavewash` objects for files that pass initial PCM checks and
are not exact duplicates.

- Native reasons (format mismatch, silence, clipping, identical PCM) still apply.
- A WaveWash report with blocking `issues` adds the reason
  `wavewash_rejected`; full issue text and warnings are preserved.
- If WaveWash analysis crashes for an individual sample, it is rejected with
  `wavewash_error` rather than silently accepted.
- Non-finite numerical measurements (e.g. negative-infinite integrated
  loudness on silence) are represented as JSON null.
- WaveWash checks currently use its stock `music_gen` profile; these
  thresholds are **starting points**, not validated for every SFX instrument.
- No automatic repair, resampling, loudness normalization, near-duplicate
  filtering, AU parameter selection, or Logic bounce is performed.
- Re-running the audit rebuilds a fresh atomic manifest snapshot; it does
  not append or alter WAV files.

Default call without `wavewash_profile` retains `native_pcm_v1`
behavior. The WaveWash layer is opt-in to preserve existing results.
