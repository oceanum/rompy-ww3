"""Canonical WW3 output transfer postprocessor."""

from __future__ import annotations

import hashlib
import json
import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from rompy.core.responses import (
    Artifact,
    ArtifactType,
    ModelRunFailure,
    ModelRunSuccess,
    PostprocessFailure,
    PostprocessResult,
    PostprocessSuccess,
    TimingInfo,
)
from rompy.transfer import TransferFailurePolicy, TransferManager
from rompy.transfer.manager import TransferBatchResult

from rompy_ww3.postprocess.naming import compute_target_name
from rompy_ww3.postprocess.persistence import (
    SCHEMA_VERSION,
    load_postprocess,
    load_postprocess_state,
    persist_postprocess,
    record_postprocess_state,
    require_model_run,
)

logger = logging.getLogger(__name__)
ModelRunPayload = ModelRunSuccess | ModelRunFailure


class WW3TransferPostprocessor:
    """Transfer typed WW3 run evidence to one or more destinations.

    The processor has one wire contract in every execution mode: it accepts a
    concrete core ``ModelRunSuccess`` or ``ModelRunFailure`` and returns a
    concrete core ``PostprocessSuccess`` or ``PostprocessFailure``.  The
    canonical postprocess sidecar is written before returning.
    """

    def __init__(self) -> None:
        """Initialize a stateless transfer processor."""

    def _create_artifact(self, path: Path, output_dir: Path) -> Artifact:
        """Create a typed local artifact from a path (legacy helper)."""
        suffix = path.suffix.lower()
        artifact_type = {
            ".nc": ArtifactType.NETCDF,
            ".yaml": ArtifactType.YAML,
            ".yml": ArtifactType.YAML,
            ".txt": ArtifactType.TEXT,
            ".list": ArtifactType.TEXT,
            ".nml": ArtifactType.TEXT,
        }.get(suffix, ArtifactType.OTHER)
        absolute = path if path.is_absolute() else output_dir / path
        size_bytes = absolute.stat().st_size if absolute.exists() else None
        return Artifact(
            path=path.as_posix(),
            artifact_type=artifact_type,
            size_bytes=size_bytes,
            description=f"WW3 output file: {path.name}",
            date=None,
        )

    def _get_output_dir(self, model_run: ModelRunPayload) -> Path:
        """Return the canonical output directory from a typed run result."""
        payload = require_model_run(model_run)
        value = payload.output_dir
        if not value:
            raise AttributeError("Cannot determine output directory from model_run")
        return Path(value)

    def _extract_start_date(self, model_run: ModelRunPayload) -> str | None:
        """Use typed core timing as the transfer date fallback."""
        payload = require_model_run(model_run)
        return self._coerce_ww3_date(payload.timing.start_time)

    def _extract_output_stride(self, model_run: ModelRunPayload) -> int | None:
        """Read an optional WW3 stride from validated result metadata."""
        payload = require_model_run(model_run)
        ww3_metadata = payload.metadata.get("ww3", {})
        if not isinstance(ww3_metadata, dict):
            return None
        stride = ww3_metadata.get("restart_stride_seconds")
        if isinstance(stride, bool):
            return None
        try:
            return int(stride) if stride is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _coerce_ww3_date(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        try:
            return value.strftime("%Y%m%d %H%M%S")
        except (AttributeError, TypeError):
            return None

    @staticmethod
    def _checksum(path: Path) -> str | None:
        if not path.is_file():
            return None
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return f"sha256:{digest.hexdigest()}"

    @staticmethod
    def _evidence(artifacts: list[Any]) -> list[dict[str, Any]]:
        return [artifact.model_dump(mode="json") for artifact in artifacts]

    @staticmethod
    def _destination_identity(destination: str) -> str:
        """Normalize a destination without persisting mutable credentials."""
        parsed = urlsplit(destination)
        netloc = parsed.hostname or ""
        if parsed.port is not None:
            netloc = f"{netloc}:{parsed.port}"
        query = sorted(
            (
                (key, value)
                for key, value in parse_qsl(parsed.query, keep_blank_values=True)
                if key.lower()
                not in {
                    "token",
                    "access_token",
                    "secret",
                    "password",
                    "signature",
                    "sig",
                    "key",
                }
            ),
            key=lambda item: (item[0], item[1]),
        )
        return urlunsplit((parsed.scheme.lower(), netloc, parsed.path, urlencode(query), ""))

    @staticmethod
    def _artifact_type_identity(value: Any) -> str:
        return getattr(value, "value", str(value))

    @classmethod
    def _identity_value(cls, value: Any, key: str = "") -> Any:
        """Return JSON-safe request options with credential fields removed."""
        if isinstance(value, dict):
            return {
                str(item_key): cls._identity_value(item_value, str(item_key))
                for item_key, item_value in sorted(value.items(), key=lambda item: str(item[0]))
                if str(item_key).lower() not in {
                    "token", "access_token", "secret", "password", "signature", "sig", "key",
                    "timestamp", "created_at", "updated_at", "at",
                }
            }
        if isinstance(value, (list, tuple)):
            return [cls._identity_value(item, key) for item in value]
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)

    def _request_identity(
        self,
        model_run: ModelRunPayload,
        *,
        local_artifacts: list[Artifact],
        remote_artifacts: list[Any],
        required_missing: list[Artifact],
        destinations: list[str],
        name_map: dict[Path, str],
        source_checksums: dict[str, str],
        artifact_types: list[ArtifactType] | None,
        naming_policy: str,
        failure_policy: str,
        required_policy: str,
        transfer_options: dict[str, Any],
    ) -> str:
        """Hash every input that can alter transfer work, excluding credentials."""
        sources = []
        workspace = Path(model_run.workspace_dir or model_run.output_dir or "").resolve()
        for artifact in local_artifacts:
            raw_path = Path(artifact.path)
            source = raw_path if raw_path.is_absolute() else workspace / raw_path
            try:
                canonical_path = source.resolve().relative_to(workspace).as_posix()
            except ValueError:
                canonical_path = source.resolve().as_posix()
            target_name = name_map.get(source)
            if target_name is None:
                fallback_path = (
                    raw_path
                    if raw_path.is_absolute()
                    else Path(model_run.workspace_dir or model_run.output_dir or "")
                    / raw_path
                )
                target_name = name_map[fallback_path]
            sources.append(
                {
                    "path": canonical_path,
                    "type": self._artifact_type_identity(artifact.artifact_type),
                    "declared_size_bytes": artifact.size_bytes,
                    "size_bytes": source.stat().st_size if source.is_file() else None,
                    "checksum": source_checksums.get(artifact.path, ""),
                    "target_name": target_name,
                }
            )
        remotes = [
            {
                "uri": self._destination_identity(artifact.uri),
                "type": self._artifact_type_identity(artifact.artifact_type),
                "size_bytes": artifact.size_bytes,
            }
            for artifact in remote_artifacts
        ]
        payload = {
            "schema_version": SCHEMA_VERSION,
            "run_id": model_run.run_id,
            "sources": sorted(sources, key=lambda item: item["path"]),
            "remote_sources": sorted(remotes, key=lambda item: item["uri"]),
            "required_missing": sorted(
                [
                    {
                        "path": artifact.path,
                        "type": self._artifact_type_identity(artifact.artifact_type),
                    }
                    for artifact in required_missing
                ],
                key=lambda item: item["path"],
            ),
            "destinations": sorted(self._destination_identity(item) for item in destinations),
            "artifact_types": sorted(
                self._artifact_type_identity(item) for item in artifact_types or []
            ),
            "required_policy": required_policy,
            "naming_policy": naming_policy,
            "failure_policy": failure_policy,
            "transfer_options": self._identity_value(transfer_options),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return f"sha256:{hashlib.sha256(encoded).hexdigest()}"

    @staticmethod
    def _file_destination_path(record: dict[str, Any]) -> Path | None:
        destination = str(record.get("destination", ""))
        if not destination.startswith("file://"):
            return None
        parsed = urlsplit(destination)
        return Path(parsed.path) / str(record.get("target_name", ""))

    @classmethod
    def _file_destination_exists(cls, record: dict[str, Any]) -> bool:
        """Validate recorded local transfers when their destination is inspectable."""
        path = cls._file_destination_path(record)
        if path is None:
            return True
        return path.is_file()

    def _record_valid(
        self,
        record: dict[str, Any],
        *,
        source: Path,
        source_checksum: str,
        destination: str,
        target_name: str,
    ) -> bool:
        """Check one prior success against current source and destination evidence."""
        destination_path = self._file_destination_path(record)
        destination_valid = self._file_destination_exists(record)
        if destination_path is not None and destination_valid:
            recorded_checksum = record.get("destination_checksum")
            recorded_size = record.get("destination_size_bytes")
            destination_valid = (
                (recorded_checksum is None or self._checksum(destination_path) == recorded_checksum)
                and (recorded_size is None or destination_path.stat().st_size == recorded_size)
            )
        return (
            record.get("path") == str(source)
            and record.get("destination") == self._destination_identity(destination)
            and record.get("target_name") == target_name
            and record.get("source_checksum") == source_checksum
            and bool(source_checksum)
            and source.is_file()
            and (
                record.get("source_size_bytes") is None
                or record.get("source_size_bytes") == source.stat().st_size
            )
            and destination_valid
        )

    def _persist_transfer_state(
        self,
        persistence_path: Path | None,
        result: PostprocessResult,
        metadata: dict[str, Any],
    ) -> PostprocessResult:
        """Persist identity and incomplete/success status outside core evidence."""
        if persistence_path is None:
            return result
        try:
            record_postprocess_state(
                persistence_path,
                "transfer",
                completed=isinstance(result, PostprocessSuccess) and result.success,
                state={
                    "identity": metadata.get("transfer_identity"),
                    "status": "success" if result.success else "failed",
                    "transfer_records": metadata.get("transfer_records", []),
                    "retry_history": metadata.get("retry_history", []),
                },
            )
        except (OSError, ValueError) as exc:
            logger.warning("Unable to persist WW3 transfer state: %s", exc)
        return result

    def _result(
        self,
        model_run: ModelRunPayload,
        *,
        output_dir: Path | None,
        artifacts: list[Artifact],
        metadata: dict[str, Any],
        start_time: datetime,
        error: str | None = None,
        persistence_dir: Path | None = None,
    ) -> PostprocessResult:
        """Construct and persist one canonical typed postprocess result."""
        end_time = datetime.now(timezone.utc)
        timing = TimingInfo(start_time=start_time, end_time=end_time)
        common = {
            "run_id": model_run.run_id,
            "artifacts": artifacts,
            "expected_outputs": list(model_run.expected_outputs),
            "missing_outputs": list(model_run.missing_outputs),
            "timing": timing,
            "metadata": metadata,
        }
        if error is None:
            if output_dir is None:
                raise ValueError("successful postprocess requires an output directory")
            result: PostprocessResult = PostprocessSuccess(
                success=True,
                output_dir=str(output_dir),
                validated=False,
                file_count=len(artifacts),
                **common,
            )
        else:
            result = PostprocessFailure(
                success=False,
                error=error,
                output_dir=str(output_dir) if output_dir is not None else None,
                **common,
            )

        # A run failure has no valid success path, even when optional evidence
        # happened to transfer.  The primary run/transfer error is retained by
        # the core persistence adapter if writing the postprocess sidecar fails.
        if persistence_dir is not None or output_dir is not None:
            persisted = persist_postprocess(
                result,
                persistence_dir or output_dir,  # type: ignore[arg-type]
                primary_error=error,
            )
            return self._persist_transfer_state(
                persistence_dir or output_dir, persisted, metadata
            )
        return result

    @staticmethod
    def _record_skipped_pairs(
        metadata: dict[str, Any],
        pairs: list[tuple[Artifact, Path, str, str]],
        reason: str,
    ) -> None:
        """Record unattempted transfer pairs as deterministic skipped evidence."""
        for artifact, source, target, destination in pairs:
            metadata["skipped_transfers"].append(
                {
                    "path": artifact.path,
                    "local_path": str(source),
                    "target_name": target,
                    "destination": destination,
                    "dest_uri": destination,
                    "reason": reason,
                }
            )
        metadata["skipped_transfer_count"] += len(pairs)
        metadata["skipped_count"] += len(pairs)

    @staticmethod
    def _final_error(
        model_run: ModelRunPayload,
        operational_error: str,
        metadata: dict[str, Any],
    ) -> str:
        """Keep model failure primary while retaining operational diagnostics."""
        if isinstance(model_run, ModelRunFailure):
            metadata.setdefault("transfer_diagnostic", {})["error"] = operational_error
            metadata["transfer_diagnostic"].setdefault("failures", [])
            return f"Model run failed: {model_run.error}"
        return operational_error

    @staticmethod
    @contextmanager
    def _operation_lock(path_or_dir: Path):
        """Serialize one run's read/transfer/write lifecycle with flock."""
        import fcntl

        root = path_or_dir if path_or_dir.is_dir() else path_or_dir.parent
        root.mkdir(parents=True, exist_ok=True)
        lock_path = root / ".postprocess-operation.lock"
        with lock_path.open("a+") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def process(
        self,
        model_run_result: ModelRunSuccess | ModelRunFailure,
        destinations: list[str],
        artifact_types: list[ArtifactType] | None = None,
        failure_policy: str = "CONTINUE",
        naming_policy: str = "restart_only",
        persistence_dir: Path | str | None = None,
        required_policy: str = "expected_outputs_required",
        **kwargs: Any,
    ) -> PostprocessResult:
        """Serialize a public transfer request for safe replay/retry."""
        model_run = require_model_run(model_run_result)
        lock_root = Path(persistence_dir or model_run.output_dir or model_run.workspace_dir or ".")
        with self._operation_lock(lock_root):
            return self._process_unlocked(
                model_run,
                destinations,
                artifact_types=artifact_types,
                failure_policy=failure_policy,
                naming_policy=naming_policy,
                persistence_dir=persistence_dir,
                required_policy=required_policy,
                **kwargs,
            )

    def _process_unlocked(
        self,
        model_run_result: ModelRunSuccess | ModelRunFailure,
        destinations: list[str],
        artifact_types: list[ArtifactType] | None = None,
        failure_policy: str = "CONTINUE",
        naming_policy: str = "restart_only",
        persistence_dir: Path | str | None = None,
        required_policy: str = "expected_outputs_required",
        **kwargs: Any,
    ) -> PostprocessResult:
        """Transfer local typed artifacts and persist the canonical result."""
        transfer_options = dict(kwargs)
        if required_policy not in {"expected_outputs_required", "optional"}:
            raise ValueError(
                "Invalid required_policy; expected 'expected_outputs_required' or 'optional'"
            )
        model_run = require_model_run(model_run_result)
        persistence_path = (
            Path(persistence_dir)
            if persistence_dir is not None
            else (Path(model_run.output_dir) if model_run.output_dir else None)
        )
        if not destinations:
            raise ValueError("destinations must be a non-empty list of strings")
        if any(not isinstance(destination, str) or not destination for destination in destinations):
            raise ValueError("destinations must be a non-empty list of strings")
        if failure_policy == "CONTINUE":
            policy = TransferFailurePolicy.CONTINUE
        elif failure_policy == "FAIL_FAST":
            policy = TransferFailurePolicy.FAIL_FAST
        else:
            raise ValueError(f"Invalid failure_policy: {failure_policy}")
        if naming_policy not in {"restart_only", "datestamp_all"}:
            raise ValueError(f"Invalid naming_policy: {naming_policy}")

        output_dir = Path(model_run.output_dir) if model_run.output_dir else None
        workspace_dir = Path(model_run.workspace_dir or model_run.output_dir or "")
        observed = self._evidence(model_run.artifacts)
        remote_artifacts = [
            item for item in model_run.artifacts if item.kind == "remote"
        ]
        remote = self._evidence(remote_artifacts)
        local_artifacts = [
            artifact
            for artifact in model_run.artifacts
            if artifact.kind == "local"
        ]
        skipped_artifacts = list(remote)
        if artifact_types is not None:
            before = local_artifacts
            local_artifacts = [
                artifact
                for artifact in local_artifacts
                if artifact.artifact_type in artifact_types
            ]
            skipped_artifacts.extend(
                artifact.model_dump(mode="json")
                for artifact in before
                if artifact not in local_artifacts
            )
        selected_types = set(artifact_types) if artifact_types is not None else None
        observed_local_paths = {artifact.path for artifact in local_artifacts}
        missing_required = [
            artifact
            for artifact in model_run.expected_outputs
            if artifact.kind == "local"
            and artifact.path not in observed_local_paths
            and (selected_types is None or artifact.artifact_type in selected_types)
        ]
        required_missing = (
            missing_required if required_policy == "expected_outputs_required" else []
        )

        metadata: dict[str, Any] = {
            "destinations": list(destinations),
            "destination_count": len(destinations),
            "requested_count": len(local_artifacts) + len(required_missing),
            "requested_transfer_count": (len(local_artifacts) + len(required_missing)) * len(destinations),
            "local_count": len(local_artifacts),
            "remote_count": len(remote),
            "skipped_count": len(skipped_artifacts),
            "skipped_transfer_count": 0,
            "skipped_transfers": [],
            "transferred_count": 0,
            "successful_transfer_count": 0,
            "failed_count": 0,
            "failed_transfer_count": 0,
            "transfer_failures": [],
            "observed_artifacts": observed,
            "remote_observed_artifacts": remote,
            "skipped_artifacts": skipped_artifacts,
            "missing_sources": self._evidence(missing_required),
            "missing_required_sources": self._evidence(required_missing),
            "required_missing_count": len(required_missing),
            "required_policy": required_policy,
            "name_map": {},
            "source_checksums": {},
            "transferred_artifacts": [],
            "transfer_records": [],
            "retry_history": [],
            "transfer_identity": None,
            "reused_count": 0,
        }
        if isinstance(model_run.metadata.get("artifact_checksums"), dict):
            metadata["source_checksums"].update(model_run.metadata["artifact_checksums"])
        metadata["transfer_identity"] = self._request_identity(
            model_run,
            local_artifacts=[],
            remote_artifacts=remote_artifacts,
            required_missing=missing_required,
            destinations=destinations,
            name_map={},
            source_checksums={},
            artifact_types=artifact_types,
            naming_policy=naming_policy,
            failure_policy=failure_policy,
            required_policy=required_policy,
            transfer_options=transfer_options,
        )

        start_time = datetime.now(timezone.utc)
        if required_missing and not local_artifacts:
            metadata["failed_count"] = len(required_missing) * len(destinations)
            metadata["failed_transfer_count"] = metadata["failed_count"]
            metadata["transfer_failures"] = [
                {
                    "path": artifact.path,
                    "target_name": artifact.path.rsplit("/", 1)[-1],
                    "destination": self._destination_identity(destination),
                    "error": "required source artifact was not observed",
                    "reason": "missing_required_source",
                }
                for artifact in required_missing
                for destination in destinations
            ]
            return self._result(
                model_run,
                output_dir=output_dir,
                artifacts=[],
                metadata=metadata,
                start_time=start_time,
                error=self._final_error(
                    model_run,
                    f"Required transfer source missing: {len(required_missing)} artifact(s)",
                    metadata,
                ),
                persistence_dir=persistence_path,
            )
        if not local_artifacts:
            if isinstance(model_run, ModelRunFailure):
                error = f"Model run failed: {model_run.error}"
                return self._result(
                    model_run,
                    output_dir=output_dir,
                    artifacts=[],
                    metadata=metadata,
                    start_time=start_time,
                    error=error,
                    persistence_dir=persistence_path,
                )
            return self._result(
                model_run,
                output_dir=output_dir,
                artifacts=[],
                metadata=metadata,
                start_time=start_time,
                persistence_dir=persistence_path,
            )

        if output_dir is None:
            error = "Cannot transfer local artifacts without a model output directory"
            metadata["failed_count"] = metadata["requested_transfer_count"]
            metadata["failed_transfer_count"] = metadata["failed_count"]
            metadata["transfer_failures"] = [
                {
                    "path": artifact.path,
                    "target_name": artifact.path.rsplit("/", 1)[-1],
                    "destination": self._destination_identity(destination),
                    "error": error,
                    "reason": "missing_output_directory",
                }
                for artifact in local_artifacts
                for destination in destinations
            ] + [
                {
                    "path": artifact.path,
                    "target_name": artifact.path.rsplit("/", 1)[-1],
                    "destination": self._destination_identity(destination),
                    "error": "required source artifact was not observed",
                    "reason": "missing_required_source",
                }
                for artifact in required_missing
                for destination in destinations
            ]
            return self._result(
                model_run,
                output_dir=None,
                artifacts=[],
                metadata=metadata,
                start_time=start_time,
                error=self._final_error(model_run, error, metadata),
                persistence_dir=persistence_path,
            )

        fallback_date = self._extract_start_date(model_run)
        output_stride = self._extract_output_stride(model_run)
        resolved_paths: list[Path] = []
        name_map: dict[Path, str] = {}
        source_checksums: dict[str, str] = dict(metadata["source_checksums"])
        for artifact in local_artifacts:
            source = Path(artifact.path)
            source = source if source.is_absolute() else workspace_dir / source
            resolved_paths.append(source)
            checksum = self._checksum(source)
            source_checksums[artifact.path] = checksum
            date = self._coerce_ww3_date(artifact.date) or fallback_date
            restart = artifact.artifact_type == ArtifactType.RESTART or (
                source.name.startswith("restart") and source.name.endswith(".ww3")
            )
            if restart and date is not None and output_stride is not None:
                target = compute_target_name(
                    source,
                    is_restart=True,
                    start_date=date,
                    output_stride=output_stride,
                    restart_path=source,
                )
            elif not restart and naming_policy == "datestamp_all" and date is not None:
                target = compute_target_name(source, date_str=date)
            else:
                target = source.name
            name_map[source] = target

        metadata["name_map"] = {str(path): name for path, name in name_map.items()}
        metadata["source_checksums"] = source_checksums
        metadata["transfer_identity"] = self._request_identity(
            model_run,
            local_artifacts=local_artifacts,
            remote_artifacts=remote_artifacts,
            required_missing=missing_required,
            destinations=destinations,
            name_map=name_map,
            source_checksums=source_checksums,
            artifact_types=artifact_types,
            naming_policy=naming_policy,
            failure_policy=failure_policy,
            required_policy=required_policy,
            transfer_options=transfer_options,
        )

        # Prior failures are retry evidence, never completion evidence.  A
        # success can be reused only when every recorded destination can still
        # be validated under the same deterministic identity.
        prior = None
        if persistence_path is not None:
            try:
                prior = load_postprocess(persistence_path)
            except (FileNotFoundError, OSError, ValueError, TypeError):
                prior = None
        prior_metadata = getattr(prior, "metadata", {}) or {}
        state_entry = load_postprocess_state(persistence_path) if persistence_path else None
        state_identity = None
        if state_entry is not None:
            nested_state = state_entry.get("state")
            state_identity = state_entry.get("identity")
            if state_identity is None and isinstance(nested_state, dict):
                state_identity = nested_state.get("identity")
        identity_matches = (
            prior is not None
            and prior.run_id == model_run.run_id
            and prior_metadata.get("transfer_identity") == metadata["transfer_identity"]
        )
        state_matches = (
            state_entry is not None
            and state_identity == metadata["transfer_identity"]
        )
        same_identity = identity_matches and state_matches
        prior_records = (
            list(prior_metadata.get("transfer_records", []))
            if same_identity
            and isinstance(prior_metadata.get("transfer_records", []), list)
            else []
        )
        if same_identity and isinstance(prior_metadata.get("retry_history"), list):
            metadata["retry_history"] = list(prior_metadata["retry_history"])

        pair_records: dict[tuple[str, str, str], dict[str, Any]] = {}
        for record in prior_records:
            if not isinstance(record, dict):
                continue
            for artifact, source in zip(local_artifacts, resolved_paths):
                target = name_map[source]
                for destination in destinations:
                    key = (
                        artifact.path,
                        self._destination_identity(destination),
                        target,
                    )
                    if self._record_valid(
                        record,
                        source=source,
                        source_checksum=source_checksums.get(artifact.path, ""),
                        destination=destination,
                        target_name=target,
                    ):
                        pair_records[key] = record

        all_pairs = [
            (artifact, source, name_map[source], destination)
            for artifact, source in zip(local_artifacts, resolved_paths)
            for destination in destinations
        ]
        pending_pairs = [
            pair
            for pair in all_pairs
            if (
                pair[0].path,
                self._destination_identity(pair[3]),
                pair[2],
            )
            not in pair_records
        ]
        metadata["transfer_records"] = list(pair_records.values())
        metadata["reused_count"] = len(pair_records)
        metadata["skipped_count"] += len(pair_records)
        metadata["skipped_transfer_count"] += len(pair_records)
        metadata["requested_transfer_count"] = (
            len(all_pairs) + len(required_missing) * len(destinations)
        )
        metadata["requested_count"] = len(local_artifacts) + len(required_missing)

        # A complete prior result is reusable only when every requested pair is
        # still valid.  Failure sidecars and incomplete state never enter this
        # branch.
        if (
            isinstance(prior, PostprocessSuccess)
            and prior.success
            and same_identity
            and state_entry is not None
            and state_entry.get("completed") is True
            and len(pair_records) == len(all_pairs)
            and not required_missing
        ):
            return prior

        primary_error: str | None = None
        successful_paths: set[Path] = {
            source
            for artifact, source, target, destination in all_pairs
            if (
                artifact.path,
                self._destination_identity(destination),
                target,
            ) in pair_records
        }
        try:
            manager = TransferManager()
            if not pending_pairs:
                batch = TransferBatchResult(total=0, succeeded=0, failed=0, items=[])
            elif len(pending_pairs) == len(all_pairs):
                # Preserve the manager's efficient batch path for a first
                # attempt.  Retry paths are split into pairs below so an
                # already successful destination is never duplicated.
                if policy is TransferFailurePolicy.FAIL_FAST:
                    # The manager's batch FAIL_FAST raises and discards its
                    # partial result, so observe each item before stopping.
                    items = []
                    succeeded = 0
                    failed = 0
                    for index, (
                        artifact,
                        source,
                        target,
                        destination,
                    ) in enumerate(pending_pairs):
                        single = manager.transfer_files(
                            files=[source],
                            destinations=[destination],
                            name_map={source: target},
                            policy=TransferFailurePolicy.CONTINUE,
                        )
                        items.extend(single.items)
                        succeeded += single.succeeded
                        failed += single.failed
                        if single.failed:
                            self._record_skipped_pairs(
                                metadata,
                                pending_pairs[index + 1 :],
                                "fail_fast_not_attempted",
                            )
                            break
                    batch = TransferBatchResult(
                        total=succeeded + failed,
                        succeeded=succeeded,
                        failed=failed,
                        items=items,
                    )
                else:
                    batch = manager.transfer_files(
                        files=resolved_paths,
                        destinations=destinations,
                        name_map=name_map,
                        policy=policy,
                    )
            else:
                items = []
                succeeded = 0
                failed = 0
                for index, (
                    artifact,
                    source,
                    target,
                    destination,
                ) in enumerate(pending_pairs):
                    single = manager.transfer_files(
                        files=[source],
                        destinations=[destination],
                        name_map={source: target},
                        policy=TransferFailurePolicy.CONTINUE,
                    )
                    items.extend(single.items)
                    succeeded += single.succeeded
                    failed += single.failed
                    if failed and policy is TransferFailurePolicy.FAIL_FAST:
                        self._record_skipped_pairs(
                            metadata,
                            pending_pairs[index + 1 :],
                            "fail_fast_not_attempted",
                        )
                        break
                batch = TransferBatchResult(
                    total=succeeded + failed,
                    succeeded=succeeded,
                    failed=failed,
                    items=items,
                )
            metadata["transferred_count"] = len(pair_records) + int(batch.succeeded)
            metadata["successful_transfer_count"] = int(batch.succeeded)
            metadata["failed_count"] = int(batch.failed)
            metadata["failed_transfer_count"] = int(batch.failed)
            for item in batch.items:
                requested_destination = item.dest_prefix or next(
                    (
                        destination
                        for artifact, source, target, destination in pending_pairs
                        if source == item.local_path and target == item.target_name
                    ),
                    destinations[0],
                )
                if item.ok:
                    successful_paths.add(item.local_path)
                    record = {
                        "path": str(item.local_path),
                        "destination": self._destination_identity(requested_destination),
                        "target_name": item.target_name,
                        "source_size_bytes": item.local_path.stat().st_size
                        if item.local_path.is_file()
                        else None,
                        "source_checksum": source_checksums.get(
                            next(
                                (artifact.path for artifact, source, target, destination in pending_pairs if source == item.local_path),
                                "",
                            ),
                            "",
                        ),
                        "dest_uri": item.dest_uri,
                    }
                    destination_path = self._file_destination_path(record)
                    if destination_path is not None and destination_path.is_file():
                        record["destination_size_bytes"] = destination_path.stat().st_size
                        record["destination_checksum"] = self._checksum(destination_path)
                    metadata["transfer_records"].append(record)
                else:
                    metadata["transfer_failures"].append(
                        {
                            "path": str(item.local_path),
                            "local_path": str(item.local_path),
                            "target_name": item.target_name,
                            "destination": item.dest_prefix,
                            "dest_uri": item.dest_uri,
                            "error": item.error or "Unknown error",
                            "reason": "missing_source"
                            if not item.local_path.is_file()
                            else "transfer_failed",
                        }
                    )
            if batch.failed:
                primary_error = (
                    f"Transfer failed: {batch.failed} of {batch.total} transfers failed"
                )
                first = metadata["transfer_failures"][0]
                primary_error += f". First error: {first['error']}"
        except Exception as exc:  # noqa: BLE001 - fail-fast must become typed evidence
            primary_error = f"Transfer failed: {type(exc).__name__}: {exc}"
            metadata["failed_count"] = 1
            metadata["failed_transfer_count"] = 1
            if pending_pairs:
                failed_artifact, failed_source, failed_target, failed_destination = (
                    pending_pairs[0]
                )
                metadata["transfer_failures"].append(
                    {
                        "path": failed_artifact.path,
                        "local_path": str(failed_source),
                        "target_name": failed_target,
                        "destination": self._destination_identity(failed_destination),
                        "dest_uri": failed_destination,
                        "error": str(exc),
                        "reason": "transfer_failed",
                    }
                )
                self._record_skipped_pairs(
                    metadata,
                    pending_pairs[1:],
                    "transfer_exception_not_attempted",
                )
            else:
                metadata["transfer_failures"].append(
                    {
                        "path": str(resolved_paths[0]),
                        "target_name": name_map[resolved_paths[0]],
                        "destination": destinations[0],
                        "dest_uri": destinations[0],
                        "error": str(exc),
                        "reason": "transfer_failed",
                    }
                )

        transferred_artifacts = [
            artifact.model_copy(
                update={"size_bytes": source.stat().st_size}
            )
            if source.is_file()
            else artifact
            for artifact, source in zip(local_artifacts, resolved_paths)
            if source in successful_paths
        ]
        metadata["transferred_artifacts"] = self._evidence(transferred_artifacts)
        if required_missing:
            missing_pairs = len(required_missing) * len(destinations)
            metadata["failed_count"] += missing_pairs
            metadata["failed_transfer_count"] += missing_pairs
            metadata["transfer_failures"].extend(
                {
                    "path": artifact.path,
                    "target_name": artifact.path.rsplit("/", 1)[-1],
                    "destination": self._destination_identity(destination),
                    "error": "required source artifact was not observed",
                    "reason": "missing_required_source",
                }
                for artifact in required_missing
                for destination in destinations
            )
            required_error = (
                f"Required transfer source missing: {len(required_missing)} artifact(s)"
            )
            primary_error = (
                f"{primary_error}; {required_error}"
                if primary_error is not None
                else required_error
            )
        if isinstance(model_run, ModelRunFailure):
            model_error = f"Model run failed: {model_run.error}"
            if primary_error is not None:
                metadata["transfer_diagnostic"] = {
                    "error": primary_error,
                    "failures": list(metadata["transfer_failures"]),
                }
            primary_error = model_error
        if primary_error is not None:
            metadata["retry_history"].append(
                {
                    "identity": metadata["transfer_identity"],
                    "error": primary_error,
                    "failed_count": metadata["failed_count"],
                    "transfer_failures": list(metadata["transfer_failures"]),
                }
            )
        if primary_error is None:
            return self._result(
                model_run,
                output_dir=output_dir,
                artifacts=transferred_artifacts,
                metadata=metadata,
                start_time=start_time,
                persistence_dir=persistence_path,
            )
        return self._result(
            model_run,
            output_dir=output_dir,
            artifacts=transferred_artifacts,
            metadata=metadata,
            start_time=start_time,
            error=primary_error,
            persistence_dir=persistence_path,
        )
