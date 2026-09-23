"""Issue #14 canonical WW3 transfer protocol tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest
from rompy.core import result_persistence
from rompy.core.responses import (
    Artifact,
    ArtifactType,
    ModelRunFailure,
    ModelRunSuccess,
    PostprocessFailure,
    PostprocessSuccess,
    RemoteArtifact,
    TimingInfo,
)
from rompy.transfer.manager import TransferBatchResult, TransferItemResult
from typer.testing import CliRunner

from rompy_ww3.cli import app
from rompy_ww3.postprocess.lifecycle import run_transfer_postprocess
from rompy_ww3.postprocess.persistence import (
    build_persisted,
    load_postprocess,
    load_postprocess_state,
    record_postprocess_state,
    write_persisted,
)
from rompy_ww3.postprocess.processor import WW3TransferPostprocessor


def _run(root: Path, artifacts, *, success: bool = True, run_id: str = "issue14"):
    timing = TimingInfo(
        start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
        end_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    common = {
        "run_id": run_id,
        "backend_used": "local",
        "output_dir": str(root),
        "workspace_dir": str(root),
        "artifacts": artifacts,
        "expected_outputs": [],
        "missing_outputs": [],
        "timing": timing,
    }
    if success:
        return ModelRunSuccess(**common)
    return ModelRunFailure(error="model failed", **common)


def test_empty_and_mixed_evidence_are_canonical_and_persisted(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    remote = RemoteArtifact(uri="s3://bucket/remote.nc", artifact_type=ArtifactType.NETCDF)
    result = WW3TransferPostprocessor().process(
        _run(root, [remote]), [f"file://{tmp_path / 'destination'}"]
    )
    assert isinstance(result, PostprocessSuccess)
    assert result.metadata["requested_count"] == 0
    assert result.metadata["remote_count"] == 1
    assert result.metadata["skipped_count"] == 1
    assert load_postprocess(root).model_dump(mode="json") == result.model_dump(mode="json")


def test_all_local_success_preserves_names_checksums_and_counts(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    (root / "one.txt").write_text("one")
    (root / "two.txt").write_text("two")
    result = WW3TransferPostprocessor().process(
        _run(
            root,
            [
                Artifact(path="one.txt", artifact_type=ArtifactType.TEXT),
                Artifact(path="two.txt", artifact_type=ArtifactType.TEXT),
            ],
        ),
        [f"file://{tmp_path / 'destination'}"],
    )
    assert isinstance(result, PostprocessSuccess)
    assert result.metadata["requested_count"] == 2
    assert result.metadata["local_count"] == 2
    assert result.metadata["transferred_count"] == 2
    assert result.metadata["failed_count"] == 0
    assert result.metadata["source_checksums"]["one.txt"].startswith("sha256:")
    assert set(result.metadata["name_map"].values()) == {"one.txt", "two.txt"}


def test_missing_required_source_is_failure(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    required = Artifact(path="required.txt", artifact_type=ArtifactType.TEXT)
    result = WW3TransferPostprocessor().process(
        _run(root, [], success=True).model_copy(update={"expected_outputs": [required]}),
        [f"file://{tmp_path / 'destination'}"],
    )
    assert isinstance(result, PostprocessFailure)
    assert result.metadata["required_missing_count"] == 1
    assert result.metadata["transfer_failures"][0]["reason"] == "missing_required_source"


def _fake_batch(monkeypatch, batch):
    class FakeManager:
        def transfer_files(self, **kwargs):
            return batch

    monkeypatch.setattr("rompy_ww3.postprocess.processor.TransferManager", FakeManager)


def test_accounting_includes_missing_pairs_and_replay_without_retry_inflation(
    tmp_path, monkeypatch
):
    root = tmp_path / "run"
    root.mkdir()
    (root / "observed.txt").write_text("observed")
    destinations = ["mock://one", "mock://two"]
    expected_missing = Artifact(path="missing.txt", artifact_type=ArtifactType.TEXT)
    observed = Artifact(path="observed.txt", artifact_type=ArtifactType.TEXT)
    batch = TransferBatchResult(
        total=2,
        succeeded=2,
        failed=0,
        items=[
            TransferItemResult(root / "observed.txt", destination, "observed.txt", f"{destination}/observed.txt", True)
            for destination in destinations
        ],
    )
    _fake_batch(monkeypatch, batch)
    model_run = _run(root, [observed], run_id="accounting").model_copy(
        update={"expected_outputs": [observed, expected_missing]}
    )
    processor = WW3TransferPostprocessor()
    first = processor.process(model_run, destinations)
    assert isinstance(first, PostprocessFailure)
    assert first.metadata["requested_transfer_count"] == 4
    assert first.metadata["successful_transfer_count"] == 2
    assert first.metadata["failed_transfer_count"] == 2
    assert first.metadata["skipped_transfer_count"] == 0
    assert len(first.metadata["transfer_failures"]) == 2
    assert (
        first.metadata["successful_transfer_count"]
        + first.metadata["failed_transfer_count"]
        + first.metadata["skipped_transfer_count"]
        == first.metadata["requested_transfer_count"]
    )
    second = processor.process(model_run, destinations)
    assert isinstance(second, PostprocessFailure)
    assert second.metadata["requested_transfer_count"] == 4
    assert second.metadata["transferred_count"] == 2
    assert second.metadata["successful_transfer_count"] == 0
    assert second.metadata["failed_transfer_count"] == 2
    assert second.metadata["skipped_transfer_count"] == 2
    assert (
        second.metadata["successful_transfer_count"]
        + second.metadata["failed_transfer_count"]
        + second.metadata["skipped_transfer_count"]
        == second.metadata["requested_transfer_count"]
    )


def test_partial_transfer_returns_successful_artifacts_and_failures(tmp_path, monkeypatch):
    root = tmp_path / "run"
    root.mkdir()
    (root / "ok.txt").write_text("ok")
    (root / "bad.txt").write_text("bad")
    destination = "mock://destination"
    batch = TransferBatchResult(
        total=2,
        succeeded=1,
        failed=1,
        items=[
            TransferItemResult(root / "ok.txt", destination, "ok.txt", destination + "/ok.txt", True),
            TransferItemResult(root / "bad.txt", destination, "bad.txt", destination + "/bad.txt", False, "denied"),
        ],
    )
    _fake_batch(monkeypatch, batch)
    result = WW3TransferPostprocessor().process(
        _run(root, [Artifact(path="ok.txt"), Artifact(path="bad.txt")]), [destination]
    )
    assert isinstance(result, PostprocessFailure)
    assert [artifact.path for artifact in result.artifacts] == ["ok.txt"]
    assert result.metadata["failed_count"] == 1
    assert result.metadata["transfer_failures"][0]["error"] == "denied"


def test_fail_fast_preserves_prior_success_and_first_failure(tmp_path, monkeypatch):
    root = tmp_path / "run"
    root.mkdir()
    (root / "ok.txt").write_text("ok")
    (root / "bad.txt").write_text("bad")
    destination = "mock://destination"
    batches = [
        TransferBatchResult(
            total=1,
            succeeded=1,
            failed=0,
            items=[TransferItemResult(root / "ok.txt", destination, "ok.txt", destination + "/ok.txt", True)],
        ),
        TransferBatchResult(
            total=1,
            succeeded=0,
            failed=1,
            items=[TransferItemResult(root / "bad.txt", destination, "bad.txt", destination + "/bad.txt", False, "denied")],
        ),
    ]
    calls = []

    class SequenceManager:
        def transfer_files(self, **kwargs):
            calls.append(kwargs)
            return batches.pop(0)

    monkeypatch.setattr("rompy_ww3.postprocess.processor.TransferManager", SequenceManager)
    result = WW3TransferPostprocessor().process(
        _run(root, [Artifact(path="ok.txt"), Artifact(path="bad.txt")]),
        [destination],
        failure_policy="FAIL_FAST",
    )
    assert isinstance(result, PostprocessFailure)
    assert [artifact.path for artifact in result.artifacts] == ["ok.txt"]
    assert result.metadata["transferred_count"] == 1
    assert result.metadata["failed_count"] == 1
    assert result.metadata["transfer_failures"][0]["dest_uri"].endswith("bad.txt")
    assert len(calls) == 2


def test_wholly_failed_transfer_is_failure(tmp_path, monkeypatch):
    root = tmp_path / "run"
    root.mkdir()
    (root / "bad.txt").write_text("bad")
    destination = "mock://destination"
    _fake_batch(
        monkeypatch,
        TransferBatchResult(
            total=1,
            succeeded=0,
            failed=1,
            items=[
                TransferItemResult(root / "bad.txt", destination, "bad.txt", destination + "/bad.txt", False, "denied")
            ],
        ),
    )
    result = WW3TransferPostprocessor().process(
        _run(root, [Artifact(path="bad.txt")]), [destination]
    )
    assert isinstance(result, PostprocessFailure)
    assert result.success is False
    assert result.metadata["transferred_count"] == 0
    assert result.metadata["failed_count"] == 1


def test_missing_source_is_failure_with_structured_evidence(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    result = WW3TransferPostprocessor().process(
        _run(root, [Artifact(path="missing.txt", artifact_type=ArtifactType.TEXT)]),
        [f"file://{tmp_path / 'destination'}"],
    )
    assert isinstance(result, PostprocessFailure)
    assert result.metadata["failed_count"] == 1
    assert result.metadata["transfer_failures"][0]["reason"] == "missing_source"


def test_existing_marker_does_not_reuse_changed_run_or_failure_sidecar(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    (root / "old.txt").write_text("old")
    write_persisted(build_persisted(_run(root, [Artifact(path="old.txt")])), root)
    first_destination = f"file://{tmp_path / 'old-destination'}"
    assert run_transfer_postprocess(root, [first_destination]).success is True

    (root / "new.txt").write_text("new")
    changed = _run(root, [Artifact(path="missing-new.txt")], run_id="changed-run")
    write_persisted(build_persisted(changed), root)
    result = run_transfer_postprocess(root, [f"file://{tmp_path / 'new-destination'}"])
    assert isinstance(result, PostprocessFailure)
    assert result.run_id == "changed-run"
    assert result.metadata.get("skipped") is None
    assert "Transfer failed" in result.error


def test_model_failure_never_becomes_transfer_success(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    result = WW3TransferPostprocessor().process(
        _run(root, [], success=False), [f"file://{tmp_path / 'destination'}"]
    )
    assert isinstance(result, PostprocessFailure)
    assert "model failed" in result.error


def test_model_failure_keeps_primary_error_when_required_source_is_missing(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    required = Artifact(path="required.txt", artifact_type=ArtifactType.TEXT)
    model_run = _run(root, [], success=False).model_copy(
        update={"expected_outputs": [required]}
    )
    result = WW3TransferPostprocessor().process(
        model_run, [f"file://{tmp_path / 'destination'}"]
    )
    assert isinstance(result, PostprocessFailure)
    assert result.error == "Model run failed: model failed"
    assert result.metadata["transfer_diagnostic"]["error"].startswith(
        "Required transfer source missing:"
    )


def test_model_failure_keeps_primary_error_when_output_directory_is_missing(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    (root / "observed.txt").write_text("observed")
    model_run = _run(
        root, [Artifact(path="observed.txt")], success=False
    ).model_copy(update={"output_dir": None, "workspace_dir": None})
    result = WW3TransferPostprocessor().process(
        model_run, [f"file://{tmp_path / 'destination'}"]
    )
    assert isinstance(result, PostprocessFailure)
    assert result.error == "Model run failed: model failed"
    assert result.metadata["transfer_diagnostic"]["error"] == (
        "Cannot transfer local artifacts without a model output directory"
    )


def test_arbitrary_inputs_and_outputs_are_rejected(tmp_path):
    processor = WW3TransferPostprocessor()
    with pytest.raises(TypeError, match="ModelRunSuccess or ModelRunFailure"):
        processor.process({"artifacts": []}, [f"file://{tmp_path / 'destination'}"])
    with pytest.raises(TypeError, match="PostprocessSuccess or PostprocessFailure"):
        from rompy_ww3.postprocess.persistence import require_postprocess

        require_postprocess({"success": True})


def test_persistence_failure_keeps_transfer_error(tmp_path, monkeypatch):
    root = tmp_path / "run"
    root.mkdir()
    (root / "missing.txt").unlink(missing_ok=True)
    monkeypatch.setattr(
        result_persistence,
        "write_postprocess_result",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("read-only")),
    )
    result = WW3TransferPostprocessor().process(
        _run(root, [Artifact(path="missing.txt", artifact_type=ArtifactType.TEXT)]),
        [f"file://{tmp_path / 'destination'}"],
    )
    assert isinstance(result, PostprocessFailure)
    assert "Transfer failed" in result.error
    assert result.persistence_diagnostic is not None
    assert result.persistence_diagnostic.primary_error == result.error


def test_fresh_subprocess_loads_and_executes_typed_transfer(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    (root / "field.txt").write_text("field")
    write_persisted(
        build_persisted(_run(root, [Artifact(path="field.txt")])), root
    )
    destination = tmp_path / "destination"
    script = """
