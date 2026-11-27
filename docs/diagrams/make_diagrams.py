"""Builds docs/img/architecture.svg and docs/img/attack-two-pipelines.gif.

Needs: Python 3 with Pillow, and Microsoft Edge (headless) to rasterise SVG frames.
Run from the repo root:  python docs/diagrams/make_diagrams.py
Every number shown comes from docs/scoreboard.md; nothing is invented here.
"""
import os, subprocess, sys, tempfile
from xml.sax.saxutils import escape
from PIL import Image

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = os.path.join("docs", "img")

# Fixed colours: these SVGs are shown as <img> on GitHub, where currentColor cannot follow the theme,
# so each figure carries its own dark background and reads the same everywhere.
BG, PANEL, LINE, TXT, DIM = "#0f172a", "#1e293b", "#475569", "#e2e8f0", "#94a3b8"
RED, GREEN, AMBER, BLUE = "#f87171", "#4ade80", "#fbbf24", "#60a5fa"
SANS = "font-family='Segoe UI, Helvetica, Arial, sans-serif'"
MONO = "font-family='Consolas, Menlo, monospace'"


def t(x, y, s, size=13, fill=TXT, anchor="start", weight="normal", mono=False):
    fam = MONO if mono else SANS
    return (f"<text x='{x}' y='{y}' font-size='{size}' fill='{fill}' text-anchor='{anchor}' "
            f"font-weight='{weight}' {fam}>{escape(s)}</text>")


def box(x, y, w, h, title, lines=(), stroke=LINE, fill=PANEL, title_fill=TXT, dashed=False, mono_lines=False, size=12):
    d = " stroke-dasharray='6 4'" if dashed else ""
    out = [f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='8' fill='{fill}' stroke='{stroke}' stroke-width='2'{d}/>",
           t(x + w / 2, y + 24, title, 14, title_fill, "middle", "bold")]
    for i, ln in enumerate(lines):
        out.append(t(x + w / 2, y + 46 + i * 18, ln, size, DIM, "middle", mono=mono_lines))
    return "\n".join(out)


def arrow(x1, y1, x2, y2, color=LINE, label=None, lab_dy=-8, dashed=False, width=2.5):
    d = " stroke-dasharray='6 4'" if dashed else ""
    ang_dx = 1 if x2 >= x1 else -1
    head = f"{x2},{y2} {x2 - 10 * ang_dx},{y2 - 6} {x2 - 10 * ang_dx},{y2 + 6}"
    s = f"<line x1='{x1}' y1='{y1}' x2='{x2 - 9 * ang_dx}' y2='{y2}' stroke='{color}' stroke-width='{width}'{d}/>"
    s += f"<polygon points='{head}' fill='{color}'/>"
    if label:
        s += t((x1 + x2) / 2, y1 + lab_dy, label, 12, color, "middle")
    return s


def svg(w, h, body, label):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}' "
            f"role='img' aria-label='{escape(label)}'><rect width='{w}' height='{h}' fill='{BG}'/>{body}</svg>")


