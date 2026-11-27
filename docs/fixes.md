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
