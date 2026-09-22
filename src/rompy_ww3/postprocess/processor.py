"""WW3 post-processing transfer postprocessor.

This module provides a postprocessor that consumes ModelRunResult.artifacts
directly and delegates file transfers to the rompy TransferManager.

The postprocessor follows the rompy postprocessor framework pattern where
configuration parameters are passed via the process() method rather than
__init__(), enabling standalone postprocessor configuration files.
"""

from __future__ import annotations

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
from rompy_ww3.postprocess.persistence import coerce_model_run

logger = logging.getLogger(__name__)


class WW3TransferPostprocessor:
    """Post-process WW3 run results by transferring output files.

    This postprocessor follows the rompy postprocessor framework pattern,
    accepting configuration parameters via the process() method rather than
    __init__(). All configuration is provided by WW3TransferConfig.

    The postprocessor:
    - Consumes ModelRunResult.artifacts directly (no file discovery)
    - Generates datestamped target names for each artifact
    - Transfers files to multiple destinations using rompy TransferManager
    - Handles failures according to the specified policy
    """

    def __init__(self) -> None:
        """Initialize the postprocessor.

        Note: This follows the new rompy postprocessor pattern where
        configuration parameters are passed via process(), not __init__().
        """

    def _create_artifact(self, path: Path, output_dir: Path) -> Artifact:
        """Create an Artifact object from a file path.

        Maps WW3 file types to ArtifactType enum, extracts file size,
        and generates a human-readable description.

        Args:
            path: Path to the file (relative to output_dir or absolute)
            output_dir: Base output directory for the model run

        Returns:
            Artifact object with metadata
        """
        # Resolve to absolute path if relative
        if not path.is_absolute():
            abs_path = output_dir / path
        else:
            abs_path = path

        # Determine artifact type from file extension
        suffix = path.suffix.lower()
        if suffix == ".nc":
            artifact_type = ArtifactType.NETCDF
        elif suffix == ".yaml" or suffix == ".yml":
            artifact_type = ArtifactType.YAML
        elif suffix == ".ww3":
            artifact_type = ArtifactType.OTHER  # Binary restart file
        elif suffix in [".txt", ".list", ".nml"]:
            artifact_type = ArtifactType.TEXT
        else:
            artifact_type = ArtifactType.OTHER

        # Extract file size if file exists
        size_bytes = None
        if abs_path.exists():
            size_bytes = abs_path.stat().st_size

        # Generate description based on file type and name
        name = path.name
        if suffix == ".ww3":
            description = f"WW3 binary restart file: {name}"
        elif suffix == ".nc":
            description = f"WW3 NetCDF output: {name}"
        elif suffix == ".yaml" or suffix == ".yml":
            description = f"WW3 configuration file: {name}"
        else:
            description = f"WW3 output file: {name}"

        return Artifact(
            path=str(path),
            artifact_type=artifact_type,
            size_bytes=size_bytes,
            description=description,
            date=None,
        )

    def _get_output_dir(self, model_run: Any) -> Path:
        """Resolve only direct in-memory output directory attributes."""
        value = getattr(model_run, "output_dir", None) or getattr(model_run, "run_dir", None)
        if not value:
            raise AttributeError("Cannot determine output directory from model_run")
        return Path(value)

    def _extract_start_date(
        self, model_run: ModelRunSuccess | ModelRunFailure
    ) -> str | None:
        """Use only typed core timing as the transfer date fallback."""
        return self._coerce_ww3_date(model_run.timing.start_time)

    def _extract_output_stride(
        self, model_run: ModelRunSuccess | ModelRunFailure
    ) -> int | None:
        """Read an optional WW3 stride from validated result metadata only."""
        ww3_metadata = model_run.metadata.get("ww3", {})
        if not isinstance(ww3_metadata, dict):
            return None
        stride = ww3_metadata.get("restart_stride_seconds")
        if isinstance(stride, bool):
            return None
        try:
            return int(stride) if stride is not None else None
        except (TypeError, ValueError):
            return None

    def _coerce_ww3_date(self, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        try:
            return value.strftime("%Y%m%d %H%M%S")
        except (AttributeError, TypeError):
            return None

    def process(
        self,
        model_run_result: Any,
        destinations: list[str],
        artifact_types: list[ArtifactType] | None = None,
        failure_policy: str = "CONTINUE",
        naming_policy: str = "restart_only",
        **kwargs,
    ) -> PostprocessResult:
        """Execute the transfer post-processing for a given model_run_result.

        Args:
            model_run_result: ModelRunResult object with artifacts list
            destinations: List of destination URIs for file transfers
            artifact_types: Optional filter for artifact types to transfer
            failure_policy: How to react to transfer failures ("CONTINUE" or "FAIL_FAST")
            **kwargs: Additional parameters (ignored)

        Returns:
            PostprocessSuccess or PostprocessFailure with transfer metadata.

        Steps:
        1. Validate the typed core ModelRunResult and destinations
        2. Get output_dir from model_run_result.output_dir
        3. Filter local typed artifacts by artifact_types if specified
        4. Return early with success if no artifacts to transfer
        5. Resolve source paths (absolute or relative to output_dir)
        6. Compute datestamp from artifact evidence or typed timing
        7. Detect restart files and compute target names
        8. Build name_map and invoke TransferManager
        9. Return PostprocessSuccess or PostprocessFailure based on transfer results
        """

        # Step 1: Validate destinations
        if not destinations:
            raise ValueError("destinations must be a non-empty list of strings")

        # Convert string policy to enum understood by the transfer backend
        if failure_policy == "CONTINUE":
            policy = TransferFailurePolicy.CONTINUE
        elif failure_policy == "FAIL_FAST":
            policy = TransferFailurePolicy.FAIL_FAST
        else:
            raise ValueError(f"Invalid failure_policy: {failure_policy}")

        model_run_result = coerce_model_run(model_run_result)

        # Step 2: Get output_dir from ModelRunResult
        output_dir = Path(model_run_result.output_dir)

        # Step 3: Get artifacts from model_run_result and apply artifact_types filter
        # Remote evidence is preserved by the core model but is not a local
        # transfer input; only local ArtifactIdentity values have ``path``.
        artifacts = [
            artifact
            for artifact in model_run_result.artifacts
            if getattr(artifact, "kind", "local") == "local"
        ]
        if artifact_types is not None:
            artifacts = [
                a
                for a in artifacts
                if a.artifact_type is not None and a.artifact_type in artifact_types
            ]

        # Step 4: Return early if no artifacts to transfer
        if not artifacts:
            # Extract run_id
            run_id = getattr(model_run_result, "run_id", "unknown")

            # Build timing
            start_time = datetime.now(timezone.utc)
            end_time = datetime.now(timezone.utc)
            timing = TimingInfo(start_time=start_time, end_time=end_time)

            return PostprocessSuccess(
                success=True,
                run_id=run_id,
                output_dir=str(output_dir),
                validated=False,
                file_count=0,
                artifacts=[],
                expected_outputs=list(model_run_result.expected_outputs),
                missing_outputs=list(model_run_result.missing_outputs),
                message=None,
                metadata={
                    "transferred_count": 0,
                    "failed_count": 0,
                    "destinations": destinations,
                },
                timing=timing,
            )

        # Step 5: Resolve source paths for all artifacts
        resolved_paths: list[Path] = []
        for artifact in artifacts:
            artifact_path = Path(artifact.path)
            if artifact_path.is_absolute():
                resolved_paths.append(artifact_path)
            else:
                resolved_paths.append(output_dir / artifact_path)

        if naming_policy not in {"restart_only", "datestamp_all"}:
            raise ValueError(f"Invalid naming_policy: {naming_policy}")

        fallback_date_str = self._extract_start_date(model_run_result)

        if fallback_date_str is None:
            timing_info = getattr(model_run_result, "timing", None)
            if timing_info is not None:
                start_time_dt = getattr(timing_info, "start_time", None)
                fallback_date_str = self._coerce_ww3_date(start_time_dt)

        # Extract output_stride for restart handling
        output_stride = self._extract_output_stride(model_run_result)

        logger.info(
            "WW3 transfer preparing %s artifacts to %s destination(s) with naming_policy=%s",
            len(artifacts),
            len(destinations),
            naming_policy,
        )

        # Step 7: Build mapping from source file to target name
        name_map: dict[Path, str] = {}
        for i, artifact in enumerate(artifacts):
            src_path = resolved_paths[i]

            artifact_date_str = (
                self._coerce_ww3_date(artifact.date) or fallback_date_str
            )

            # Step 8: Detect restart files
            is_restart = False
            if artifact.artifact_type == ArtifactType.RESTART or src_path.name.startswith("restart") and src_path.name.endswith(".ww3"):
                is_restart = True

            if is_restart:
                if artifact_date_str is not None and output_stride is not None:
                    target_name = compute_target_name(
                        src_path,
                        is_restart=True,
                        start_date=artifact_date_str,
                        output_stride=output_stride,
                        restart_path=src_path,
                    )
                else:
                    target_name = src_path.name
            else:
                if naming_policy == "datestamp_all" and artifact_date_str is not None:
                    target_name = compute_target_name(
                        src_path, date_str=artifact_date_str
                    )
                else:
                    target_name = src_path.name

            name_map[src_path] = target_name

        for src_path, target_name in name_map.items():
            logger.info("WW3 transfer target %s -> %s", src_path.name, target_name)

        # Step 9: Perform the transfers
        files = resolved_paths
        manager = TransferManager()
        result = manager.transfer_files(
            files=files,
            destinations=destinations,
            name_map=name_map,
            policy=policy,
        )

        logger.info(
            "WW3 transfer completed: %s succeeded, %s failed",
            result.succeeded,
            result.failed,
        )

        # Step 10: Build result - timing starts now
        start_time = datetime.now(timezone.utc)

        # Extract run_id with fallback
        run_id = getattr(model_run_result, "run_id", "unknown")

        # Build transfer metadata with detailed failure information
        transfer_failures = []
        for item in result.items:
            if not item.ok:
                transfer_failures.append(
                    {
                        "local_path": str(item.local_path),
                        "target_name": item.target_name,
                        "dest_uri": item.dest_uri,
                        "error": item.error or "Unknown error",
                    }
                )

        metadata = {
            "transferred_count": int(result.succeeded),
            "failed_count": int(result.failed),
            "destinations": destinations,
            "name_map": {str(k): v for k, v in name_map.items()},
            "transfer_failures": transfer_failures,
        }

        # Calculate timing
        end_time = datetime.now(timezone.utc)
        timing = TimingInfo(
            start_time=start_time,
            end_time=end_time,
        )

        # Step 11: Build result artifacts from successfully transferred artifacts only
        successful_paths = {item.local_path for item in result.items if item.ok}
        result_artifacts = [
            artifacts[i]
            for i, src_path in enumerate(resolved_paths)
            if src_path in successful_paths
        ]

        # Return success or failure based on transfer result
        if result.all_succeeded():
            return PostprocessSuccess(
                success=True,
                run_id=run_id,
                output_dir=str(output_dir),
                validated=False,
                file_count=len(artifacts),
                artifacts=result_artifacts,
                expected_outputs=list(model_run_result.expected_outputs),
                missing_outputs=list(model_run_result.missing_outputs),
                message=None,
                metadata=metadata,
                timing=timing,
            )
        else:
            # Extract error message from failed transfers
            error_msg = (
                f"Transfer failed: {result.failed} of {len(artifacts)} files failed"
            )
            if result.items:
                failed_items = [item for item in result.items if not item.ok]
                if failed_items and failed_items[0].error:
                    error_msg += f". First error: {failed_items[0].error}"

            # For failures, artifacts list contains only successfully transferred files
            return PostprocessFailure(
                success=False,
                run_id=run_id,
                error=error_msg,
                output_dir=str(output_dir),
                artifacts=result_artifacts,
                expected_outputs=list(model_run_result.expected_outputs),
                missing_outputs=list(model_run_result.missing_outputs),
                message=None,
                metadata=metadata,
                timing=timing,
            )