# --------------------------------------------------------------------------- architecture (static)
def architecture():
    W, H = 1280, 640
    b = [t(24, 38, "How a change reaches production in this repo, and what guards each hop", 20, TXT, weight="bold"),
         t(24, 62, "Controls listed under each step are the ones that exist in the repo today. Arrows are labelled with what crosses them.", 13, DIM)]
    bw, gap, x0, y0, bh = 120, 66, 22, 150, 70
    steps = [
        ("Pull request", ["title, body =", "untrusted text", "greeter: no secrets", "permissions: {}"], RED),
        ("Required checks", ["test + build + zizmor", "PR required", "admin enforced"], AMBER),
        ("main", ["actions pinned to SHA", "Dependabot, 7-day", "cooldown"], BLUE),
        ("Build job", ["harden-runner: block", "scoped token", "SBOM + vuln scan"], BLUE),
        ("GHCR image", ["digest-pinned base", "Cosign signature", "verified in CI"], BLUE),
        ("Deploy job", ["env approval (human)", "main branch only", "egress allowlist"], AMBER),
        ("Azure", ["OIDC, no stored key", "Reader role only", "subject = production"], GREEN),
    ]
    xs = [x0 + i * (bw + gap) for i in range(len(steps))]
    for i, (name, ctl, col) in enumerate(steps):
        b.append(box(xs[i], y0, bw, bh, name, [], stroke=col, title_fill=col))
        for j, c in enumerate(ctl):
            b.append(t(xs[i] + bw / 2, y0 + bh + 26 + j * 19, c, 12, TXT if j else DIM, "middle"))
    labels = [("opens", "PR"), ("checks", "pass"), ("squash", "merge"), ("push +", "sign"), ("pull by", "digest"), ("approve", "+ OIDC")]
    for i in range(len(steps) - 1):
        b.append(arrow(xs[i] + bw + 3, y0 + bh / 2, xs[i + 1] - 3, y0 + bh / 2, LINE))
        cx = xs[i] + bw + gap / 2
        b.append(t(cx, y0 + bh / 2 - 22, labels[i][0], 11, DIM, "middle"))
        b.append(t(cx, y0 + bh / 2 - 9, labels[i][1], 11, DIM, "middle"))
    # Untrusted zone marker
    b.append(f"<rect x='{xs[0]-10}' y='{y0-34}' width='{bw+20}' height='{bh+34+100}' rx='10' fill='none' stroke='{RED}' stroke-width='1.5' stroke-dasharray='5 4'/>")
    b.append(t(xs[0] + bw / 2, y0 - 16, "untrusted", 12, RED, "middle", "bold"))
    # Long-lived secrets removed
    b.append(f"<rect x='{xs[-1]-10}' y='{y0-34}' width='{bw+20}' height='{bh+34+100}' rx='10' fill='none' stroke='{GREEN}' stroke-width='1.5' stroke-dasharray='5 4'/>")
    b.append(t(xs[-1] + bw / 2, y0 - 16, "cloud", 12, GREEN, "middle", "bold"))
    # The mechanism under the figure: which job holds which power
    y2 = 410
    b.append(t(24, y2, "What each job is allowed to hold (this is the part that stops one weak step becoming a full compromise)", 15, TXT, weight="bold"))
    rows = [("test", "contents: read", "no secrets, no cloud"),
            ("build", "contents: read, packages: write, id-token: write", "signs with a one-time identity; no stored key"),
            ("deploy", "id-token: write only", "needs a human approval; Azure accepts only the production environment")]
    for i, (j, perm, note) in enumerate(rows):
        yy = y2 + 28 + i * 34
        b.append(f"<rect x='24' y='{yy-18}' width='1232' height='28' rx='6' fill='{PANEL}'/>")
        b.append(t(40, yy, j, 13, BLUE, weight="bold", mono=True))
        b.append(t(120, yy, perm, 13, TXT, mono=True))
        b.append(t(620, yy, note, 13, DIM))
    b.append(f"<rect x='24' y='{y2+140}' width='1232' height='62' rx='8' fill='none' stroke='{AMBER}' stroke-width='1.5'/>")
    b.append(t(40, y2 + 164, "Not stopped by any of this:", 13, AMBER, weight="bold"))
    b.append(t(40, y2 + 186, "a third-party action that was already malicious when pinned  ·  exfiltration to a host on the allowlist  ·  one maintainer who can change the rules (0 required approvals)", 13, TXT))
    return svg(W, H, "\n".join(b), "Architecture: a pull request passes required checks, merges to main, is built, signed and pushed, then deployed to Azure through OIDC after a human approval")


# --------------------------------------------------------------------------- animated story (frames)
W, H = 1200, 675
LANE_Y = {"before": 118, "after": 352}
LANE_H = 214
X = {"atk": 36, "wf": 340, "sec": 660, "log": 900}
BW = {"atk": 220, "wf": 250, "sec": 190, "log": 264}


