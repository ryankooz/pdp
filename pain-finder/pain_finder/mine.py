"""Going deeper on keywords, learned from the data instead of guessed.

learn_phrases     n-grams (3-5 words) that are far more common in painful posts
                  than in everything collected: how people actually phrase pain.
extract_problems  pull the problem itself out of sentences like "how do I get rid
                  of ___", "struggling with ___ for 6 years", "my ___ won't go away",
                  with severity: years suffered, money spent, doctors seen.
autocomplete      what people type into Google about a problem.
"""

import json
import math
import re
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path

import requests

from . import analyze
from .reddit import _post_from_listing

STRONG = ("wish_for_solution", "tried_everything", "desperation", "unknown_cause", "unspoken")


# --- Corpus -----------------------------------------------------------------------

def load_posts(paths):
    """Posts from cache folders (any backend's search responses) and results.json files."""
    posts = {}
    for path in map(Path, paths):
        files = sorted(path.glob("*.json")) if path.is_dir() else [path]
        for f in files:
            try:
                data = json.loads(f.read_text())
            except (ValueError, OSError):
                continue
            rows = []
            if isinstance(data, dict) and isinstance(data.get("threads"), list):
                rows = data["threads"]  # a results.json
            elif isinstance(data, dict) and isinstance(data.get("data"), list):
                rows = [_post_from_listing(d) for d in data["data"] if "title" in d]
            elif isinstance(data, dict) and isinstance(data.get("data"), dict):
                rows = [_post_from_listing(c["data"]) for c in data["data"].get("children", [])
                        if c.get("kind") == "t3"]
            for p in rows:
                posts.setdefault(p["id"], p)
    # Scheduled threads and copy-pasted posts would dominate the counts.
    return analyze.drop_recurring(list(posts.values()), min_repeats=2)


def _text(p):
    return p["title"] + ". " + (p.get("body") or "")


# --- 1. Learn phrases ----------------------------------------------------------------

_CLAUSE = re.compile(r"[.,!?;:()\[\]\n\"]+")
_EDGE_JUNK = {"and", "or", "but", "the", "a", "an", "to", "of", "so", "that", "with", "in", "on", "for"}


def _ngrams(text, lo=3, hi=5):
    """Set of n-grams inside clauses, with known pain phrases cut out."""
    out = set()
    for clause in _CLAUSE.split(analyze._light(text)):
        chunk = analyze._strip_pain_phrases(analyze.normalise(clause))
        for part in chunk.split("|"):
            w = part.split()
            for n in range(lo, hi + 1):
                for i in range(len(w) - n + 1):
                    g = w[i:i + n]
                    if g[0] in _EDGE_JUNK or g[-1] in _EDGE_JUNK or any(x.isdigit() for x in g):
                        continue
                    out.add(" ".join(g))
    return out


def learn_phrases(posts, min_posts=12, min_lift=2.5, top=150, min_subs=4):
    """Phrases over-represented in strong-pain posts versus the whole corpus.

    The known library phrases are cut out before counting, so what comes back
    is new wording people use around their pain, not the phrases we seeded.
    """
    pain_df, all_df = Counter(), Counter()
    subs = defaultdict(set)
    examples = defaultdict(list)
    n_pain = 0
    for p in posts:
        text = _text(p)
        grams = _ngrams(text)
        all_df.update(grams)
        hits = analyze.pain_hits(analyze.normalise(text))
        if any(c in hits for c in STRONG):
            n_pain += 1
            pain_df.update(grams)
            for g in grams:
                subs[g].add(p["subreddit"].lower())
                if len(examples[g]) < 2:
                    examples[g].append(p)
    n_all = len(posts)
    if not n_pain:
        return []
    rows = []
    for g, k in pain_df.items():
        # Pain wording that is shared across communities, not one sub's jargon.
        if k < min_posts or len(subs[g]) < min_subs:
            continue
        lift = (k / n_pain) / ((all_df[g] + 1) / n_all)
        if lift < min_lift:
            continue
        rows.append({"phrase": g, "pain_posts": k, "all_posts": all_df[g], "subreddits": len(subs[g]),
                     "lift": round(lift, 2), "score": round(lift * math.log(k), 2)})
    rows.sort(key=lambda r: -r["score"])
    # Drop a phrase when a longer one containing it covers most of the same posts.
    kept = []
    for r in rows:
        if any(r["phrase"] in k["phrase"] and k["pain_posts"] >= 0.7 * r["pain_posts"] for k in kept):
            continue
        kept = [k for k in kept
                if not (k["phrase"] in r["phrase"] and r["pain_posts"] >= 0.7 * k["pain_posts"])]
        kept.append(r)
        if len(kept) >= top:
            break
    for r in kept:
        r["examples"] = [_snippet(p, r["phrase"]) for p in examples[r["phrase"]]]
    return kept


