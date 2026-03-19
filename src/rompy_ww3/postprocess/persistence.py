from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from rompy.core.responses import ModelRunResult
from typing import cast

from pydantic import Field


# Sidecar constants
RUN_JSON = "run_result.json"
SCHEMA_VERSION = 1


def _atomic_write(path: Path, data: bytes) -> None:
    """Atomically write bytes to path using a temp file and os.replace.

    Ensures the target directory exists and that the replace is atomic on POSIX.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, str(path))
    finally:
        if os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except Exception:
                pass


def _sha256_of_file(path: Path) -> str:
    """Return hex SHA256 checksum of a file. If file missing, return empty string."""
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _strip_all_duration_seconds(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {
            k: _strip_all_duration_seconds(v)
            for k, v in payload.items()
            if k != "duration_seconds"
        }
    if isinstance(payload, list):
        return [_strip_all_duration_seconds(v) for v in payload]
    return payload


def _ensure_no_duration_seconds(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Remove timing.duration_seconds if present in a payload dict.

    This avoids Model validation failures caused by model_dump(mode='json')
    which may inject computed fields not accepted by the TimingInfo model.
    """
    timing = payload.get("timing")
    if timing is None:
        return payload

    # Normalize timing to a plain dict if it's a pydantic model or object
    if hasattr(timing, "model_dump"):
        tdict = timing.model_dump()
    elif isinstance(timing, dict):
        tdict = dict(timing)
    else:
        try:
            tdict = dict(vars(timing))
        except Exception:
            tdict = {}

    if "duration_seconds" in tdict:
        tdict.pop("duration_seconds", None)
        payload["timing"] = tdict
    return payload


class PersistedRunResult(ModelRunResult):
    """Persisted run result extending rompy.core.responses.ModelRunResult.

    Adds schema_version, persisted_at, optional config payload,
    artifact_checksums mapping, and postprocess state metadata.
    """

    # Pydantic models in rompy.core.responses are expected; we add attributes
    schema_version: int = SCHEMA_VERSION
    persisted_at: datetime | None = None
    config: Optional[Dict[str, Any]] = None
    artifact_checksums: Dict[str, str] = Field(default_factory=dict)
    postprocess: Dict[str, Any] = Field(default_factory=dict)


def build_persisted(
    model_run: Any, *, config: Optional[Dict[str, Any]] = None
) -> PersistedRunResult:
    """Build a PersistedRunResult from a ModelRunResult-like object.

    Accepts either a rompy.core.responses.ModelRunResult or a duck-typed object
    (SimpleNamespace etc.). Ensures duration_seconds is stripped before
    creating the validated PersistedRunResult instance.
    """
    # Prefer pydantic model_dump when available to get dict form
    if hasattr(model_run, "model_dump"):
        payload = model_run.model_dump()
    else:
        # Fallback: shallow dict of attributes
        payload = {k: v for k, v in vars(model_run).items()}

    # Remove duration_seconds if present
    payload = _ensure_no_duration_seconds(payload)

    # Attach optional config
    if config is not None:
        payload["config"] = config

    # Set persisted_at timestamp
    payload.setdefault("persisted_at", datetime.now(timezone.utc))
    payload.setdefault("schema_version", SCHEMA_VERSION)

    # Instantiate PersistedRunResult with validation
    creator = getattr(PersistedRunResult, "model_validate", None)
    if callable(creator):
        return cast(PersistedRunResult, creator(payload))
    # Fallback for older pydantic: parse_obj
    return PersistedRunResult.parse_obj(payload)


def write_persisted(result: PersistedRunResult, output_dir: Path) -> Path:
    """Write persisted result to output_dir/run_result.json atomically and return path."""
    output_dir = Path(output_dir)
    dest = output_dir / RUN_JSON
    # Use pydantic model_dump to get serializable dict if available
    dump = result.model_dump() if hasattr(result, "model_dump") else result.dict()
    if isinstance(dump, dict):
        dump = _ensure_no_duration_seconds(dump)

        dump = _strip_all_duration_seconds(dump)
    pa = dump.get("persisted_at")
    if isinstance(pa, datetime):
        dump["persisted_at"] = pa.isoformat()

    creator = getattr(PersistedRunResult, "model_validate", None)
    if callable(creator):
        validated = cast(PersistedRunResult, creator(dump))
    else:
        validated = PersistedRunResult.parse_obj(dump)

    try:
        timing_field = getattr(validated, "timing", None)
        if isinstance(timing_field, dict) and "duration_seconds" in timing_field:
            new_timing = dict(timing_field)
            new_timing.pop("duration_seconds", None)
            setattr(validated, "timing", new_timing)
    except Exception:
        pass

    base_dump = (
        validated.model_dump() if hasattr(validated, "model_dump") else validated.dict()
    )
    sanitized_dump = _strip_all_duration_seconds(base_dump)
    sanitized_model = None
    creator = getattr(PersistedRunResult, "model_validate", None)
    if callable(creator):
        sanitized_model = cast(PersistedRunResult, creator(sanitized_dump))
    else:
        sanitized_model = PersistedRunResult.parse_obj(sanitized_dump)
    json_text = sanitized_model.model_dump_json(indent=2)

    try:
        obj = json.loads(json_text)
        obj = _strip_all_duration_seconds(obj)
        json_text = json.dumps(obj, indent=2)
    except Exception:
        pass
    data = json_text.encode("utf-8")
    _atomic_write(dest, data)
    return dest