def lane(kind, state):
    y = LANE_Y[kind]
    is_b = kind == "before"
    col = RED if is_b else GREEN
    b = [f"<rect x='18' y='{y}' width='{W-36}' height='{LANE_H}' rx='12' fill='none' stroke='{col}' stroke-opacity='0.55' stroke-width='1.5'/>",
         t(34, y + 26, "BEFORE" if is_b else "AFTER", 14, col, weight="bold")]
    cy = y + 56
    bh = 120
    # attacker
    b.append(box(X["atk"], cy, BW["atk"], bh, "Pull request", ["title (attacker-written):", 'hi"; echo $TOKEN | base64'], stroke=RED if state >= 1 else LINE, mono_lines=False, size=12))
    # workflow
    wf_lines = (["title pasted into run:", "trigger: pull_request_target", "token: write-all"] if is_b
                else ["title passed via env:, quoted", "trigger: pull_request", "permissions: {}"])
    b.append(box(X["wf"], cy, BW["wf"], bh, "pr-greeter" + (" (before)" if is_b else " (after)"), wf_lines, stroke=col if state >= 1 else LINE))
    # secret
    sec_lines = ["dummy canary secret", "mapped into the job"] if is_b else ["dummy canary secret", "not mapped into this job"]
    sec_stroke = RED if (is_b and state >= 2) else LINE
    b.append(box(X["sec"], cy, BW["sec"], bh, "DEMO_API_TOKEN", sec_lines, stroke=sec_stroke, dashed=not is_b))
    # log
    if is_b:
        log_lines = ["Q0FOQVJZ… (base64 of the canary)"] if state >= 3 else ["(waiting)"]
        log_col = RED if state >= 3 else LINE
    else:
        log_lines = ["Thanks for the pull request:", 'hi"; echo … (plain text)'] if state >= 2 else ["(waiting)"]
        log_col = GREEN if state >= 2 else LINE
    b.append(box(X["log"], cy, BW["log"], bh, "Workflow log (public)", log_lines, stroke=log_col, mono_lines=True))
    my = cy + bh / 2
    # arrows
    a1 = RED if state >= 1 else LINE
    b.append(arrow(X["atk"] + BW["atk"] + 3, my, X["wf"] - 3, my, a1, "opens PR" if state < 1 else "title runs" if is_b else "title = data"))
    # workflow -> secret
    if is_b:
        a2 = RED if state >= 2 else LINE
        b.append(arrow(X["wf"] + BW["wf"] + 3, my, X["sec"] - 3, my, a2, "reads" if state >= 2 else "", dashed=state < 2))
    elif state >= 2:
        x1, x2 = X["wf"] + BW["wf"] + 8, X["sec"] - 8
        b.append(f"<line x1='{x1}' y1='{my}' x2='{x2}' y2='{my}' stroke='{GREEN}' stroke-width='2.5' stroke-dasharray='6 4'/>")
        mx = (x1 + x2) / 2
        b.append(f"<g stroke='{GREEN}' stroke-width='3'><line x1='{mx-7}' y1='{my-7}' x2='{mx+7}' y2='{my+7}'/><line x1='{mx+7}' y1='{my-7}' x2='{mx-7}' y2='{my+7}'/></g>")
        b.append(t(mx, my - 30, "nothing", 12, GREEN, "middle"))
        b.append(t(mx, my - 17, "to read", 12, GREEN, "middle"))
    # workflow -> log, routed UNDER the secret box so it is clear the workflow (not the secret) prints
    on = state >= 3 if is_b else state >= 2
    c = (RED if is_b else GREEN) if on else LINE
    dash = "" if on else " stroke-dasharray='6 4'"
    sx, ly, lx = X["wf"] + BW["wf"] - 40, cy + bh + 22, X["log"] + BW["log"] / 2
    b.append(f"<polyline points='{sx},{cy+bh} {sx},{ly} {lx},{ly} {lx},{cy+bh+9}' fill='none' stroke='{c}' stroke-width='2.5'{dash}/>")
    b.append(f"<polygon points='{lx},{cy+bh+2} {lx-6},{cy+bh+12} {lx+6},{cy+bh+12}' fill='{c}'/>")
    if on:
        b.append(t((sx + lx) / 2, ly - 6, "prints $TOKEN, base64-encoded" if is_b else "prints the title as text", 12, c, "middle"))
    return "\n".join(b)


def story_frame(bstate, astate, caption, headline="Same attack, two pipelines"):
    body = [t(24, 40, headline, 26, TXT, weight="bold"),
            t(24, 68, "A crafted pull-request title, replayed against my own repo (dummy secret, my account only)", 14, DIM),
            lane("before", bstate), lane("after", astate),
            f"<rect x='18' y='{H-84}' width='{W-36}' height='64' rx='10' fill='{PANEL}'/>",
            t(W / 2, H - 46, caption, 19, TXT, "middle", "bold")]
    return svg(W, H, "\n".join(body), caption)


