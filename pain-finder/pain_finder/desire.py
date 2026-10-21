"""What people want back: desires sorted by the same depth levels as pain.

  L2 body     "walk without pain", "sleep through the night"
  L3 life     "play with my kids again", "go out without worrying", "my social life back"
  L4 identity "feel like myself again", "be the mom I want to be", "stop hiding", "be normal"

Desires are pulled from sentences like "I just want to ___", "all I want is ___",
"I wish I could ___", "I'd give anything to ___", "I want my ___ back",
"I miss being able to ___", "I dream of ___". Each one is given a level and a
theme ("feel normal / like myself", "do things with my kids", ...). Crisis
sentences are skipped, as in depth.py.
"""

import re
from collections import Counter, defaultdict

from .depth import CRISIS, _norm, sentences

_ROLE = r"(?:mom|mother|mum|dad|father|parent|wife|husband|partner|girlfriend|boyfriend|friend|person|woman|man)"

FRAMES = {
    "I just want to ___": r"\bi (?:just |really |so badly |desperately |honestly |only |simply )?(?:want|wanna|need) "
                          r"to ((?:be able to )?(?:feel|be|have|go|live|enjoy|play|run|wear|eat|sleep|date|travel|work|"
                          r"look|stop|hold|walk|dance|swim|hike|keep up|leave|socialize|smile|laugh|love|get back|"
                          r"get my|fit|move|breathe|function|exist|lift|carry|chase|keep|wake|sit|stand|kiss|hug|"
                          r"cuddle|make it|finish|start|go back|not)[a-z' ]{2,80})",
    "all I want is ___": r"\ball i (?:want|need|ask for|wish for) is (?:to |for )?([a-z' ]{3,80})",
    "I want my ___ back": r"\bi (?:just )?want (my [a-z' ]{3,40} back)\b",
    "I wish I could ___": r"\bi (?:just |really )?wish i (?:could|was able to|were able to) (?:just )?([a-z' ]{3,80})",
    "I'd give anything to ___": r"\b(?:i would|id|i'd) give (?:anything|everything|my left arm|so much) "
                                r"(?:to|for|just to) ([a-z' ]{3,80})",
    "I miss being able to ___": r"\bi miss (?:being able to |feeling |being |the days when i could |when i could )"
                                r"([a-z' ]{3,80})",
    "I dream of ___": r"\bi (?:dream|dream about|dream of|fantasi[sz]e about|long to|long for|ache to|yearn to|"
                      r"yearn for) ([a-z' ]{3,80})",
    "one day I want to ___": r"\b(?:one day|someday|some day|eventually) i (?:want|hope|would love|wanna) to "
                             r"([a-z' ]{3,80})",
    "I want to be the ___ who": rf"\bi (?:want|wanted|need) to be (?:the (?:kind of |type of )?{_ROLE}|someone|a "
                                rf"{_ROLE}) (?:who|that) ([a-z' ]{{3,80}})",
    "if only I could ___": r"\bif only i (?:could|was able to|didnt have to) ([a-z' ]{3,80})",
}
_FRAMES = {k: re.compile(v) for k, v in FRAMES.items()}

