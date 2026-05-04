---
description: Deep research a topic for a book chapter - source mining, citation chasing, adversarial testing
allowed-tools: Read, Bash(grep:*), Bash(find:*), Bash(wc:*), Bash(ls:*), Bash(cat:*), WebSearch, WebFetch, Agent
---

# Chapter Research Skill

Research a topic for a book chapter. Produces a sourced outline with adversarial findings.

## Input

`$ARGUMENTS` contains: `<topic>` and optionally `corpus:<path>` to a directory of source documents (transcripts, notes, papers).

Examples:
- `/research evaluations for AI code factories`
- `/research agent sandboxing corpus:/path/to/transcripts`

If no corpus path given, default to:
- `/Users/martparve/Library/Mobile Documents/com~apple~CloudDocs/SDD/AI Native Dev Podcast/raw/` (podcast transcripts)
- `/Users/martparve/Library/Mobile Documents/com~apple~CloudDocs/SDD/AI-Native-Dev-Sources.md` (source catalog)

## Constraints

- **Engineering bias.** Prioritize practitioner experience, implementation details, measured outcomes, and failure postmortems over theoretical frameworks, taxonomies, and opinion pieces. A Stripe blog post about what broke beats a thought-leader thread about what should work.
- **Source diversity.** No single origin (podcast, blog, company) should exceed 30% of cited sources. Flag and rebalance if this is violated.
- **Existing bibliography.** Read `chapters/23-bibliography.md` before starting. Reuse existing keys where possible. Do not duplicate entries.
- **Existing chapters.** Read the topic's neighboring chapters to understand what's already covered and what the chapter needs to add. Avoid restating material from other chapters.

## Phase 1: Source Mining (parallel agents OK, cap at 3)

Goal: extract claims, quotes, and data points relevant to the topic from the known corpus.

### Steps

1. **Size-check the corpus.** Run `wc -c` on each file. Skip files over 50KB without sampling first (read first 200 lines, check relevance, then read in full only if relevant).

2. **Keyword scan.** Grep the corpus for topic-relevant terms. Cast a wide net - include synonyms, related concepts, and negations ("eval", "evaluation", "benchmark", "test", "measure", "judge", "score", "grader", "non-determinism", "flaky", etc.). Record which files have hits.

3. **Deep read.** For each file with hits, read the relevant sections. Extract:
   - **Claims** - factual assertions with enough context to verify ("X improved Y by Z%")
   - **Quotes** - verbatim text worth citing directly
   - **Data points** - numbers, percentages, study sizes
   - **Named sources** - people, companies, papers, tools mentioned that could be chased

4. **Catalog.** Produce a working list: one row per finding, columns: `source | claim | quote | type (data/opinion/framework/tool)`.

## Phase 2: Citation Chasing

Goal: follow references outward from Phase 1 findings. Fill gaps in source diversity.

### Steps

1. **Identify chase targets.** From Phase 1 catalog, list:
   - Papers or blog posts cited by name but not yet read
   - People or companies mentioned whose primary source hasn't been checked
   - Claims that sound specific but lack a primary source

2. **Web search for primary sources.** For each chase target, search for the original publication. Read the abstract/summary. If relevant, extract claims and data points into the catalog.

3. **Diversity check.** Count sources by origin. If any single origin exceeds 30%, explicitly search for alternative perspectives:
   - Different companies (not just FAANG)
   - Academic papers (not just blog posts)
   - Practitioners who disagree with the dominant narrative
   - Non-English-language sources if the topic has international dimensions

4. **Gap analysis.** Compare catalog coverage against a mental model of what the chapter needs. Identify missing perspectives: "we have no sources on cost", "no one contradicts the main claim", "all sources are from 2024, nothing from 2025-2026."

## Phase 3: Adversarial Research

Goal: actively find evidence that challenges, complicates, or limits the chapter's likely claims. This is not optional. Every chapter claim that goes unchallenged is a chapter claim that hasn't been stress-tested.

### 3a. Counter-Evidence

