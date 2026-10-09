"""WW3 adapter for the core transfer postprocessor.

WW3 supplies target naming and configuration compatibility.  Core owns artifact
reconciliation, checksums, retries, redaction, fan-out, replay, locking,
result construction, and canonical persistence.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from rompy.core import result_persistence
from rompy.core.responses import (
    ArtifactType,
    ModelRunFailure,
    ModelRunSuccess,
    PostprocessResult,
)
from rompy.postprocess.protocol import PostprocessContext, PostprocessFailurePolicy
from rompy.postprocess.transfer import (
    TransferPostprocessor,
    TransferPostprocessorConfig,
)

from .naming import target_naming_for_run

ModelRunPayload = ModelRunSuccess | ModelRunFailure


class WW3TransferPostprocessor:
    """Thin WW3 naming/configuration adapter over core transfer."""

    name = "ww3_transfer"
    input_protocol = "context"

    def __init__(self, config: Any | None = None) -> None:
        self.config = config

    @staticmethod
    def _restore_ww3_extensions(result: ModelRunPayload, root: Path | str | None):
        if root is None:
            return result
        try:
            sidecar = result_persistence.load_run_result(Path(root))
        except (FileNotFoundError, ValueError, OSError):
            return result
        context = sidecar.normalized_context
        if context is None or not context.extensions:
            return result
        metadata = dict(result.metadata or {})
        ww3 = dict(metadata.get("ww3", {}))
        extensions = context.extensions
        nested_ww3 = extensions.get("ww3")
        if isinstance(nested_ww3, dict):
            ww3.update(nested_ww3)
            extensions = {
                key: value for key, value in extensions.items() if key != "ww3"
            }
        ww3.update(extensions)
        metadata["ww3"] = ww3
        return result.model_copy(update={"metadata": metadata})

    @staticmethod
    def _artifact_root(result: ModelRunPayload) -> Path | None:
        """Choose the run root containing the declared local artifacts.

        Core normally uses ``output_dir``.  Older WW3 runs can declare paths
        relative to their workspace, so retain that compatibility only when
        the declared artifacts are not present under the output directory.
        """
        output = Path(result.output_dir) if result.output_dir else None
        workspace = Path(result.workspace_dir) if result.workspace_dir else None
        paths = [
            Path(artifact.path)
            for artifact in result.artifacts
            if isinstance(getattr(artifact, "path", None), str)
            and "://" not in artifact.path
            and not Path(artifact.path).is_absolute()
        ]
        if output is not None and all((output / path).is_file() for path in paths):
            return output
        if workspace is not None and all((workspace / path).is_file() for path in paths):
            return workspace
        return output or workspace

    @staticmethod
    def _context(
        value: PostprocessContext | ModelRunPayload, persistence_dir: Path | str | None
    ) -> PostprocessContext:
        if isinstance(value, PostprocessContext):
            restored = WW3TransferPostprocessor._restore_ww3_extensions(
                value.run_result, persistence_dir or value.staging_dir
            )
            if restored is not value.run_result:
                value = replace(value, run_result=restored)
            root = WW3TransferPostprocessor._artifact_root(value.run_result)
            if root is not None and root != value.output_dir:
                return replace(value, output_dir=root)
            return value
        if isinstance(value, (ModelRunSuccess, ModelRunFailure)):
            value = WW3TransferPostprocessor._restore_ww3_extensions(
                value, persistence_dir or value.workspace_dir or value.output_dir
            )
            context = PostprocessContext.from_run_result(value, staging_dir=persistence_dir)
            root = WW3TransferPostprocessor._artifact_root(value)
            if root is not None and root != context.output_dir:
                context = replace(context, output_dir=root)
            return context
        raise TypeError(
            "WW3 transfer requires a PostprocessContext or concrete "
            "ModelRunSuccess or ModelRunFailure"
        )

    def _settings(
        self,
        *,
        destinations: list[str] | None,
        artifact_types: list[ArtifactType] | None,
        failure_policy: str | None,
        naming_policy: str | None,
        required_policy: str | None,
        max_retries: int | None,
    ) -> tuple[TransferPostprocessorConfig, str]:
        config = self.config
        configured_destinations = getattr(config, "destinations", None)
        effective_destinations = (
            destinations if destinations is not None else configured_destinations
        )
        if effective_destinations is None:
            raise ValueError("destinations must be a non-empty list of strings")
        effective_types = (
            artifact_types
            if artifact_types is not None
            else getattr(config, "artifact_types", None)
        )
        effective_failure = failure_policy or getattr(
            config, "failure_policy", "CONTINUE"
        )
        effective_naming = naming_policy or getattr(
            config, "naming_policy", "restart_only"
        )
        effective_required = required_policy or getattr(
            config, "required_policy", "expected_outputs_required"
        )
        effective_retries = (
            max_retries
            if max_retries is not None
            else getattr(config, "max_retries", 0)
        )
        if effective_failure in {"CONTINUE", "continue"}:
            core_failure = PostprocessFailurePolicy.CONTINUE
        elif effective_failure in {"FAIL_FAST", "fail_fast"}:
            core_failure = PostprocessFailurePolicy.FAIL_FAST
        else:
            raise ValueError(f"Invalid failure_policy: {effective_failure}")
        if effective_naming not in {"restart_only", "datestamp_all"}:
            raise ValueError(f"Invalid naming_policy: {effective_naming}")
        if effective_required not in {"expected_outputs_required", "optional"}:
            raise ValueError(f"Invalid required_policy: {effective_required}")
        transfer_config = TransferPostprocessorConfig(
            destinations=list(effective_destinations),
            artifact_types=effective_types,
            required=effective_required == "expected_outputs_required",
            failure_policy=core_failure,
            max_retries=effective_retries,
            state_namespace="ww3-transfer",
        )
        return transfer_config, effective_naming

    def process(
        self,
        context_or_result: PostprocessContext | ModelRunPayload,
        destinations: list[str] | None = None,
        artifact_types: list[ArtifactType] | None = None,
        failure_policy: str | None = None,
        naming_policy: str | None = None,
        persistence_dir: Path | str | None = None,
        required_policy: str | None = None,
        max_retries: int | None = None,
        **kwargs: Any,
    ) -> PostprocessResult:
        """Delegate transfer execution to core with a WW3 naming strategy.

        ``ModelRunResult`` input remains accepted for direct callers from the
        pre-composable API.  Core's ``ModelRun`` and pipeline paths provide the
        same typed evidence as a ``PostprocessContext``.
        """
        context = self._context(context_or_result, persistence_dir)
        transfer_config, effective_naming = self._settings(
            destinations=destinations,
            artifact_types=artifact_types,
            failure_policy=failure_policy,
            naming_policy=naming_policy,
            required_policy=required_policy,
            max_retries=max_retries,
        )
        delegate = TransferPostprocessor(
            transfer_config,
            target_naming=target_naming_for_run(context.run_result, effective_naming),
        )
        return delegate.process(context)


__all__ = ["WW3TransferPostprocessor"]
