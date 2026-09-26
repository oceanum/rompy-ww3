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
    ):
        if isinstance(value, PostprocessContext):
            return value
        if isinstance(value, (ModelRunSuccess, ModelRunFailure)):
            context = PostprocessContext.from_run_result(
                value, staging_dir=persistence_dir
            )
            # Older WW3 results may use ``output_dir`` for a generated child
            # directory while artifact paths remain relative to workspace_dir.
            # Keep that compatibility at the adapter boundary; core still
            # owns reconciliation and path safety.
            if value.workspace_dir:
                workspace = Path(value.workspace_dir)
                context = replace(context, output_dir=workspace)
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

    @staticmethod
    def _legacy_metadata(
        context: PostprocessContext, result: PostprocessResult
    ) -> dict[str, Any]:
        """Project core pair evidence for callers of the old WW3 result API.

        Transfer decisions and accounting remain core-owned; these aliases are
        read-only compatibility evidence and are not consulted for replay.
        """
        metadata = dict(result.metadata)
        transfer = metadata.get("transfer", {})
        pairs = transfer.get("pairs", []) if isinstance(transfer, dict) else []
        succeeded = [item for item in pairs if item.get("status") == "succeeded"]
        failed = [item for item in pairs if item.get("status") == "failed"]
        skipped = [
            item for item in pairs if item.get("status") in {"skipped", "unattempted"}
        ]
        name_map: dict[str, str] = {}
        source_checksums: dict[str, str] = {}
        for item in pairs:
            source = str(item.get("source", ""))
            if source.startswith("local:"):
                path = source.removeprefix("local:")
                name = str(item.get("destination", "")).rsplit("/", 1)[-1]
                root = context.output_dir or context.staging_dir
                name_map[str(root / path) if root is not None else path] = name
                if item.get("source_checksum"):
                    source_checksums[path] = str(item["source_checksum"])
        replayed = [item for item in pairs if item.get("status") == "skipped"]
        local_count = len(
            {
                str(item.get("source", ""))
                for item in pairs
                if str(item.get("source", "")).startswith("local:")
            }
        )
        remote_count = sum(
            1 for item in context.artifacts if getattr(item, "kind", None) == "remote"
        )
        metadata.update(
            {
                "destinations": sorted(
                    {
                        str(item.get("destination", "")).rsplit("/", 1)[0]
                        for item in pairs
                        if item.get("destination")
                    }
                ),
                "name_map": name_map,
                "source_checksums": source_checksums,
                "transfer_records": succeeded,
                "transfer_failures": failed,
                "requested_count": local_count,
                "requested_transfer_count": len(pairs),
                "local_count": local_count,
                "remote_count": remote_count,
                "transferred_count": len(succeeded) + len(replayed),
                "successful_transfer_count": len(succeeded),
                "failed_count": len(failed),
                "failed_transfer_count": len(failed),
                "skipped_transfer_count": len(skipped),
                "skipped_count": len(skipped) + remote_count,
                "reused_count": len(replayed),
                "transferred_artifacts": [
                    item.model_dump(mode="json") for item in result.artifacts
                ],
            }
        )
        return metadata

    @staticmethod
    def _get_output_dir(model_run: ModelRunPayload) -> Path:
        """Compatibility accessor for canonical typed run results."""
        if not isinstance(model_run, (ModelRunSuccess, ModelRunFailure)):
            raise TypeError(
                "WW3 transfer requires a concrete ModelRunSuccess or ModelRunFailure"
            )
        if not model_run.output_dir:
            raise AttributeError("Cannot determine output directory from model_run")
        return Path(model_run.output_dir)

    @staticmethod
    def _extract_start_date(model_run: ModelRunPayload) -> str | None:
        """Compatibility accessor for the WW3 naming strategy input."""
        if not isinstance(model_run, (ModelRunSuccess, ModelRunFailure)):
            raise TypeError(
                "WW3 transfer requires a concrete ModelRunSuccess or ModelRunFailure"
            )
        value = getattr(model_run.timing, "start_time", None)
        return value.strftime("%Y%m%d %H%M%S") if value is not None else None

    @staticmethod
    def _extract_output_stride(model_run: ModelRunPayload) -> int | None:
        """Read the typed WW3 restart stride hint without private config access."""
        if not isinstance(model_run, (ModelRunSuccess, ModelRunFailure)):
            raise TypeError(
                "WW3 transfer requires a concrete ModelRunSuccess or ModelRunFailure"
            )
        value = (model_run.metadata.get("ww3", {}) or {}).get("restart_stride_seconds")
        if isinstance(value, bool) or value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

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
        result = delegate.process(context)
        return result.model_copy(
            update={"metadata": self._legacy_metadata(context, result)}
        )


__all__ = ["WW3TransferPostprocessor"]
