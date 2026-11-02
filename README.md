# toolcall-reliability-harness

A small, dependency-free harness that grades **agent tool-call traces** against a tool registry, so a failed run
tells you *why* it failed (not just a pass/fail score). Built as a proof of concept for teams shipping agents that act
on real apps (email, CRM, calendar) where one bad call is costly.

## What it checks
| Finding | Meaning |
|---|---|
| `unknown_tool` | agent invented a tool that is not in the registry |
| `missing_arg` / `bad_type` / `extra_arg` | call does not match the tool schema |
| `unapproved_write` | a write tool marked `needs_approval` ran without an approval step (action-level permissions) |
| `loop` | same tool + args repeated beyond a limit (retry storms) |
| `ignored_error` | the agent reported success after its last tool call errored |

## Run
```bash
pip install pytest
python -m pytest -q
PYTHONPATH=src python -m tcr.cli data/traces.json
```
Sample output: `traces=6 pass_rate=0.333` with each failing trace and its reasons.

## Extend
Add tools to `src/tcr/registry.py`; add traces to `data/traces.json` (record real agent runs in the same shape).
Next steps: replay traces against a sandbox, auto-generate a repair prompt from findings, track pass rate per release.
