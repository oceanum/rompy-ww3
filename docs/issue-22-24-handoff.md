# WW3 composable postprocess handoff (#22–#24)

This branch keeps WW3 artifact discovery, validation, and target naming in
`rompy_ww3` and delegates transfer lifecycle behavior to the core processor.

| Source | Exact ref |
| --- | --- |
| WW3 baseline | `1c125bd2da170d77b21e95d44b1320fcb244e2d8` |
| Core generic transfer | `b43c11ae0fe0f24e25786117d30128812a188760` |

`WW3TransferPostprocessor` is a compatibility/configuration adapter. It supplies
`WW3TargetNaming` to core and does not own transfer reconciliation, checksums,
credential redaction, retries, locks, result construction, or canonical
postprocess persistence. `expected_artifacts()`, `validate_outputs()`, and
`generate_manifest()` remain WW3-owned because they encode namelist rules.

## Test migration for the #22–#24 integration gate

The legacy Issue #14 matrix reached removed WW3 `TransferManager`, marker-state,
identity, and record-validation internals. Those tests were not made green by
restoring those internals. The 39 legacy test definitions (including the
parameterized cases) were migrated to 18 public-behavior tests in
`tests/postprocess/test_issue14_transfer_protocol.py`:

| Legacy coverage | Public replacement tests |
| --- | --- |
| `test_empty_and_mixed_evidence_are_canonical_and_persisted`, `test_all_local_success_preserves_names_checksums_and_counts`, `test_remote_and_mixed_observed_evidence_survives_transfer_result` | `test_public_modelrun_path_delegates_ww3_naming_and_core_pairs`, `test_public_modelrun_filter_preserves_observed_evidence`, `test_public_core_preserves_remote_and_local_observed_evidence` |
| `test_missing_required_source_is_failure`, `test_missing_source_is_failure_with_structured_evidence`, `test_accounting_includes_missing_pairs_and_replay_without_retry_inflation` | `test_public_lifecycle_reports_required_missing_and_persists_core_sidecar`, `test_public_modelrun_continue_accounts_for_failed_core_pairs` |
| `test_fail_fast_marks_unattempted_pairs_skipped`, `test_transfer_manager_exception_marks_first_pair_failed_and_rest_skipped`, `test_partial_transfer_returns_successful_artifacts_and_failures`, `test_fail_fast_preserves_prior_success_and_first_failure`, `test_wholly_failed_transfer_is_failure` | `test_public_modelrun_continue_accounts_for_failed_core_pairs`, `test_public_modelrun_fail_fast_marks_remaining_pairs_unattempted` |
| `test_existing_marker_does_not_reuse_changed_run_or_failure_sidecar`, `test_model_failure_never_becomes_transfer_success`, `test_model_failure_keeps_primary_error_when_required_source_is_missing`, `test_model_failure_keeps_primary_error_when_output_directory_is_missing` | `test_public_pipeline_accepts_typed_model_failure_without_private_fallback`, `test_public_lifecycle_and_cli_use_canonical_postprocess_sidecar` |
| `test_identical_replay_reuses_only_valid_prior_success`, `test_partial_retry_skips_audited_success_and_merges_evidence`, `test_partial_retry_pair_exception_preserves_prior_success`, `test_source_checksum_change_invalidates_replay_identity` | `test_public_modelrun_retry_and_replay_use_core_state`, `test_public_modelrun_replay_identity_changes_when_source_changes` |
| `test_request_identity_covers_run_destination_policy_filter_required_remote_and_options`, `test_request_identity_changes_for_source_path_and_declared_size`, `test_destination_query_order_is_canonical_and_credentials_are_excluded`, `test_duplicate_destinations_and_artifacts_transfer_once_and_replay` | `test_public_destination_identity_is_secret_free_and_stable`, `test_public_destination_evidence_uses_redacted_uri_path` |
| `test_duplicate_artifact_conflict_is_typed_and_preserves_model_error`, `test_required_duplicate_evidence_is_canonical_for_identity_and_replay`, `test_conflicting_required_duplicate_evidence_is_typed_before_missing_return`, `test_arbitrary_inputs_and_outputs_are_rejected` | `test_public_core_rejects_arbitrary_processor_input`, `test_public_core_requires_non_empty_destinations` |
| `test_destination_secrets_are_absent_from_result_and_persisted_state`, `test_uri_credentials_and_remote_artifacts_are_canonical_in_success_serialization`, `test_uri_credentials_are_scrubbed_from_failure_and_state_serialization`, `test_model_failure_remains_primary_with_transfer_failure_diagnostic` | `test_public_core_redacts_destination_and_backend_secrets` |
| `test_persistence_failure_keeps_transfer_error`, `test_fresh_subprocess_loads_and_executes_typed_transfer`, `test_cli_displays_canonical_failure_error_and_exits_nonzero`, `test_cli_and_lifecycle_use_same_canonical_sidecar` | `test_public_lifecycle_and_cli_use_canonical_postprocess_sidecar`, `test_public_cli_failure_reports_canonical_error_and_nonzero_exit`; installed acceptance remains in `test_gate2_installed_acceptance.py` |
| `test_concurrent_public_replay_transfers_each_pair_once`, `test_incomplete_or_malformed_state_never_reuses_success_sidecar`, `test_destination_disappearance_invalidates_recorded_success`, `test_nested_state_shapes_are_repaired_and_replay_reuses`, `test_atomic_state_updates_remain_valid_under_concurrent_writes` | `test_public_core_rejects_malformed_replay_state_without_reusing_success`; WW3 marker atomicity remains covered by `test_persistence.py`, while core locking/replay is exercised through the public ModelRun path |

The migrated assertions retain typed result checks, pair accounting, target
names, checksums/replay identities, redaction, canonical sidecars, and CLI exit
behavior. They use only `tmp_path` destinations or a monkeypatched core
`get_transfer` backend. No production destination or credential is used.

WW3-specific naming, expected-artifact, and `validate_outputs` tests remain in
their original suites (`test_naming.py`, `test_artifact_handling.py`,
`test_validate_outputs.py`, and the adapter naming test). The artifact filter
assertion now intentionally checks that core preserves all observed evidence
while only selected artifacts produce transfer pairs.

## Compatibility and rollback

The existing `ww3_transfer` fields (`destinations`, `artifact_types`,
`failure_policy`, `naming_policy`, and `required_policy`) remain accepted.
`max_retries` is forwarded to core. Standalone CLI and programmatic paths load
core schema-v2 run sidecars and persist one core postprocess sidecar. The
legacy `postprocess_state.json` completion hint remains readable for callers but
is not the transfer authority.

Rollback is the exact WW3 baseline above together with core response-schema pin
`e4fca8d6193a4315684417a31ccd101cba8c2b1c`; do not mix WW3 adapter code with
that older core.

## Residual risks

- Core replay state intentionally does not verify that a previously successful
  remote object still exists; a later core change may add destination auditing.
- A concurrent public call that observes the core transfer lock reports the
  typed lock failure; the old WW3 marker-repair/concurrency behavior is not
  restored.
- The installed-wheel acceptance test must run in a clean environment with
  both `rompy` and `rompy_ww3` installed as wheels. Source-editable core paths
  are deliberately rejected by that test.
- The only observed unrelated warnings are existing Pydantic deprecations,
  test functions returning booleans in `test_namelist_comparator.py`, and
  expected missing-artifact warnings from `test_validate_outputs.py`.
