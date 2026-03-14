"""WW3 post-processing transfer postprocessor.

This module provides a postprocessor that, given a WW3 model_run object,
discovers the relevant output files, computes datestamped target names, and
delegates the actual file transfers to the rompy TransferManager.

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
from rompy_ww3.postprocess.discovery import generate_manifest
from rompy_ww3.postprocess.naming import compute_target_name


class WW3TransferPostprocessor:
    """Post-process WW3 run results by transferring output files.

    This postprocessor follows the rompy postprocessor framework pattern,
    accepting configuration parameters via the process() method rather than
    __init__(). All configuration is provided by WW3TransferConfig.

    The postprocessor:
    - Discovers WW3 output files based on output_types filter
    - Generates datestamped target names for each file
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
            path=str(path),  # Store relative path as string
            artifact_type=artifact_type,
            size_bytes=size_bytes,
            description=description,
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
        model_run: Any,
        destinations: List[str],
        output_types: Dict[str, Any],
        failure_policy: str = "CONTINUE",
        **kwargs,
    ) -> PostprocessResult:
        """Execute the transfer post-processing for a given model_run.

        Args:
            model_run: The model run object containing output directory information
            destinations: List of destination URIs for file transfers
            output_types: Manifest filter describing which WW3 output types to include
            failure_policy: How to react to transfer failures ("CONTINUE" or "FAIL_FAST")
            **kwargs: Additional parameters (ignored)

        Returns:
            PostprocessSuccess or PostprocessFailure with transfer metadata.

        Steps:
        1. Extract configuration from model_run (start_date, output_stride)
        2. Resolve the output directory from the model_run
        3. Generate a manifest of files to transfer
        4. Compute per-file target names
        5. Invoke TransferManager.transfer_files with the computed mapping
        6. Return PostprocessSuccess or PostprocessFailure based on transfer results
        """

        # Validate destinations
        if not destinations:
            raise ValueError("destinations must be a non-empty list of strings")

        # Convert string policy to enum understood by the transfer backend
        if failure_policy == "CONTINUE":
            policy = TransferFailurePolicy.CONTINUE
        elif failure_policy == "FAIL_FAST":
            policy = TransferFailurePolicy.FAIL_FAST
        else:
            raise ValueError(f"Invalid failure_policy: {failure_policy}")

        # 1) Extract configuration from model_run
        start_date = self._extract_start_date(model_run)
        stop_date = self._extract_stop_date(model_run)
        output_stride = self._extract_output_stride(model_run)

        # 2) Determine where WW3 outputs live
        output_dir = self._get_output_dir(model_run)

        # 3) Build deterministic manifest of files to transfer
        files = generate_manifest(
            output_dir, output_types, start_date, stop_date, output_stride
        )
        files = [Path(p) if not isinstance(p, Path) else p for p in files]

        # Build artifacts_planned from manifest files (Task 2 + Task 3)
        artifacts_planned: List[Artifact] = []
        for file_path in files:
            # Determine artifact type from filename and configured output types
            filename = file_path.name

            if filename.startswith("restart"):
                # Restart files - Task 2
                artifact_type = ArtifactType.OTHER
            elif filename.startswith("ww3.") and filename.endswith(".nc"):
                # Field output: ww3.*.nc - Task 3
                artifact_type = (
                    ArtifactType.NETCDF
                    if "field" in output_types
                    else ArtifactType.OTHER
                )
            elif filename.startswith("points.") and filename.endswith(".nc"):
                # Point output: points.*.nc - Task 3
                artifact_type = (
                    ArtifactType.NETCDF
                    if "point" in output_types
                    else ArtifactType.OTHER
                )
            elif filename.startswith("track.") and filename.endswith(".nc"):
                # Track output: track.*.nc - Task 3
                artifact_type = (
                    ArtifactType.NETCDF
                    if "track" in output_types
                    else ArtifactType.OTHER
                )
            else:
                # Other files (e.g., spec.nc, arbitrary *.nc)
                artifact_type = ArtifactType.OTHER

            # Determine size if file exists; be resilient if it does not
            try:
                size_bytes = file_path.stat().st_size
            except (OSError, FileNotFoundError):
                size_bytes = None

            artifacts_planned.append(
                Artifact(
                    path=str(file_path),
                    artifact_type=artifact_type,
                    size_bytes=size_bytes,
                    description=None,
                )
            )

        # 4) Build mapping from source file to target name
        name_map: Dict[Path, str] = {}
        for f in files:
            # Check if it's a restart file (restart.ww3 or restart001.ww3, etc.)
            is_restart = f.name.startswith("restart") and f.name.endswith(".ww3")
            if is_restart:
                if start_date is not None and output_stride is not None:
                    target_name = compute_target_name(
                        f,
                        is_restart=True,
                        start_date=start_date,
                        output_stride=output_stride,
                        restart_path=f,
                    )
                else:
                    target_name = f.name
            else:
                target_name = compute_target_name(f, date_str=start_date)
            name_map[f] = target_name

        # 5) Perform the transfers
        manager = TransferManager()
        result = manager.transfer_files(
            files=files,
            destinations=destinations,
            name_map=name_map,
            policy=policy,
        )

        # 6) Return PostprocessSuccess or PostprocessFailure based on transfer results
        start_time = datetime.now(timezone.utc)

        # Extract run_id with fallback
        run_id = getattr(model_run, "run_id", "unknown")

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
        # Attach planned artifacts information for Task 3 downstream processing
        metadata["artifacts_planned"] = artifacts_planned

        # Calculate timing
        end_time = datetime.now(timezone.utc)
        timing = TimingInfo(
            start_time=start_time,
            end_time=end_time,
        )

        # Create artifacts only for successfully transferred files
        # Build mapping from local_path to successfully transferred items
        successful_paths = {item.local_path for item in result.items if item.ok}
        observed_artifacts = [
            self._create_artifact(f, output_dir) for f in files if f in successful_paths
        ]

        # Return success or failure based on transfer result
        if result.all_succeeded():
            return PostprocessSuccess(
                success=True,
                run_id=run_id,
                output_dir=str(output_dir),
                validated=False,
                file_count=len(files),
                artifacts=observed_artifacts,
                message=None,
                metadata=metadata,
                timing=timing,
            )
        else:
            # Extract error message from failed transfers
            error_msg = f"Transfer failed: {result.failed} of {len(files)} files failed"
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
                artifacts=observed_artifacts,
                message=None,
                metadata=metadata,
                timing=timing,
            )
