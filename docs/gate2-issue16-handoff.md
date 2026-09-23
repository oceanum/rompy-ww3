# Issue #16 Gate 2 handoff

**Status:** checked locally; not published or deployed

This handoff records the Gate 2 integration/publication evidence for the
`response_schema` base. The validated release-candidate implementation source
is exactly `ea4d19cf45520541bd3c9886717d9246a5218d80`
(`origin/response_schema`). The evidence-only candidate adds no production
runtime changes: it adds the standalone metadata test adjustment and this
handoff document. Those evidence files are intentionally distinct from the
release-candidate implementation source; artifact hashes below are not
claimed as hashes of the implementation commit itself.

## Pins and artifacts

| Item | Value |
| --- | --- |
| WW3 source baseline | `ea4d19cf45520541bd3c9886717d9246a5218d80` |
| Core response-schema pin | `e4fca8d6193a4315684417a31ccd101cba8c2b1c` |
| Wheel | `rompy_ww3-0.1.0-py3-none-any.whl` |
| Wheel SHA-256 | `a22b30824b44f9901e15ecd69b0ab17d80394657a42e626dcf9c9874fe73325e` |
| Sdist | `rompy_ww3-0.1.0.tar.gz` |
| Sdist SHA-256 | `c1a7180919c4842d66c740ab32a434b2ed56503eec4aaede4da3291a4f3ced50` |

These hashes are the artifacts in `/tmp/ww3-gate2-build-final`, built from
this evidence worktree after the metadata-test adjustment and before the
handoff document was added. Wheel ZIP timestamps make raw wheel hashes
build-instance-specific; the clean baseline comparison below proves member
content is unchanged. The sdist intentionally includes the evidence test
change, while the Markdown handoff is not included by `MANIFEST.in`.

The downstream Ops pin is the wheel SHA-256 above together with core commit
`e4fca8d6193a4315684417a31ccd101cba8c2b1c`; do not substitute a floating
core revision.

## Build and archive evidence

Build command (isolated `uv` build environment):

```text
rm -rf /tmp/ww3-gate2-build-final
uv build --out-dir /tmp/ww3-gate2-build-final .
sha256sum /tmp/ww3-gate2-build-final/*
```

Both wheel and sdist were produced. `twine check` passed for both. The wheel
contains 85 entries, including the package modules and all declared entry
points. The sdist contains 168 entries and includes the copied core fixture
corpus (9 fixture files). The archive manifests were captured with
`unzip -Z1 rompy_ww3-0.1.0-py3-none-any.whl` and `tar tzf
rompy_ww3-0.1.0.tar.gz`. An archive manifest scan found no `.git`, virtualenv,
`.env`, `.pi`, `.sisyphus`, cache, temporary, credential, token, password, or
`.pyc` paths.

A clean `git archive` of release-candidate source `ea4d19cf45520541bd3c9886717d9246a5218d80`
and a clean archive with only the evidence candidate applied were compared.
Both wheels had the same 85 member paths and byte-identical member payloads,
including `METADATA`, `RECORD`, and all `rompy_ww3/*.py` files; only ZIP
container timestamps changed. The sdists differed in exactly one member:
`tests/postprocess/test_issue13_sidecars.py`. This proves production wheel
package bytes are unchanged and precisely identifies the intentional sdist
difference.

Wheel entry points:

```text
rompy_ww3 = rompy_ww3.cli:app
ww3multi = rompy_ww3.config:MultiConfig
ww3shel = rompy_ww3.config:ShelConfig
ww3_transfer = rompy_ww3.postprocess.config:WW3TransferConfig
```

The wheel metadata declares the exact core direct reference:

```text
rompy @ git+https://github.com/rom-py/rompy.git@e4fca8d6193a4315684417a31ccd101cba8c2b1c
```

## Clean install proof

A fresh environment outside the workspace was created at
`/tmp/ww3-gate2-final-venv` (CPython 3.12.13). The reproducible install
sequence was:

```text
uv venv /tmp/ww3-gate2-final-venv --python 3.12
uv pip install --python /tmp/ww3-gate2-final-venv/bin/python \
  'rompy @ git+https://github.com/rom-py/rompy.git@e4fca8d6193a4315684417a31ccd101cba8c2b1c'
uv pip install --python /tmp/ww3-gate2-final-venv/bin/python \
  /tmp/ww3-gate2-build-final/rompy_ww3-0.1.0-py3-none-any.whl
/tmp/ww3-gate2-final-venv/bin/python -m pip freeze
/tmp/ww3-gate2-final-venv/bin/python -m pip check
```

Core was installed directly from GitHub at the frozen commit, then the wheel
was installed from the staged artifact; no editable install, `PYTHONPATH`, or
workspace import was used (`env -u PYTHONPATH` was used for fresh subprocess
smoke). `pip check` reported `No broken requirements found`.

Observed in a fresh subprocess:

```text
rompy version: 2.0.0a0
rompy_ww3 version: 0.1.0
rompy origin: /tmp/ww3-gate2-final-venv/lib/python3.12/site-packages/rompy/__init__.py
rompy_ww3 origin: /tmp/ww3-gate2-final-venv/lib/python3.12/site-packages/rompy_ww3/__init__.py
direct_url commit: e4fca8d6193a4315684417a31ccd101cba8c2b1c
```

The clean environment recorded `pip freeze` (132 packages after adding
validation tools), and the installed metadata exposed all four entry points
listed above. `rompy_ww3 --help` exposed the public `postprocess` command.

