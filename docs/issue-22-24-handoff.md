# WW3 composable postprocess handoff (#22–#24)

This branch keeps WW3 artifact discovery and naming in `rompy_ww3` and delegates
transfer lifecycle behavior to the core processor.

| Source | Exact ref |
| --- | --- |
| WW3 baseline | `1c125bd2da170d77b21e95d44b1320fcb244e2d8` |
| Core generic transfer | `b43c11ae0fe0f24e25786117d30128812a188760` |

`WW3TransferPostprocessor` is a compatibility/configuration adapter. It supplies
`WW3TargetNaming` to core and does not own transfer reconciliation, checksums,
credential redaction, retries, locks, result construction, or canonical
postprocess persistence. `expected_artifacts()`, `validate_outputs()`, and
`generate_manifest()` remain WW3-owned because they encode namelist rules.

## Compatibility and rollback

The existing `ww3_transfer` fields (`destinations`, `artifact_types`,
`failure_policy`, `naming_policy`, and `required_policy`) remain accepted.
`max_retries` is forwarded to core. Standalone CLI and programmatic paths load
core schema-v2 run sidecars and persist one core postprocess sidecar. The
legacy `postprocess_state.json` completion hint remains readable for callers but
is not the transfer authority.

Rollback is the exact WW3 baseline above together with core response-schema
pin `e4fca8d6193a4315684417a31ccd101cba8c2b1c`; do not mix WW3 adapter code with
that older core. No production destinations or credentials are used by tests.
