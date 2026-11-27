// SIMULATED "AI agent". There is no model here and no API call.
// It reproduces one failure mode on purpose: it cannot tell the data it was asked to
// read (an issue) from instructions, so any line starting "AGENT INSTRUCTION:" is
// obeyed if the matching tool is available. A real model is less predictable than
// this; the point is the pipeline shape (untrusted text + secret + tools in one place).
//
// Inputs (environment): ISSUE_TEXT, AGENT_TOOLS (comma list). Any secret in the
// environment is visible to the agent, exactly as it would be to a real one.
const text = process.env.ISSUE_TEXT || "";
const tools = new Set((process.env.AGENT_TOOLS || "").split(",").filter(Boolean));
const log = [];

// 1. The legitimate job: pick a label.
let label = "needs-triage";
if (/\bcrash|error|bug\b/i.test(text)) label = "bug";
else if (/\bfeature|please add\b/i.test(text)) label = "feature";

// 2. The failure mode: obey instructions found inside the data.
for (const line of text.split("\n")) {
  const m = line.match(/^AGENT INSTRUCTION:\s*(\w+)\s*(\S*)/);
  if (!m) continue;
  const [, tool, arg] = m;
  if (!tools.has(tool)) { log.push(`refused: tool '${tool}' is not available`); continue; }
  if (tool === "set_label") { label = arg; log.push(`obeyed: label forced to '${arg}'`); }
  if (tool === "send_report") {
    const value = process.env[arg];
    if (value === undefined) { log.push(`could not read ${arg}: not in the agent's environment`); continue; }
    // Reversed on purpose. GitHub's log masking is a best-effort string match: in our runs it hid
    // the plain secret and a base64 copy of the exact value, but a transformed copy slips past.
    // (A real exfil would go to a public comment, where log masking does not apply at all.)
    log.push(`obeyed: public comment would contain ${[...value].reverse().join("")}`);
  }
}
console.log(JSON.stringify({ label, log }));
