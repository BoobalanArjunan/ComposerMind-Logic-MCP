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
