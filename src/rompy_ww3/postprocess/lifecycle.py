from __future__ import annotations

from pathlib import Path
from typing import Any

from rompy.core.responses import (
    PostprocessResult,
    PostprocessSuccess,
)

from .persistence import (
    is_step_completed,
    load_persisted,
    load_postprocess,
    mark_step_completed,
    require_postprocess,
)
from .processor import WW3TransferPostprocessor

# Stable step name for transfer postprocess
TRANSFER_STEP = "transfer"


def run_transfer_postprocess(
    path_or_dir: Path | str,
    destinations: list[str],
    artifact_types: list[Any] | None = None,
    failure_policy: str = "CONTINUE",
) -> PostprocessResult:
    """Run the WW3 transfer postprocess for a persisted run result.

    - path_or_dir: directory containing run_result.json or path to run_result.json
    - destinations, artifact_types, failure_policy: forwarded to processor.process

    Behaviour:
    - Loads the persisted run via load_persisted
    - If the transfer step is already marked completed in the separate WW3
      lifecycle state file, returns a PostprocessSuccess with zero actions.
    - Otherwise invokes WW3TransferPostprocessor.process and records lifecycle
      counters separately, leaving the core-owned run sidecar unchanged.

    This function keeps behavior intentionally small and testable.
    """
    p = Path(path_or_dir)

    # Load persisted run result (raises FileNotFoundError if missing)
    persisted = load_persisted(p)

    # If already completed, return early with a light-weight success result
    if is_step_completed(p, TRANSFER_STEP):
        # Return the canonical persisted result, not a reconstructed duck-typed
        # response.  This keeps repeated CLI/in-process consumption auditable.
        try:
            persisted_result = load_postprocess(p)
            return persisted_result.model_copy(
                update={
                    "metadata": {
                        **persisted_result.metadata,
                        "skipped": True,
                    }
                }
            )
        except FileNotFoundError:
            # A legacy lifecycle marker without its canonical result is not a
            # valid completed step; rerun to repair the evidence.
            pass

    # Not completed yet - run processor
    processor = WW3TransferPostprocessor()
    result = require_postprocess(
        processor.process(
            persisted,
            destinations=destinations,
            artifact_types=artifact_types,
            failure_policy=failure_policy,
            persistence_dir=p if p.is_dir() else p.parent,
        )
    )

    # Record lifecycle state separately; the core-owned run sidecar is immutable.
    if isinstance(result, PostprocessSuccess) and result.success:
        state = {}
        meta = getattr(result, "metadata", {}) or {}
        if "transferred_count" in meta:
            state["transferred_count"] = int(meta.get("transferred_count", 0))
        if "failed_count" in meta:
            state["failed_count"] = int(meta.get("failed_count", 0))
        if "destinations" in meta:
            state["destinations"] = list(meta.get("destinations", []))
        mark_step_completed(p, TRANSFER_STEP, state=state)

    return result
