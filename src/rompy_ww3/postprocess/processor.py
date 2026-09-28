"""WW3 adapter for the core transfer postprocessor.

WW3 supplies target naming and configuration compatibility.  Core owns artifact
reconciliation, checksums, retries, redaction, fan-out, replay, locking,
result construction, and canonical persistence.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

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
    def _context(
        value: PostprocessContext | ModelRunPayload, persistence_dir: Path | str | None
    ) -> PostprocessContext:
        if isinstance(value, PostprocessContext):
            # Core creates contexts with ``output_dir`` from the run result.
            # WW3 artifacts are workspace-relative, so use the same workspace
            # authority as direct typed-result calls when a generated output
            # child is present.
            workspace = value.run_result.workspace_dir
            if workspace:
                return replace(value, output_dir=Path(workspace))
            return value
        if isinstance(value, (ModelRunSuccess, ModelRunFailure)):
            context = PostprocessContext.from_run_result(
                value, staging_dir=persistence_dir
            )
            if value.workspace_dir:
                context = replace(context, output_dir=Path(value.workspace_dir))
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
