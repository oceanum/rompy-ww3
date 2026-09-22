"""Adapters for the canonical rompy run-result sidecar.

WW3 does not define a run-result wire format.  ``rompy.core`` owns the
schema-v2 envelope, validation, and persistence; this module only provides the
small adapter surface used by the WW3 postprocess lifecycle.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from rompy.core import result_persistence
from rompy.core.responses import (
    ModelRunFailure,
    ModelRunSuccess,
    NormalizedContext,
    PostprocessFailure,
    PostprocessResultSidecar,
    PostprocessSuccess,
    RunResultSidecar,
)

RUN_JSON = result_persistence.RUN_RESULT_FILENAME
POSTPROCESS_JSON = result_persistence.POSTPROCESS_RESULT_FILENAME
SCHEMA_VERSION = 2
POSTPROCESS_STATE_JSON = "postprocess_state.json"
ModelRunPayload = ModelRunSuccess | ModelRunFailure
PostprocessPayload = PostprocessSuccess | PostprocessFailure


def _atomic_write(path: Path, data: bytes) -> None:
    """Write a small lifecycle state file atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def require_model_run(result: Any) -> ModelRunPayload:
    """Require a concrete canonical core ModelRunResult instance."""
    if not isinstance(result, (ModelRunSuccess, ModelRunFailure)):
        raise TypeError(
            "WW3 persistence requires rompy.core ModelRunSuccess or "
            "ModelRunFailure; regenerate a canonical schema-v2 run result"
        )
    return result


def require_postprocess(result: Any) -> PostprocessPayload:
    """Require a concrete canonical core postprocess result instance."""
    if not isinstance(result, (PostprocessSuccess, PostprocessFailure)):
        raise TypeError(
            "WW3 postprocess persistence requires rompy.core PostprocessSuccess "
            "or PostprocessFailure"
        )
    return result


def build_persisted(result: ModelRunPayload) -> RunResultSidecar:
    """Build a canonical schema-v2 run envelope from a typed core result."""
    payload = require_model_run(result)
    metadata = payload.metadata
    normalized_context = None
    context = metadata.get("normalized_context")
    if isinstance(context, dict):
        try:
            normalized_context = NormalizedContext.model_validate(context)
        except ValidationError:
            normalized_context = None
    return RunResultSidecar(
        run_id=payload.run_id,
        status="success" if payload.success else "failed",
        success=payload.success,
        error=getattr(payload, "error", None),
        staging_dir=payload.workspace_dir,
        normalized_context=normalized_context,
        payload=payload,
    )


def write_persisted(
    result: RunResultSidecar | ModelRunPayload, output_dir: Path
) -> Path:
    """Write a canonical ``run_result.json`` using the core writer."""
    sidecar = (
        result if isinstance(result, RunResultSidecar) else build_persisted(result)
    )
    return result_persistence.write_run_result(Path(output_dir), sidecar)


def build_postprocess_persisted(result: PostprocessPayload) -> PostprocessResultSidecar:
    """Build the core schema-v2 envelope for a typed postprocess result."""
    payload = require_postprocess(result)
    return PostprocessResultSidecar(
        run_id=payload.run_id,
        status="success" if payload.success else "failed",
        success=payload.success,
        error=getattr(payload, "error", None),
        staging_dir=payload.output_dir,
        payload=payload,
    )


def persist_postprocess(
    result: PostprocessPayload,
    output_dir: Path,
    *,
    primary_error: str | None = None,
) -> PostprocessPayload:
    """Persist a typed postprocess result through the core public adapter.

    ``persist_result`` converts writer failures into a typed failure and keeps
    ``primary_error`` as the operation error when transfer and persistence both
    fail.  The result is checked after the adapter so arbitrary values cannot
    cross the persistence boundary.
    """
    payload = require_postprocess(result)
    sidecar = build_postprocess_persisted(payload)
    persisted = result_persistence.persist_result(
        payload,
        sidecar,
        Path(output_dir),
        primary_error=primary_error,
    )
    return require_postprocess(persisted)


def write_postprocess(
    result: PostprocessPayload,
    output_dir: Path,
    *,
    primary_error: str | None = None,
) -> PostprocessPayload:
    """Persist a canonical postprocess result and return its typed payload."""
    return persist_postprocess(result, output_dir, primary_error=primary_error)


def load_postprocess(path_or_dir: Path) -> PostprocessPayload:
    """Load the canonical typed postprocess payload from its core sidecar."""
    sidecar = result_persistence.load_postprocess_result(Path(path_or_dir))
    return require_postprocess(sidecar.payload)


def load_persisted(path_or_dir: Path) -> ModelRunPayload:
    """Strictly load and return the canonical typed ``ModelRunResult`` payload.

    The core loader rejects missing, malformed, wrong-kind, wrong-version,
    envelope-mismatch, and flat legacy documents with actionable regeneration
    guidance.  No migration or heuristic reader is provided here.
    """
    sidecar = result_persistence.load_run_result(Path(path_or_dir))
    return require_model_run(sidecar.payload)


def _sha256_of_file(path: Path) -> str:
    if not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_artifact_checksums(result: ModelRunPayload) -> dict[str, str]:
    """Compute checksums for local typed artifacts without mutating the result."""
    payload = require_model_run(result)
    workspace_dir = payload.workspace_dir or payload.output_dir
    output_dir = Path(workspace_dir or "")
    checksums: dict[str, str] = {}
    for artifact in payload.artifacts:
        if getattr(artifact, "kind", None) != "local":
            continue
        path = Path(artifact.path)
        checksums[artifact.path] = _sha256_of_file(
            path if path.is_absolute() else output_dir / path
        )
    return checksums


def _state_path(path_or_dir: Path) -> Path:
    path = Path(path_or_dir)
    return (
        path / POSTPROCESS_STATE_JSON
        if path.is_dir()
        else path.parent / POSTPROCESS_STATE_JSON
    )


def mark_step_completed(
    path_or_dir: Path, step: str, state: dict[str, Any] | None = None
) -> None:
    """Record WW3 lifecycle state separately from core-owned run evidence.

    In particular, this never edits ``run_result.json``.  The state file is
    deliberately not a run-result sidecar and cannot be consumed as one.
    """
    marker = _state_path(Path(path_or_dir))
    if not (Path(path_or_dir).is_dir() or Path(path_or_dir).exists()):
        raise FileNotFoundError(Path(path_or_dir))
    try:
        payload = (
            json.loads(marker.read_text(encoding="utf-8")) if marker.exists() else {}
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid WW3 postprocess state {marker}: {exc}") from exc
    post = payload.setdefault("steps", {})
    entry = post.setdefault(step, {})
    entry.update({"completed": True, "at": datetime.now(timezone.utc).isoformat()})
    if state is not None:
        entry.setdefault("state", {}).update(state)
    _atomic_write(
        marker, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    )


def is_step_completed(path_or_dir: Path, step: str) -> bool:
    """Return whether a WW3-only lifecycle marker is complete."""
    marker = _state_path(Path(path_or_dir))
    if not marker.exists():
        return False
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return bool(payload.get("steps", {}).get(step, {}).get("completed"))
