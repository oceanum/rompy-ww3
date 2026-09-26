"""Standalone WW3 transfer entry point over the core postprocess runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rompy.core.responses import PostprocessResult
from rompy.postprocess.protocol import PostprocessFailurePolicy
from rompy.postprocess.runner import run_postprocess_pipeline

from .config import WW3TransferConfig
from .persistence import load_persisted, mark_step_completed, require_postprocess
from .processor import WW3TransferPostprocessor

TRANSFER_STEP = "transfer"


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

    Core owns the context handoff, transfer lifecycle, result construction, and
    canonical postprocess sidecar.  The legacy ``postprocess_state.json`` marker
    is retained only as a read-compatible completion hint for existing callers.
    """
    path = Path(path_or_dir)
    persisted = load_persisted(path)
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
    result = require_postprocess(result)
    if result.success:
        mark_step_completed(root, TRANSFER_STEP, state={"core_owned": True})
    return result
