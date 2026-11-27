# Demonstrations of the "before" state

All run on my own repos on 2026-11-27 with dummy canary secrets. Nothing real was exposed.

## Demo 1: script injection through a PR title (weakness a)
PR #1 title: `hi"; echo "$DEMO_API_TOKEN" | base64; echo "`
The `pr-greeter` workflow pasted the title into a shell script. The log printed the base64 of the dummy token (`Q0FOQVJZ...`), which decodes to `CANARY-demo-token-not-a-real-secret`. GitHub's log masking showed `***` for the exact secret but not for its base64 form.
Evidence: `img/pr1.png`, `img/run-greeter.png`, `measurements/demo1-greeter-log.txt`.

GitHub's run page also showed: "On December 2, 2026, GitHub will restrict `pull_request_target` on public repositories by default." (Docs: https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target . The page says the default policy does not address command injection.)

## Demo 2: moving a tag changes what runs (weakness b)
Throwaway harmless action: https://github.com/Aleem8088/demo-action. Workflow `demo-movable-tag.yml` uses it as `@v1`.
- Run 1 fetched SHA `0df90fa1f2bb56e8e194638329e9b05438270bd3` (benign output).
- I moved tag `v1` to a new commit. Run 2 of the unchanged workflow fetched SHA `10c854599868bae9bc4dec9556dad4dcae5a507e` and printed different output.
Evidence: `img/demo-action-repo.png`.

## Demo 3: broad vs minimal GITHUB_TOKEN (weakness c)
`demo-token-power.yml`: both jobs try to create a branch. `permissions: write-all` succeeded; `contents: read` failed with HTTP 403 "Resource not accessible by integration".
Evidence: `img/run-token-power.png`.

## Weakness (d), static cloud secret
Not staged (the values are fake). Measured later as a count of long-lived cloud secrets: 3 before, target 0 after OIDC.

Limits: I own every repo involved, so these show mechanisms, not real-world frequency.

## Fix 1 re-run of Demo 2 (pinned)
After pinning `demo-action` to the benign SHA `0df90fa1...`, the workflow fetched exactly that SHA and printed the original message, even though the tag `v1` still points at the tampered commit.
