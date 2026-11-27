# Threat model

Scope: the CI/CD pipeline of this one small repo (Node service, GitHub Actions, GHCR image, Azure deploy via OIDC). Written after the fact from what I built and tested; it is a map of what I considered, not a security certification.

## What is worth protecting
| Asset | Why it matters |
|---|---|
| `main` branch and workflow files | Whoever changes a workflow controls everything the pipeline can do |
| Secrets and cloud access | Stored secrets leak; cloud access can change or delete real resources |
| The published image | Consumers trust it came from this pipeline |
| `GITHUB_TOKEN` | Write access to code, packages, issues |

## Who I considered
1. A stranger who can open an issue or pull request (public repo).
2. A compromised or malicious third-party action or base image.
3. A contributor who makes an honest, risky mistake (including me).
4. Not considered: a compromised GitHub, runner escape, a stolen maintainer account, a malicious npm dependency beyond Dependabot, insider abuse.

## Attack paths, controls, and what is left

| # | Path | Control in this repo | Evidence | What it does NOT stop |
|---|---|---|---|---|
| 1 | PR title or issue text pasted into a shell script (script injection) | Text passed through `env:` and quoted; secret removed from the job; trigger moved from `pull_request_target` to `pull_request` | PRs #1 vs #7/#8; zizmor `template-injection` | Other untrusted-text flows (action inputs, files read at runtime); fork PRs not tested |
| 2 | Action tag moved to malicious code | Full-SHA pinning, Dependabot with 7-day cooldown | Demo 2 re-run: tag moved, pinned workflow unchanged | An action already malicious when pinned; pinned code still runs with whatever the job grants |
| 3 | Over-broad token | `permissions: {}` default, per-job minimum | 17 write + 3 read to 0 write + 2 read | A job that legitimately needs a write scope still has it (`build` has `packages: write`, `id-token: write`) |
| 4 | Static cloud secret stolen | OIDC: short-lived token, subject limited to this repo's `production` environment, Reader role | Run 45956627317; negative tests refused (AADSTS700213, write denied) | A job allowed into `production` can still use Reader access; trust policy mistakes (missing `sub` condition) would reopen it |
| 5 | Risky workflow merged | zizmor required check; PR required; admin enforced | PR #9 blocked at the check; PR #12 refusals | Rules live in settings; an admin can switch them off and nothing alerts. I also merged PR #9 once by mistake before enforcing admins (disclosed in `fixes.md`) |
| 6 | Data sent out of a job | harden-runner in block mode with per-job allowlists | `demo-egress-block.yml` | Exfiltration to an allowed host (e.g. `github.com`); allowlists built from one run can miss hosts (this happened twice); telemetry goes to StepSecurity |
| 7 | Tampered or vulnerable image | Digest-pinned base, scan (report-only), SBOM, keyless Cosign signature verified in CI | Scan rows 178 to 28 | A signature proves where the image was built, not that it is safe. 28 OS-package rows remain. Signing record is public and permanent |
| 8 | Unreviewed deploy | `production` environment needs approval and accepts `main` only | Two approved deploys; branch policy refusal | No second reviewer exists (0 required approvals); a tricked approver still approves |
| 9 | AI agent steered by untrusted text | Split design: reader with no secret/tools, privileged step validates output against an allowlist | Run 46029843286 | Wrong-but-allowed answers, misleading text, real-model behaviour (the agent was simulated) |

## Residual risks, ranked by how much I would worry
1. **One maintainer.** Every control is operated by the person it protects against. A second reviewer is the biggest missing control.
2. **Allowed destinations.** Egress filtering by domain cannot see abuse of a permitted domain.
3. **Trust in pinned third-party code.** Pinning freezes what you trust; it does not vet it.
4. **Settings are not code.** Branch protection and environment rules can be changed without a pull request.
5. **Untested items.** Force-push and branch-deletion blocking, fork PRs, non-admin contributor flow, a real AI product.

## Platform changes to check
GitHub's docs say public repos get a default block on `pull_request_target` from 2026-12-02, and that this does not fix command injection. Its 2026 roadmap lists further planned controls; check which are live before relying on them.
