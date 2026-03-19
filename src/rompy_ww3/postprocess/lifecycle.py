from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from rompy.core.responses import (
    PostprocessResult,
    PostprocessSuccess,
)

from .persistence import load_persisted, is_step_completed, mark_step_completed
from .processor import WW3TransferPostprocessor

# Stable step name for transfer postprocess
TRANSFER_STEP = "transfer"


def run_transfer_postprocess(
    path_or_dir: Path | str,
    destinations: list[str],
    artifact_types: Optional[list[Any]] = None,
    failure_policy: str = "CONTINUE",
) -> PostprocessResult:
    """Run the WW3 transfer postprocess for a persisted run result.

    - path_or_dir: directory containing run_result.json or path to run_result.json
    - destinations, artifact_types, failure_policy: forwarded to processor.process

    Behaviour:
    - Loads the persisted run via load_persisted
    - If the transfer step is already marked completed in run_result.json, returns a
      PostprocessSuccess with zero actions (idempotent) using stored run fields.
    - Otherwise invokes WW3TransferPostprocessor.process and on success marks
      the step completed in run_result.json recording transferred/failed counts.

    This function keeps behavior intentionally small and testable.
    """
    p = Path(path_or_dir)

    # Load persisted run result (raises FileNotFoundError if missing)
    persisted = load_persisted(p)

    # If already completed, return early with a light-weight success result
    if is_step_completed(p, TRANSFER_STEP):
        # Build a trivial PostprocessSuccess reflecting no-op
        # We prefer to return a PostprocessSuccess object consistent with
        # rompy.core.responses expectations; construct minimal fields.
        return PostprocessSuccess(
            success=True,
            run_id=getattr(persisted, "run_id", "unknown"),
            output_dir=str(getattr(persisted, "output_dir", "")),
            validated=False,
            file_count=0,
            artifacts=[],
            message="skipped: already completed",
            metadata={"skipped": True},
            timing=None,
        )

    # Not completed yet - run processor
    processor = WW3TransferPostprocessor()
    result = processor.process(
        persisted,
        destinations=destinations,
        artifact_types=artifact_types,
        failure_policy=failure_policy,
    )

    # On success, record completion metadata into run_result.json
    try:
        if isinstance(result, PostprocessSuccess) and result.success:
            state = {}
            meta = getattr(result, "metadata", {}) or {}
            # capture useful counters if present
            if "transferred_count" in meta:
                state["transferred_count"] = int(meta.get("transferred_count", 0))
            if "failed_count" in meta:
                state["failed_count"] = int(meta.get("failed_count", 0))
            # Record destinations used
            if "destinations" in meta:
                state["destinations"] = list(meta.get("destinations", []))

            mark_step_completed(p, TRANSFER_STEP, state=state)
    except Exception:
        # Don't mask result - re-raise after allowing test to observe result
        raise

    return result