For each major claim in the catalog, search for:
- **Direct contradictions.** Someone measured the opposite result, or argues the opposite position with evidence.
- **Boundary conditions.** The claim is true in context X but false in context Y (different team size, different language, different domain).
- **Outdated evidence.** The claim was true in 2024 but the landscape has changed.

Search queries should be explicitly adversarial:
- `"[topic] doesn't work"`, `"[topic] failed"`, `"[topic] overrated"`
- `"[recommended practice] problems"`, `"[recommended practice] limitations"`
- `"[cited tool] alternatives"`, `"[cited tool] criticism"`

Record counter-evidence in the catalog with type `adversarial/counter`.

### 3b. Failure Cases

Search specifically for:
- Teams that tried the recommended approach and abandoned it (postmortems, retrospectives, HN threads)
- Known failure modes and edge cases
- Scale-dependent failures ("works for 10 engineers, breaks at 100")
- Cost or complexity that made the approach impractical

Search patterns:
- `"we tried [practice] and"`, `"stopped using [tool]"`, `"[practice] postmortem"`
- Site-specific: `site:news.ycombinator.com`, `site:reddit.com/r/programming`

Record with type `adversarial/failure`.

### 3c. Assumption Stress-Testing

List the top 5 assumptions the chapter will make (e.g., "teams have enough historical data to build an eval corpus", "LLM judges can be calibrated reliably"). For each:

1. State the assumption explicitly.
2. Search for evidence that the assumption doesn't hold universally.
3. Determine: is this a real limitation the chapter should acknowledge, or a solvable problem the chapter should address?

Record with type `adversarial/assumption`.

### 3d. Adversarial Summary

Produce a standalone section listing:
- Claims that survived adversarial testing (strong)
- Claims that need qualification (conditional)
- Claims that should be dropped or reframed (weak)
- Assumptions the chapter must acknowledge as limitations

## Phase 4: Synthesis

Goal: produce the chapter outline with full source mapping.

### Steps

1. **Structure.** Draft 9-13 H2 sections following the book's chapter pattern:
   - Opening scene-setting paragraph (no heading)
   - Conceptual framing (what, why, how it differs from adjacent concepts)
   - Technical sections (the bulk)
   - Practical guidance (tooling, economics, implementation)
   - Closing section (lifecycle, future direction)

2. **Source mapping.** For each section, list:
   - Primary sources (back the main claim)
   - Supporting sources (add evidence or examples)
   - Adversarial sources (counter-evidence, limitations, failure cases to address)

3. **Case study candidates.** Identify 2-3 candidates for blockquote case studies (book format: `> **Case Study: Title**`). Prefer case studies with:
   - Specific, named people and organizations
   - Quantitative results
   - Honest description of what didn't work

4. **Tension map.** For each section, note where the adversarial findings create productive tension. The chapter should address these, not hide from them. Format: `TENSION: [claim] vs [counter-evidence] -> [how the chapter should handle it]`.

5. **New bibliography entries.** List sources that need to be added to the bibliography, with proposed citation keys matching existing patterns.

## Output

Write the outline to `chapters/OUTLINE-<slug>.md` with this structure:

```markdown
# Chapter Outline: <Title>

**Thesis:** <one paragraph>

## Source Diversity Check
- Total unique sources: N
- By origin: [breakdown]
- Adversarial sources: N (target: at least 20% of total)

## Adversarial Summary
[From Phase 3d]

---

## <Section Title>
[Section description]
Sources: [keys]
Adversarial: [counter-evidence or "none found"]
TENSION: [if applicable]

---

[Repeat for each section]

## Case Study Candidates
[2-3 candidates with source, key quote, and why it's useful]

## New Bibliography Entries
[Table of new sources to add]

## Existing Bibliography Keys Used
[List of keys already in 23-bibliography.md]
```

After writing the outline, report to the user:
- Total sources found (catalog size)
- Source diversity breakdown
- Number of adversarial findings
- Top 3 tensions the chapter should address
- Recommended next step (usually: "review the outline, then `/research` again on specific weak areas, or start writing")
