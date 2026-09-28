"""Deprecated compatibility aliases for core result persistence.

Canonical sidecars and transfer state are owned by ``rompy.core`` and
``rompy.postprocess``.  WW3 no longer implements persistence, locking,
checksums, or lifecycle state here.  New code should import the core APIs
directly; these aliases remain temporarily for downstream WW3 callers.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from rompy.core import result_persistence
from rompy.core.artifacts import compute_source_checksum
from rompy.core.responses import (
    ModelRunFailure,
    ModelRunSuccess,
    NormalizedContext,
    PostprocessFailure,
    PostprocessSuccess,
    RunResultSidecar,
)

RUN_JSON = result_persistence.RUN_RESULT_FILENAME
POSTPROCESS_JSON = result_persistence.POSTPROCESS_RESULT_FILENAME
SCHEMA_VERSION = 2
ModelRunPayload = ModelRunSuccess | ModelRunFailure
PostprocessPayload = PostprocessSuccess | PostprocessFailure


def _deprecated() -> None:
    warnings.warn(
        "rompy_ww3.postprocess.persistence is deprecated; use rompy.core "
        "result_persistence and rompy.postprocess APIs instead",
        DeprecationWarning,
        stacklevel=3,
    )


def require_model_run(result: Any) -> ModelRunPayload:
    _deprecated()
    if not isinstance(result, (ModelRunSuccess, ModelRunFailure)):
        raise TypeError(
            "expected a concrete core ModelRunResult: ModelRunSuccess or ModelRunFailure"
        )
    return result


def require_postprocess(result: Any) -> PostprocessPayload:
    _deprecated()
    if not isinstance(result, (PostprocessSuccess, PostprocessFailure)):
        raise TypeError("expected a concrete core PostprocessResult")
    return result


def build_persisted(result: ModelRunPayload) -> RunResultSidecar:
    """Compatibility constructor; canonical ownership remains in core."""
    _deprecated()
    payload = require_model_run(result)
    context = payload.metadata.get("normalized_context")
    normalized_context = (
        NormalizedContext.model_validate(context) if isinstance(context, dict) else None
    )
    return RunResultSidecar(
        run_id=payload.run_id,
        status="success" if payload.success else "failed",
        success=payload.success,
        error=getattr(payload, "error", None),
        staging_dir=payload.workspace_dir,
        normalized_context=normalized_context,
        payload=payload,
    )


def write_persisted(result: RunResultSidecar | ModelRunPayload, output_dir: Path) -> Path:
    _deprecated()
    sidecar = result if isinstance(result, RunResultSidecar) else build_persisted(result)
    return result_persistence.write_run_result(Path(output_dir), sidecar)


def load_persisted(path_or_dir: Path) -> ModelRunPayload:
    _deprecated()
    return result_persistence.load_run_result(Path(path_or_dir)).payload


def load_postprocess(path_or_dir: Path) -> PostprocessPayload:
    _deprecated()
    return result_persistence.load_postprocess_result(Path(path_or_dir)).payload


def compute_artifact_checksums(result: ModelRunPayload) -> dict[str, str]:
    """Compatibility view over the core artifact checksum implementation."""
    _deprecated()
    payload = require_model_run(result)
    root = Path(payload.workspace_dir or payload.output_dir or "")
    return {
        artifact.path: compute_source_checksum(artifact, root)
        for artifact in payload.artifacts
        if getattr(artifact, "kind", None) == "local"
    }


def persist_postprocess(*args: Any, **kwargs: Any) -> PostprocessPayload:
    _deprecated()
    raise RuntimeError(
        "WW3 no longer persists postprocess results; use run_postprocess_pipeline"
    )


def write_postprocess(*args: Any, **kwargs: Any) -> PostprocessPayload:
    return persist_postprocess(*args, **kwargs)


__all__ = [
    "RUN_JSON",
    "POSTPROCESS_JSON",
    "SCHEMA_VERSION",
    "ModelRunPayload",
    "PostprocessPayload",
    "build_persisted",
    "compute_artifact_checksums",
    "load_persisted",
    "load_postprocess",
    "persist_postprocess",
    "require_model_run",
    "require_postprocess",
    "write_persisted",
    "write_postprocess",
]
