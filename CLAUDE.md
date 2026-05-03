# Production Ready

**Building and Operating an AI Code Factory** - a systems engineering book by Mart Parve. MIT licensed.

## Project Structure

```
chapters/              Markdown source (00-introduction through 22-bibliography)
cover.png              Book cover (1600x2560 PNG)
production-ready.epub  Built EPUB for Kindle/e-readers (committed artifact)
metadata.yaml          Pandoc metadata (title, author, license)
epub.css               Kindle/e-ink optimized stylesheet
build_epub.py          EPUB build + citation post-processing script
```

## Writing Style

- **Professional engineering book tone.** Direct, opinionated, concrete. Write like a senior engineer explaining something to a peer.
- **No em dashes** (Unicode U+2014). Use short dashes (-) or colons (:) instead.
- **No dramatic stacking.** Never write single-sentence paragraphs stacked for fake dramatic effect ("This happened. Everything changed. Here's why."). Combine into flowing sentences.
- **Humble voice.** "This book aims to" not "this book is your roadmap." Don't make authority claims on behalf of the author.
- **No filler or corporate jargon.** No "leverage", "synergy", "ecosystem", "thought leadership." Every sentence earns its place.
- **Headless factory** (cloud-hosted, event-driven agent execution) is the destination architecture. The book does not assume developers run agents from their IDE.
- **Size-agnostic.** No assumptions about the reader's company size. Describe what is needed, not what "transfers" from a specific company.
- **No fabrication.** Do not invent details, extrapolate biographical claims, or put conclusions in the author's mouth. Stick to what the source material says.

## Citations

All sources live in `chapters/22-bibliography.md`. Chapters reference them with short inline keys in brackets.

### Key Formats

- **Podcast episodes:** `[ANDev-NNN]` (AI Native Dev Podcast by Tessl, e.g. `[ANDev-052]`)
- **Named sources:** `[Author-Keyword]` (e.g. `[GitClear-2025]`, `[Stripe-Minions-1]`, `[Beck-augmented]`)
- **Tool references:** Single-word keys like `[BMAD]`, `[Goose]`, `[Kiro]`

### Rules

- **One source, one bibliography entry, cited many times.** Never duplicate a source in the bibliography.
- **Deduplicate within a passage.** Within a blockquote block or paragraph, cite each source only once (first occurrence). Do not repeat the same key on every sentence.
- **Biographical context belongs in running text**, not as a citation. Write "Steve Kuliski, an engineer at Stripe" in the prose, don't create a `[Kuliski-bio]` citation.

### Adding New Sources

1. Add the entry to `chapters/22-bibliography.md` under the appropriate section (podcast or other)
2. Use a key that matches the existing patterns
3. If the key doesn't match the regex in `build_epub.py`, add it to the `CITE_KEY` pattern

## Building the EPUB

Requires `pandoc` and Python 3.

```bash
python3 build_epub.py
```

The build script:
1. Runs pandoc with metadata, cover, CSS, and all chapters in order
2. Post-processes the EPUB: citation keys become superscript hyperlinks to anchored bibliography entries
3. Bibliography entries get `id` anchors but are NOT superscripted

### EPUB Styling Conventions

- Serif body font (Georgia), 1.5 line-height, justified text
- Monospace code at 0.8em with word-wrap, 1px border, no background colors (e-ink)
- Citations render as `<sup>` at 0.7em, linked to bibliography, no underline
- Blockquotes have left border, `page-break-inside: avoid`
- No background colors anywhere (e-ink optimization)

## Contributing

- Edit markdown files in `chapters/`. Do not hand-edit the EPUB.
- After changes, rebuild the EPUB with `python3 build_epub.py` and commit both the markdown changes and the rebuilt EPUB.
- Chapter files are numbered `NN-slug.md`. The bibliography is always the last chapter (`22-bibliography.md`).
- Follow the citation and writing conventions above. New content should match the existing tone and structure.