def _migrate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize/migrate payloads to latest schema (v1).

    Currently ensures schema_version exists and strips duration_seconds.
    """
    if payload.get("schema_version") is None:
        payload["schema_version"] = SCHEMA_VERSION
    payload = _ensure_no_duration_seconds(payload)
    return payload


def load_persisted(path_or_dir: Path) -> PersistedRunResult:
    """Load a persisted run result from a run_result.json file or directory.

    If a directory is provided, looks for run_result.json inside it.
    Performs migration/normalization before validating the model.
    """
    p = Path(path_or_dir)
    if p.is_dir():
        p = p / RUN_JSON
    if not p.exists():
        raise FileNotFoundError(f"Persisted run file not found: {p}")

    raw = json.loads(p.read_text())
    raw = _migrate_payload(raw)

    # Convert persisted_at back to datetime if needed
    pa = raw.get("persisted_at")
    if isinstance(pa, str):
        try:
            raw["persisted_at"] = datetime.fromisoformat(pa)
        except Exception:
            raw["persisted_at"] = None

    creator = getattr(PersistedRunResult, "model_validate", None)
    if callable(creator):
        return cast(PersistedRunResult, creator(raw))
    return PersistedRunResult.parse_obj(raw)


def compute_artifact_checksums(result: PersistedRunResult) -> Dict[str, str]:
    """Compute SHA256 checksums for artifacts in the result (relative to output_dir).

    Returns a mapping of artifact.path -> hex checksum (empty string if file missing).
    """
    out = {}
    output_dir = Path(getattr(result, "output_dir", ""))
    artifacts = getattr(result, "artifacts", []) or []
    for a in artifacts:
        p = Path(a.path)
        if not p.is_absolute():
            fp = output_dir / p
        else:
            fp = p
        out[str(a.path)] = _sha256_of_file(fp)
    # Attach into result object as well
    try:
        result.artifact_checksums = out
    except Exception:
        pass
    return out


def mark_step_completed(
    path_or_dir: Path, step: str, state: Optional[Dict[str, Any]] = None
) -> None:
    """Record a postprocess step completion marker inside the persisted run_result.json.

    This function is idempotent: repeated calls for the same step will update
    the timestamp/state but not duplicate entries.
    """
    p = Path(path_or_dir)
    if p.is_dir():
        p = p / RUN_JSON
    if not p.exists():
        raise FileNotFoundError(p)
    payload = json.loads(p.read_text())
    payload = _migrate_payload(payload)
    post = payload.get("postprocess") or {}
    now = datetime.now(timezone.utc).isoformat()
    entry = post.get(step, {})
    entry.update({"completed": True, "at": now})
    if state is not None:
        entry.setdefault("state", {}).update(state)
    post[step] = entry
    payload["postprocess"] = post
    # Write deterministically and safely without using default=str
    # - Strip any timing.duration_seconds that could be produced during JSON
    #   serialization in other paths
    # - Normalize/strip any residual duration fields in nested structures
    # - Convert datetime-like fields to ISO strings if needed
    cleaned = _strip_all_duration_seconds(payload)
    # Ensure any datetime-like fields are serialized properly
    if isinstance(cleaned, dict):
        pa = cleaned.get("persisted_at")
        if isinstance(pa, datetime):
            cleaned["persisted_at"] = pa.isoformat()
    # Dump with explicit key sorting for deterministic output
    json_text = json.dumps(cleaned, indent=2, sort_keys=True)
    _atomic_write(p, json_text.encode("utf-8"))


def is_step_completed(path_or_dir: Path, step: str) -> bool:
    """Return True if the named postprocess step is marked completed in run_result.json."""
    p = Path(path_or_dir)
    if p.is_dir():
        p = p / RUN_JSON
    if not p.exists():
        return False
    payload = json.loads(p.read_text())
    post = payload.get("postprocess") or {}
    entry = post.get(step)
    return bool(entry and entry.get("completed"))