def title_frame():
    b = [t(W / 2, 250, "I attacked my own pipeline", 52, TXT, "middle", "bold"),
         t(W / 2, 305, "and measured what each fix actually stops", 26, DIM, "middle"),
         t(W / 2, 400, "GitHub Actions  ·  my own public repo  ·  dummy secrets", 18, BLUE, "middle"),
         t(W / 2, 560, "github.com/Aleem8088/pipeline-security-lab", 20, TXT, "middle", mono=True)]
    return svg(W, H, "\n".join(b), "Title card")


def score_frame():
    b = [t(W / 2, 80, "What changed, measured", 36, TXT, "middle", "bold")]
    items = [("10 → 0", "zizmor findings", "two workflow files, same tool, same command"),
             ("17 write → 0", "GITHUB_TOKEN write scopes", "test job, from real job logs"),
             ("1 → 0", "stored cloud credentials", "static key replaced by OIDC")]
    for i, (big, name, sub) in enumerate(items):
        x = 40 + i * 384
        b.append(f"<rect x='{x}' y='140' width='360' height='210' rx='14' fill='{PANEL}' stroke='{GREEN}' stroke-width='2'/>")
        b.append(t(x + 180, 220, big, 40, GREEN, "middle", "bold"))
        b.append(t(x + 180, 264, name, 18, TXT, "middle", "bold"))
        b.append(t(x + 180, 296, sub, 13, DIM, "middle"))
    b.append(f"<rect x='40' y='390' width='1120' height='150' rx='12' fill='none' stroke='{AMBER}' stroke-width='1.5'/>")
    b.append(t(60, 424, "What it does not stop", 18, AMBER, weight="bold"))
    for i, s in enumerate(["A third-party action that was already malicious when I pinned it",
                           "Data sent to a host on the allowlist (for example github.com)",
                           "One maintainer who can change the rules: required approvals = 0"]):
        b.append(t(60, 456 + i * 26, "•  " + s, 16, TXT))
    b.append(t(W / 2, 600, "Small lab, one repo, mostly one run each. Not a benchmark.", 15, DIM, "middle"))
    b.append(t(W / 2, 636, "github.com/Aleem8088/pipeline-security-lab", 18, TXT, "middle", mono=True))
    return svg(W, H, "\n".join(b), "Scoreboard card")


FRAMES = [  # (svg, hold_ms)
    (title_frame(), 2600),
    (story_frame(0, 0, "Same crafted title, two pipelines"), 2200),
    (story_frame(1, 0, "Before: the title is pasted into a shell script"), 2400),
    (story_frame(2, 0, "Before: that script can read the secret"), 2200),
    (story_frame(3, 0, "Before: the secret is now in a public log (encoded)"), 3000),
    (story_frame(3, 1, "After: the title arrives as data, not code"), 2400),
    (story_frame(3, 2, "After: printed as plain text. The job holds no secret."), 3400),
    (score_frame(), 5200),
]


def render(svg_text, png_path, tmp):
    p = os.path.join(tmp, "f.svg")
    with open(p, "w", encoding="utf-8") as f:
        f.write(svg_text)
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={W},{H + 90}", f"--screenshot={png_path}",
                    "file:///" + p.replace("\\", "/")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "architecture.svg"), "w", encoding="utf-8") as f:
        f.write(architecture())
    with tempfile.TemporaryDirectory() as tmp:
        imgs = []
        for i, (s, _) in enumerate(FRAMES):
            png = os.path.join(tmp, f"{i}.png")
            render(s, png, tmp)
            im = Image.open(png).convert("RGB").crop((0, 0, W, H))
            imgs.append(im)
        pal = [im.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for im in imgs]
        pal[0].save(os.path.join(OUT, "attack-two-pipelines.gif"), save_all=True, append_images=pal[1:],
                    duration=[d for _, d in FRAMES], loop=0, optimize=True, disposal=1)
        imgs[4].save(os.path.join(OUT, "attack-two-pipelines-still.png"))
    print("ok")


if __name__ == "__main__":
    sys.exit(main())