# Theme rules: (level, theme, pattern on the completion). First match wins, so
# the deeper (identity) themes are listed first.
THEMES = [
    (4, "feel normal / like myself again", r"\b(?:feel|be|look) (?:normal|like (?:myself|me|a normal|a person|a "
                                           r"human|the old me|i used to)|myself|human|whole|like everyone else)\b"
                                           r"|\bthe old me\b|\bmyself again\b|\bnormal again\b"),
    (4, "confidence / feel attractive", r"\b(?:confident|confidence|attractive|beautiful|pretty|sexy|desirable|"
                                        r"comfortable in my (?:own )?(?:skin|body)|good about myself|look in the "
                                        r"mirror|like what i see|love my body|proud of (?:myself|my body))\b"),
    (4, "be a good parent / partner", rf"\b(?:the {_ROLE}|a good {_ROLE}|a better {_ROLE}|a present|the kind of "
                                      r"(?:mom|dad|parent)|there for (?:my|them|him|her)|make (?:them|him|her|my "
                                      r"\w+) proud|not (?:be )?a burden)\b"),
    (4, "be seen / believed / not judged", r"\b(?:believed|taken seriously|understood|seen|heard|accepted|not "
                                           r"(?:be )?judged|without (?:being )?judged|fit in|belong|be liked|be "
                                           r"wanted|be noticed|matter)\b"),
    (4, "stop hiding / no shame", r"\b(?:stop|not have to|without) (?:hiding|hide|being (?:embarrassed|ashamed|"
                                  r"self conscious)|worrying (?:what|about what|if people)|pretending|covering|"
                                  r"apologi[sz]ing|making excuses)\b|\bnot (?:be|feel) (?:embarrassed|ashamed|gross|"
                                  r"disgusting|self conscious)\b"),
    (4, "be loved / not alone", r"\b(?:loved|lovable|loveable|love and be loved|someone to love|find (?:love|"
                                r"someone|a partner|the one)|not (?:be|feel) (?:alone|lonely)|stop being (?:alone|"
                                r"lonely)|be held|a relationship|be cared for|closer to (?:my|him|her)|(?:his|her|"
                                r"their) touch|be wanted|be desired|be chosen)\b"),
    (4, "connect / make friends / be social", r"\b(?:make friends|have friends|real friends|be (?:more )?social|"
                                              r"talk to (?:people|strangers|anyone)|be approachable|connect with|"
                                              r"fit in|belong|be part of|people to talk to|a friend)\b"),
    (4, "feel happy / at peace / free", r"\b(?:happy|happiness|at peace|peace of mind|(?:be|feel|live) free|"
                                        r"freedom|calm|safe|enjoy (?:life|my life|living)|joy|feel alive|alive "
                                        r"again|hope\w*)\b"),
    (4, "be independent / capable", r"\b(?:independent|independence|take care of myself|on my own|capable|"
                                    r"useful|productive|my own money|support myself|not (?:rely|depend|lean))\b"),
    (3, "do things with my kids / family", r"\b(?:my kids|my children|my son|my daughter|my baby|my family|my "
                                           r"grandkids|my toddler|my boys|my girls)\b"),
    (3, "intimacy / sex life", r"\b(?:sex|intimate|intimacy|make love|sex life|kiss|cuddle)\b"),
    (3, "go out / social life / travel", r"\b(?:go out|going out|go outside|leave (?:the|this|my) house|social "
                                         r"life|socialize|see my friends|hang out|travel|vacation|a trip|"
                                         r"concerts|restaurants|go on dates|start dating|date again|go places|"
                                         r"go to the (?:beach|park|pool|gym|store|grocery store|movies)|go to "
                                         r"(?:parties|weddings|events))\b"),
    (3, "work / career / school", r"\b(?:(?:go back to|return to|keep|hold down|keep my|get a|find a|start a|"
                                  r"stay at|show up to|focus at) (?:work|job|career|business)|my (?:job|career)|"
                                  r"work (?:again|full time|normally)|finish (?:my )?(?:degree|school|studies)|"
                                  r"go back to school|get promoted|a promotion|start a business)\b"),
    (3, "active life / sport / hobbies", r"\b(?:go (?:running|hiking|swimming|dancing|climbing|biking|"
                                         r"skiing|surfing)|(?:run|hike|swim|dance|work out|exercise|lift|cycle|"
                                         r"play (?:sports|soccer|basketball|tennis|golf|with)) (?:again|without|"
                                         r"like i used|every|normally|pain)|get back (?:to|into) (?:the gym|"
                                         r"running|lifting|sports|my hobbies)|enjoy my hobbies|my hobbies)\b"),
    (3, "eat / wear what I want", r"\b(?:eat (?:what|normally|out|anything|without|like a normal|food i "
                                  r"love)|wear (?:what|shorts|tank|a dress|dresses|clothes|short sleeves|sandals|"
                                  r"anything|a swimsuit|a bikini|shoes)|dress (?:the way|how) i want|buy clothes)\b"),
    (3, "my life back", r"\b(?:my life back|a normal life|live (?:my life|normally|a normal)|get on with my life|"
                        r"move on with my life|my old life|live (?:my|a) life)\b"),
    (2, "sleep", r"\b(?:sleep|rest|wake up|fall asleep|stay asleep)\b"),
    (2, "no pain / body works", r"\b(?:without (?:pain|hurting)|pain free|stop (?:hurting|itching|sweating|"
                                r"smelling|bleeding|burning|aching|ringing|the pain|the blurring)|breathe|(?:walk|"
                                r"bend|sit|stand|move|see|hear) (?:without|again|normally|properly|for more than)|"
                                r"be cured|get cured|heal|get better|be healthy|feel better|lose (?:the )?weight|"
                                r"keep my hair|reverse|clear skin|my skin)\b"),
]
_THEMES = [(lv, name, re.compile(rx)) for lv, name, rx in THEMES]
_CUT = re.compile(r"\b(?:but|because|cause|so that i can t|which|since|although|though|however|and then|lol|"
                  r"haha|edit|any advice|anyone|does anyone|is that|is it)\b")
