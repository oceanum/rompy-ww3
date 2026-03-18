"""WW3 post-processing transfer postprocessor.

This module provides a postprocessor that consumes ModelRunResult.artifacts
directly and delegates file transfers to the rompy TransferManager.

The postprocessor follows the rompy postprocessor framework pattern where
configuration parameters are passed via the process() method rather than
__init__(), enabling standalone postprocessor configuration files.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from rompy.core.responses import (
    PostprocessResult,
    PostprocessSuccess,
    PostprocessFailure,
    Artifact,
    ArtifactType,
    TimingInfo,
)
from rompy.transfer import TransferManager, TransferFailurePolicy
from rompy_ww3.postprocess.naming import compute_target_name


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
        pass

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
        """Resolve the output directory from a model_run object.

        The resolution order mirrors the public expectations:
        1) model_run.output_dir
        2) model_run.run_dir
        3) model_run.config.output_dir

        If a run_id is present, it will be appended to form the actual
        simulation output directory (e.g., simulations/glob3/).
        """
        base_dir = None
        for attr in ("output_dir", "run_dir"):
            value = getattr(model_run, attr, None)
            if value:
                base_dir = Path(value)
                break

        if base_dir is None:
            config = getattr(model_run, "config", None)
            if config is not None:
                od = getattr(config, "output_dir", None)
                if od:
                    base_dir = Path(od)

        if base_dir is None:
            raise AttributeError("Cannot determine output directory from model_run")

        # Check for run_id and append it to form the actual output directory
        run_id = getattr(model_run, "run_id", None)
        if run_id:
            base_dir = base_dir / run_id

        return base_dir

    def _extract_start_date(self, model_run: Any) -> Optional[str]:
        """Extract start date from model_run configuration.

        Attempts to extract from:
        1) model_run.config.ww3_shel.domain.start
        2) model_run.config.ww3_multi.domain.start
        3) model_run.period.start (converted to WW3 format)

        Returns:
            Optional[str]: Start date in 'YYYYMMDD HHMMSS' format, or None if not found
        """
        config = getattr(model_run, "config", None)
        if config is None:
            return None

        # Try ww3_shel component
        ww3_shel = getattr(config, "ww3_shel", None)
        if ww3_shel is not None:
            domain = getattr(ww3_shel, "domain", None)
            if domain is not None:
                start = getattr(domain, "start", None)
                if start is not None:
                    return start

        # Try ww3_multi component
        ww3_multi = getattr(config, "ww3_multi", None)
        if ww3_multi is not None:
            domain = getattr(ww3_multi, "domain", None)
            if domain is not None:
                start = getattr(domain, "start", None)
                if start is not None:
                    return start

        # Try period object (from rompy ModelRun)
        period = getattr(model_run, "period", None)
        if period is not None:
            start = getattr(period, "start", None)
            if start is not None:
                # Convert datetime to WW3 format
                try:
                    from datetime import datetime

                    if isinstance(start, str):
                        start = datetime.fromisoformat(start)
                    return start.strftime("%Y%m%d %H%M%S")
                except Exception:
                    pass

        return None

    def _extract_stop_date(self, model_run: Any) -> Optional[str]:
        """Extract stop date from model_run configuration.

        Attempts to extract from:
        1) model_run.config.ww3_shel.domain.stop
        2) model_run.config.ww3_multi.domain.stop
        3) model_run.period.stop (converted to WW3 format)

        Returns:
            Optional[str]: Stop date in 'YYYYMMDD HHMMSS' format, or None if not found
        """
        config = getattr(model_run, "config", None)
        if config is None:
            return None

        ww3_shel = getattr(config, "ww3_shel", None)
        if ww3_shel is not None:
            domain = getattr(ww3_shel, "domain", None)
            if domain is not None:
                stop = getattr(domain, "stop", None)
                if stop is not None:
                    return stop

        ww3_multi = getattr(config, "ww3_multi", None)
        if ww3_multi is not None:
            domain = getattr(ww3_multi, "domain", None)
            if domain is not None:
                stop = getattr(domain, "stop", None)
                if stop is not None:
                    return stop

        period = getattr(model_run, "period", None)
        if period is not None:
            stop = getattr(period, "stop", None)
            if stop is not None:
                try:
                    from datetime import datetime

                    if isinstance(stop, str):
                        stop = datetime.fromisoformat(stop)
                    return stop.strftime("%Y%m%d %H%M%S")
                except Exception:
                    pass

        return None

    def _extract_output_stride(self, model_run: Any) -> Optional[int]:
        """Extract restart output stride from model_run configuration.

        Attempts to extract from:
        1) model_run.config.ww3_shel.output_date.restart.stride
        2) model_run.config.ww3_multi.output_date.restart.stride

        Returns:
            Optional[int]: Output stride in seconds, or None if not found
        """
        config = getattr(model_run, "config", None)
        if config is None:
            return None

        # Try ww3_shel component
        ww3_shel = getattr(config, "ww3_shel", None)
        if ww3_shel is not None:
            output_date = getattr(ww3_shel, "output_date", None)
            if output_date is not None:
                restart = getattr(output_date, "restart", None)
                if restart is not None:
                    stride = getattr(restart, "stride", None)
                    if stride is not None:
                        # Convert string to int (WW3 stores as string)
                        try:
                            return int(stride)
                        except (ValueError, TypeError):
                            pass

        # Try ww3_multi component
        ww3_multi = getattr(config, "ww3_multi", None)
        if ww3_multi is not None:
            output_date = getattr(ww3_multi, "output_date", None)
            if output_date is not None:
                restart = getattr(output_date, "restart", None)
                if restart is not None:
                    stride = getattr(restart, "stride", None)
                    if stride is not None:
                        try:
                            return int(stride)
                        except (ValueError, TypeError):
                            pass

        return None

    def process(
        self,
        model_run_result: Any,
        destinations: List[str],
        artifact_types: Optional[List[ArtifactType]] = None,
        failure_policy: str = "CONTINUE",
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
        1. Validate destinations and convert failure_policy to enum
        2. Get output_dir from model_run_result.output_dir
        3. Filter artifacts by artifact_types if specified
        4. Return early with success if no artifacts to transfer
        5. Resolve source paths (absolute or relative to output_dir)
        6. Compute datestamp for each artifact (artifact.date → timing.start_time → config fallback)
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

        # Step 2: Get output_dir from ModelRunResult
        output_dir = Path(model_run_result.output_dir)

        # Step 3: Get artifacts from model_run_result and apply artifact_types filter
        artifacts = model_run_result.artifacts
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
                message=None,
                metadata={
                    "transferred_count": 0,
                    "failed_count": 0,
                    "destinations": destinations,
                },
                timing=timing,
            )

        # Step 5: Resolve source paths for all artifacts
        resolved_paths: List[Path] = []
        for artifact in artifacts:
            artifact_path = Path(artifact.path)
            if artifact_path.is_absolute():
                resolved_paths.append(artifact_path)
            else:
                resolved_paths.append(output_dir / artifact_path)

        # Step 6: Compute datestamp for target naming - use fallback order
        # Prepare fallback date sources
        fallback_date_str: Optional[str] = None

        # Fallback 1: timing.start_time from model_run_result
        timing_info = getattr(model_run_result, "timing", None)
        if timing_info is not None:
            start_time_dt = getattr(timing_info, "start_time", None)
            if start_time_dt is not None:
                # Convert datetime to WW3 format YYYYMMDD HHMMSS
                fallback_date_str = start_time_dt.strftime("%Y%m%d %H%M%S")

        # Fallback 2: _extract_start_date from model_run_result (duck-typed model_run)
        if fallback_date_str is None:
            fallback_date_str = self._extract_start_date(model_run_result)

        # Extract output_stride for restart handling
        output_stride = self._extract_output_stride(model_run_result)

        # Step 7: Build mapping from source file to target name
        name_map: Dict[Path, str] = {}
        for i, artifact in enumerate(artifacts):
            src_path = resolved_paths[i]

            # Compute date_str for this artifact using the fallback order
            artifact_date_str = fallback_date_str
            if artifact.date is not None:
                artifact_date_str = artifact.date

            # Step 8: Detect restart files
            is_restart = False
            if artifact.artifact_type == ArtifactType.RESTART:
                is_restart = True
            elif src_path.name.startswith("restart") and src_path.name.endswith(".ww3"):
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
                if artifact_date_str is not None:
                    target_name = compute_target_name(
                        src_path, date_str=artifact_date_str
                    )
                else:
                    target_name = src_path.name

            name_map[src_path] = target_name

        # Step 9: Perform the transfers
        files = resolved_paths
        manager = TransferManager()
        result = manager.transfer_files(
            files=files,
            destinations=destinations,
            name_map=name_map,
            policy=policy,
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
                message=None,
                metadata=metadata,
                timing=timing,
            )
