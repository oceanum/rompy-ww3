"""Installed-wheel subprocess acceptance matrix for issue #16 Gate 2."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parents[1] / "fixtures" / "core_return_schema_v2"
FIXTURE_HASHES = {
    "run_success.json": "9e64d49a896a9fa521daa2cb5d0067517b3b65da5eb380d04c5d72e584d1ce9f",
    "run_failure.json": "d1da8ea12df2c3a40ae00c2f41fc1f345a0d4b2292f12dbeb75c2652eb267643",
    "adversarial/legacy_v1.json": "3c43fa6af22b2244292f3366a2c31fc4b2997e049bd98493b215187f1500abd6",
    "adversarial/malformed.json": "6f5e7359678e8924994c6dbfb317d70fb6443042df93c6d531bef3aa73974ba9",
    "adversarial/unsupported_v99.json": "b3975b59c2922984132d9a7e8febb142abb6ef7b36640e1c8db382cbd18d8265",
    "adversarial/wrong_kind.json": "d13d994a831fe9c7b156a08bfa30c4e1bbd8db28aa7628490fc33396db830875",
}

ACCEPTANCE_SCRIPT = r'''
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import sysconfig
from datetime import datetime, timezone
from importlib import import_module
from importlib.metadata import entry_points
from pathlib import Path

from rompy.core import result_persistence
from rompy.core.responses import (
    Artifact,
    ArtifactType,
    ModelRunFailure,
    ModelRunSuccess,
    PostprocessFailure,
    PostprocessSuccess,
    TimingInfo,
)
from rompy_ww3.postprocess.lifecycle import run_transfer_postprocess
from rompy_ww3.postprocess.persistence import (
    build_persisted,
    load_postprocess,
    write_persisted,
)
from rompy_ww3.postprocess.processor import WW3TransferPostprocessor

fixture_root = Path(sys.argv[1]).resolve()
purelib = Path(sysconfig.get_paths()["purelib"]).resolve()
script = Path(sys.executable).parent / "rompy_ww3"
assert script.is_file(), script


def assert_site_package(module_name: str) -> str:
    module = import_module(module_name)
    origin = Path(module.__file__).resolve()
    assert origin.is_relative_to(purelib), (module_name, origin, purelib)
    assert "site-packages" in origin.parts, origin
    assert not origin.is_relative_to(fixture_root), origin
    return str(origin)


origins = {
    name: assert_site_package(name) for name in ("rompy", "rompy_ww3")
}
required = {
    ("console_scripts", "rompy_ww3"),
    ("rompy.config", "ww3multi"),
    ("rompy.config", "ww3shel"),
    ("rompy.postprocess.config", "ww3_transfer"),
}
loaded = {}
for group, name in required:
    matches = [ep for ep in entry_points(group=group) if ep.name == name]
    assert len(matches) == 1, (group, name, matches)
    loaded[name] = matches[0].load()
    assert callable(loaded[name]), (name, loaded[name])
    assert_site_package(matches[0].module)


def command(*args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        list(args),
        cwd=fixture_root.parent / "outside-cwd",
        env={**os.environ, "PYTHONNOUSERSITE": "1"},
        text=True,
        capture_output=True,
        check=False,
    )
    if check:
        assert completed.returncode == 0, completed.stdout + completed.stderr
    return completed


command(str(script), "--help", check=True)
command(str(script), "postprocess", "--help", check=True)


def fixture_hashes() -> dict[str, str]:
    observed = {}
    for relative, expected in {
        "run_success.json": "9e64d49a896a9fa521daa2cb5d0067517b3b65da5eb380d04c5d72e584d1ce9f",
        "run_failure.json": "d1da8ea12df2c3a40ae00c2f41fc1f345a0d4b2292f12dbeb75c2652eb267643",
        "adversarial/legacy_v1.json": "3c43fa6af22b2244292f3366a2c31fc4b2997e049bd98493b215187f1500abd6",
        "adversarial/malformed.json": "6f5e7359678e8924994c6dbfb317d70fb6443042df93c6d531bef3aa73974ba9",
        "adversarial/unsupported_v99.json": "b3975b59c2922984132d9a7e8febb142abb6ef7b36640e1c8db382cbd18d8265",
        "adversarial/wrong_kind.json": "d13d994a831fe9c7b156a08bfa30c4e1bbd8db28aa7628490fc33396db830875",
    }.items():
        digest = hashlib.sha256((fixture_root / relative).read_bytes()).hexdigest()
        assert digest == expected, (relative, digest, expected)
        observed[relative] = digest
    return observed


def model(
    root: Path,
    run_id: str,
    artifacts: list[Artifact],
    expected: list[Artifact] | None = None,
    failure: str | None = None,
):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    common = {
        "run_id": run_id,
        "backend_used": "local",
        "output_dir": str(root),
        "workspace_dir": str(root),
        "artifacts": artifacts,
        "expected_outputs": expected or [],
        "missing_outputs": [],
        "timing": TimingInfo(start_time=start, end_time=start),
        "metadata": {"gate": "2"},
    }
    if failure is not None:
        return ModelRunFailure(success=False, error=failure, **common)
    return ModelRunSuccess(success=True, **common)


def write_run(root: Path, result) -> None:
    root.mkdir(parents=True, exist_ok=True)
    write_persisted(build_persisted(result), root)


def raw_postprocess(root: Path) -> dict:
    raw = json.loads((root / "postprocess_result.json").read_text())
    assert raw["kind"] == "postprocess_result"
    assert raw["schema_version"] == 2
    assert isinstance(raw["payload"]["success"], bool)
    return raw


def cli(root: Path, destination: str, *options: str):
    return command(
        str(script),
        "postprocess",
        str(root),
        "-d",
        destination,
        *options,
    )


fixture_hashes()

# Direct and CLI paths consume one canonical run sidecar and produce identical
# persisted evidence on replay; the CLI performs no alternate serialization.
parity = fixture_root.parent / "parity"
(parity / "outputs").mkdir(parents=True)
(parity / "outputs" / "wave.nc").write_bytes(b"wave")
parity_result = model(
    parity,
    "gate2-parity",
    [Artifact(path="outputs/wave.nc", artifact_type=ArtifactType.NETCDF)],
)
write_run(parity, parity_result)
destination = f"file://{(fixture_root.parent / 'parity-destination').resolve()}"
direct = run_transfer_postprocess(parity, [destination])
assert isinstance(direct, PostprocessSuccess)
direct_raw = raw_postprocess(parity)
replay = cli(parity, destination)
assert replay.returncode == 0, replay.stdout + replay.stderr
assert raw_postprocess(parity) == direct_raw
assert isinstance(load_postprocess(parity), PostprocessSuccess)

# Artifact filters select only the requested type and preserve canonical JSON.
filtered = fixture_root.parent / "filtered"
(filtered / "outputs").mkdir(parents=True)
(filtered / "outputs" / "wave.nc").write_bytes(b"wave")
(filtered / "outputs" / "note.txt").write_text("note")
write_run(
    filtered,
    model(
        filtered,
        "gate2-filter",
        [
            Artifact(path="outputs/wave.nc", artifact_type=ArtifactType.NETCDF),
            Artifact(path="outputs/note.txt", artifact_type=ArtifactType.TEXT),
        ],
    ),
)
filtered_destination = fixture_root.parent / "filtered-destination"
filtered_result = cli(filtered, f"file://{filtered_destination}", "-a", "netcdf")
assert filtered_result.returncode == 0, filtered_result.stdout + filtered_result.stderr
filtered_raw = raw_postprocess(filtered)
assert filtered_raw["payload"]["metadata"]["transferred_count"] == 1
assert (filtered_destination / "wave.nc").is_file()
assert not (filtered_destination / "note.txt").exists()

# CONTINUE transfers observed artifacts while recording required missing output;
# FAIL_FAST exits before any transfer.
for policy, expected_transfers in (("CONTINUE", 1), ("FAIL_FAST", 0)):
    root = fixture_root.parent / policy.lower()
    (root / "outputs").mkdir(parents=True)
    (root / "outputs" / "z-ok.txt").write_text("ok")
    write_run(
        root,
        model(
            root,
            "gate2-" + policy.lower(),
            [
                Artifact(path="outputs/a-missing.txt", artifact_type=ArtifactType.TEXT),
                Artifact(path="outputs/z-ok.txt", artifact_type=ArtifactType.TEXT),
            ],
        ),
    )
    destination_path = fixture_root.parent / (policy.lower() + "-destination")
    result = cli(root, f"file://{destination_path}", "-p", policy)
    assert result.returncode == 1
    payload = raw_postprocess(root)["payload"]
    assert payload["success"] is False
    assert payload["metadata"]["transferred_count"] == expected_transfers
    if expected_transfers:
        assert (destination_path / "z-ok.txt").is_file()

# A canonical model failure remains a typed postprocess failure with a nonzero
# CLI exit and the primary model error retained in the JSON envelope.
model_failure_root = fixture_root.parent / "model-failure"
write_run(
    model_failure_root,
    model(model_failure_root, "gate2-model-failure", [], failure="model blew up"),
)
model_failure_result = cli(model_failure_root, "mock://temporary-model-failure")
assert model_failure_result.returncode == 1
model_failure_payload = raw_postprocess(model_failure_root)["payload"]
assert model_failure_payload["success"] is False
assert "model blew up" in model_failure_payload["error"]
assert isinstance(load_postprocess(model_failure_root), PostprocessFailure)

# Persistence errors map to a typed failure and retain the transfer error.
persistence_root = fixture_root.parent / "persistence-failure"
persistence_root.mkdir()
missing = model(
    persistence_root,
    "gate2-persistence-failure",
    [Artifact(path="missing.txt", artifact_type=ArtifactType.TEXT)],
)
original_writer = result_persistence.write_postprocess_result
result_persistence.write_postprocess_result = lambda *args, **kwargs: (_ for _ in ()).throw(OSError("read-only"))
try:
    persistence_result = WW3TransferPostprocessor().process(
        missing, [f"file://{fixture_root.parent / 'persistence-destination'}"]
    )
finally:
    result_persistence.write_postprocess_result = original_writer
assert isinstance(persistence_result, PostprocessFailure)
assert persistence_result.persistence_diagnostic is not None
assert "Transfer failed" in persistence_result.error

# Core-v1, flat WW3-v1, and all invalid canonical envelopes must be rejected
# with actionable regeneration guidance through the public CLI.
flat = fixture_root.parent / "flat-ww3-v1.json"
flat.write_text(json.dumps({"success": True, "run_id": "flat", "artifacts": []}))
invalid = [
    fixture_root / "adversarial" / "legacy_v1.json",
    fixture_root / "adversarial" / "malformed.json",
    fixture_root / "adversarial" / "unsupported_v99.json",
    fixture_root / "adversarial" / "wrong_kind.json",
    flat,
]
for path in invalid:
    rejected = cli(path, "mock://invalid-sidecar")
    assert rejected.returncode == 1, (path, rejected.stdout, rejected.stderr)
    message = (rejected.stdout + rejected.stderr).lower()
    assert any(word in message for word in ("regenerat", "canonical", "invalid", "unsupported")), message

print(json.dumps({"origins": origins, "fixture_hashes": fixture_hashes(), "matrix": "pass"}, sort_keys=True))
'''


def test_installed_wheel_acceptance_matrix(tmp_path: Path) -> None:
    """Run the public Gate 2 matrix outside the source workspace."""
    fixture_copy = tmp_path / "fixture-evidence" / "core_return_schema_v2"
    shutil.copytree(FIXTURES, fixture_copy)
    outside_cwd = fixture_copy.parent / "outside-cwd"
    outside_cwd.mkdir()
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONNOUSERSITE"] = "1"
    completed = subprocess.run(
        [sys.executable, "-c", ACCEPTANCE_SCRIPT, str(fixture_copy)],
        cwd=outside_cwd,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert '"matrix": "pass"' in completed.stdout
    assert "site-packages" in completed.stdout
