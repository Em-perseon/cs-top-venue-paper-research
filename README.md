# CS Top Venue Paper Research

用于 Codex 的计算机科学顶会论文调研 skill，面向 AI/ML、NLP、数据库与数据挖掘方向。它的目标不是只给一个短名单，而是在明确 venue、年份、来源状态和证据等级的前提下，尽可能完整地发现近年相关论文，并输出可追溯的 Markdown 调研报告。

## 适用场景

- 调研某个研究方向近三年的顶会、期刊、投稿、workshop、技术报告和预印本论文。
- 为论文选题、开题、相关工作、survey 或技术路线梳理构建候选文献池。
- 需要区分 `accepted/published`、`submitted/under_review`、`workshop`、`technical_report`、`preprint_supplement` 等来源状态。
- 需要用固定结构产出中文文献调研报告，并保留来源 URL、代码链接、benchmark、主要结果和检索缺口。

## 项目结构

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── venue_whitelist.json
└── scripts/
    └── build_venue_queries.py
```

- `SKILL.md`：Codex skill 的主说明文件，定义触发场景、调研流程、报告结构和交付要求。
- `scripts/build_venue_queries.py`：根据 topic、年份、track 和 venue mode 生成检索计划。
- `references/venue_whitelist.json`：顶会、期刊、来源 URL、别名和 strict/broad 模式白名单。
- `agents/openai.yaml`：OpenAI agent 展示名、简述和默认 prompt。

## 核心策略

默认年份窗口是运行时当前年份及前两年。例如当前年份为 2026 时，默认覆盖 `2024, 2025, 2026`。如果用户明确指定年份，则使用用户指定范围。

默认 track 包括：

- `ml`：AI/ML
- `nlp`：自然语言处理
- `dbdm`：数据库、信息检索与数据挖掘

默认 venue mode 是 `broad`，它包含 `strict` venue 和额外的领域核心 venue。只有用户明确要求“只看 CCF A”“只看最顶级 venue”或“严格模式”时，才使用 `strict`。

## 快速开始

生成默认 broad 模式的检索计划：

```bash
python3 scripts/build_venue_queries.py \
  --current-year 2026 \
  --topic "retrieval augmented generation" \
  --tracks ml,nlp,dbdm \
  --mode broad \
  --pretty
```

生成简短 Markdown 风格摘要：

```bash
python3 scripts/build_venue_queries.py \
  --current-year 2026 \
  --topic "retrieval augmented generation" \
  --tracks ml,nlp,dbdm \
  --mode broad \
  --summary
```

包含公开投稿、under-review 记录和预印本补充来源：

```bash
python3 scripts/build_venue_queries.py \
  --current-year 2026 \
  --topic "long-context reasoning" \
  --tracks ml,nlp,dbdm \
  --mode broad \
  --include-submissions \
  --include-preprints \
  --pretty
```

指定固定年份：

```bash
python3 scripts/build_venue_queries.py \
  --years 2023,2024,2025 \
  --topic "LLM agent memory" \
  --tracks ml,nlp \
  --mode strict \
  --summary
