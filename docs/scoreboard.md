# Scoreboard: before and after

Every row says how it was measured. "Before" is the tag `before-state`; "after" is `main` on 2026-11-27 (commit 016c885 and later docs). Small lab, one repo, one run each unless noted. Nothing here is a benchmark.

| What | Before | After | How measured |
|---|---|---|---|
| zizmor findings, regular persona, scored files (`ci.yml`, `pr-greeter.yml`) | 10 (8 high, 2 medium) | **0** | `zizmor .`, `measurements/before-zizmor.txt`, `final-zizmor-scored.txt` |
| zizmor findings, auditor persona, same two files | 21 (9 high, 6 medium) | **6** (0 high, 0 medium; 4 informational, 2 low) | `measurements/final-comparison.txt` |
| zizmor, whole repo, regular persona | n/a | 0 (1 ignored, 34 suppressed) | `final-zizmor-all.txt`. Includes weak-by-design demo files, which carry inline ignores |
| zizmor, whole repo, auditor persona | n/a | 35 (14 info, 15 low, 4 medium, 0 high) | `final-zizmor-auditor.txt`. All in demo/new workflows; the repo grew from 2 to 8 workflow files, so this is not comparable to the baseline |
| `GITHUB_TOKEN` scopes in the `test` job | 17 write + 3 read | **0 write + 2 read** | "GITHUB_TOKEN Permissions" block of real logs, runs 45950056517 and 45955222047 |
| Stored cloud credentials | 1 (dummy client secret) | **0** | secret list; replaced by OIDC (run 45956627317). Three Azure IDs were kept as masked secrets, then deleted at teardown; they were identifiers, not credentials |
| Repo secrets now | 4 (`DEMO_API_TOKEN` + 3 Azure) | 1 (`DEMO_API_TOKEN`, dummy, used only by the deliberate demos) | `gh secret list` |
| Secrets exposed by the crafted PR title | 1 (canary printed, base64 form, PR #1) | **0** (same title replayed, PRs #7 and #8: printed as plain text) | logs in `measurements/demo1-*` |
| Third-party actions pinned to a full SHA (ci/greeter) | 5 `unpinned-uses` findings | 0 (SHAs, version in a comment) | zizmor `unpinned-uses` 5 to 0 |
| Image vulnerability-scan rows (Grype, one scan each) | 178 (node:20-alpine) | **28** (node:24-alpine, npm/yarn removed, non-root) | `measurements/image-scan-*.txt`. Rows = package+advisory pairs, not distinct bugs; remaining 28 are Alpine OS packages |
| Image provenance | none | SBOM attached, keyless Cosign signature verified in CI | `ci.yml` build job |
| Who can change `main` / deploy | anyone with write access, no checks | PR + `test`,`build`,`zizmor` required, admin enforced; deploy needs approval and `main`-only | API settings; direct push and `--admin` merge refused (PR #12) |
| Egress from CI jobs | open | block mode with per-job allowlists | `demo-egress-block.yml`: `github.com` allowed, `example.org` blocked |
| AI step: secret leaked to injected text | yes (simulated agent) | no | run 46029843286. Simulation, not a real model |

## Things that did not improve, or got worse
- The auditor count for the whole repo is higher than at baseline only because I added demo workflows. The like-for-like row (21 to 6) is the fair one.
- The 28 remaining scan rows are unpatched OS packages; the scan is report-only on purpose.
- Approvals required on `main`: 0. One maintainer cannot approve their own work.
- Dependabot opened major-version PRs I have not reviewed.

## Not measured
Real attacker behaviour, fork PRs, real AI products, time cost of the changes, false-positive rates of the tools.
