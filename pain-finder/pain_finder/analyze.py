"""Scoring threads for pain, and grouping them into problems.

Thread score (all components are kept in the output so you can re-weight):

  post_pain     sum of category weights for each distinct pain phrase in the
                title/body (see phrases.PAIN_CATEGORIES)
  comment_pain  the same for comments, at 40% weight, capped at 30
  agreement     comments saying "same here", "following", "thought I was the
                only one" ... (other people share the problem)
  stories       comments describing their own experience
  solutions     comments claiming a fix ("what worked for me", "cured") —
                a counter-signal: lots of these means the gap is smaller
  engagement    log(upvotes) + 1.5 * log(comments)

  validation = (post_pain + comment_pain) * (1 + engagement / 10)
               + 6 * log(1 + agreement) + 4 * log(1 + stories)

Problems are found by pulling key phrases (1-3 words) out of every scored
thread and greedily picking the phrase that covers the most validation, then
removing its threads and repeating. Each problem keeps its threads, the
subreddits it spans, and the solutions people say they already tried.
"""

import math
import re
from collections import Counter, defaultdict

from .phrases import (AGREEMENT_PHRASES, PAIN_CATEGORIES, SOLUTION_CLAIM_PHRASES,
                      STORY_PHRASES, TRIED_PATTERN)

# Agreement phrases that only count when they are (nearly) the whole comment,
# since "following" or "bump" also appear in ordinary sentences.
SHORT_ONLY = {"following", "following this", "bump", "saving this", "remindme", "remind me!"}

STOPWORDS = set("""
a about above after again against ago all almost alone along already also although always am among an
and another any anybody anyone anything anyway anywhere are aren around as ask asked asking at away
back bad be became because become been before being below best better between big bit both but by
came can cannot cant could couldn couldnt day days did didn didnt different do does doesn doesnt doing
don done dont down due during each early either else end enough etc even ever every everyone everything
feel feeling feels felt few find first for found from full get gets getting give go goes going gone good
got gotten great guy guys had hadn hand happen happened happens hard has hasn have haven having he help
her here hers herself hey hi him himself his how however i id if ill im in instead into is isn isnt it
its itself ive just keep kind know known last later least less let like likely little long look looking
lot lots made make makes making many may maybe me mean means might mine more most much must my myself
need needed needs never new next no non none nor not nothing now of off often oh ok okay old on once one
ones only or other others our out over own part people per perhaps place please point pretty probably
put quite rather re real really right said same saw say says see seem seems seen several she should
shouldn since so some somehow someone something sometimes soon sort still stuff such sure take taken
takes taking tell than thank thanks that thats the their them themselves then there these they thing
things think this those though thought through time times to today together told too took toward try
tried tries trying turn two under until up upon us use used using usually very via want wanted wants was
wasn way ways we week weeks well went were weren what whatever when where whether which while who whole
whom why will with within without won wont work worked working works would wouldn wouldnt yeah year
years yes yet you youd youll your youre yours yourself youve month months anymore lately recently
literally actually basically honestly currently especially seriously totally completely constantly
super extremely advice question questions post posts reddit sub subreddit thread edit update tldr tl dr
anyone else idea ideas tips experience experiences issue issues problem problems help helps helped
struggling struggle struggles dealing deal
""".split())

try:
    from wordfreq import zipf_frequency
except ImportError:  # optional: without it only STOPWORDS filter problem names
    zipf_frequency = None

# Word commonness on the Zipf scale (7 = "the", 3 = "tinnitus"). A one-word
# problem must be rarer than UNIGRAM_MAX ("insomnia" yes, "started" no); a
# multi-word one needs at least one word rarer than PHRASE_MAX ("hair loss" yes,
# "few hours" no).
UNIGRAM_MAX = 4.7
PHRASE_MAX = 5.1

_URL = re.compile(r"https?://\S+|www\.\S+")
_NON_WORD = re.compile(r"[^a-z0-9\s'-]")
_SPLIT_ITEMS = re.compile(r",|\band\b|\bor\b|\bplus\b|/|&|\bas well as\b|\betc\b")
_ITEM_STOP = re.compile(
    r"\b(but|which|that|because|since|when|while|for|it|so|then|though|without|with no|"
    r"already|still|before|after|now|nothing|none|yet|over|multiple times|many times)\b.*$"
)
_ITEM_LEAD = re.compile(r"^(a|an|the|some|every|all|different|various|other|many|my|lots of|"
                        r"so many|several|few|couple of|bunch of|literally|also|even)\s+")
