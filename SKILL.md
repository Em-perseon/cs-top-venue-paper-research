---
name: cs-top-venue-paper-research
description: Research recent computer science papers from top-tier venues, focused on AI/ML, NLP, and DB/Data Mining. Use when Codex needs to find, crawl, verify, summarize, or build a literature review from recent conferences, journals, venue submissions, workshops, and preprints, with a dynamic rolling window of the current calendar year and the previous two calendar years. When this skill is invoked for a paper-research request, Codex must create a Markdown report file as the primary deliverable and should search for as many relevant papers as possible, including accepted/published papers, submissions, workshops, technical reports, and preprints in clearly labeled status groups.
---

# CS Top Venue Paper Research

## Overview

Use this skill to run recent paper research for AI/ML, NLP, and DB/Data Mining with explicit publication/source status. Default to the current calendar year plus the previous two calendar years, recomputed from the actual current date at runtime. Use top-venue filters before ranking accepted work, and include accepted/published papers, submitted/under-review venue papers, workshops, technical reports, and arXiv/preprint supplements in clearly labeled groups.

This skill is optimized for breadth. When the user asks for `调研`, `找论文`, `相关论文`, `有没有`, `有无`, `文献`, `方向`, or similar paper-discovery work, default to finding as many relevant papers as possible. Do not wait for the user to say "comprehensive", "多找", or "越多越好".

## Mandatory Deliverable Contract

When this skill is invoked for a paper-research request, the assistant MUST create or update a Markdown report file during the same turn. The Markdown file is the primary deliverable.

Required behavior:

1. Do not answer only in chat unless the user explicitly asks for a quick answer, no file, or no Markdown.
2. Create a `.md` report in the output location before the final response.
3. The final chat response must be short and include a clickable path to the `.md` report.
4. The report must start with one large paper table after the title and any one-line scope note. Do not put a long coverage report before the table.
5. Include as many relevant papers as can be verified from searched sources. Prefer a larger table with status labels over a compact ranked shortlist.
6. Keep the fixed report structure in `Output Shape` unless the user explicitly asks for a different format.
7. If a section has no records, keep the section and write `None found under the searched sources`.
8. Do not add a later "newly found" or "补检新增" section in a fresh report; integrate every verified paper into the one large table and the proper notes/analysis sections.

## Defaults

- Year window: always compute dynamically from the actual current date as `{current_year-2}, {current_year-1}, {current_year}` unless the user explicitly provides years.
- Tracks: `ml`, `nlp`, and `dbdm` unless the user narrows the scope.
- Venue mode: `broad` by default. Use `strict` only when the user explicitly asks for only CCF A, only top venues, or the smallest elite set.
- Paper status: include accepted/published papers, submitted/under-review venue papers, workshops, peer-reviewed supplements, technical reports, and preprints by default. Label status in the table.
- Preprint supplement: include arXiv and other non-venue preprints by default when they are relevant and traceable.
- Paper types: full/main-track conference papers, regular journal articles, venue-hosted submissions, relevant workshop papers, technical reports, and arXiv/preprint papers.
- Exclude from the main table only records that are off-topic, duplicate, unverifiable, or have no traceable source URL. Keep plausible but unverifiable near-misses in `Excluded or Low-Confidence Candidates`.

## Maximum Paper Collection Policy

- There is no `balanced` versus `max` mode. The default mode is maximum useful paper collection.
- Build a candidate pool before ranking. Search accepted/published venues, public OpenReview submissions, venue workshops, arXiv, Semantic Scholar, OpenAlex, Papers With Code, GitHub/project pages, and survey references.
- Search synonym expansions and method/task variants, not only the literal topic. For example, for "agent memory", also search `long-term memory`, `episodic memory`, `semantic memory`, `procedural memory`, `working memory`, `memory management`, `memory bank`, `memory retrieval`, `memory consolidation`, `reflective memory`, `self-evolving agents`, `experience replay`, `personalization memory`, `graph memory`, `KV cache memory`, `multimodal memory`, `embodied agent memory`, `memory benchmark`, `memory injection`, and `memory extraction`.
- Include high-signal workshop, technical report, and preprint results in the large paper table with clear status labels. Do not present them as accepted top-venue work unless venue/status is verified.
- Integrate every verified result into the large paper table. Avoid presenting late discoveries as a separate "newly found" section in a fresh report.
- Use source-by-source enumeration when a source exposes a searchable paper list. For each searched source/year, record query strings, hits kept, and hits discarded.
- Prefer breadth over compactness in candidate discovery, then deduplicate and cluster. It is acceptable and preferred for the report to contain a large table.
- If fewer than 10 relevant papers are found, broaden query families and include a `Search Attempts and Gaps` note explaining sources searched and why the result set is small.
- If time or source access prevents exhaustive verification, return a coverage ledger and label the report as "candidate set from searched sources", not "complete".

