# Production Ready

**Building and Operating an AI Code Factory** - a systems engineering book by Mart Parve. MIT licensed.

## Project Structure

```
chapters/              Markdown source (00-introduction through 24-bibliography)
cover.png              Book cover (1600x2560 PNG)
production-ready.epub  Built EPUB for Kindle/e-readers (committed artifact)
tools/
  build_epub.py        EPUB build + citation post-processing script
  metadata.yaml        Pandoc metadata (title, author, license)
  epub.css             Kindle/e-ink optimized stylesheet
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

All sources live in `chapters/24-bibliography.md`. Chapters reference them with short inline keys in brackets.

### Key Formats

- **Podcast episodes:** `[ANDev-NNN]` (AI Native Dev Podcast by Tessl, e.g. `[ANDev-052]`)
- **Named sources:** `[Author-Keyword]` (e.g. `[GitClear-2025]`, `[Stripe-Minions-1]`, `[Beck-augmented]`)
- **Tool references:** Single-word keys like `[BMAD]`, `[Goose]`, `[Kiro]`

### Rules

- **One source, one bibliography entry, cited many times.** Never duplicate a source in the bibliography.
- **Deduplicate within a passage.** Within a blockquote block or paragraph, cite each source only once (first occurrence). Do not repeat the same key on every sentence.
- **Biographical context belongs in running text**, not as a citation. Write "Steve Kuliski, an engineer at Stripe" in the prose, don't create a `[Kuliski-bio]` citation.

### Adding New Sources

1. Add the entry to `chapters/24-bibliography.md` under the appropriate section (podcast or other)
2. Use a key that matches the existing patterns
3. If the key doesn't match the regex in the build script, add it to the `CITE_KEY` pattern

## Building the EPUB

Requires `pandoc` and Python 3.

```bash
python3 tools/build_epub.py
```

Run from the project root. After any content change, rebuild the EPUB before committing.

### What the Build Does

1. Runs pandoc with `metadata.yaml`, `cover.png`, `epub.css`, and all `chapters/*.md` files in order
2. Post-processes the EPUB:
   - **Chapter citations:** `[ANDev-052]` becomes `<sup><a href="bibliography.xhtml#ANDev-052">[ANDev-052]</a></sup>` - superscript, clickable, linked to bibliography
   - **Bibliography entries:** `**[ANDev-052]**` gets an `id` anchor for linking, stays bold (not superscript)
3. Outputs `production-ready.epub`

### EPUB Styling Conventions

Maintain these when modifying `epub.css`:

- Serif body font (Georgia), 1.5 line-height, justified text, no indent
- Monospace code at 0.8em with `pre-wrap` word breaking, 1px border, no background colors
- Citations render as `<sup>` at 0.7em, links inherit text color, no underline
- Blockquotes: left border (3px #666), 0.95em, left-aligned, `page-break-inside: avoid`
- Tables: collapsed borders, 0.85em, `page-break-inside: avoid`
- H1: `page-break-before: always`, 1.6em
- **No background colors anywhere** (e-ink optimization)

### Citation Key Regex

The build script recognizes these patterns in `CITE_KEY`:

- `ANDev-\d{3}` - podcast episodes
- `[A-Z][A-Za-z]+-[A-Za-z0-9-]+` - multi-word keys (e.g. `Stripe-Minions-1`)
- `[A-Z][a-z]+[-]\d+` - author-year (e.g. `Corso-2025`)
- Single-word names: `BMAD`, `Goose`, `Kiro`, `Devin`, `Cursor`, `Aider`, `Factory`, `Graphite`, `CodeRabbit`, `Qodo`, `Nix`, `Flox`, `Dash0`, `Tessl`, `SpecKit`, `BacklogMD`, `TerminalBench`, `Guardrails`, `WebMCP`, `AAIF`, `ACP`, `TBD`, `promptfoo`, `METR`

When adding a source with a key that doesn't match, update the regex.

## Commands

### `/research <topic>` - Chapter Research

Deep-researches a topic for a new chapter. Four phases: source mining from known corpus, citation chasing for external sources, adversarial testing (counter-evidence, failure cases, assumption stress-testing), and synthesis into a sourced outline.

Key constraints:
- Engineering over philosophy: prioritize practitioner data and failure postmortems over opinion
- Source diversity: no single origin exceeds 30% of citations
- Adversarial findings target: at least 20% of sources should challenge the chapter's claims
- Output: `chapters/OUTLINE-<slug>.md` with source mapping and tension analysis

See `.claude/commands/research.md` for the full skill definition.

## Contributing

- Edit markdown files in `chapters/`. Do not hand-edit the EPUB.
- After changes, rebuild the EPUB and commit both the markdown changes and the rebuilt EPUB.
- Chapter files are numbered `NN-slug.md`. The bibliography is always the last chapter (`24-bibliography.md`).
- Follow the citation and writing conventions above. New content should match the existing tone and structure.
