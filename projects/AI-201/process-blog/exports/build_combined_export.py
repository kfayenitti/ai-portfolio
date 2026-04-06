#!/usr/bin/env python3
"""Build blog-style HTML + PDF from week-01 and week-02 process markdown."""
from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = Path(__file__).resolve().parent
WEEK1 = ROOT / "week-01.md"
WEEK2 = ROOT / "week-02.md"
HTML_OUT = OUT_DIR / "process-blog-weeks-01-02.html"
PDF_OUT = OUT_DIR / "process-blog-weeks-01-02.pdf"

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
:root {
  --text: #1a1a1a;
  --muted: #5c5c5c;
  --rule: #d0d0d0;
  --accent: #2563eb;
  --bg: #ffffff;
}
@page { margin: 2cm 1.5cm; }
* { box-sizing: border-box; }
html {
  font-size: 17px;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
body {
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, "Times New Roman", serif;
  line-height: 1.55;
  color: var(--text);
  background: var(--bg);
  max-width: 42rem;
  margin: 0 auto;
  padding: 2.5rem 1.5rem 4rem;
}
.doc-header {
  border-bottom: 1px solid var(--rule);
  padding-bottom: 1.25rem;
  margin-bottom: 2.5rem;
}
.doc-header h1 {
  font-size: 1.65rem;
  font-weight: 600;
  margin: 0 0 0.35rem 0;
  letter-spacing: -0.02em;
}
.doc-header .meta {
  color: var(--muted);
  font-size: 0.95rem;
  margin: 0;
}
.week {
  margin-bottom: 3rem;
}
.week h2 {
  font-size: 1.35rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  padding-top: 0.5rem;
  border-top: 2px solid var(--text);
  letter-spacing: -0.02em;
}
.week:first-of-type h2 { border-top: none; padding-top: 0; }
.week h3 {
  font-size: 1.05rem;
  font-weight: 600;
  margin: 1.5rem 0 0.6rem 0;
  color: var(--text);
}
.week .topic {
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--accent);
  font-weight: 600;
  margin: 1.75rem 0 0.5rem 0;
  font-family: system-ui, -apple-system, sans-serif;
}
p { margin: 0 0 0.85rem 0; }
ul, ol { margin: 0 0 1rem 0; padding-left: 1.25rem; }
li { margin-bottom: 0.25rem; }
li ul { margin-top: 0.35rem; margin-bottom: 0.35rem; }
.interaction {
  margin: 1.25rem 0;
  padding: 1rem 1.1rem;
  background: #f7f8fa;
  border-radius: 6px;
  page-break-inside: avoid;
}
.interaction p { margin: 0 0 0.5rem 0; font-size: 0.95rem; }
.interaction p:last-child { margin-bottom: 0; }
.interaction strong {
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted);
}
.footer-note {
  margin-top: 3rem;
  padding-top: 1rem;
  border-top: 1px solid var(--rule);
  font-size: 0.85rem;
  color: var(--muted);
}
@media print {
  body { padding: 0; max-width: none; }
}
code { font-size: 0.9em; }
"""


def inline_md(raw: str) -> str:
    parts = re.split(r"(\*\*.+?\*\*)", raw)
    out: list[str] = []
    for p in parts:
        if p.startswith("**") and p.endswith("**") and len(p) > 4:
            out.append("<strong>" + html.escape(p[2:-2]) + "</strong>")
        else:
            out.append(html.escape(p))
    return "".join(out)


def target_ul_depth(leading: int) -> int:
    """Nesting depth for ul stack; notes use 3 spaces per sub-level."""
    return 1 + (leading // 3)


def parse_markdown_to_fragments(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    stack: int = 0  # ul nesting depth

    def close_to(depth: int) -> None:
        nonlocal stack
        while stack > depth:
            out.append("</ul>")
            stack -= 1

    i = 0
    while i < len(lines):
        raw = lines[i]
        line_no_nl = raw.rstrip("\n")
        stripped = line_no_nl.strip()
        leading = len(line_no_nl) - len(line_no_nl.lstrip(" "))

        if not stripped:
            close_to(0)
            i += 1
            continue

        if stripped.startswith("## ") and not stripped.startswith("### "):
            close_to(0)
            title = stripped[3:].strip()
            out.append(f"<h2>{inline_md(title)}</h2>")
            i += 1
            continue

        if stripped.startswith("### "):
            close_to(0)
            title = stripped[4:].strip()
            out.append(f"<h3>{inline_md(title)}</h3>")
            i += 1
            continue

        m_bullet = re.match(r"^[*\-]\s+(.+)$", stripped)
        if m_bullet:
            tgt = target_ul_depth(leading)
            content = m_bullet.group(1)
            while stack < tgt:
                out.append("<ul>")
                stack += 1
            while stack > tgt:
                out.append("</ul>")
                stack -= 1
            out.append(f"<li>{inline_md(content)}</li>")
            i += 1
            continue

        close_to(0)

        caps_topic = (
            stripped.isupper()
            and 15 < len(stripped) < 120
            and re.search(r"[/A-Z]", stripped)
            and not re.search(r"[a-z]", stripped)
        )
        if caps_topic:
            out.append(f'<p class="topic">{html.escape(stripped)}</p>')
            i += 1
            continue

        out.append(f"<p>{inline_md(stripped)}</p>")
        i += 1

    close_to(0)
    return "\n".join(out)


def wrap_ai_interactions(html_fragment: str) -> str:
    """Group consecutive - **Prompt:** blocks into .interaction cards for week 2 style."""
    lines = html_fragment.split("\n")
    result: list[str] = []
    buf: list[str] = []
    in_card = False

    def flush_buf() -> None:
        nonlocal buf, in_card
        if buf:
            result.append('<div class="interaction">\n' + "\n".join(buf) + "\n</div>")
            buf = []
        in_card = False

    for line in lines:
        if "<p>" in line and "<strong>Prompt:</strong>" in line:
            if in_card and buf:
                flush_buf()
            in_card = True
            buf.append(line)
        elif in_card:
            if line.startswith("<h2>") or line.startswith("<h3>") or line.startswith('<p class="topic">'):
                flush_buf()
                result.append(line)
            elif line.startswith("<p>") and buf:
                buf.append(line)
            elif line.startswith("<ul>"):
                flush_buf()
                result.append(line)
            else:
                buf.append(line)
        else:
            result.append(line)

    flush_buf()
    return "\n".join(result)


def trim_week2_orphan(text: str) -> str:
    lines = text.rstrip().split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    if lines and lines[-1].strip() == "## Week 1, Session 1":
        lines.pop()
    return "\n".join(lines) + "\n"


def main() -> None:
    w1 = WEEK1.read_text(encoding="utf-8")
    w2 = trim_week2_orphan(WEEK2.read_text(encoding="utf-8"))

    body1 = parse_markdown_to_fragments(w1)
    body2 = wrap_ai_interactions(parse_markdown_to_fragments(w2))

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI 201 Process Blog — Weeks 1 &amp; 2 · Katherine Faye Nitti</title>
<style>{CSS}</style>
</head>
<body>
<header class="doc-header">
  <h1>AI 201 · Process Blog</h1>
  <p class="meta">Katherine Faye Nitti · Weeks 1 &amp; 2 combined · Export for portfolio / website</p>
</header>

<article class="week" id="week-1">
{body1}
</article>

<article class="week" id="week-2">
{body2}
</article>

<p class="footer-note">Source files: <code>process-blog/week-01.md</code> and <code>process-blog/week-02.md</code> (unchanged in repo).</p>
</body>
</html>
"""

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text(doc, encoding="utf-8")
    print(f"Wrote {HTML_OUT}")

    if Path(CHROME).is_file():
        url = HTML_OUT.as_uri()
        cmd = [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={PDF_OUT}",
            url,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise SystemExit(f"Chrome failed: {proc.stderr or proc.stdout}")
        print(f"Wrote {PDF_OUT}")
    else:
        print("Chrome not found; HTML only.")


if __name__ == "__main__":
    main()
