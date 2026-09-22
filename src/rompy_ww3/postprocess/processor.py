"""Canonical WW3 output transfer postprocessor."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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

from rompy_ww3.postprocess.naming import compute_target_name
from rompy_ww3.postprocess.persistence import persist_postprocess, require_model_run

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
            return persist_postprocess(
                result,
                persistence_dir or output_dir,  # type: ignore[arg-type]
                primary_error=error,
            )
        return result

    def process(
        self,
        model_run_result: ModelRunSuccess | ModelRunFailure,
        destinations: list[str],
        artifact_types: list[ArtifactType] | None = None,
        failure_policy: str = "CONTINUE",
        naming_policy: str = "restart_only",
        persistence_dir: Path | str | None = None,
        **kwargs: Any,
    ) -> PostprocessResult:
        """Transfer local typed artifacts and persist the canonical result."""
        del kwargs
        model_run = require_model_run(model_run_result)
        persistence_path = Path(persistence_dir) if persistence_dir is not None else None
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
        remote = [item for item in observed if item.get("kind") == "remote"]
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
        required_missing = [
            artifact
            for artifact in model_run.expected_outputs
            if artifact.kind == "local"
            and artifact.path not in observed_local_paths
            and (selected_types is None or artifact.artifact_type in selected_types)
        ]

        metadata: dict[str, Any] = {
            "destinations": list(destinations),
            "destination_count": len(destinations),
            "requested_count": len(local_artifacts) + len(required_missing),
            "requested_transfer_count": (len(local_artifacts) + len(required_missing)) * len(destinations),
            "local_count": len(local_artifacts),
            "remote_count": len(remote),
            "skipped_count": len(skipped_artifacts),
            "transferred_count": 0,
            "failed_count": 0,
            "transfer_failures": [],
            "observed_artifacts": observed,
            "remote_observed_artifacts": remote,
            "skipped_artifacts": skipped_artifacts,
            "missing_required_sources": self._evidence(required_missing),
            "required_missing_count": len(required_missing),
            "name_map": {},
            "source_checksums": {},
            "transferred_artifacts": [],
        }
        if isinstance(model_run.metadata.get("artifact_checksums"), dict):
            metadata["source_checksums"].update(model_run.metadata["artifact_checksums"])

        start_time = datetime.now(timezone.utc)
        if required_missing and not local_artifacts:
            metadata["failed_count"] = len(required_missing) * len(destinations)
            metadata["transfer_failures"] = [
                {
                    "path": artifact.path,
                    "target_name": artifact.path.rsplit("/", 1)[-1],
                    "error": "required source artifact was not observed",
                    "reason": "missing_required_source",
                }
                for artifact in required_missing
            ]
            return self._result(
                model_run,
                output_dir=output_dir,
                artifacts=[],
                metadata=metadata,
                start_time=start_time,
                error=(
                    f"Required transfer source missing: {len(required_missing)} artifact(s)"
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
            metadata["transfer_failures"] = [
                {
                    "path": artifact.path,
                    "target_name": artifact.path.rsplit("/", 1)[-1],
                    "error": error,
                    "reason": "missing_output_directory",
                }
                for artifact in local_artifacts
            ]
            return self._result(
                model_run,
                output_dir=None,
                artifacts=[],
                metadata=metadata,
                start_time=start_time,
                error=error,
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
            if checksum:
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
        primary_error: str | None = None
        successful_paths: set[Path] = set()
        try:
            batch = TransferManager().transfer_files(
                files=resolved_paths,
                destinations=destinations,
                name_map=name_map,
                policy=policy,
            )
            metadata["transferred_count"] = int(batch.succeeded)
            metadata["failed_count"] = int(batch.failed)
            for item in batch.items:
                if item.ok:
                    successful_paths.add(item.local_path)
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
            artifact
            for artifact, source in zip(local_artifacts, resolved_paths)
            if source in successful_paths
        ]
        metadata["transferred_artifacts"] = self._evidence(transferred_artifacts)
        if required_missing:
            metadata["failed_count"] += len(required_missing) * len(destinations)
            metadata["transfer_failures"].extend(
                {
                    "path": artifact.path,
                    "target_name": artifact.path.rsplit("/", 1)[-1],
                    "error": "required source artifact was not observed",
                    "reason": "missing_required_source",
                }
                for artifact in required_missing
            )
            required_error = (
                f"Required transfer source missing: {len(required_missing)} artifact(s)"
            )
            primary_error = (
                f"{primary_error}; {required_error}"
                if primary_error is not None
                else required_error
            )
        if isinstance(model_run, ModelRunFailure) and primary_error is None:
            primary_error = f"Model run failed: {model_run.error}"
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
