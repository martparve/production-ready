#!/usr/bin/env python3
"""
Build production-ready.epub with post-processing:
- Bibliography entries get anchor IDs (not superscript)
- Inline citation keys become superscript hyperlinks to bibliography
"""

import zipfile
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
EPUB_PATH = ROOT / "production-ready.epub"
TMP_EPUB = ROOT / "production-ready.tmp.epub"

CITE_KEY = (
    r'ANDev-\d{3}'
    r'|PE-\d{2}'
    r'|[A-Z][A-Za-z]+-[A-Za-z0-9-]+'
    r'|[A-Z][a-z]+[-]\d+'
    r'|BMAD|Goose|Kiro|Devin|Cursor|Aider|Factory|Graphite|CodeRabbit|Qodo'
    r'|Nix|Flox|Dash0|Tessl|SpecKit|BacklogMD|TerminalBench|Guardrails|WebMCP'
    r'|AAIF|ACP|TBD|promptfoo|METR'
)
CITE_RE = re.compile(r'\[(' + CITE_KEY + r')\]')


def build_raw_epub():
    """Run pandoc to build the initial EPUB."""
    chapters = sorted(ROOT.glob("chapters/[0-2][0-9]-*.md"))
    cmd = [
        "pandoc",
        f"--metadata-file={TOOLS / 'metadata.yaml'}",
        "--epub-cover-image=cover.png",
        f"--css={TOOLS / 'epub.css'}",
        "--toc",
        "--toc-depth=2",
        "--split-level=1",
        "-o", str(TMP_EPUB),
    ] + [str(c) for c in chapters]

    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    if result.returncode != 0:
        print(f"pandoc error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"pandoc built {TMP_EPUB.name}")


def find_bib_filename(zin):
    """Find the bibliography xhtml file by content."""
    for name in sorted(zin.namelist()):
        if not name.startswith('EPUB/text/ch'):
            continue
        content = zin.read(name).decode('utf-8')
        if '<h1' in content and 'Bibliography' in content:
            return name
    return None


def process_bibliography(text, bib_filename):
    """Add anchor IDs to bibliography entries. Do NOT superscript them."""
    def add_anchor(m):
        key = m.group(1)
        anchor_id = key
        return f'<strong id="{anchor_id}">[{key}]</strong>'

    text = re.sub(
        r'<strong>\[(' + CITE_KEY + r')\]</strong>',
        add_anchor,
        text
    )
    return text


def process_chapter(text, bib_filename):
    """Convert inline citation keys to superscript hyperlinks."""
    citations = 0
    bib_base = bib_filename.split('/')[-1]

    def replace_cite(m):
        nonlocal citations
        citations += 1
        key = m.group(1)
        return f'<sup><a href="{bib_base}#{key}">[{key}]</a></sup>'

    text = CITE_RE.sub(replace_cite, text)
    return text, citations


def postprocess_epub():
    """Post-process EPUB: link citations to bibliography."""
    total_citations = 0
    total_anchors = 0

    with zipfile.ZipFile(TMP_EPUB, 'r') as zin:
        bib_filename = find_bib_filename(zin)
        if not bib_filename:
            print("ERROR: bibliography chapter not found", file=sys.stderr)
            sys.exit(1)
        print(f"Bibliography: {bib_filename}")

        with zipfile.ZipFile(EPUB_PATH, 'w') as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)

                if item.filename.startswith('EPUB/text/') and item.filename.endswith('.xhtml'):
                    text = data.decode('utf-8')

                    if item.filename == bib_filename:
                        before = text
                        text = process_bibliography(text, bib_filename)
                        total_anchors = len(re.findall(r' id="', text)) - len(re.findall(r' id="', before))
                    else:
                        text, count = process_chapter(text, bib_filename)
                        total_citations += count

                    data = text.encode('utf-8')

                if item.filename == 'mimetype':
                    zout.writestr(item, data, compress_type=zipfile.ZIP_STORED)
                else:
                    zout.writestr(item, data)

    TMP_EPUB.unlink()
    print(f"Post-processed: {total_citations} citation links, {total_anchors} bibliography anchors")


def main():
    build_raw_epub()
    postprocess_epub()

    size = EPUB_PATH.stat().st_size / 1024 / 1024
    print(f"Output: {EPUB_PATH.name} ({size:.1f} MB)")


if __name__ == '__main__':
    main()
