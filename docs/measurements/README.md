# Measurements

Raw tool output, kept so the before/after numbers can be checked.

## Baseline (before state, tag `before-state`)
Tool: zizmor 1.33.1, default ("regular") persona, run from the repo root with `zizmor .`.

| Rule | Findings | Severity |
|---|---|---|
| unpinned-uses | 5 | high |
| dangerous-triggers | 1 | high |
| template-injection | 1 | high |
| excessive-permissions | 1 | high |
| artipacked (checkout keeps credentials) | 2 | medium |
| **Total** | **10** | 8 high, 2 medium |

With `--persona auditor` (more false positives allowed) zizmor reports 21.
Files: `before-zizmor.txt`, `before-zizmor.json`.

Note: zizmor does not flag the static cloud secret as a finding. That weakness is measured differently (see later write-up): by listing which long-lived secrets exist in the repo.
