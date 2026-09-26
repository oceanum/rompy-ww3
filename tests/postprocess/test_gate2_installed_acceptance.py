"""Installed-wheel subprocess acceptance matrix for issue #16 Gate 2."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parents[1] / "fixtures" / "core_return_schema_v2"
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
from rompy.model import ModelRun
from rompy_ww3.postprocess.config import WW3TransferConfig
from rompy_ww3.postprocess.lifecycle import run_transfer_postprocess
from rompy_ww3.postprocess.persistence import (
    build_persisted,
    load_postprocess,
    write_persisted,
)
from rompy_ww3.postprocess.processor import WW3TransferPostprocessor
from rompy_ww3 import cli as cli_module
from rompy_ww3.cli import app
from typer.testing import CliRunner

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

# Direct and CLI paths consume one canonical run sidecar; CLI replay records
# the same request identity as a skipped core pair rather than copying stale
# direct-process metadata.
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
replayed_raw = raw_postprocess(parity)
assert replayed_raw["kind"] == direct_raw["kind"] == "postprocess_result"
assert replayed_raw["payload"]["success"] is True
assert replayed_raw["payload"]["metadata"]["transfer"]["replayed_pairs"] == 1
assert replayed_raw["payload"]["metadata"]["transfer"]["pairs"][0]["request_id"] == direct_raw["payload"]["metadata"]["transfer"]["pairs"][0]["request_id"]
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
assert sum(
    pair["status"] == "succeeded"
    for pair in filtered_raw["payload"]["metadata"]["transfer"]["pairs"]
) == 1
assert (filtered_destination / "wave.nc").is_file()
assert not (filtered_destination / "note.txt").exists()

# Both public policies report the missing local source as a typed failure;
# the core checksum boundary prevents any transfer before that source exists.
for policy in ("CONTINUE", "FAIL_FAST"):
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
    assert sum(
    pair["status"] == "succeeded"
    for pair in payload["metadata"].get("transfer", {}).get("pairs", [])
) == 0
    assert "not a regular file" in payload["error"].lower()
    assert not (destination_path / "z-ok.txt").exists()

# A failed run remains the primary typed postprocess failure through the
# public lifecycle and CLI; transfer evidence cannot mask the model error.
model_failure_root = fixture_root.parent / "model-failure"
write_run(
    model_failure_root,
    model(model_failure_root, "gate2-model-failure", [], failure="model blew up"),
)
model_failure_result = cli(model_failure_root, "mock://temporary-model-failure")
assert model_failure_result.returncode == 1
model_failure_payload = raw_postprocess(model_failure_root)["payload"]
assert model_failure_payload["success"] is False
assert model_failure_payload["error"] == "model blew up"
assert isinstance(load_postprocess(model_failure_root), PostprocessFailure)

# Persistence errors map to a typed failure while retaining the canonical
# sidecar captured immediately before the write failure.
persistence_root = fixture_root.parent / "persistence-failure"
persistence_root.mkdir()
(persistence_root / "present.txt").write_text("present")
missing = model(
    persistence_root,
    "gate2-persistence-failure",
    [Artifact(path="present.txt", artifact_type=ArtifactType.TEXT)],
)
write_run(persistence_root, missing)
original_writer = result_persistence.write_postprocess_result
direct_sidecars = []
def fail_persistence(staging_dir, sidecar):
    direct_sidecars.append(sidecar)
    raise OSError("read-only")
result_persistence.write_postprocess_result = fail_persistence
try:
    persistence_result = ModelRun(
        run_id=missing.run_id,
        output_dir=persistence_root,
        run_id_subdir=False,
    ).postprocess(
        WW3TransferConfig(
            destinations=[f"file://{fixture_root.parent / 'persistence-destination'}"]
        ),
        processor_input=missing,
    )
finally:
    result_persistence.write_postprocess_result = original_writer
assert isinstance(persistence_result, PostprocessFailure)
assert persistence_result.persistence_diagnostic is not None
assert "read-only" in persistence_result.error
assert len(direct_sidecars) == 1
assert direct_sidecars[0].kind == "postprocess_result"
assert direct_sidecars[0].schema_version == 2
assert isinstance(direct_sidecars[0].payload, PostprocessSuccess)
assert persistence_result.persistence_diagnostic.primary_error is None

# Inject the same failure below the installed public CLI/lifecycle path. The
# captured canonical sidecar remains the pre-write success payload, while the
# returned CLI result carries the typed persistence diagnostic.
cli_sidecars = []
cli_results = []
def fail_cli_persistence(staging_dir, sidecar):
    cli_sidecars.append(sidecar)
    raise OSError("read-only")
real_lifecycle = cli_module.run_transfer_postprocess
def capture_cli_result(*args, **kwargs):
    result = real_lifecycle(*args, **kwargs)
    cli_results.append(result)
    return result
result_persistence.write_postprocess_result = fail_cli_persistence
cli_module.run_transfer_postprocess = capture_cli_result
try:
    cli_result = CliRunner().invoke(
        app,
        [
            "postprocess",
            str(persistence_root),
            "-d",
            f"file://{fixture_root.parent / 'persistence-destination'}",
        ],
    )
finally:
    result_persistence.write_postprocess_result = original_writer
    cli_module.run_transfer_postprocess = real_lifecycle
assert cli_result.exit_code == 1, cli_result.stdout + (str(cli_result.exception) if cli_result.exception else "")
assert len(cli_sidecars) == 1
cli_sidecar = cli_sidecars[0]
assert cli_sidecar.kind == "postprocess_result"
assert cli_sidecar.schema_version == 2
assert isinstance(cli_sidecar.payload, PostprocessSuccess)
assert cli_results[0].persistence_diagnostic is not None
assert len(cli_results) == 1
assert isinstance(cli_results[0], PostprocessFailure)
assert cli_results[0].persistence_diagnostic is not None
assert "read-only" in cli_results[0].error
assert cli_results[0].persistence_diagnostic.primary_error is None
assert cli_results[0].persistence_diagnostic.error == persistence_result.persistence_diagnostic.error
assert "Transfer failed" in cli_result.stdout
assert "Transfer completed" not in cli_result.stdout
assert "Skipped" not in cli_result.stdout

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