from pathlib import Path
import sys
from rompy.core.responses import PostprocessSuccess
from rompy_ww3.postprocess.lifecycle import run_transfer_postprocess
result = run_transfer_postprocess(Path(sys.argv[1]), [sys.argv[2]])
assert isinstance(result, PostprocessSuccess)
print(result.__class__.__name__)
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(Path(__file__).parents[2] / "src"), *sys.path]
    )
    completed = subprocess.run(
        [sys.executable, "-c", script, str(root), f"file://{destination}"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    assert completed.stdout.strip() == "PostprocessSuccess"
    assert isinstance(load_postprocess(root), PostprocessSuccess)


@pytest.mark.parametrize(
    "error",
    [
        "Transfer failed: partial source denied",
        "Required transfer source missing: 1 artifact(s)",
        "Model run failed: model failed",
        "Transfer failed: transfer error (persistence: read-only)",
    ],
)
def test_cli_displays_canonical_failure_error_and_exits_nonzero(
    tmp_path, monkeypatch, error
):
    root = tmp_path / "run"
    root.mkdir()
    failure = PostprocessFailure(
        run_id="cli-failure",
        error=error,
        output_dir=str(root),
        artifacts=[],
        expected_outputs=[],
        missing_outputs=[],
        timing=TimingInfo(
            start_time=datetime.now(timezone.utc), end_time=datetime.now(timezone.utc)
        ),
    )
    monkeypatch.setattr("rompy_ww3.cli.run_transfer_postprocess", lambda *args, **kwargs: failure)
    result = CliRunner().invoke(app, ["postprocess", str(root), "-d", "mock://destination"])
    assert result.exit_code == 1
    assert error in result.stdout
    assert "Transfer completed" not in result.stdout
    assert "Skipped" not in result.stdout


def test_identical_replay_reuses_only_valid_prior_success(tmp_path, monkeypatch):
    root = tmp_path / "run-replay"
    root.mkdir()
    (root / "field.txt").write_text("field")
    destination = f"file://{tmp_path / 'destination-replay'}"
    model_run = _run(root, [Artifact(path="field.txt", artifact_type=ArtifactType.TEXT)])
    write_persisted(build_persisted(model_run), root)
    first = run_transfer_postprocess(root, [destination])
    assert isinstance(first, PostprocessSuccess)

    calls = []
    monkeypatch.setattr(
        "rompy_ww3.postprocess.processor.TransferManager",
        lambda: (_ for _ in ()).throw(AssertionError("replay transferred")),
    )
    second = run_transfer_postprocess(root, [destination])
    assert isinstance(second, PostprocessSuccess)
    assert second.metadata["transfer_identity"] == first.metadata["transfer_identity"]
    assert second.metadata["transferred_count"] == 1
    assert not calls


def test_partial_retry_skips_audited_success_and_merges_evidence(tmp_path, monkeypatch):
    root = tmp_path / "run-retry"
    root.mkdir()
    (root / "ok.txt").write_text("ok")
    (root / "bad.txt").write_text("bad")
    destination = "mock://destination"
    attempts = [
        TransferBatchResult(
            total=2,
            succeeded=1,
            failed=1,
            items=[
                TransferItemResult(root / "ok.txt", destination, "ok.txt", destination + "/ok.txt", True),
                TransferItemResult(root / "bad.txt", destination, "bad.txt", destination + "/bad.txt", False, "denied"),
            ],
        ),
        TransferBatchResult(
            total=1,
            succeeded=1,
            failed=0,
            items=[
                TransferItemResult(root / "bad.txt", destination, "bad.txt", destination + "/bad.txt", True),
            ],
        ),
    ]
    calls = []

    class RetryManager:
        def transfer_files(self, **kwargs):
            calls.append(kwargs)
            return attempts.pop(0)

    monkeypatch.setattr("rompy_ww3.postprocess.processor.TransferManager", RetryManager)
    model_run = _run(
        root,
        [Artifact(path="ok.txt"), Artifact(path="bad.txt")],
    )
    write_persisted(build_persisted(model_run), root)
    first = run_transfer_postprocess(root, [destination])
    assert isinstance(first, PostprocessFailure)
    second = run_transfer_postprocess(root, [destination])
    assert isinstance(second, PostprocessSuccess)
    assert len(calls) == 2
    assert [path.name for path in calls[1]["files"]] == ["bad.txt"]
    assert second.metadata["transferred_count"] == 2
    assert len(second.metadata["transfer_records"]) == 2
    assert len(second.metadata["retry_history"]) == 1


def test_request_identity_covers_run_destination_policy_filter_required_remote_and_options(
    tmp_path, monkeypatch
):
    root = tmp_path / "identity"
    root.mkdir()
    (root / "field.txt").write_text("field")
    base = _run(
        root,
        [Artifact(path="field.txt", artifact_type=ArtifactType.TEXT)],
    )

    class IdentityManager:
        def transfer_files(self, **kwargs):
            items = [
                TransferItemResult(
                    source,
                    destination,
                    target,
                    f"{destination}/{target}",
                    True,
                )
                for source in kwargs["files"]
                for destination in kwargs["destinations"]
                for target in [kwargs["name_map"][source]]
            ]
            return TransferBatchResult(
                total=len(items), succeeded=len(items), failed=0, items=items
            )

    monkeypatch.setattr("rompy_ww3.postprocess.processor.TransferManager", IdentityManager)
    processor = WW3TransferPostprocessor()
    remote_a = RemoteArtifact(uri="s3://bucket/a", artifact_type=ArtifactType.TEXT)
    remote_b = RemoteArtifact(uri="s3://bucket/b", artifact_type=ArtifactType.TEXT)
    variants = [
        (base, ["mock://a"], None, "restart_only", "expected_outputs_required", {}),
        (base.model_copy(update={"run_id": "other"}), ["mock://a"], None, "restart_only", "expected_outputs_required", {}),
        (base, ["mock://b"], None, "restart_only", "expected_outputs_required", {}),
        (base, ["mock://a"], None, "datestamp_all", "expected_outputs_required", {}),
        (base, ["mock://a"], [ArtifactType.NETCDF], "restart_only", "expected_outputs_required", {}),
        (base, ["mock://a"], None, "restart_only", "optional", {}),
        (base, ["mock://a"], None, "restart_only", "expected_outputs_required", {"compression": "gzip"}),
        (base.model_copy(update={"artifacts": [remote_a]}), ["mock://a"], None, "restart_only", "expected_outputs_required", {}),
        (base.model_copy(update={"artifacts": [remote_b]}), ["mock://a"], None, "restart_only", "expected_outputs_required", {}),
    ]
    identities = []
    for run, destinations, filters, naming, required, options in variants:
        result = processor.process(
            run,
            destinations=destinations,
            artifact_types=filters,
            naming_policy=naming,
            required_policy=required,
            **options,
        )
        identities.append(result.metadata["transfer_identity"])
    assert len(set(identities)) == len(identities)
    assert all("gzip" not in identity and "202" not in identity for identity in identities)
    token_a = processor.process(base, ["mock://credentials?token=one"])
    token_b = processor.process(base, ["mock://credentials?token=two"])
    assert token_a.metadata["transfer_identity"] == token_b.metadata["transfer_identity"]


def test_request_identity_changes_for_source_path_and_declared_size(tmp_path, monkeypatch):
    root = tmp_path / "identity-source"
    root.mkdir()
    (root / "one.txt").write_text("one")
    (root / "two.txt").write_text("one")

    class IdentityManager:
        def transfer_files(self, **kwargs):
            items = [
                TransferItemResult(
                    source, destination, kwargs["name_map"][source],
                    f"{destination}/{kwargs['name_map'][source]}", True
                )
                for source in kwargs["files"]
                for destination in kwargs["destinations"]
            ]
            return TransferBatchResult(len(items), len(items), 0, items)

    monkeypatch.setattr("rompy_ww3.postprocess.processor.TransferManager", IdentityManager)
    processor = WW3TransferPostprocessor()
    first = processor.process(
        _run(root, [Artifact(path="one.txt", size_bytes=3)]), ["mock://source"]
    )
    second = processor.process(
        _run(root, [Artifact(path="two.txt", size_bytes=3)]), ["mock://source"]
    )
    third = processor.process(
        _run(root, [Artifact(path="one.txt", size_bytes=99)]), ["mock://source"]
    )
    assert len({first.metadata["transfer_identity"], second.metadata["transfer_identity"], third.metadata["transfer_identity"]}) == 3


def test_destination_query_order_is_canonical_and_credentials_are_excluded():
    processor = WW3TransferPostprocessor()
    first = processor._destination_identity(
        "s3://bucket/path?z=2&a=1&a=0&token=first"
    )
    second = processor._destination_identity(
        "s3://bucket/path?a=0&token=second&a=1&z=2"
    )
    assert first == second
    assert "token" not in first
    assert processor._destination_identity("s3://bucket/path?a=1") != first


def test_model_failure_remains_primary_with_transfer_failure_diagnostic(tmp_path, monkeypatch):
    root = tmp_path / "run-model-failure"
    root.mkdir()
    (root / "bad.txt").write_text("bad")
    destination = "mock://destination"
    _fake_batch(
        monkeypatch,
        TransferBatchResult(
            1,
            0,
            1,
            [TransferItemResult(root / "bad.txt", destination, "bad.txt", destination + "/bad.txt", False, "denied")],
        ),
    )
    result = WW3TransferPostprocessor().process(
        _run(root, [Artifact(path="bad.txt")], success=False), [destination]
    )
    assert isinstance(result, PostprocessFailure)
    assert result.error == "Model run failed: model failed"
    assert result.metadata["transfer_diagnostic"]["failures"][0]["error"] == "denied"
    assert result.metadata["retry_history"][0]["error"] == result.error


def test_concurrent_public_replay_transfers_each_pair_once(tmp_path, monkeypatch):
    root = tmp_path / "run-concurrent"
    root.mkdir()
    (root / "field.txt").write_text("field")
    destination = "mock://destination"
    model_run = _run(root, [Artifact(path="field.txt")])
    write_persisted(build_persisted(model_run), root)
    calls = []
    calls_lock = threading.Lock()

    class SlowManager:
        def transfer_files(self, **kwargs):
            with calls_lock:
                calls.append(kwargs)
            time.sleep(0.1)
            source = kwargs["files"][0]
            target = kwargs["name_map"][source]
            return TransferBatchResult(
                1,
                1,
                0,
                [TransferItemResult(source, destination, target, destination + "/" + target, True)],
            )

    monkeypatch.setattr("rompy_ww3.postprocess.processor.TransferManager", SlowManager)
    results = []
    barrier = threading.Barrier(2)

    def invoke():
        barrier.wait()
        results.append(run_transfer_postprocess(root, [destination]))

    threads = [threading.Thread(target=invoke) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(calls) == 1
    assert len(results) == 2
    assert all(isinstance(result, PostprocessSuccess) for result in results)
    state = json.loads((root / "postprocess_state.json").read_text())
    assert state["steps"]["transfer"]["completed"] is True
    assert isinstance(load_postprocess(root), PostprocessSuccess)


def test_source_checksum_change_invalidates_replay_identity(tmp_path):
    root = tmp_path / "run-checksum"
    root.mkdir()
    (root / "field.txt").write_text("before")
    destination = f"file://{tmp_path / 'destination-checksum'}"
    model_run = _run(root, [Artifact(path="field.txt", artifact_type=ArtifactType.TEXT)])
    write_persisted(build_persisted(model_run), root)
    first = run_transfer_postprocess(root, [destination])
    assert isinstance(first, PostprocessSuccess)
    (root / "field.txt").write_text("after")
    second = run_transfer_postprocess(root, [destination])
    assert isinstance(second, PostprocessSuccess)
    assert second.metadata["transfer_identity"] != first.metadata["transfer_identity"]
    assert (tmp_path / "destination-checksum" / "field.txt").read_text() == "after"


def test_incomplete_or_malformed_state_never_reuses_success_sidecar(tmp_path, monkeypatch):
    root = tmp_path / "run-state"
    root.mkdir()
    (root / "field.txt").write_text("field")
    model_run = _run(root, [Artifact(path="field.txt", artifact_type=ArtifactType.TEXT)])
    destination = f"file://{tmp_path / 'destination-state'}"
    processor = WW3TransferPostprocessor()
    first = processor.process(model_run, [destination])
    assert isinstance(first, PostprocessSuccess)
    calls = []

    class StateManager:
        def transfer_files(self, **kwargs):
            calls.append(kwargs)
            destination_path = Path(destination.removeprefix("file://"))
            destination_path.mkdir(parents=True, exist_ok=True)
            (destination_path / "field.txt").write_text("field")
            return TransferBatchResult(
                total=1,
                succeeded=1,
                failed=0,
                items=[
                    TransferItemResult(
                        root / "field.txt", destination, "field.txt",
                        destination + "/field.txt", True
                    )
                ],
            )

    monkeypatch.setattr("rompy_ww3.postprocess.processor.TransferManager", StateManager)
    (root / "postprocess_state.json").write_text("not json")
    retried_again = processor.process(model_run, [destination])
    assert isinstance(retried_again, PostprocessSuccess)
    assert len(calls) == 1
    recovered_state = load_postprocess_state(root)
    assert recovered_state is not None
    assert recovered_state.get("completed") is True
    assert recovered_state.get("identity") == retried_again.metadata["transfer_identity"]
    assert len(retried_again.metadata["transfer_records"]) == 1
    record = retried_again.metadata["transfer_records"][0]
    assert record["destination"] == destination
    assert processor._record_valid(
        record,
        source=root / "field.txt",
        source_checksum=retried_again.metadata["source_checksums"]["field.txt"],
        destination=destination,
        target_name="field.txt",
    )
    loaded_retry = load_postprocess(root)
    assert len(loaded_retry.metadata["transfer_records"]) == 1
    assert loaded_retry.metadata["transfer_identity"] == recovered_state.get("identity")
    assert processor._record_valid(
        loaded_retry.metadata["transfer_records"][0],
        source=root / "field.txt",
        source_checksum=loaded_retry.metadata["source_checksums"]["field.txt"],
        destination=destination,
        target_name="field.txt",
    )
    replay = processor.process(model_run, [destination])
    assert isinstance(replay, PostprocessSuccess)
    assert len(calls) == 1


def test_destination_disappearance_invalidates_recorded_success(tmp_path, monkeypatch):
    root = tmp_path / "run-destination"
    root.mkdir()
    (root / "field.txt").write_text("field")
    destination_root = tmp_path / "destination-disappears"
    destination = f"file://{destination_root}"
    model_run = _run(root, [Artifact(path="field.txt", artifact_type=ArtifactType.TEXT)])
    processor = WW3TransferPostprocessor()
    first = processor.process(model_run, [destination])
    assert isinstance(first, PostprocessSuccess)
    (destination_root / "field.txt").unlink()
    calls = []

    class DestinationManager:
        def transfer_files(self, **kwargs):
            calls.append(kwargs)
            destination_root.mkdir(exist_ok=True)
            (destination_root / "field.txt").write_text("field")
            return TransferBatchResult(
                1, 1, 0,
                [TransferItemResult(root / "field.txt", destination, "field.txt", destination + "/field.txt", True)],
            )

    monkeypatch.setattr("rompy_ww3.postprocess.processor.TransferManager", DestinationManager)
    second = processor.process(model_run, [destination])
    assert isinstance(second, PostprocessSuccess)
    assert calls



@pytest.mark.parametrize(
    "malformed",
    [
        "not json",
        [],
        7,
        {"steps": []},
        {"steps": {"transfer": []}},
        {"steps": {"transfer": {"state": []}}},
    ],
)
def test_nested_state_shapes_are_repaired_and_replay_reuses(tmp_path, monkeypatch, malformed):
    root = tmp_path / "nested-state"
    root.mkdir()
    (root / "field.txt").write_text("field")
    destination = "mock://nested-state"
    model_run = _run(root, [Artifact(path="field.txt", artifact_type=ArtifactType.TEXT)])
    calls = []

    class StateManager:
        def transfer_files(self, **kwargs):
            calls.append(kwargs)
            source = kwargs["files"][0]
            target = kwargs["name_map"][source]
            return TransferBatchResult(
                total=1,
                succeeded=1,
                failed=0,
                items=[TransferItemResult(source, destination, target, destination + "/" + target, True)],
            )

    monkeypatch.setattr("rompy_ww3.postprocess.processor.TransferManager", StateManager)
    processor = WW3TransferPostprocessor()
    assert isinstance(processor.process(model_run, [destination]), PostprocessSuccess)
    state_path = root / "postprocess_state.json"
    if isinstance(malformed, str):
        state_path.write_text(malformed)
    else:
        state_path.write_text(json.dumps(malformed))
    retried = processor.process(model_run, [destination])
    reused = processor.process(model_run, [destination])
    assert isinstance(retried, PostprocessSuccess)
    assert isinstance(reused, PostprocessSuccess)
    assert len(calls) == 2
    repaired = json.loads(state_path.read_text())
    assert isinstance(repaired, dict)
    assert isinstance(repaired["steps"], dict)
    assert isinstance(repaired["steps"]["transfer"], dict)
    assert isinstance(repaired["steps"]["transfer"].get("state"), dict)


def test_atomic_state_updates_remain_valid_under_concurrent_writes(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    root = tmp_path / "run-atomic"
    root.mkdir()

    def write_state(index):
        record_postprocess_state(
            root,
            "transfer",
            completed=index % 2 == 0,
            state={"identity": f"identity-{index}", "index": index},
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(write_state, range(32)))
    entry = load_postprocess_state(root)
    assert entry is not None
    assert isinstance(entry.get("state"), dict)
    assert (root / "postprocess_state.json").read_text().endswith("\n")


def test_cli_and_lifecycle_use_same_canonical_sidecar(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    (root / "field.txt").write_text("field")
    model_run = _run(root, [Artifact(path="field.txt", artifact_type=ArtifactType.TEXT)])
    write_persisted(build_persisted(model_run), root)
    destination = f"file://{tmp_path / 'destination'}"
    direct = run_transfer_postprocess(root, [destination])
    repeated_destination = f"file://{root.parent / 'destination-repeated'}"
    repeated = run_transfer_postprocess(root, [repeated_destination])
    assert repeated.success is True
    assert repeated.metadata.get("skipped") is None
    assert (root.parent / "destination-repeated" / "field.txt").exists()
    cli = CliRunner().invoke(app, ["postprocess", str(root), "-d", destination])
    assert cli.exit_code == 0
    assert isinstance(direct, PostprocessSuccess)
    persisted = load_postprocess(root)
    assert persisted.metadata["transferred_count"] == direct.metadata["transferred_count"]
    assert json.loads((root / "postprocess_result.json").read_text())["kind"] == "postprocess_result"
