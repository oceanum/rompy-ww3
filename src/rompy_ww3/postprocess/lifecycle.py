from __future__ import annotations

from pathlib import Path
from typing import Any

from rompy.core.responses import (
    PostprocessResult,
    PostprocessSuccess,
)

from .persistence import load_persisted, mark_step_completed, require_postprocess
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
    - Loads the persisted run via load_persisted.
    - Always invokes WW3TransferPostprocessor.process for the current typed run
      and transfer request. Existing lifecycle markers and postprocess sidecars
      are observational only; safe request identity belongs to #15.
    - Records lifecycle counters separately after success, leaving the core-owned
      run sidecar unchanged.

    This function keeps behavior intentionally small and testable.
    """
    p = Path(path_or_dir)

    # Load persisted run result (raises FileNotFoundError if missing)
    persisted = load_persisted(p)

    # Lifecycle markers are observational only.  Safe completion identity is a
    # #15 concern, so every current run/request is executed even when an old
    # marker or postprocess sidecar exists.
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
