import json
import os
import tempfile

import pytest

from src.evaluation.schemas import build_evaluation_entry


def sample_eval(ts, tr, ds, dr, wt, wd):
    return build_evaluation_entry(ts, tr, ds, dr, wt, wd)


def test_rank_attempts_weighted_average_and_tie_breakers():
    # Weights
    wt = 0.6
    wd = 0.4

    # Attempts with same combined score but different task score for tie-breaker
    a_eval = sample_eval(0.9, "good", 0.3, "ok", wt, wd)  # combined = 0.9*0.6 + 0.3*0.4 = 0.66
    b_eval = sample_eval(0.8, "good", 0.5, "ok", wt, wd)  # combined = 0.8*0.6 + 0.5*0.4 = 0.68
    c_eval = sample_eval(0.9, "good", 0.3, "ok", wt, wd)  # combined = 0.66, same as a

    attempts = [
        {"path": "attempts/ModelA/attempt_1", "model": "ModelA", "evaluation": a_eval},
        {"path": "attempts/ModelB/attempt_2", "model": "ModelB", "evaluation": b_eval},
        {"path": "attempts/ModelC/attempt_3", "model": "ModelC", "evaluation": c_eval},
    ]

    from src.evaluation import ranking

    ranked = ranking.rank_attempts(attempts, weights={"task_relevance": wt, "documentation_relevance": wd})

    # First should be B (highest combined)
    assert ranked[0]["path"] == "attempts/ModelB/attempt_2"

    # A and C tie on combined; tie-break by higher task_relevance score (equal), then model name asc
    assert ranked[1]["path"] == "attempts/ModelA/attempt_1"
    assert ranked[2]["path"] == "attempts/ModelC/attempt_3"


def test_write_metadata_includes_baseline_and_weights_tmpdir():
    wt = 0.5
    wd = 0.5

    from src.evaluation import ranking

    ranked = [
        {"path": "attempts/ModelX/attempt_1", "model": "ModelX", "combined_score": 0.9},
        {"path": "attempts/ModelY/attempt_2", "model": "ModelY", "combined_score": 0.7},
    ]

    with tempfile.TemporaryDirectory() as tmp:
        out_dir = os.path.join(tmp, "COMBINED_RESULTS")
        baseline = ranked[0]["path"]
        metadata = ranking.build_metadata(baseline, {"task_relevance": wt, "documentation_relevance": wd}, ranked)
        assert metadata["baseline_path"] == baseline
        assert metadata["weights"]["task_relevance"] == wt
        assert metadata["weights"]["documentation_relevance"] == wd
        assert isinstance(metadata["ranked"], list)

        ranking.write_metadata(out_dir, metadata)
        path = os.path.join(out_dir, "metadata.json")
        assert os.path.exists(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["baseline_path"] == baseline
        assert data["weights"]["task_relevance"] == wt
        assert len(data["ranked"]) == 2