## Venue Whitelist

`strict` is the high-precision set. `broad` includes all strict venues plus field-core venues for better coverage.

AI/ML:

- strict: NeurIPS, ICML, AAAI, IJCAI, JMLR, Artificial Intelligence, TPAMI
- broad additions: ICLR, AISTATS, UAI, COLT, JAIR

NLP:

- strict: ACL, TACL
- broad additions: EMNLP, NAACL, COLING, Computational Linguistics, TASLP

DB/Data Mining:

- strict: SIGMOD, VLDB/PVLDB, ICDE, KDD/SIGKDD, SIGIR, TODS, TOIS, TKDE, VLDBJ
- broad additions: WWW/The Web Conference, WSDM, CIKM, ICDM, PODS, TKDD

## Quick Start

Generate the venue/year/query plan:

```bash
python3 scripts/build_venue_queries.py --current-year <CURRENT_YEAR> --topic "retrieval augmented generation" --tracks ml,nlp,dbdm --mode broad
```

Include public submitted or under-review papers, such as ICLR OpenReview submissions:

```bash
python3 scripts/build_venue_queries.py --current-year <CURRENT_YEAR> --topic "retrieval augmented generation" --tracks ml --mode broad --include-submissions
```

Include arXiv/preprint supplements:

```bash
python3 scripts/build_venue_queries.py --current-year <CURRENT_YEAR> --topic "long-context reasoning" --tracks ml,nlp,dbdm --mode broad --include-submissions --include-preprints
```

Replace `<CURRENT_YEAR>` with the current calendar year from the runtime environment before running the command. Do not hardcode a fixed year range in the skill or report unless the user explicitly asks for that range.

Load `references/venue_whitelist.json` when you need to inspect or adjust the venue set.

## Output Location

Do not save research reports inside the skill directory unless the user explicitly asks to edit the skill itself.

Always produce a Markdown report file when this skill is invoked for paper research:

1. If the user is working in a specific project folder, workspace, or newly opened folder, save reports under that folder, preferably in a `调研/` or `research/` subdirectory.
2. If the user names an output directory, save there.
3. If no project/output directory is clear, default to:

```text
/Users/host/Desktop/学习资料整理/研究生/感兴趣/调研
```

Use descriptive filenames such as:

```text
{topic-slug}-top-venue-research-{YYYY}-{YYYY}.md
{topic-slug}-papers.csv
{topic-slug}-papers.json
```

If the target directory is outside the writable workspace and file creation requires approval, request permission before writing there.

## Workflow

1. Resolve the year window.
   - Use the user's explicit years if provided.
   - Otherwise compute the rolling three-year window from the actual current date: `{current_year-2}, {current_year-1}, {current_year}`.
   - Do not reuse old examples or past reports as the year window; recompute it every time the skill is invoked.
   - For the current year, expect incomplete proceedings until each conference has published accepted papers.

2. Select venues from the whitelist.
   - Use `strict` for highest precision.
   - Use `broad` for comprehensive CS-top-venue research in the requested fields.
   - Preserve aliases during matching: `KDD` and `SIGKDD`, `WWW` and `The Web Conference`, `NeurIPS` and `NIPS`.

3. Search canonical sources first.
   - DBLP for normalized venue/year bibliographic records.
   - OpenReview for ICLR and recent ML conference metadata when available.
   - ACL Anthology for ACL, EMNLP, NAACL, COLING, and TACL.
   - Proceedings or publisher pages for NeurIPS, ICML/PMLR, VLDB, SIGMOD, KDD, SIGIR, WWW, WSDM, CIKM, ICDE, and journals.
   - Search public venue-hosted submission systems such as OpenReview for relevant submissions and label these records as `submitted` or `under_review`.
   - Search arXiv, Semantic Scholar, OpenAlex, Papers With Code, and author/project pages and label non-venue records as `preprint_supplement` or `technical_report`.

