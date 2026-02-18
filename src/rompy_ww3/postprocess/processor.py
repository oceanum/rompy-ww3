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

    def process(
        self,
        model_run: Any,
        destinations: List[str],
        output_types: Dict[str, Any],
        failure_policy: str = "CONTINUE",
        start_date: Optional[str] = None,
        output_stride: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, object]:
        """Execute the transfer post-processing for a given model_run.

        Args:
            model_run: The model run object containing output directory information
            destinations: List of destination URIs for file transfers
            output_types: Manifest filter describing which WW3 output types to include
            failure_policy: How to react to transfer failures ("CONTINUE" or "FAIL_FAST")
            start_date: Optional date string (YYYYMMDD HHMMSS) for generating target names
            output_stride: Optional stride in seconds for restart file naming
            **kwargs: Additional parameters (ignored)

        Returns:
            Dictionary with transfer results:
            - success: bool indicating if all transfers succeeded
            - transferred_count: number of successful transfers
            - failed_count: number of failed transfers
            - results: list of per-file transfer results

        Steps:
        1. Resolve the output directory from the model_run
        2. Generate a manifest of files to transfer
        3. Compute per-file target names
        4. Invoke TransferManager.transfer_files with the computed mapping
        5. Return a structured summary of the transfer results
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

        # 1) Determine where WW3 outputs live
        output_dir = self._get_output_dir(model_run)

        # 2) Build manifest of files to transfer
        files = generate_manifest(output_dir, output_types)
        files = [Path(p) if not isinstance(p, Path) else p for p in files]

        # 3) Build mapping from source file to target name
        # Use Path objects as keys to satisfy TransferManager expectations
        name_map: Dict[Path, str] = {}
        for f in files:
            # Detect restart files for special compute_target_name usage
            is_restart = f.name == "restart.ww3"
            if is_restart:
                # If restart-specific params are available, compute a proper
                # restart target name. Otherwise, fall back to a stable name
                # based on the file name to avoid raising during tests.
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

        # 4) Perform the transfers
        manager = TransferManager()
        result = manager.transfer_files(
            files=files,
            destinations=destinations,
            name_map=name_map,
            policy=policy,
        )

        # 5) Normalize the result into a predictable dict
        # TransferBatchResult exposes: total, succeeded, failed, items, and all_succeeded()
        return {
            "success": bool(result.all_succeeded()),
            "transferred_count": int(result.succeeded),
            "failed_count": int(result.failed),
            "results": result.items,
        }