## Core fixtures and schema compatibility

The WW3-owned fixture corpus is copied byte-for-byte from the frozen core Gate
1 corpus and was consumed, not regenerated:

| Fixture | SHA-256 |
| --- | --- |
| `run_success.json` | `9e64d49a896a9fa521daa2cb5d0067517b3b65da5eb380d04c5d72e584d1ce9f` |
| `run_failure.json` | `d1da8ea12df2c3a40ae00c2f41fc1f345a0d4b2292f12dbeb75c2652eb267643` |
| `adversarial/legacy_v1.json` | `3c43fa6af22b2244292f3366a2c31fc4b2997e049bd98493b215187f1500abd6` |
| `adversarial/malformed.json` | `6f5e7359678e8924994c6dbfb317d70fb6443042df93c6d531bef3aa73974ba9` |
| `adversarial/unsupported_v99.json` | `b3975b59c2922984132d9a7e8febb142abb6ef7b36640e1c8db382cbd18d8265` |
| `adversarial/wrong_kind.json` | `d13d994a831fe9c7b156a08bfa30c4e1bbd8db28aa7628490fc33396db830875` |

The strict loader accepts canonical schema-v2 typed run results and rejects
core-v1, flat WW3-v1, malformed, unsupported-version, and wrong-kind
payloads with canonical regeneration guidance. The WW3 writer emits only the
core-owned `run_result.json` envelope; transfer state is separate and there
is no competing flat `run_result` writer.

## #13–#15 closure review

The preceding reviewed integrations are present on the source baseline:

- #13 merged by PR #17 at `07c113b123fb0eb620c8e9767d2195f5d889fa82`.
- #14 merged by PR #18 at `747787878b9139c4580f912c342d721bd2c1e69a`.
- #15 merged by PR #19 at `ea4d19cf45520541bd3c9886717d9246a5218d80`.

The Gate 2 installed-artifact run exercises their combined contract: typed
processor/CLI parity, persisted credentials-safe destination evidence,
expected/observed/missing artifacts, deterministic target names and checksums,
model/transfer failures, replay identity, partial retry state, and a single
core-owned flat run-result writer.

## Test and lifecycle evidence

Commands and results:

```text
PYTHONPATH="$PWD/src" /tmp/ww3-gate2-venv/bin/python -m pytest -q tests
334 passed, 66 warnings

cd /tmp && /tmp/ww3-gate2-final-venv/bin/python -m pytest -q ww3_gate2_final_tests
334 passed, 66 warnings

/tmp/ww3-gate2-final-venv/bin/ruff check tests/postprocess/test_issue13_sidecars.py
All checks passed!

/tmp/ww3-gate2-final-venv/bin/python -m compileall -q src tests
passed

/tmp/ww3-gate2-final-venv/bin/twine check /tmp/ww3-gate2-build-final/*
PASSED for wheel and sdist
```

The installed-artifact subprocess smoke also passed public imports, CLI help
and postprocess, direct typed processor/lifecycle execution, canonical
run/postprocess sidecar load/persist round trips, strict rejection, model
failure mapping, replay identity, and temporary `file://` transfer
success. Failure and retry accounting remain covered by the issue #14/#15
regression suites.

The test change in this Gate 2 patch reads the installed distribution's
`Requires-Dist` metadata rather than assuming a workspace `pyproject.toml`;
this is required for the same full suite to run from an installed wheel.

## Compatibility matrix

| Surface | Result | Notes |
| --- | --- | --- |
| Core schema-v2, exact commit | PASS | Direct GitHub install and fixture hashes agree |
| WW3 wheel clean install | PASS | Site-packages origins; `pip check`/`uv pip check` clean |
| WW3 sdist metadata | PASS | `twine check`; intended fixtures in sdist |
| Public imports and entry points | PASS | Console, config, and postprocess groups |
| CLI help and postprocess | PASS | Temporary/mock destination only |
| Typed processor and lifecycle | PASS | Success/failure/replay/persistence sidecars |
| Source test tree | PASS | 334 passed |
| Installed artifact test tree | PASS | 334 passed |
| Python 3.10 CI path | NOT RUN HERE | Existing CI targets it; no local 3.10 runtime was available |
| WW3 executable/Docker regression runs | NOT RUN | Gate used mocks/temp destinations; no model deployment |

## Warnings and residual risks

Known non-blocking warnings were observed: Pydantic deprecation warnings,
pytest warnings for legacy tests returning booleans, and expected-missing
artifact warnings in validation tests. The build emits the existing
setuptools warning that the TOML license table form is deprecated. The full
repository `ruff check .` has pre-existing baseline violations; the exact PR
CI path checks changed Python files, and the changed Gate 2 test passes Ruff.

No PyPI publish, remote transfer, deployment, or production destination was
used. Python 3.10 and compiled WW3 execution remain CI/Ops responsibilities.

## Rollback and regeneration

Rollback the Gate 2 patch to the prior `response_schema` head if the clean
artifact or CI evidence is rejected; do not change the frozen core pin while
rolling back. For stale, v1, flat, malformed, wrong-kind, or unsupported
sidecars, delete/regenerate the canonical schema-v2 `run_result.json` using
the pinned core writer. Do not migrate or heuristically reinterpret legacy
payloads. Transfer retry/replay state is disposable WW3 postprocess state and
must not be merged into the core run sidecar.

No publication or deployment is authorized by this handoff.