3a. Execute a source matrix rather than a single search pass.
   - Proceedings: NeurIPS, ICML/PMLR, ICLR/OpenReview, AAAI, IJCAI, ACL Anthology, EMNLP, NAACL, COLING, KDD, WWW, SIGIR, WSDM, CIKM, ICDE, SIGMOD, VLDB/PVLDB, journals in the whitelist.
   - Submissions and workshops: public OpenReview venues for the selected years, especially ICLR/NeurIPS/ICML workshops directly matching the topic. Include these in the large paper table with status labels.
   - Indexes: DBLP, Semantic Scholar, OpenAlex, Crossref, arXiv, Papers With Code, Google Scholar snippets when available through search, and author/project pages.
   - Query families: combine the user's topic with venue/year terms, then run synonym families for mechanisms, tasks, evaluation, safety, and systems. For each family, search both quoted exact titles/terms and unquoted broader variants.
   - Backward/forward snowballing: inspect related-work sections, cited-by pages, repository paper lists, and recent surveys to recover papers missed by keyword search. Add only records with a traceable source URL.
   - Keep a candidate ledger with `source`, `query`, `raw_hit_count_or_observed_hits`, `kept_count`, and `reason_for_exclusions`.

4. Crawl content after venue/status verification.
   - Extract abstract, introduction-level problem statement, method summary, experimental setup, datasets/benchmarks, main results, limitations, and claimed contributions from legal public pages or PDFs.
- Prefer official HTML/PDF, OpenReview PDFs, ACL Anthology PDFs, PMLR PDFs, and author-provided open PDFs.
- Do not bypass paywalls. If full text is unavailable, use abstract and metadata and mark `content_coverage=metadata_only`.
- Provide an expanded Chinese abstract summary of 3-6 sentences per important paper. Do not reduce the abstract to a one-line blurb unless the user explicitly asks for a compact table.
- Provide the method summary in Chinese by default. Keep technical terms, method names, benchmark names, dataset names, model names, venue names, and code/project names in their original form when that is clearer for the user's topic.
- Preserve a structured per-paper note with `Abstract`, `Method`, `Datasets/benchmarks`, and `Main results` whenever producing a research report or literature review.
   - If quoting original abstract text verbatim, keep excerpts short and attribute the source. Prefer paraphrased expanded summaries for full reports.

5. Enrich after venue verification.
   - Use Semantic Scholar, OpenAlex, Crossref, Unpaywall, arXiv, and Papers With Code only after the title or DOI is matched to a whitelisted venue.
   - Add abstract, citation count, influential citation count, PDF URL, code URL, dataset URL, and DOI when available.
   - Admit arXiv-only records into the large paper table with `preprint_supplement` status. Do not describe them as accepted/published top-venue work unless venue/status is verified.

6. Deduplicate and validate.
   - Normalize title by lowercasing, stripping punctuation, and collapsing whitespace.
   - Merge records by DOI, DBLP key, OpenReview forum ID, ACL Anthology ID, or normalized title.
   - Require `title`, `authors`, `year`, `paper_status`, `source_group`, and at least one source URL.
   - For preprints, set `venue=arXiv` or the relevant repository and `venue_mode=preprint_supplement`.
   - Keep near-misses in `Excluded or Low-Confidence Candidates` when they are likely relevant but lack venue verification or a traceable source.

7. Sort and cluster for the user's research question.
   - Sort the large paper table by topical relevance first, then venue/status confidence, recency, code/data availability, and methodological fit.
   - For very broad topics, still keep one large paper table first; use later synthesis sections to cluster methods, datasets/benchmarks, systems, evaluation, applications, and surveys.

## Coverage Standard

Aim to enumerate every matching paper from every selected venue/year when the source exposes proceedings, then add submissions, workshops, technical reports, and preprints. If the topic is broad and results are large, keep the large table and move lower-confidence items to the excluded appendix; do not replace the large table with only a ranked shortlist.

