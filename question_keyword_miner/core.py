"""Collect question keywords from a Search Console export and (optionally) Google autocomplete.

Questions are found by their first word (how, what, why, can, does...) or a question mark. Each one gets
a question type, the answer format that fits it, and, with GSC data, an action based on its position.
"""
import json
import re
import time
import urllib.parse
import urllib.request

import pandas as pd

from .report import find_column, to_number

# NP Digital, May 2025 (1 billion queries): "Only 17% of Google searches are phrased as questions."
# "Average question query length is 10.3 words." "Most question-based queries start with how or what."
# Source: https://neilpatel.com/marketing-stats/google-question-search-statistics/
NP_QUESTION_SHARE = 17.0

QUESTION_WORDS = ["how", "what", "why", "when", "where", "who", "which", "can", "does", "do", "is", "are",
                  "should", "will", "could", "would", "whats", "how's", "what's"]
TYPE_OF = {"whats": "what", "what's": "what", "how's": "how", "does": "yes/no", "do": "yes/no", "is": "yes/no",
           "are": "yes/no", "can": "yes/no", "should": "yes/no", "will": "yes/no", "could": "yes/no",
           "would": "yes/no"}

# Answer format per question type (general featured-snippet practice; NP insight:
# "Format answers for featured snippets, especially for how and what terms").
ANSWER_FORMAT = {
    "how": "Numbered steps under an H2 that repeats the question",
    "what": "One-sentence definition first (40-60 words), then detail",
    "why": "Short answer first, then a bulleted list of reasons",
    "which": "Comparison table with a clear pick",
    "when": "The date, time or condition in the first sentence",
    "where": "The place or location in the first sentence",
    "who": "Name the person or role in the first sentence",
    "yes/no": "Start with yes or no, then one line of why",
}

# Prefixes sent to autocomplete for each seed.
AUTOCOMPLETE_PREFIXES = ["how", "what", "why", "when", "where", "which", "can", "is", "does", "should"]
USER_AGENT = "question-keyword-miner/1.0 (+https://github.com/marketing-MEER/question-keyword-miner)"

COLS = ["question", "type", "words", "source", "seed", "clicks", "impressions", "position", "action", "answer_format"]


def question_type(text: str) -> str | None:
    q = str(text).lower().strip()
    if not q:
        return None
    first = q.split()[0]
    if first in QUESTION_WORDS:
        return TYPE_OF.get(first, first)
    if q.endswith("?"):
        return "other"
    return None


def action(position: float, impressions: float) -> str:
    """General best practice, based on where the page ranks for the question today."""
    if not impressions:
        return "Not ranking yet: answer it in an FAQ block or a new section"
    if position <= 3:
        return "Top 3: keep the answer short and first so it can win or hold the snippet"
    if position <= 10:
        return "Page one: add a direct answer under an H2 that matches the question"
    if position <= 20:
        return "Page two: answer it higher up on the page and link to it from related pages"
    return "Far back: answer it on a page about this exact topic, or write a new page"


def load_gsc(path) -> pd.DataFrame:
    raw = pd.read_csv(path)
    q = find_column(raw, ["query", "queries", "top queries", "keyword", "search term"]) or raw.columns[0]
    out = pd.DataFrame({"query": raw[q].astype(str).str.strip().str.lower()})
    for name, cands in {"clicks": ["clicks"], "impressions": ["impressions", "volume", "search volume"],
                        "position": ["position", "average position"]}.items():
        c = find_column(raw, cands)
        out[name] = to_number(raw[c]) if c else 0.0
    out = out[out["query"] != ""]
    return out.groupby("query", as_index=False).agg(clicks=("clicks", "sum"), impressions=("impressions", "sum"),
                                                    position=("position", "mean"))


def fetch_suggestions(query: str, lang: str = "en", country: str = "us", timeout: float = 10) -> list[str]:
    """Google autocomplete suggestions (the free endpoint browsers use). Returns [] on any error."""
    url = ("https://suggestqueries.google.com/complete/search?client=firefox&"
           + urllib.parse.urlencode({"q": query, "hl": lang, "gl": country}))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
        return [str(s).lower() for s in data[1]]
    except Exception:
        return []


def autocomplete(seeds, fetch=fetch_suggestions, delay: float = 1.0, **kw) -> pd.DataFrame:
    """Ask autocomplete '<prefix> <seed>' for every prefix; keep suggestions that are questions."""
    rows = []
    for seed in seeds:
        for prefix in AUTOCOMPLETE_PREFIXES:
            for s in fetch(f"{prefix} {seed}", **kw):
                if question_type(s):
                    rows.append({"question": s, "seed": seed})
            if delay:
                time.sleep(delay)
    return pd.DataFrame(rows, columns=["question", "seed"]).drop_duplicates("question")


def _seed_for(text, seeds):
    for s in seeds:
        if re.search(r"\b" + re.escape(s.lower()) + r"\b", text):
            return s
    return ""


def mine(gsc: pd.DataFrame | None, suggestions: pd.DataFrame | None, seeds=()) -> pd.DataFrame:
    rows = {}
    if gsc is not None:
        for r in gsc.itertuples(index=False):
            t = question_type(r.query)
            if t:
                rows[r.query] = {"question": r.query, "type": t, "words": len(r.query.split()), "source": "gsc",
                                 "seed": _seed_for(r.query, seeds), "clicks": int(r.clicks),
                                 "impressions": int(r.impressions), "position": round(float(r.position), 1),
                                 "action": action(r.position, r.impressions)}
    if suggestions is not None:
        for r in suggestions.itertuples(index=False):
            if r.question in rows:
                rows[r.question]["source"] = "gsc + autocomplete"
                continue
            rows[r.question] = {"question": r.question, "type": question_type(r.question),
                                "words": len(r.question.split()), "source": "autocomplete", "seed": r.seed,
                                "clicks": 0, "impressions": 0, "position": None, "action": action(0, 0)}
    out = pd.DataFrame(list(rows.values()), columns=COLS)
    out["answer_format"] = out["type"].map(ANSWER_FORMAT).fillna("Answer in the first sentence")
    return out.sort_values(["impressions", "question"], ascending=[False, True]).reset_index(drop=True)


def type_summary(questions: pd.DataFrame) -> pd.DataFrame:
    g = questions.groupby("type").agg(questions=("question", "size"), impressions=("impressions", "sum"),
                                      clicks=("clicks", "sum"), avg_words=("words", "mean")).reset_index()
    g["avg_words"] = g["avg_words"].round(1)
    g["answer_format"] = g["type"].map(ANSWER_FORMAT).fillna("Answer in the first sentence")
    return g.sort_values(["questions", "impressions"], ascending=False).reset_index(drop=True)


def overview(gsc: pd.DataFrame | None, questions: pd.DataFrame) -> dict:
    from_gsc = questions[questions["source"].str.startswith("gsc")]
    total = len(gsc) if gsc is not None else 0
    return {"gsc_queries": total, "gsc_questions": len(from_gsc),
            "question_share_pct": round(len(from_gsc) / total * 100, 1) if total else None,
            "autocomplete_only": int((questions["source"] == "autocomplete").sum()),
            "avg_words": round(float(questions["words"].mean()), 1) if len(questions) else 0.0}
