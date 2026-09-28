"""Standalone WW3 transfer entry point over the core postprocess runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rompy.core.result_persistence import load_run_result
from rompy.core.responses import PostprocessResult
from rompy.postprocess.protocol import PostprocessFailurePolicy
from rompy.postprocess.runner import run_postprocess_pipeline

from .config import WW3TransferConfig
from .processor import WW3TransferPostprocessor


def run_transfer_postprocess(
    path_or_dir: Path | str,
    destinations: list[str],
    artifact_types: list[Any] | None = None,
    failure_policy: str = "CONTINUE",
    required_policy: str = "expected_outputs_required",
    naming_policy: str = "restart_only",
    max_retries: int = 0,
) -> PostprocessResult:
    """Run WW3 transfer from a persisted canonical run result.

    Core owns the sidecar loading, context handoff, transfer lifecycle, result
    construction, and canonical postprocess persistence.  WW3 does not maintain
    a second lifecycle marker or persistence state document.
    """
    path = Path(path_or_dir)
    persisted = load_run_result(path).payload
    root = path if path.is_dir() else path.parent
    config = WW3TransferConfig(
        destinations=destinations,
        artifact_types=artifact_types,
        failure_policy=failure_policy,
        naming_policy=naming_policy,
        required_policy=required_policy,
        max_retries=max_retries,
    )
    policy = (
        PostprocessFailurePolicy.CONTINUE
        if failure_policy in {"CONTINUE", "continue"}
        else PostprocessFailurePolicy.FAIL_FAST
    )
    result = run_postprocess_pipeline(
        persisted,
        [WW3TransferPostprocessor(config)],
        staging_dir=root,
        failure_policy=policy,
    )
    return result
