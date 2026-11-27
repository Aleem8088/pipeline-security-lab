# pipeline-security-lab: I attacked my own pipeline

A tiny Node service plus a GitHub Actions setup that is **deliberately insecure at first**. I demonstrate each weakness on my own repo with dummy canary secrets, then fix them one commit at a time and measure the result.

> Everything here is defensive and educational. Only my own repo and my own accounts are involved. The "secrets" are dummy values that unlock nothing.

## The four weaknesses in the "before" state

| | Weakness | Where |
|---|---|---|
| a | Script injection: PR title pasted into a shell script (on `pull_request_target`, which has secrets) | `.github/workflows/pr-greeter.yml` |
| b | Third-party actions referenced by movable tags, not commit SHAs | `.github/workflows/ci.yml` |
| c | `permissions: write-all` | both workflows |
| d | A long-lived cloud credential stored as a repo secret | `ci.yml`, deploy job |

## Plan
1. Before state (this commit; tagged `before-state`).
2. Demonstrate each weakness safely.
3. One fix per commit: pin to SHAs + Dependabot, least-privilege permissions, Azure OIDC instead of the static key, zizmor in CI, harden-runner, SBOM + image scan + Cosign, branch protection and approval gates.
4. Before/after table from real tool output, with what each fix does *and does not* stop.

## Run locally
```bash
npm ci && npm test
npm start     # http://localhost:3000
```

## Status
Early work in progress. Findings and results will be added here as they are measured, not before.

<!-- retest 2 -->
