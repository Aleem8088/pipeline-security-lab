# Step 9: prompt injection in an AI step (simulated)

**Idea.** An agent that reads untrusted text while holding a secret and a tool that can publish text can be steered by that text. Passing the text through `env:` (Fix 3) stops *shell* injection; it does not stop *prompt* injection.

**Reported research (primary pages read 2026-11-27).**
- Aikido, "PromptPwnd" (Dec 2025): https://aikido.dev/blog/promptpwnd-github-actions-ai-agents . Gemini CLI, Claude Code Actions, Codex Actions, GitHub AI Inference workflows. Their PoC used a private fork with test credentials. Google patched within four days (per Aikido).
- SecurityWeek, "Comment and Control" (Apr 2026): https://www.securityweek.com/claude-code-gemini-cli-github-copilot-agents-vulnerable-to-prompt-injection-via-comments/ . Research by Aonan Guan with Zhengyu Liu and Gavin Zhong (Johns Hopkins). Claude Code Security Review, Gemini CLI Action, Copilot Agent. Vendor fixes were specific patches; GitHub called it a known architectural limitation.
- I did not reproduce these against real products. Unsourced claims on the Aikido page (e.g. Fortune 500 impact) are not repeated here.

**What this repo does.** `demo-ai-injection.yml` (manual) runs `demo-ai/fake-agent.js`, a **simulation**: no model, no API. It obeys `AGENT INSTRUCTION:` lines if the tool exists. It demonstrates the pipeline shape only. Secret: dummy canary.

| Job | Agent has secret | Agent tools | Injected text effect |
|---|---|---|---|
| `vulnerable` | yes | set_label, send_report | canary leaked (reversed), label forced to `wontfix` |
| `analyze` | no | none | both instructions refused |
| `apply` | n/a | n/a | sees only a label; allowlist `bug/feature/question/needs-triage` |

Evidence: `measurements/ai-injection-runs.txt` (run 46029843286).

**Masking note.** GitHub masked the plain canary and an exact-value base64 copy (an earlier test). The demo reverses the value, which masking cannot match. Masking is best-effort, not a boundary; real exfiltration goes to a public comment where log masking does not apply.

**Does not stop.** Wrong-but-allowed answers (integrity), misleading free-text output, tools you add later, a real model's unpredictability. The apply step prints rather than writes.
