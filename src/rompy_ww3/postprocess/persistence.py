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

from pydantic import TypeAdapter, ValidationError
from rompy.core import result_persistence
from rompy.core.responses import (
    ModelRunFailure,
    ModelRunResult,
    ModelRunSuccess,
    NormalizedContext,
    RunResultSidecar,
)

RUN_JSON = result_persistence.RUN_RESULT_FILENAME
SCHEMA_VERSION = 2
POSTPROCESS_STATE_JSON = "postprocess_state.json"
ModelRunPayload = ModelRunSuccess | ModelRunFailure


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


def _require_model_run(result: Any) -> ModelRunPayload:
    """Require a concrete core result after any explicit in-memory adaptation."""
    if not isinstance(result, (ModelRunSuccess, ModelRunFailure)):
        raise TypeError(
            "WW3 persistence requires rompy.core ModelRunSuccess or "
            "ModelRunFailure; regenerate a canonical schema-v2 run result"
        )
    return result


def coerce_model_run(result: Any) -> ModelRunPayload:
    """Adapt a core-compatible in-memory result to the typed core model.

    This adapter is not a sidecar reader: files always go through the strict
    core loader. It exists for callers that still hand the postprocessor an
    object returned by an older in-process runner.
    """
    if isinstance(result, (ModelRunSuccess, ModelRunFailure)):
        return result
    if not hasattr(result, "model_dump") and not hasattr(result, "__dict__"):
        raise TypeError("expected a core-compatible ModelRunResult object")
    raw = result.model_dump() if hasattr(result, "model_dump") else vars(result).copy()
    raw.setdefault("success", True)
    raw.setdefault("backend_used", "local")
    raw.setdefault("expected_outputs", [])
    raw.setdefault("missing_outputs", [])
    if raw.get("success") is True:
        raw.pop("error", None)
    timing = raw.get("timing")
    if hasattr(timing, "model_dump"):
        raw["timing"] = timing.model_dump()
        timing = raw["timing"]
    elif timing is not None and not isinstance(timing, dict):
        raw["timing"] = vars(timing).copy()
        timing = raw["timing"]
    if isinstance(timing, dict):
        timing.pop("duration_seconds", None)
        if "end_time" not in timing:
            timing["end_time"] = timing.get("start_time")
    allowed = {
        "success", "run_id", "metadata", "persistence_diagnostic", "artifacts",
        "expected_outputs", "missing_outputs", "backend_used", "error", "timing",
        "output_dir", "workspace_dir", "message",
    }
    raw = {key: value for key, value in raw.items() if key in allowed}
    try:
        return _require_model_run(TypeAdapter(ModelRunResult).validate_python(raw))
    except Exception as exc:
        raise TypeError(
            "WW3 persistence requires a core-compatible ModelRunResult; "
            "regenerate a canonical schema-v2 run result"
        ) from exc


def build_persisted(result: ModelRunPayload, *, config: Any = None) -> RunResultSidecar:
    """Build a canonical schema-v2 run envelope from a typed core result.

    ``config`` is intentionally rejected rather than persisted in a competing
    WW3-only extension.  Configuration belongs to the core normalized context
    or result metadata.
    """
    # ``config`` was accepted by the retired WW3-v1 writer. It is deliberately
    # ignored rather than copied into the canonical envelope.
    payload = coerce_model_run(result)
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
    result: RunResultSidecar | ModelRunPayload | Any, output_dir: Path
) -> Path:
    """Write a canonical ``run_result.json`` using the core writer."""
    sidecar = result if isinstance(result, RunResultSidecar) else build_persisted(result)
    return result_persistence.write_run_result(Path(output_dir), sidecar)


def load_persisted(path_or_dir: Path) -> ModelRunPayload:
    """Strictly load and return the canonical typed ``ModelRunResult`` payload.

    The core loader rejects missing, malformed, wrong-kind, wrong-version,
    envelope-mismatch, and flat legacy documents with actionable regeneration
    guidance.  No migration or heuristic reader is provided here.
    """
    sidecar = result_persistence.load_run_result(Path(path_or_dir))
    return _require_model_run(sidecar.payload)


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
    payload = _require_model_run(result)
    output_dir = Path(payload.output_dir or "")
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
    return path / POSTPROCESS_STATE_JSON if path.is_dir() else path.parent / POSTPROCESS_STATE_JSON


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
        payload = json.loads(marker.read_text(encoding="utf-8")) if marker.exists() else {}
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid WW3 postprocess state {marker}: {exc}") from exc
    post = payload.setdefault("steps", {})
    entry = post.setdefault(step, {})
    entry.update({"completed": True, "at": datetime.now(timezone.utc).isoformat()})
    if state is not None:
        entry.setdefault("state", {}).update(state)
    _atomic_write(marker, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode())


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
