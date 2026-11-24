import json
import wave
from composer_logic_mcp.dataset import audit_dataset

def make_wav(path, value):
    with wave.open(str(path), "wb") as w:
        w.setparams((2, 3, 48000, 0, "NONE", "not compressed"))
        w.writeframes(value.to_bytes(3, "little", signed=True) * 200)

def test_audit(tmp_path):
    make_wav(tmp_path / "a.wav", 100000)
    make_wav(tmp_path / "b.wav", 100000)
    make_wav(tmp_path / "c.wav", 0)
    (tmp_path / "d.wav").write_bytes(b"bad")
    target = tmp_path / "manifest.json"
    result = audit_dataset(tmp_path, target)
    assert result["accepted"] == 1
    assert result["rejected"] == 3
    assert result["samples"][1]["reasons"] == ["exact_pcm_duplicate"]
    assert result["samples"][2]["reasons"] == ["low_rms"]
    assert result["samples"][3]["reasons"] == ["invalid_wav"]
    assert json.loads(target.read_text()) == result
    assert audit_dataset(tmp_path, target) == result

def test_wavewash_layer_rejects_and_serializes_nonfinite(tmp_path, monkeypatch):
    import sys
    from dataclasses import dataclass
    from types import SimpleNamespace
    import pytest

    @dataclass
    class FakeProfile:
        name: str

    def inspect(path, profile):
        assert profile.name == "music_gen"
        return SimpleNamespace(
            passed=False, issues=["LOW_SNR: synthetic test"],
            warnings=["FAKE_STEREO"], lufs=float("-inf"),
            sample_rate=48000, snr_db=0.0
        )

    fake = SimpleNamespace(
        __version__="0.2.0", PROFILES={"music_gen": FakeProfile("music_gen")},
        analyze_file=inspect
    )
    monkeypatch.setitem(sys.modules, "wavewash", fake)
    make_wav(tmp_path / "test.wav", 100000)
    manifest = tmp_path / "result.json"
    result = audit_dataset(tmp_path, manifest, "music_gen")
    assert result["accepted"] == 0
    assert result["samples"][0]["reasons"] == ["wavewash_rejected"]
    assert result["samples"][0]["wavewash"]["metrics"]["lufs"] is None
    assert result["samples"][0]["wavewash"]["issues"] == ["LOW_SNR: synthetic test"]
    assert json.loads(manifest.read_text()) == result
    with pytest.raises(ValueError, match="Unsupported"):
        audit_dataset(tmp_path, manifest, "not_a_profile")