```

## 脚本参数

| 参数 | 说明 |
| --- | --- |
| `--topic` | 研究主题或关键词短语。 |
| `--tracks` | 逗号分隔的 track，可选 `ml,nlp,dbdm`。不传则使用全部默认 track。 |
| `--mode` | venue 选择模式，支持 `broad` 和 `strict`，默认 `broad`。 |
| `--current-year` | 用于滚动年份窗口的当前年份。未提供时使用系统当前年份。 |
| `--years-back` | 从当前年份向前回溯的年数，默认 `2`。 |
| `--years` | 显式指定年份列表，例如 `2024,2025,2026`。优先级高于滚动窗口。 |
| `--start-year` / `--end-year` | 显式指定起止年份。 |
| `--include-submissions` | 包含 OpenReview 等公开投稿或 under-review 来源。 |
| `--include-preprints` | 增加 arXiv、Semantic Scholar、OpenAlex、Papers With Code 等预印本检索计划。 |
| `--pretty` | 以缩进 JSON 输出完整计划。 |
| `--summary` | 输出紧凑摘要，便于人工检查。 |

## 输出内容

脚本默认输出 JSON，主要字段包括：

- `generated_at`：计划生成时间。
- `years`：实际覆盖年份。
- `mode`：venue 模式。
- `tracks`：选中的研究方向。
- `venue_count`：选中 venue 数量。
- `venues`：每个 venue 在每个年份下的检索查询。
- `preprint_queries`：预印本补充检索计划，仅在启用 `--include-preprints` 时出现。
- `source_priority`：建议优先使用的来源顺序。
- `exclusion_terms`：默认排除或谨慎处理的记录类型。

## Codex Skill 使用方式

在 Codex 中调用该 skill 时，可以这样描述任务：

```text
Use $cs-top-venue-paper-research to find recent AI/ML, NLP, and DB/Data Mining papers from top venues, submissions, workshops, and preprints on retrieval-augmented generation.
```

当该 skill 被用于论文调研任务时，必须创建或更新一个 Markdown 报告文件，而不是只在聊天中回答。报告的首个主体部分应是 `## Paper Table`，之后再给 per-paper notes、结构类型综合、推荐阅读顺序、insights、研究入口和检索缺口。

默认报告结构：

```text
# {Topic} Paper Research ({YYYY}-{YYYY})
## Paper Table
## Per-Paper Notes
## Structure Type Synthesis
## Recommended Reading Order
## Insights
## Research Topic Entry Points
## Excluded or Low-Confidence Candidates
## Search Attempts and Gaps
```

如果没有明确输出目录，skill 默认将调研报告保存到：

```text
/Users/host/Desktop/学习资料整理/研究生/感兴趣/调研
```

如果该目录不可写，执行者应先请求写入权限，或根据用户指定的位置保存。

## Venue 白名单

白名单位于 `references/venue_whitelist.json`。当前包含：

- AI/ML：NeurIPS、ICML、ICLR、AAAI、IJCAI、AISTATS、UAI、COLT、JMLR、Artificial Intelligence、TPAMI、JAIR 等。
- NLP：ACL、EMNLP、NAACL、COLING、TACL、Computational Linguistics、TASLP 等。
- DB/Data Mining：SIGMOD、VLDB/PVLDB、ICDE、KDD/SIGKDD、SIGIR、WWW、WSDM、CIKM、ICDM、PODS、TODS、TOIS、TKDE、VLDBJ、TKDD 等。

修改 venue 集合时，优先编辑该 JSON 文件，而不是在脚本中硬编码 venue。

## 开发与验证

本项目只依赖 Python 标准库。修改脚本或白名单后，可以运行以下命令做基本验证：

```bash
python3 scripts/build_venue_queries.py \
  --current-year 2026 \
  --topic "retrieval augmented generation" \
  --tracks ml,nlp,dbdm \
  --mode broad \
  --include-submissions \
  --include-preprints \
  --summary
```

也可以检查 JSON 是否能正常生成：

```bash
python3 scripts/build_venue_queries.py \
  --current-year 2026 \
  --topic "agent memory" \
  --tracks ml,nlp \
  --mode strict \
  --pretty
```

## 维护原则

- 不要把固定年份写死在 skill 逻辑中；默认年份窗口应根据运行时当前日期动态计算。
- 不要把投稿、workshop、技术报告或预印本描述为已录用顶会论文，除非来源明确验证。
- 检索结果宁可多收集再标注状态，也不要只保留紧凑 shortlist。
- 所有主表记录至少需要标题、年份、状态分组和可追溯来源 URL。
- 新增 venue 时应同时维护别名、来源 URL、venue 类型和 strict/broad 模式。
