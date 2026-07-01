#!/usr/bin/env python3
"""
Build static, dependency-free HTML from the editable *.dc.html sources.

Usage:  python3 build.py
Output: docs/  (index.html, synthetic-data.html, ai-evaluation.html,
                industry.html, img/, .nojekyll)  ready for GitHub Pages.

The .dc.html files stay as your editable source (open them in your design
tool). This script just produces the deploy folder. Re-run after any edit.
"""

import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")

# source .dc.html  ->  (output filename, <title>, <meta description>)
PAGES = {
    "Portfolio - Home.dc.html": (
        "index.html",
        "Meena M — HCI / UX Researcher",
        "HCI / UX researcher with a PhD in Human Centered Design & Engineering. "
        "Aligning technology with human needs and behavior.",
    ),
    "Project - Synthetic Data.dc.html": (
        "synthetic-data.html",
        "Synthetic Data Generation, Grounded in HCI Research — Meena M",
        "Grounding LLM-generated synthetic data in empirical HCI research to make "
        "it useful for designing and evaluating AI systems.",
    ),
    "Project - AI Evaluation.dc.html": (
        "ai-evaluation.html",
        "Human-Centered AI Evaluation — Meena M",
        "A human-centered evaluation of a toxicity-detection model — where its "
        "judgments diverge from how people actually read harm.",
    ),
    "Industry - Big Tech UXR.dc.html": (
        "industry.html",
        "UX Research at Meta — Meena M",
        "UX research in Meta's Monetization org, balancing usability and security "
        "for advertiser tools.",
    ),
}

# tiny "MM" mark, inlined as the favicon (no extra file to host)
FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%232f5fb0'/"
    "%3E%3Ctext x='50' y='50' dy='.35em' text-anchor='middle' "
    "font-family='Georgia,serif' font-size='34' fill='white'%3EMM%3C/text%3E%3C/svg%3E"
)


def extract(src):
    """Pull font <link>s, the <style> block, and the body out of a .dc.html."""
    helmet = re.search(r"<helmet>(.*?)</helmet>", src, re.S)
    helmet = helmet.group(1) if helmet else ""

    links = re.findall(r"<link\b[^>]*>", helmet)
    style = re.search(r"<style>.*?</style>", helmet, re.S)
    style = style.group(0) if style else ""

    # body = everything between the bundler thumbnail <template> and </x-dc>
    body = re.search(r"</template>(.*?)</x-dc>", src, re.S)
    if not body:  # fall back to whatever is inside <x-dc>
        body = re.search(r"<x-dc>(.*?)</x-dc>", src, re.S)
    body = body.group(1).strip() if body else ""

    return links, style, body


def convert_hovers(body):
    """Turn dc's `style-hover="..."` attributes into real CSS :hover rules."""
    rules = []
    counter = [0]

    def repl(match):
        tag = match.group(0)
        rule = re.search(r'style-hover="([^"]*)"', tag).group(1).strip().rstrip(";")
        cls = f"dch{counter[0]}"
        counter[0] += 1
        rules.append(f"  .{cls}:hover {{ {rule}; }}")
        tag = re.sub(r'\s*style-hover="[^"]*"', "", tag)
        if 'class="' in tag:
            tag = tag.replace('class="', f'class="{cls} ', 1)
        else:
            tag = re.sub(r"^<(\w[\w-]*)", rf'<\1 class="{cls}"', tag)
        return tag

    body = re.sub(r'<[a-zA-Z][^>]*style-hover="[^"]*"[^>]*>', repl, body)
    return body, rules


def build_page(src_name, out_name, title, desc):
    with open(os.path.join(ROOT, src_name), encoding="utf-8") as f:
        src = f.read()

    links, style, body = extract(src)

    if "<x-import" in body or "x-dc" in body:
        print(f"  ! {src_name}: still contains a dc component (x-import/x-dc); "
              "static output may not render it.", file=sys.stderr)

    # static-HTML fixes for constructs that only worked under the dc runtime
    body = body.replace('defaultChecked="true"', "checked")
    body, hover_rules = convert_hovers(body)

    if hover_rules and style:
        style = style.replace(
            "</style>", "\n  /* generated :hover (was style-hover) */\n"
            + "\n".join(hover_rules) + "\n</style>"
        )

    head_links = "\n".join(links)
    esc_desc = desc.replace('"', "&quot;")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{esc_desc}">
<link rel="icon" href="{FAVICON}">
{head_links}
{style}
</head>
<body>
{body}
</body>
</html>
"""
    with open(os.path.join(DOCS, out_name), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ {out_name}")


def main():
    if os.path.isdir(DOCS):
        shutil.rmtree(DOCS)
    os.makedirs(DOCS)

    print("Building docs/ …")
    for src_name, (out_name, title, desc) in PAGES.items():
        build_page(src_name, out_name, title, desc)

    if os.path.isdir(os.path.join(ROOT, "img")):
        shutil.copytree(os.path.join(ROOT, "img"), os.path.join(DOCS, "img"))
        print("  ✓ img/")

    open(os.path.join(DOCS, ".nojekyll"), "w").close()  # let GitHub serve files as-is
    print("  ✓ .nojekyll")
    print("Done. Deploy the docs/ folder (see DEPLOY.md).")


if __name__ == "__main__":
    main()