_TRAIL = {"and", "or", "but", "the", "a", "an", "to", "of", "so", "that", "with", "in", "on", "for", "is", "it",
          "i", "my", "me", "im", "was", "are", "be", "just", "really", "like"}


def _clip(x, max_words=12):
    x = _CUT.split(x)[0]
    w = x.split()[:max_words]
    while w and w[-1] in _TRAIL:
        w.pop()
    return " ".join(w) if len(w) >= 2 else None


def classify(completion):
    for lv, name, rx in _THEMES:
        if rx.search(completion):
            return lv, name
    return 0, None


def desires_in(text):
    """[{frame, want, level, theme, sentence}] for one post."""
    out = []
    for s in sentences(text):
        n = _norm(s)
        if CRISIS.search(n):
            return []  # never surface anything from a crisis post
        for frame, rx in _FRAMES.items():
            for m in rx.finditer(n):
                want = _clip(m.group(1))
                if not want:
                    continue
                lv, theme = classify(want)
                if theme:
                    out.append({"frame": frame, "want": want, "level": lv, "theme": theme,
                                "sentence": " ".join(s.split())[:300]})
    return out


def analyse(posts, problems=None):
    by_id = {}
    themes = Counter()
    theme_posts = defaultdict(set)
    theme_subs = defaultdict(set)
    wants = defaultdict(Counter)
    quotes = defaultdict(list)
    levels = Counter()
    frames = Counter()
    for p in posts:
        ds = desires_in(p["title"] + ". " + (p.get("body") or ""))
        by_id[p["id"]] = ds
        seen = set()
        for d in ds:
            frames[d["frame"]] += 1
            wants[d["theme"]][d["want"]] += 1
            if d["theme"] in seen:
                continue
            seen.add(d["theme"])
            themes[d["theme"]] += 1
            levels[d["level"]] += 1
            theme_posts[d["theme"]].add(p["id"])
            theme_subs[d["theme"]].add(p["subreddit"])
            if len(quotes[d["theme"]]) < 400:
                quotes[d["theme"]].append({**d, "subreddit": p["subreddit"], "score": p.get("score", 0),
                                           "permalink": p.get("permalink", ""), "title": p["title"][:120]})
    theme_level = {name: lv for lv, name, _ in THEMES}
    theme_rows = [{"theme": t, "level": theme_level[t], "posts": n, "subreddits": len(theme_subs[t]),
                   "top_wants": wants[t].most_common(15),
                   "quotes": sorted(quotes[t], key=lambda q: -q["score"])[:8]}
                  for t, n in themes.most_common()]

    problem_rows = []
    for prob in problems or []:
        ds = [d for i in prob["thread_ids"] for d in by_id.get(i, [])]
        threads = [i for i in prob["thread_ids"] if i in by_id]
        if not threads:
            continue
        with_l34 = sum(1 for i in threads if any(d["level"] >= 3 for d in by_id[i]))
        t = Counter(d["theme"] for d in ds if d["level"] >= 3)
        qs = sorted((d for d in ds if d["level"] >= 3), key=lambda d: -d["level"])
        problem_rows.append({"problem": prob["problem"], "threads": len(threads),
                             "l34_desire_share": round(with_l34 / len(threads), 2),
                             "themes": t.most_common(5), "wants": [d["want"] for d in qs][:10],
                             "quotes": [d["sentence"] for d in qs][:5]})
    problem_rows.sort(key=lambda r: -(r["l34_desire_share"] * r["threads"] ** 0.5))
    return {"posts": len(posts), "levels": dict(levels), "frames": frames.most_common(),
            "themes": theme_rows, "problems": problem_rows}