_JUNK_ITEMS = {"everything", "anything", "something", "it", "this", "that", "them", "all",
               "lots", "nothing", "things", "stuff", "everything else", "a lot", "so much",
               "many things", "every", "everything under the sun", "", "to", "one", "both"}


def _light(text):
    """Lowercase, no URLs or apostrophes, punctuation kept (for item extraction)."""
    text = (text or "").lower().replace("’", "'").replace("‘", "'")
    text = _URL.sub(" ", text).replace("'", "")  # "i've" -> "ive"; phrases get the same
    return re.sub(r"\s+", " ", text).strip()


def normalise(text):
    """_light plus punctuation removed (for phrase matching)."""
    return re.sub(r"\s+", " ", _NON_WORD.sub(" ", _light(text))).strip()


def _compile(phrases):
    alts = sorted({normalise(p) for p in phrases}, key=len, reverse=True)
    return re.compile(r"\b(" + "|".join(re.escape(a) for a in alts) + r")\b")


_CATEGORY_RE = {name: _compile(c["phrases"]) for name, c in PAIN_CATEGORIES.items()}
_WEIGHTS = {name: c["weight"] for name, c in PAIN_CATEGORIES.items()}
_AGREE_RE = _compile(AGREEMENT_PHRASES)
_STORY_RE = _compile(STORY_PHRASES)
_SOLUTION_RE = _compile(SOLUTION_CLAIM_PHRASES)
_TRIED_RE = re.compile(TRIED_PATTERN.replace("'", ""))  # text has apostrophes stripped
_SHORT_ONLY = {normalise(p) for p in SHORT_ONLY}


def pain_hits(norm_text):
    """{category: set(matched phrases)} for normalised text."""
    hits = {}
    for name, rx in _CATEGORY_RE.items():
        found = set(rx.findall(norm_text))
        if found:
            hits[name] = found
    return hits


def _pain_value(hits):
    return sum(_WEIGHTS[c] * len(p) for c, p in hits.items())


def _is_agreement(norm_comment):
    for m in _AGREE_RE.findall(norm_comment):
        if m not in _SHORT_ONLY or len(norm_comment) < 80:
            return True
    return False


def extract_tried(text):
    """Things people say they tried: "I've tried melatonin, magnesium and CBD"."""
    items = []
    for m in _TRIED_RE.finditer(_light(text)):
        for raw in _SPLIT_ITEMS.split(m.group(1)):
            item = _ITEM_STOP.sub("", raw.strip()).strip()
            item = _ITEM_LEAD.sub("", item).strip(" -\"*")
            words = item.split()
            if not words or item in _JUNK_ITEMS or len(words) > 4:
                continue
            if all(w in STOPWORDS for w in words):
                continue
            items.append(item)
    return items


def score_thread(post, comments):
    title_body = normalise(post["title"] + " " + post["body"])
    post_hits = pain_hits(title_body)

    comment_hits = defaultdict(set)
    comment_pain = 0.0
    agreement = stories = solutions = 0
    tried = Counter(extract_tried(post["title"] + ". " + post["body"]))
    agree_examples, story_examples = [], []
    for c in comments:
        nb = normalise(c["body"])
        h = pain_hits(nb)
        for cat, ps in h.items():
            comment_hits[cat] |= ps
        comment_pain += 0.4 * _pain_value(h)
        if _is_agreement(nb):
            agreement += 1
            if len(agree_examples) < 3 and 15 < len(c["body"]) < 300:
                agree_examples.append(c["body"].strip())
        if _STORY_RE.search(nb):
            stories += 1
            if len(story_examples) < 3 and 80 < len(c["body"]) < 600:
                story_examples.append(c["body"].strip())
        if _SOLUTION_RE.search(nb):
            solutions += 1
        tried.update(extract_tried(c["body"]))
    comment_pain = min(comment_pain, 30.0)

    post_pain = _pain_value(post_hits)
    engagement = math.log1p(max(post["score"], 0)) + 1.5 * math.log1p(post["num_comments"])
    validation = ((post_pain + comment_pain) * (1 + engagement / 10)
                  + 6 * math.log1p(agreement) + 4 * math.log1p(stories))

    gap_hits = sum(len(post_hits.get(c, ())) + len(comment_hits.get(c, ()))
                   for c in ("wish_for_solution", "tried_everything", "unknown_cause"))
    return {
        **post,
        "post_pain": round(post_pain, 2),
        "comment_pain": round(comment_pain, 2),
        "agreement": agreement,
        "stories": stories,
        "solutions": solutions,
        "engagement": round(engagement, 2),
        "validation": round(validation, 2),
        "gap_signal": round(gap_hits / (1 + solutions), 2),
        "categories": sorted(set(post_hits) | set(comment_hits)),
        "matched_phrases": sorted({p for ps in post_hits.values() for p in ps}),
        "tried": tried.most_common(15),
        "comments_analyzed": len(comments),
        "agree_examples": agree_examples,
        "story_examples": story_examples,
    }


