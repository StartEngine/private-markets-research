"""Render the executed notebook as a StartEngine-styled article PDF.

Reads private_markets.ipynb (already executed), extracts the prose, charts,
callouts, and tables — never the code — and prints a branded article to
private_markets_article.pdf via headless Chromium.

Usage:  uv run python make_article_pdf.py
"""

from __future__ import annotations

import base64
from pathlib import Path

import mistune
import nbformat
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
NOTEBOOK = HERE / "private_markets.ipynb"
OUT = HERE / "private_markets_article.pdf"

# StartEngine blog palette (extracted from startengine.com/blog)
CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
:root {
  --mint: #01D1B8; --deep: #185C65; --ink: #0E1A1C;
  --body: #374151; --muted: #6B7280; --bg: #FDFDFB;
}
* { box-sizing: border-box; }
body { font-family: 'IBM Plex Sans', -apple-system, sans-serif; color: var(--body);
       background: var(--bg); margin: 0; }
.page { max-width: 720px; margin: 0 auto; padding: 48px 32px; }
.kicker { color: var(--deep); font-weight: 600; letter-spacing: .12em;
          text-transform: uppercase; font-size: 12px; margin-bottom: 10px; }
.kicker::before { content: ''; display: inline-block; width: 26px; height: 4px;
                  background: var(--mint); border-radius: 2px; margin-right: 10px;
                  vertical-align: middle; }
h1 { color: var(--ink); font-size: 34px; line-height: 1.15; font-weight: 700;
     margin: 0 0 6px; }
h2 { color: var(--ink); font-size: 22px; font-weight: 600; margin: 36px 0 10px;
     padding-top: 14px; border-top: 3px solid var(--mint); }
p, li { font-size: 15px; line-height: 1.65; }
a { color: var(--deep); text-decoration: none; border-bottom: 1px solid var(--mint); }
strong { color: var(--ink); }
em { color: var(--muted); }
blockquote { margin: 18px 0; padding: 14px 18px; background: #F0FBF9;
             border-left: 4px solid var(--mint); border-radius: 0 8px 8px 0; }
blockquote p { margin: 0; font-size: 16px; color: var(--ink); }
figure { margin: 22px 0; }
figure img { width: 100%; border: 1px solid #E5E7EB; border-radius: 10px; }
table { border-collapse: collapse; width: 100%; font-size: 13.5px; margin: 14px 0; }
th { text-align: left; color: var(--deep); border-bottom: 2px solid var(--mint);
     padding: 7px 10px; }
td { border-bottom: 1px solid #E5E7EB; padding: 7px 10px; }
tr:nth-child(even) td { background: #F7FAF9; }
hr { border: none; border-top: 1px solid #E5E7EB; margin: 32px 0; }
.foot { color: var(--muted); font-size: 12px; line-height: 1.55; }
.foot em { font-size: 12px; }
"""

md = mistune.create_markdown(plugins=["table", "strikethrough"])


def render() -> str:
    nb = nbformat.read(NOTEBOOK, as_version=4)
    parts: list[str] = []
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            src = cell.source
            # The methods/disclaimer block reads better small — detect by heading.
            if src.lstrip().startswith(("---", "## Methods")) or "## Methods" in src:
                parts.append(f'<div class="foot">{md(src)}</div>')
            else:
                parts.append(md(src))
        elif cell.cell_type == "code":
            for out in cell.get("outputs", []):
                data = out.get("data", {})
                if "image/png" in data:
                    parts.append(
                        f'<figure><img src="data:image/png;base64,{data["image/png"].strip()}"/></figure>'
                    )
                elif "text/markdown" in data:  # the callout lines
                    parts.append(md(data["text/markdown"]))
                elif "text/html" in data:  # pandas tables
                    parts.append(data["text/html"])
                # plain text streams (if any) are intentionally dropped
    body = "\n".join(parts)
    # Drop the notebook's own H1 block and rebuild a branded title.
    title_html = (
        '<p class="kicker">StartEngine Research</p>'
        "<h1>The Case for Private Markets, Told Entirely From Public Data</h1>"
        '<p style="color:var(--muted); margin-top:4px;">June 2026 · '
        "<strong>draft for internal review</strong></p>"
    )
    # the notebook's own byline duplicates the styled one — drop it
    import re as _re
    body = _re.sub(r"<p><em>StartEngine research notebook.*?</em></p>", "", body, count=1)
    first_h1 = body.find("<h1>")
    if first_h1 != -1:
        end = body.find("</h1>", first_h1) + len("</h1>")
        body = body[:first_h1] + title_html + body[end:]
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>{CSS}</style></head><body><div class='page'>{body}</div></body></html>"
    )


def main() -> None:
    html = render()
    tmp = HERE / "_article.html"
    tmp.write_text(html)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(tmp.as_uri())
        page.wait_for_load_state("networkidle")  # let the webfont arrive
        page.pdf(
            path=str(OUT),
            format="Letter",
            print_background=True,
            margin={"top": "0.6in", "bottom": "0.7in", "left": "0.5in", "right": "0.5in"},
        )
        browser.close()
    tmp.unlink()
    print(f"wrote {OUT} ({OUT.stat().st_size//1024} KB)")


if __name__ == "__main__":
    main()
