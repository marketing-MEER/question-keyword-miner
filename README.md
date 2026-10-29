<div align="center">

# ❓ question-keyword-miner

### Pull every question keyword out of Search Console and Google autocomplete, with the answer format and next step for each.

[![tests](https://github.com/marketing-MEER/question-keyword-miner/actions/workflows/ci.yml/badge.svg)](https://github.com/marketing-MEER/question-keyword-miner/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![No API keys](https://img.shields.io/badge/API%20keys-none%20needed-brightgreen)
[![Part of SEO Toolbox](https://img.shields.io/badge/part%20of-SEO%20Toolbox-orange)](https://github.com/marketing-MEER/seo-toolbox)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Meer%20Hamza-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)

[🚀 Quick start](#quick-start) · [⚙️ How it works](#how-it-works) · [📄 Report](#report) · [❓ FAQ](#faq) · [👤 Author](#author)

</div>

---

## 💡 What it does

Question keywords are where featured snippets, People Also Ask boxes and AI answers come from, but they hide inside long Search Console exports, and the free way to find new ones (typing "how ...", "why ..." into Google) takes ages.

`question-keyword-miner` pulls every question out of your Search Console queries, can ask Google autocomplete for more questions about your topics, and tells you for each one which answer format fits and what to do based on where you rank today.

- ✅ Questions found by their first word (how, what, why, can, does, is, should...) or a question mark
- ✅ Optional Google autocomplete mining for any seed topic, polite and free
- ✅ Answer format per question type and an action per question from its GSC position
- ✅ Free, MIT licensed, no API keys. Works with the exports you already have.

## 📊 Why this matters

> **83% of Google Searches Aren't Questions** · NP Digital, May 2025 (1 billion queries)
> - Only 17% of Google searches are phrased as questions.
> - Average question query length is 10.3 words.
> - Most question-based queries start with how or what.
>
> **Growth of Question-Based Search Queries** · NP Digital, March 2026 (survey of 1,000 people)
> - Question-based searches grew from 8 percent in 2023 to 21 percent in 2026.
> - Over one-fifth of searches are now question-based.
>
> Data: [question search statistics](https://neilpatel.com/marketing-stats/google-question-search-statistics/) · [growth of question searches](https://neilpatel.com/marketing-stats/percent-of-google-searches-are-questions/)

**How question-keyword-miner uses this:** the insights say *"format answers for featured snippets, especially for how and what terms"* and *"target long-tail question keywords"*. So every question gets the answer format that fits its type, your share of question queries is shown next to the 17% benchmark, and autocomplete questions you don't rank for yet are listed as new content.

<a id="quick-start"></a>

## 🚀 Quick start

```bash
git clone https://github.com/marketing-MEER/question-keyword-miner.git
cd question-keyword-miner
pip install -e .
question-keyword-miner --gsc examples/gsc_queries.csv --seed sourdough
# also ask Google autocomplete (needs internet):
question-keyword-miner --gsc examples/gsc_queries.csv --seed sourdough --autocomplete
```

This writes **`question_keywords.html`** (a formatted report you can open, share or print to PDF) and **`question_keywords.xlsx`** (all the data).

> [!TIP]
> If the `question-keyword-miner` command isn't found, use `python -m question_keyword_miner`.

## 📥 Input

| Input | Notes |
|---|---|
| `--gsc FILE` | Search Console → Performance → Search results → Queries → Export (CSV). Detected columns: `Top queries`/`Query`, `Clicks`, `Impressions`, `Position`. Any keyword CSV works too (volume is used as impressions) |
| `--seed TERM` | Topics to mine with `--autocomplete`, comma separated. Seeds also tag GSC questions that contain them |

You need at least one: a GSC file, or seeds with `--autocomplete`.

<a id="how-it-works"></a>

## ⚙️ How it works

1. **Find questions**: a query is a question if its first word is a question word (how, what, why, when, where, who, which, can, does, do, is, are, should, will...) or it ends with "?". "however" or "whatsapp" don't count: the whole first word must match.
2. **Autocomplete** (opt-in): for each seed it asks Google's free suggestion endpoint for `how <seed>`, `what <seed>`, `why <seed>`, `when <seed>`, `where <seed>`, `which <seed>`, `can <seed>`, `is <seed>`, `does <seed>` and `should <seed>`, one request per second, and keeps the suggestions that are questions.
3. **Answer format** per type (general featured-snippet practice):

| Type | Answer format |
|---|---|
| how | Numbered steps under an H2 that repeats the question |
| what | One-sentence definition first (40-60 words), then detail |
| why | Short answer first, then a bulleted list of reasons |
| which | Comparison table with a clear pick |
| when / where / who | The fact in the first sentence |
| yes/no (can, is, does, should...) | Start with yes or no, then one line of why |

4. **Action** from the GSC position: top 3 = keep the answer short and first; page one = add a direct answer under an H2; page two = move the answer up and link to it; further back or not ranking = answer it on a page about that exact topic, or write a new one.

### Options

| Option | Default | What it does |
|---|---|---|
| `--gsc` | none | Search Console queries export |
| `--seed` | none | Seed topics, comma separated (repeatable) |
| `--autocomplete` | off | Ask Google autocomplete for questions about each seed (about 10 requests per seed) |
| `--lang`, `--country` | `en`, `us` | Autocomplete language and country |
| `--delay` | `1.0` | Seconds between autocomplete requests (never below 0.5) |
| `-o`, `--output` | `question_keywords` | File name for the report (`.html` + `.xlsx`) |

<a id="report"></a>

## 📄 The report

| Section / Excel sheet | Shows |
|---|---|
| Summary cards | Questions found, average words, share of GSC queries that are questions, new questions from autocomplete |
| Benchmark panels | The two NP Digital stats on question searches |
| **Types** | Questions, impressions, clicks and average length per question type, with the answer format |
| **One sheet per type** | Each question with source (gsc, autocomplete or both), seed, clicks, impressions, position and action |
| **All questions** | Everything, with the answer format |

<details>
<summary>📄 Example: real output from <code>examples/</code> (fictional baking blog, GSC file only)</summary>

12 of 18 queries are questions (66.7%). The sample was built around questions, so it is far above NP Digital's 17%.

| type | questions | impressions | clicks | avg words | answer format |
|---|---|---|---|---|---|
| yes/no | 4 | 10,100 | 58 | 4.8 | Start with yes or no, then one line of why |
| how | 3 | 22,400 | 970 | 5 | Numbered steps under an H2 that repeats the question |
| why | 1 | 6,300 | 95 | 7 | Short answer first, then a bulleted list of reasons |
| what | 1 | 4,800 | 40 | 6 | One-sentence definition first (40-60 words), then detail |

| question | type | impressions | position | action |
|---|---|---|---|---|
| how to make sourdough starter | how | 14,100 | 3.2 | Page one: add a direct answer under an H2 that matches the question |
| how long to proof sourdough | how | 5,200 | 2.8 | Top 3: keep the answer short and first so it can win or hold the snippet |
| what flour is best for sourdough | what | 4,800 | 12.6 | Page two: answer it higher up on the page and link to it from related pages |
| is sourdough bread healthy | yes/no | 3,700 | 23.5 | Far back: answer it on a page about this exact topic, or write a new page |
| where to buy sourdough starter | where | 880 | 31.2 | Far back: answer it on a page about this exact topic, or write a new page |

</details>

## 🧰 More free SEO tools

This repo is one tool in the **[SEO Toolbox](https://github.com/marketing-MEER/seo-toolbox)**, a family of free, single-purpose SEO tools. Related:
- [long-tail-revenue-scorer](https://github.com/marketing-MEER/long-tail-revenue-scorer): score keywords by revenue potential from their length and intent
- [keyword-intent-classifier](https://github.com/marketing-MEER/keyword-intent-classifier): tag keywords by search intent
- [topic-cluster-planner](https://github.com/marketing-MEER/topic-cluster-planner): group the questions into pillar and spoke pages
- [seo-workhorse](https://github.com/marketing-MEER/seo-workhorse): audit, clustering, redirects and GSC quick wins in one CLI

<a id="faq"></a>

## ❓ FAQ

<details><summary><b>Is the autocomplete endpoint allowed?</b></summary>

It is the public endpoint browsers use for search suggestions, and it needs no key. The tool sends about 10 requests per seed with at least half a second between them (one second by default) and its own user agent. Keep seed lists short; for hundreds of seeds use a paid keyword tool instead.
</details>

<details><summary><b>Why do autocomplete questions have no volume?</b></summary>

Autocomplete gives suggestions, not search volume. A suggestion only shows up when enough people type it, so treat them as real demand of unknown size and check the big ones in a keyword tool.
</details>

<details><summary><b>Is my data sent anywhere?</b></summary>

Your GSC file never leaves your computer. Only with `--autocomplete` does the tool send requests, and they contain only your seed words with a question prefix, sent to suggestqueries.google.com.
</details>

## 🧪 Tests

```bash
python -m unittest discover -s tests -t . -v
```

## 📄 License

[MIT](LICENSE). Free for personal and commercial use. Benchmark figures © their original publishers and quoted with a link to the source.

<a id="author"></a>

## 👤 Author

**Meer Hamza** · SEO Team Lead · Berlin 🇩🇪
10+ years in SEO, AEO and GEO. I build small tools that take the spreadsheet work out of SEO.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)
[![Email](https://img.shields.io/badge/Email-meerhamza5%40gmail.com-D14836?logo=gmail&logoColor=white)](mailto:meerhamza5@gmail.com)

<div align="center">

**If this saved you time, a ⭐ helps other SEOs find it.**

</div>
