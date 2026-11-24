import json
import pytest
from composer_logic_mcp import diversity

def test_similarity(tmp_path, monkeypatch):
    np = pytest.importorskip("numpy")
    vectors = {"a": np.array([1., 0.]), "b": np.array([1., 0.]), "c": np.array([0., 1.])}
    monkeypatch.setattr(diversity, "fingerprint", lambda path: vectors[path])
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"samples": [
        {"path": p, "status": "accepted"} for p in vectors
    ] + [{"path": "ignored", "status": "rejected"}]}))
    result = diversity.analyze_diversity(manifest)
    assert result["analyzed"] == 3
    assert result["potential_near_duplicates"] == 1
    assert result["samples"][1]["nearest_previous"] == "a"
    assert result["samples"][2]["similarity"] == 0
    assert not result["errors"]
    with pytest.raises(ValueError):
        diversity.analyze_diversity(manifest, 1.1)