Do not stop at a small top-venue set. A small accepted/published set is acceptable only if accompanied by submissions, workshops, technical reports, preprints, a candidate ledger, a query/source log, and a clear explanation of why records were excluded from the main table.

Never claim "all papers" unless you have searched every selected venue/year plus the requested preprint sources and can show the query/source log. Prefer "all papers found under this source and venue policy" or "candidate set from searched sources."

Always report in the later coverage/log section:

- selected years
- selected tracks
- venue mode
- paper statuses included
- section/status groups included
- venues searched
- preprint sources searched, if any
- workshop/submission sources searched, if any
- query families searched, especially synonym expansions
- candidate counts by section/status group
- explicit exclusions
- coverage gaps, especially for current-year proceedings not yet published

## Output Shape

For human-readable reports, use this fixed structure and order:

1. `# {Topic} Paper Research ({YYYY}-{YYYY})`
2. One-line scope note.
3. `## Paper Table`
4. `## Per-Paper Notes`
5. `## Structure Type Synthesis`
6. `## Recommended Reading Order`
7. `## Insights`
8. `## Research Topic Entry Points`
9. `## Excluded or Low-Confidence Candidates`
10. `## Search Attempts and Gaps`

The first substantive section must be `## Paper Table`. Put coverage and query details near the end, not before the table.

Paper table rules:

- Use one large table that includes accepted/published papers, submitted/under-review papers, workshops, peer-reviewed supplements, technical reports, and arXiv/preprint supplements together.
- Use `Status group` to distinguish publication/source status.
- Default table columns:

```text
#, Paper, Year, Venue / source, Status group, Source URL, Code, Relevance
```

- If there are many papers, do not shorten the table to only the strongest papers. Include all verified relevant papers and use concise relevance notes.
- If a source URL is long, use a Markdown link in the Paper or Source URL cell.

Per-paper notes:

```text
### Paper title

- Abstract: 用中文写 3-6 句详细摘要，说明问题背景、核心动机、研究对象、系统/方法做什么、适用场景和主要发现。保留该论文和该领域的专用名词、方法名、模型名、数据集名、benchmark 名和 venue 名。
- Method: 用中文概括方法机制，保留方法名和关键模块名；说明该方法的输入、核心流程、模型/算法/系统结构、训练或推理方式，以及它如何解决目标问题。
- Datasets/benchmarks: 列出数据集、benchmark、任务环境或评测对象；如果来源页没有明确给出，写 `not found on source page`，不要臆测。
- Main results: 用中文列出主要实验结果、提升幅度或定性结论；如果只有作者声称而没有具体数值，标注为 reported/claimed。
```

For machine-readable exports, include these fields:

```text
title, authors, year, paper_status, source_group, venue, paper_type, source_url, doi, pdf_url,
openreview_url, dblp_url, acl_url, arxiv_url, code_url, citations,
topic_match_reason, expanded_abstract_summary_zh, method_summary_zh, datasets, main_results,
contribution_summary, limitations, content_coverage
```

For a literature review, add:

- one large paper table before any coverage report
- a candidate ledger and query/source log
- the structured per-paper notes after the tables
- structure type synthesis after per-paper notes
- recommended reading order
- an `Insights` section summarizing what the assistant learned after reading many papers
- a `Research Topic Entry Points` section with possible thesis/paper directions
- contradictions or unresolved questions

## Guardrails

- Do not use citation count alone as the ranking criterion for recent papers.
- It is acceptable and preferred to include accepted/published papers, submitted/under-review papers, workshops, technical reports, and preprints in one large table, but every row must include a clear `Status group`.
- Do not describe submitted, workshop, technical report, or preprint records as accepted/published top-venue work unless the source verifies that status.
- Include relevant workshop papers by default when they are traceable and topic-relevant; label them as `workshop`.
- Do not treat venue abbreviations as sufficient proof; verify the venue/year/source URL.
- If a venue renamed itself or publishes under multiple series, record the alias used and the canonical venue.
- If access is blocked by a paywall, keep metadata and link to DOI/publisher, then search for legal open copies through Unpaywall, arXiv, or author pages.
