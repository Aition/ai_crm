#!/usr/bin/env python3
"""
Normalize docs for cleaner chunking:
- remove YAML front matter
- strip HTML tags
- flatten ::: admonition blocks (keep content, remove wrappers)
- normalize blank lines and heading spacing
"""

import os
import re

DOCS_ROOT = "/Users/joey/ai_crm/docs"
ALLOWED_PREFIXES = ("product/", "reference/", "guides/", "sdk/")

FRONT_MATTER_RE = re.compile(r"^---\s*[\s\S]*?---\s*", re.MULTILINE)
HTML_TAG_RE = re.compile(r"<[^>]+>")
ADMONITION_START_RE = re.compile(r"^:::\s*([a-zA-Z\u4e00-\u9fff0-9_\- ]+)?\s*(.*)$")
ADMONITION_END_RE = re.compile(r"^:::\s*$")


def iter_docs():
    for root, _, files in os.walk(DOCS_ROOT):
        for file in files:
            if not (file.endswith(".md") or file.endswith(".txt")):
                continue
            rel_path = os.path.relpath(os.path.join(root, file), DOCS_ROOT)
            if not rel_path.startswith(ALLOWED_PREFIXES):
                continue
            if os.path.basename(file).startswith("dify-"):
                continue
            yield os.path.join(root, file)


def strip_front_matter(text: str) -> str:
    return FRONT_MATTER_RE.sub("", text, count=1)


def strip_html(text: str) -> str:
    return HTML_TAG_RE.sub("", text)


def normalize_admonitions(text: str) -> str:
    lines = text.splitlines()
    out = []
    in_admonition = False
    for line in lines:
        if not in_admonition:
            m = ADMONITION_START_RE.match(line)
            if m:
                in_admonition = True
                # Preserve a lightweight heading to keep intent
                title = (m.group(2) or m.group(1) or "").strip()
                if title:
                    out.append(f"**{title}**")
                continue
            out.append(line)
        else:
            if ADMONITION_END_RE.match(line):
                in_admonition = False
                out.append("")
                continue
            out.append(line)
    return "\n".join(out)


def normalize_spacing(text: str) -> str:
    # ensure blank line before headings
    text = re.sub(r"\n(#+\s)", r"\n\n\1", text)
    # collapse 3+ blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # strip trailing spaces
    text = "\n".join(line.rstrip() for line in text.splitlines())
    # trim leading/trailing blank lines
    return text.strip() + "\n"


def clean_text(text: str) -> str:
    text = strip_front_matter(text)
    text = normalize_admonitions(text)
    text = strip_html(text)
    text = normalize_spacing(text)
    return text


def main():
    files = list(iter_docs())
    print(f"Found {len(files)} docs")
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()
        cleaned = clean_text(original)
        if cleaned != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(cleaned)
        print(f"✓ {os.path.relpath(path, DOCS_ROOT)}")


if __name__ == "__main__":
    main()
