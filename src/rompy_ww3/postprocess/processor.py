"""WW3 post-processing transfer postprocessor.

This module provides a postprocessor that, given a WW3 model_run object,
discovers the relevant output files, computes datestamped target names, and
delegates the actual file transfers to the rompy TransferManager.

The postprocessor follows the rompy postprocessor framework pattern where
configuration parameters are passed via the process() method rather than
__init__(), enabling standalone postprocessor configuration files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

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

    def _get_output_dir(self, model_run: Any) -> Path:
        """Resolve the output directory from a model_run object.

        The resolution order mirrors the public expectations:
        1) model_run.output_dir
        2) model_run.run_dir
        3) model_run.config.output_dir
        """
        for attr in ("output_dir", "run_dir"):
            value = getattr(model_run, attr, None)
            if value:
                return Path(value)

        config = getattr(model_run, "config", None)
        if config is not None:
            od = getattr(config, "output_dir", None)
            if od:
                return Path(od)

        raise AttributeError("Cannot determine output directory from model_run")

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
    ) -> Dict[str, object]:
        """Execute the transfer post-processing for a given model_run.

        Args:
            model_run: The model run object containing output directory information
            destinations: List of destination URIs for file transfers
            output_types: Manifest filter describing which WW3 output types to include
            failure_policy: How to react to transfer failures ("CONTINUE" or "FAIL_FAST")
            **kwargs: Additional parameters (ignored)

        Returns:
            Dictionary with transfer results:
            - success: bool indicating if all transfers succeeded
            - transferred_count: number of successful transfers
            - failed_count: number of failed transfers
            - results: list of per-file transfer results

        Steps:
        1. Extract configuration from model_run (start_date, output_stride)
        2. Resolve the output directory from the model_run
        3. Generate a manifest of files to transfer
        4. Compute per-file target names
        5. Invoke TransferManager.transfer_files with the computed mapping
        6. Return a structured summary of the transfer results
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
        output_stride = self._extract_output_stride(model_run)

        # 2) Determine where WW3 outputs live
        output_dir = self._get_output_dir(model_run)

        # 3) Build manifest of files to transfer
        files = generate_manifest(output_dir, output_types)
        files = [Path(p) if not isinstance(p, Path) else p for p in files]

        # 4) Build mapping from source file to target name
        name_map: Dict[Path, str] = {}
        for f in files:
            is_restart = f.name == "restart.ww3"
            if is_restart:
                if start_date is not None and output_stride is not None:
                    target_name = compute_target_name(
                        f,
                        is_restart=True,
                        start_date=start_date,
                        output_stride=output_stride,
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

        # 6) Normalize the result into a predictable dict
        return {
            "success": bool(result.all_succeeded()),
            "transferred_count": int(result.succeeded),
            "failed_count": int(result.failed),
            "results": result.items,
        }