# --- Grouping into problems ----------------------------------------------------------

def _strip_pain_phrases(norm_text):
    for rx in list(_CATEGORY_RE.values()) + [_AGREE_RE, _STORY_RE, _SOLUTION_RE]:
        norm_text = rx.sub(" | ", norm_text)
    return norm_text


_CLAUSE = re.compile(r"[.,!?;:()\[\]\n\"]+")


def _keyphrases(text):
    """Set of 1-3 word phrases with no stopwords, not crossing punctuation or pain phrases."""
    out = set()
    clauses = (normalise(c) for c in _CLAUSE.split(_light(text)))
    for chunk in _strip_pain_phrases(" | ".join(clauses)).split("|"):
        words = [w.strip("-") for w in chunk.split()]
        run = []
        for w in words + [""]:
            if w and w not in STOPWORDS and len(w) > 2 and not w.isdigit():
                run.append(w)
                continue
            for n in (1, 2, 3):
                for i in range(len(run) - n + 1):
                    out.add(" ".join(run[i:i + n]))
            run = []
    return out


_zipf_cache = {}


def _specific(phrase):
    """True if a key phrase names something specific rather than everyday words."""
    if zipf_frequency is None:
        return True
    zs = []
    for w in phrase.split():
        if w not in _zipf_cache:
            _zipf_cache[w] = zipf_frequency(w, "en")
        zs.append(_zipf_cache[w])
    if len(zs) == 1:
        return zs[0] < UNIGRAM_MAX
    return min(zs) < PHRASE_MAX


def cluster_problems(threads, max_problems=25, min_threads=2, ignore=()):
    """Greedy keyphrase cover. Returns problems sorted by total validation."""
    ignore = {normalise(i) for i in ignore}
    phrase_threads = defaultdict(set)
    for idx, t in enumerate(threads):
        text = t["title"] + ". " + t["body"][:2000]
        for kp in _keyphrases(text):
            if kp not in ignore:
                phrase_threads[kp].add(idx)

    n = max(len(threads), 1)
    # Phrases in more than a third of all threads are too generic to be a problem.
    candidates = {kp: ids for kp, ids in phrase_threads.items()
                  if len(ids) >= min_threads and len(ids) / n <= 0.34 and _specific(kp)}
    remaining = set(range(len(threads)))
    problems = []
    while candidates and len(problems) < max_problems:
        def value(item):
            kp, ids = item
            live = ids & remaining
            if len(live) < min_threads:
                return 0.0
            subs = len({threads[i]["subreddit"].lower() for i in live})
            length_bonus = {1: 1.0, 2: 1.4, 3: 1.6}[len(kp.split())]
            return (sum(threads[i]["validation"] for i in live) * length_bonus
                    * (1 + 0.15 * min(subs - 1, 5)))
        best, best_ids = max(candidates.items(), key=value)
        if value((best, best_ids)) <= 0:
            break
        live = sorted(best_ids & remaining, key=lambda i: -threads[i]["validation"])
        remaining -= set(live)
        del candidates[best]
        problems.append(_summarise(best, [threads[i] for i in live]))
    problems.sort(key=lambda p: -p["reddit_score"])
    return problems


def _summarise(keyphrase, members):
    tried = Counter()
    cats = Counter()
    for t in members:
        tried.update(dict(t["tried"]))
        cats.update(t["categories"])
    subs = Counter(t["subreddit"] for t in members)
    total_validation = sum(t["validation"] for t in members)
    return {
        "problem": keyphrase,
        "threads": len(members),
        "subreddits": subs.most_common(8),
        "reddit_score": round(total_validation * (1 + 0.1 * (len(subs) - 1)), 1),
        "total_upvotes": sum(max(t["score"], 0) for t in members),
        "total_comments": sum(t["num_comments"] for t in members),
        "agreement": sum(t["agreement"] for t in members),
        "stories": sum(t["stories"] for t in members),
        "solution_claims": sum(t["solutions"] for t in members),
        "gap_signal": round(sum(t["gap_signal"] for t in members) / len(members), 2),
        "pain_categories": cats.most_common(),
        "already_tried": tried.most_common(15),
        "top_threads": members[:8],
    }