def write_report(out, res, meta):
    import csv
    import json
    out.mkdir(parents=True, exist_ok=True)
    (out / "desires.json").write_text(json.dumps({"meta": meta, **res}, indent=2, default=str))
    with open(out / "desires.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["level", "theme", "what_they_want", "sentence", "subreddit", "upvotes", "link"])
        for r in res["themes"]:
            for q in r["quotes"]:
                w.writerow([q["level"], q["theme"], q["want"], q["sentence"], q["subreddit"], q["score"],
                            q["permalink"]])
    with open(out / "desire_keywords.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["level", "theme", "wording", "count"])
        for r in res["themes"]:
            for want, n in r["top_wants"]:
                w.writerow([r["level"], r["theme"], want, n])

    lv = res["levels"]
    L = ["# What they want back: Level 3–4 desires", "",
         f"{res['posts']:,} posts · {meta['run_at']} · desires found: "
         f"L4 identity {lv.get(4, 0):,} · L3 life {lv.get(3, 0):,} · L2 body {lv.get(2, 0):,}", "",
         "Pulled from *I just want to ___*, *all I want is ___*, *I wish I could ___*, *I'd give anything "
         "to ___*, *I want my ___ back*, *I miss being able to ___*, *I dream of ___*.", ""]
    for level, title in ((4, "Level 4: who they want to be again"), (3, "Level 3: the life they want back"),
                         (2, "Level 2: what they want their body to do")):
        rows = [r for r in res["themes"] if r["level"] == level]
        if not rows:
            continue
        L += [f"## {title}", ""]
        for r in rows:
            L.append(f"### {r['theme']} · {r['posts']} posts · {r['subreddits']} communities")
            L.append("")
            L.append("Wording: " + ", ".join(f"“{w}”" + (f" ({n})" if n > 1 else "")
                                             for w, n in r["top_wants"][:10]))
            L.append("")
            L += [f"> {q['sentence']}  \n> — r/{q['subreddit']}\n" for q in r["quotes"][:4]]
    if res["problems"]:
        L += ["## Desires by problem", "",
              "| Problem | Threads | Express L3–4 desire | Main desires |", "|---|---|---|---|"]
        for r in res["problems"]:
            L.append(f"| **{r['problem']}** | {r['threads']} | {r['l34_desire_share']:.0%} | "
                     + ", ".join(f"{t} ({n})" for t, n in r["themes"][:3]) + " |")
        for r in res["problems"]:
            if r["quotes"]:
                L += ["", f"### {r['problem']}: what they want", ""]
                L += [f"> {q}\n" for q in r["quotes"][:4]]
    (out / "desires.md").write_text("\n".join(L) + "\n")
    return out
