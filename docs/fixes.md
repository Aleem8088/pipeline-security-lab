# Fixes, one commit each

## Fix 1: pin actions to full SHAs, add Dependabot (commit 5bcbb30)
- Every `uses:` pinned to a 40-character commit SHA, version kept as a comment. SHAs were resolved through the GitHub API from each action's own repo.
- `.github/dependabot.yml`: weekly updates for `github-actions` and `npm`, 7-day cooldown (zizmor's `dependabot-cooldown` audit rejects less than 7).
- `persist-credentials: false` on `actions/checkout`.

Measured with zizmor 1.33.1 (default persona) on `ci.yml` + `pr-greeter.yml` (+ `dependabot.yml` after):

| Finding | Before | After |
|---|---|---|
| unpinned-uses | 5 | 0 |
| artipacked | 2 | 0 |
| excessive-permissions | 1 | 1 |
| dangerous-triggers | 1 | 1 |
| template-injection | 1 | 1 |
| **Total** | **10** | **3** |

Not stopped by this fix: an action that was already malicious when pinned; what a pinned action can do once running; the injection; the stored secret; movable Docker base-image tags.
Open follow-up: Dependabot opened major-version bumps (checkout 4 to 7, build-push-action 5 to 7, setup-node 4 to 7, buildx 3 to 4, express 4 to 5). They are not merged; each needs review.

## Fix 2: least-privilege token permissions (commit 89c215f)
- `permissions: {}` at the top of `ci.yml` and `pr-greeter.yml`; `test` and `build` jobs get `contents: read`; `deploy` gets none.
- Measured from job logs ("GITHUB_TOKEN Permissions" block): `test` job went from 17 write + 3 read scopes (run 45950056517, `write-all`) to 0 write + 2 read (Contents, Metadata) (run 45955222047). `deploy`: Metadata read only.
- zizmor (same scope): 3 to 2 findings (`excessive-permissions` gone). Output: `measurements/after-fix2-zizmor.txt`.

Not stopped: the script injection itself; any secret mapped into a job. The Demo 1 leak was a repo secret, so this fix would not have prevented it. `pr-greeter.yml` was checked with zizmor only, not re-run after the change.

## Fix 3: stop the script injection (commits 0a6b0a1, 4394af1, b53c207)
- 3a: PR title passed via `env: PR_TITLE` and referenced as `"$PR_TITLE"`, never inside the script text.
- 3b: removed `DEMO_API_TOKEN` from the greeter job (it never needed a secret).
- 3c: `pull_request_target` replaced by `pull_request`.

Proof: the identical crafted title replayed.
- After 3a (PR #7, run 45955540040, secret still mapped on purpose): title printed as plain text, no base64 output. Log: `measurements/demo1-retest-after-3a-log.txt`.
- After 3c (PR #8, run 45955859269): same result, no secret in the environment. Log: `measurements/demo1-retest-after-3c-log.txt`.

zizmor (same scope): 2 to 0 findings. Output: `measurements/after-fix3-zizmor.txt`.

Not covered: other untrusted-text flows (action inputs, files read at runtime, AI steps); fork PRs not tested; "0 findings" excludes the stored static secret in the deploy job and the intentionally weak demo workflows.

## Fix 4: Azure OIDC instead of a stored client secret (commit 8d46445)
- `infra/setup-azure-oidc.sh` creates: empty resource group, app registration + service principal, a federated credential trusting only `repo:Aleem8088@<ownerId>/pipeline-security-lab@<repoId>:environment:production`, and the Reader role on that resource group. `infra/teardown-azure-oidc.sh` removes it.
- The `deploy` job uses `azure/login@<sha> # v2.3.1` with `permissions: id-token: write` and `environment: production`. Run 45956627317: "Azure CLI login succeeds by using OIDC", signed in as a service principal, read the resource group. Log excerpt: `measurements/fix4-deploy-oidc-log.txt`.
- Negative tests (`demo-oidc-limits.yml`, run 45956826233), both expected to fail: (1) no environment, so subject `...:ref:refs/heads/main` was refused with AADSTS700213; (2) right environment but Reader role, so a write was refused with AuthorizationFailed.
- Stored long-lived cloud credentials: 1 (dummy client secret) to 0. Three Azure identifiers are kept as masked secrets; they are not credentials.
- zizmor on the scored files: still 0.

Teardown: after verification I deleted the app registration and resource group (verified none left), deleted the Azure secrets, and set the repo variable `AZURE_DEPLOY=false`, which makes the deploy job skip. To re-enable: run the setup script, store the three IDs it prints, set `AZURE_DEPLOY=true`.

Not stopped: a compromised step inside the deploy job can use the token while the job runs; anyone able to run a job in the unprotected `production` environment can log in (approval gate comes later); a too-loose subject rule would undo the protection. Tested with Reader on an empty resource group only.

Bug found in my own script and fixed: the federated credential and role assignment had silently failed on the first run (Windows path to `/tmp`, role assignment by app id too early, errors hidden by `|| true`).