def _snippet(p, phrase, width=90):
    text = " ".join(analyze._light(_text(p)).split())
    norm_words = phrase.split()
    m = re.search(r"\b" + r"\W+".join(map(re.escape, norm_words)) + r"\b", text)
    if not m:
        return f"r/{p['subreddit']}: {p['title'][:width]}"
    a, b = max(0, m.start() - width // 2), m.end() + width // 2
    return f"r/{p['subreddit']}: …{text[a:b]}…"


# --- 2. Extract problems and severity ------------------------------------------------

_DET = r"(?:my |this |these |the |a |an |our |his |her |their |severe |chronic |constant |bad |terrible |awful )*"
_X = r"([a-z][a-z' -]{2,45})"
CAPTURE = {
    "how do I get rid of": rf"how (?:do|can|would|should|to) (?:i |you |we )?(?:get rid of|stop|fix|cure|treat|heal|reduce|manage|deal with|cope with|overcome|beat|prevent|handle) {_DET}{_X}",
    "struggling with __ for": rf"(?:struggl\w*|deal\w*|suffer\w*|liv\w*|battl\w*) with {_DET}{_X}? (?:for|since|ever since|my whole)",
    # Only the 1-3 words right before "won't go away" are the problem.
    "__ won't go away": r"(?:my|this|the|these|our|his|her) ((?:[a-z'-]+ ){0,2}[a-z'-]+) (?:wont|will not|doesnt|does not|never|just wont|still wont) (?:go away|stop|get better|improve|heal|clear up|leave|end)",
    "I wish there was": r"i wish (?:there was|there were|someone (?:would make|made)|i could find|someone would invent) (?:a |an |some |something |someone )?([a-z][a-z' -]{3,60})",
    "why is there no": r"why (?:is there no|isnt there a|isnt there an|arent there|doesnt anyone make|has no one made|is nobody making) ([a-z][a-z' -]{3,60})",
    "nothing helps my": rf"nothing (?:helps|works for|fixes|has helped|has fixed) {_DET}{_X}",
}
_CAPTURE_RE = {k: re.compile(v) for k, v in CAPTURE.items()}

_NUMWORDS = {"a few": 3, "few": 3, "a couple": 2, "couple": 2, "several": 5, "many": 8, "so many": 8,
             "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
             "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20, "multiple": 3,
             "countless": 10, "dozens of": 24, "a dozen": 12}
_NUM = r"(\d{1,3}|" + "|".join(sorted(map(re.escape, _NUMWORDS), key=len, reverse=True)) + r")"
_YEARS = re.compile(rf"(?:for|over|past|last|almost|nearly|about)\s+(?:the\s+)?(?:past\s+|last\s+)?{_NUM}\+?\s*(?:years|yrs)")
_MONEY = re.compile(r"(?:spent|paid|wasted|cost me|costs?|dropped|invested)[^.!?]{0,30}?\$\s?(\d[\d,]{1,7})(k?)")
_DOCTORS = re.compile(rf"{_NUM}\s+(?:different\s+)?(doctors|drs|specialists|dermatologists|derms|gastroenterologists|gis|"
                      r"urologists|neurologists|gynecologists|gyns|ents|dentists|orthodontists|therapists|psychiatrists|"
                      r"vets|physios|physical therapists|chiropractors|endocrinologists|rheumatologists|allergists)")


def _num(s):
    return int(s) if s.isdigit() else _NUMWORDS.get(s, 0)


def severity(text):
    t = analyze._light(text)
    years = max((_num(m.group(1)) for m in _YEARS.finditer(t)), default=0)
    money = max((int(m.group(1).replace(",", "")) * (1000 if m.group(2) else 1) for m in _MONEY.finditer(t)),
                default=0)
    doctors = max((_num(m.group(1)) for m in _DOCTORS.finditer(t)), default=0)
    return {"years": min(years, 60), "money": min(money, 1_000_000), "doctors": min(doctors, 50)}


# "how do I stop my dog from barking" names the problem "dog barking".
_ADJ_LEAD = re.compile(r"^(recurring|persistent|constant|chronic|severe|painful|weird|random|bad|terrible|awful|"
                       r"horrible|annoying|stubborn|frequent|daily|nightly|extreme|intense|sudden|mild)\s+")
_WHO = {"dog", "dogs", "cat", "cats", "puppy", "kitten", "baby", "toddler", "son", "daughter", "kid", "kids",
        "child", "husband", "wife", "partner", "boyfriend", "girlfriend", "neighbor", "neighbour", "neighbors",
        "landlord", "boss", "mom", "dad", "roommate", "skin", "hair", "face", "body", "brain", "mind"}
_VAGUE = {"pain", "situation", "problem", "problems", "issue", "issues", "symptoms", "condition", "thing",
          "things", "life", "feelings", "feeling", "stuff", "it", "this", "everything", "weight", "health",
          "body", "mind", "brain", "skin", "hair", "face", "dog", "cat", "baby", "kid", "kids", "son",
          "daughter", "husband", "wife", "partner", "mom", "dad", "boss", "job", "work", "money", "stress"}


def _clean_x(raw):
    words = raw.strip(" -'").split()
    if len(words) >= 3 and words[0] in _WHO and words[1] in ("from", "keeps", "constantly", "always"):
        words = [words[0]] + words[2:]
    x = analyze._ITEM_STOP.sub("", " ".join(words)).strip(" -'")
    x = analyze._ITEM_LEAD.sub("", x)
    for _ in range(3):
        x = _ADJ_LEAD.sub("", x)
    words = [w for w in x.split() if w][:4]
    while words and words[-1] in analyze.STOPWORDS:
        words.pop()
    while words and words[0] in analyze.STOPWORDS:
        words.pop(0)
    if not words or all(w in analyze.STOPWORDS for w in words):
        return None
    x = " ".join(words)
    if x in analyze._JUNK_ITEMS or x in _VAGUE:
        return None
    if len(words) == 1 and analyze.zipf_frequency and analyze.zipf_frequency(x, "en") >= 4.6:
        return None  # an everyday word on its own ("situation", "weight") names nothing
    return x


def extract_problems(posts, min_posts=3, top=200):
    """Problems named directly by people, with how long/how much/how many doctors."""
    agg = defaultdict(lambda: {"posts": set(), "patterns": Counter(), "subs": Counter(),
                               "years": [], "money": [], "doctors": [], "examples": []})
    for p in posts:
        text = _text(p)
        light = " ".join(analyze._light(text).split())
        found = {}
        for name, rx in _CAPTURE_RE.items():
            for m in rx.finditer(light):
                x = _clean_x(m.group(1))
                if x:
                    found.setdefault(x, name)
        if not found:
            continue
        sev = severity(text)
        for x, pattern in found.items():
            a = agg[x]
            if p["id"] in a["posts"]:
                continue
            a["posts"].add(p["id"])
            a["patterns"][pattern] += 1
            a["subs"][p["subreddit"]] += 1
            for k in ("years", "money", "doctors"):
                if sev[k]:
                    a[k].append(sev[k])
            if len(a["examples"]) < 3:
                a["examples"].append({"title": p["title"][:140], "subreddit": p["subreddit"],
                                      "permalink": p.get("permalink", "")})
    # Merge plural into singular ("migraines" -> "migraine") when both appear.
    for x in [k for k in agg if k.endswith("s") and k[:-1] in agg]:
        a, b = agg[x[:-1]], agg.pop(x)
        a["posts"] |= b["posts"]
        for k in ("patterns", "subs"):
            a[k].update(b[k])
        for k in ("years", "money", "doctors", "examples"):
            a[k] += b[k]
    rows = []
    for x, a in agg.items():
        n = len(a["posts"])
        if n < min_posts:
            continue
        med_years = statistics.median(a["years"]) if a["years"] else 0
        sev_score = (1 + 0.15 * min(med_years, 20)
                     + 0.5 * len(a["money"]) / n + 0.5 * len(a["doctors"]) / n)
        rows.append({
            "problem": x, "posts": n, "subreddits": len(a["subs"]),
            "top_subreddits": a["subs"].most_common(4),
            "how_they_say_it": a["patterns"].most_common(3),
            "median_years": med_years, "mention_years": len(a["years"]),
            "mention_money": len(a["money"]), "max_money": max(a["money"], default=0),
            "mention_doctors": len(a["doctors"]), "max_doctors": max(a["doctors"], default=0),
            "score": round(n * sev_score * (1 + 0.1 * min(len(a["subs"]) - 1, 5)), 1),
            "examples": a["examples"],
        })
    rows.sort(key=lambda r: -r["score"])
    return rows[:top]


# --- 3. Google autocomplete ------------------------------------------------------------

TEMPLATES = [
    "why does my {k}", "why do i have {k}", "why is my {k}", "how to get rid of {k}", "how to stop {k}",
    "how to fix {k}", "{k} won't go away", "{k} not going away", "{k} nothing works", "{k} tried everything",
    "{k} keeps coming back", "{k} worse at night", "{k} after", "{k} when", "{k} cause", "{k} caused by",
    "{k} treatment", "{k} cure", "{k} remedy", "best {k}", "{k} vs", "is {k}", "can {k}", "{k} reddit",
    "{k} in women", "{k} in men", "{k} at 30", "{k} home remedy",
]


class Autocomplete:
    URL = "https://suggestqueries.google.com/complete/search"

    def __init__(self, cache, pause=0.6, lang="en", geo="us"):
        self.cache, self.pause, self.lang, self.geo = cache, pause, lang, geo
        self.s = requests.Session()
        self._last = 0.0

    def get(self, q):
        key = json.dumps(["ac", q, self.lang, self.geo])
        hit = self.cache.get(key)
        if hit is not None:
            return hit
        wait = self.pause - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.time()
        try:
            r = self.s.get(self.URL, params={"client": "firefox", "q": q, "hl": self.lang, "gl": self.geo},
                           timeout=20)
            out = r.json()[1] if r.ok else []
        except (requests.RequestException, ValueError, IndexError):
            out = []
        self.cache.put(key, out)
        return out

    def expand(self, keyword, alphabet=True):
        """Every suggestion for the keyword under the templates (and a-z), most-suggested first."""
        seen = Counter()
        source = {}
        queries = [t.format(k=keyword) for t in TEMPLATES]
        if alphabet:
            queries += [f"{keyword} {c}" for c in "abcdefghijklmnopqrstuvwxyz"]
        for q in queries:
            for s in self.get(q):
                s = s.strip().lower()
                if s and s != q:
                    seen[s] += 1
                    source.setdefault(s, q)
        return [{"query": s, "hits": n, "from": source[s]} for s, n in seen.most_common()]


# --- Report -------------------------------------------------------------------------------

def write_mine_report(out, meta, phrases, problems):
    out.mkdir(parents=True, exist_ok=True)
    (out / "mine.json").write_text(json.dumps({"meta": meta, "phrases": phrases, "problems": problems},
                                              indent=2, default=str))
    import csv
    with open(out / "learned_phrases.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["phrase", "pain_posts", "all_posts", "lift", "score", "example_1", "example_2"])
        for r in phrases:
            w.writerow([r["phrase"], r["pain_posts"], r["all_posts"], r["lift"], r["score"],
                        *(r["examples"] + ["", ""])[:2]])
    with open(out / "named_problems.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["problem", "posts", "subreddits", "score", "median_years", "posts_mentioning_years",
                    "posts_mentioning_money", "max_money", "posts_mentioning_doctors", "max_doctors",
                    "how_they_say_it", "top_subreddits", "example"])
        for r in problems:
            w.writerow([r["problem"], r["posts"], r["subreddits"], r["score"], r["median_years"],
                        r["mention_years"], r["mention_money"], r["max_money"], r["mention_doctors"],
                        r["max_doctors"], "; ".join(f"{p} ({n})" for p, n in r["how_they_say_it"]),
                        "; ".join(f"r/{s} ({n})" for s, n in r["top_subreddits"]),
                        r["examples"][0]["permalink"] if r["examples"] else ""])

    L = ["# Keyword mining", "",
         f"{meta['posts']:,} posts · {meta['pain_posts']:,} with strong pain language · {meta['run_at']}", "",
         "## Problems people name themselves", "",
         "Pulled from sentences like *how do I get rid of ___*, *struggling with ___ for years*, "
         "*my ___ won't go away*. Severity comes from the same posts: years suffered, money spent, "
         "doctors seen.", "",
         "| # | Problem | Posts | Subs | Median years | $ mentioned | Max $ | Doctors mentioned | How they say it |",
         "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(problems[:80], 1):
        how = ", ".join(p for p, _ in r["how_they_say_it"][:2])
        L.append(f"| {i} | **{r['problem']}** | {r['posts']} | {r['subreddits']} | "
                 f"{r['median_years'] or '–'} | {r['mention_money']} | "
                 f"{('$' + format(r['max_money'], ',')) if r['max_money'] else '–'} | "
                 f"{r['mention_doctors']} | {how} |")
    L += ["", "## New pain phrases learned from the posts", "",
          "Word sequences that are much more common in painful posts than in all posts "
          "(**lift** = how many times more common). Known library phrases are cut out first, so "
          "these are new. Add the good ones to `my_phrases.txt`.", "",
          "| # | Phrase | Pain posts | Lift | Example |", "|---|---|---|---|---|"]
    for i, r in enumerate(phrases, 1):
        ex = r["examples"][0].replace("|", "\\|") if r["examples"] else ""
        L.append(f"| {i} | “{r['phrase']}” | {r['pain_posts']} | ×{r['lift']} | {ex} |")
    (out / "mine.md").write_text("\n".join(L) + "\n")
    return out
