# WW3 issue #13 sidecar fixtures

Copied byte-for-byte from the frozen core return-schema-v2 corpus at merge
`61ef30d0035e09ab5244059089b085bd1a9745b4` (core Gate 1 handoff).

| fixture | SHA-256 |
|---|---|
| `run_success.json` | `9e64d49a896a9fa521daa2cb5d0067517b3b65da5eb380d04c5d72e584d1ce9f` |
| `run_failure.json` | `d1da8ea12df2c3a40ae00c2f41fc1f345a0d4b2292f12dbeb75c2652eb267643` |
| `adversarial/legacy_v1.json` | `3c43fa6af22b2244292f3366a2c31fc4b2997e049bd98493b215187f1500abd6` |
| `adversarial/malformed.json` | `6f5e7359678e8924994c6dbfb317d70fb6443042df93c6d531bef3aa73974ba9` |
| `adversarial/unsupported_v99.json` | `b3975b59c2922984132d9a7e8febb142abb6ef7b36640e1c8db382cbd18d8265` |
| `adversarial/wrong_kind.json` | `d13d994a831fe9c7b156a08bfa30c4e1bbd8db28aa7628490fc33396db830875` |

The adversarial documents are rejection-only fixtures. WW3 provides no
migration or heuristic reader; callers must regenerate a canonical v2
`run_result.json`.
