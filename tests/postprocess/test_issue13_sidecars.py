"""Issue #13 canonical run-result sidecar contract tests."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from rompy.core import result_persistence
from rompy.core.responses import ModelRunFailure, ModelRunSuccess

from rompy_ww3.postprocess.persistence import (
    RUN_JSON,
    build_persisted,
    load_persisted,
    write_persisted,
)

FIXTURES = Path(__file__).parents[1] / "fixtures" / "core_return_schema_v2"
CORE_SHA = "e4fca8d6193a4315684417a31ccd101cba8c2b1c"


def test_core_fixture_hashes_are_frozen() -> None:
    expected = {
        "run_success.json": "9e64d49a896a9fa521daa2cb5d0067517b3b65da5eb380d04c5d72e584d1ce9f",
        "run_failure.json": "d1da8ea12df2c3a40ae00c2f41fc1f345a0d4b2292f12dbeb75c2652eb267643",
    }
    for name, digest in expected.items():
        assert hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest() == digest


@pytest.mark.parametrize(
    ("name", "result_type"),
    [("run_success.json", ModelRunSuccess), ("run_failure.json", ModelRunFailure)],
)
def test_canonical_run_fixture_preserves_typed_payload(name: str, result_type: type) -> None:
    sidecar = result_persistence.load_run_result(FIXTURES / name)
    loaded = load_persisted(FIXTURES / name)
    assert isinstance(sidecar.payload, result_type)
    assert isinstance(loaded, result_type)
    assert loaded.model_dump(mode="json") == sidecar.payload.model_dump(mode="json")
    assert loaded.artifacts
    assert loaded.expected_outputs
    assert loaded.missing_outputs
    assert loaded.metadata["normalized_context"]["config_hash"] == "sha256:fixture-config"


@pytest.mark.parametrize(
    "name",
    [
        "adversarial/malformed.json",
        "adversarial/legacy_v1.json",
        "adversarial/unsupported_v99.json",
        "adversarial/wrong_kind.json",
    ],
)
def test_invalid_and_legacy_documents_are_rejected_with_regeneration_guidance(name: str) -> None:
    with pytest.raises((ValueError, json.JSONDecodeError), match="(?i)(invalid|unsupported|expected|regenerate|canonical)"):
        load_persisted(FIXTURES / name)


def test_ww3_writes_only_core_envelope_and_never_former_flat_shape(tmp_path: Path) -> None:
    result = load_persisted(FIXTURES / "run_success.json")
    destination = write_persisted(build_persisted(result), tmp_path)
    assert destination == tmp_path / RUN_JSON
    raw = json.loads(destination.read_text())
    assert raw["kind"] == "run_result"
    assert raw["schema_version"] == 2
    assert raw["payload"] == result.model_dump(mode="json")
    assert "postprocess" not in raw
    assert "artifact_checksums" not in raw
    assert "config" not in raw


def test_fresh_process_loads_same_typed_model_run_result(tmp_path: Path) -> None:
    script = """
from pathlib import Path
from rompy_ww3.postprocess.persistence import load_persisted
from rompy.core.responses import ModelRunFailure, ModelRunSuccess
result = load_persisted(Path(__import__('sys').argv[1]))
assert isinstance(result, (ModelRunSuccess, ModelRunFailure))
print(result.__class__.__name__)
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(Path(__file__).parents[2] / "src"), *sys.path]
    )
    completed = subprocess.run(
        [sys.executable, "-c", script, str(FIXTURES / "run_success.json")],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    assert completed.stdout.strip() == "ModelRunSuccess"
