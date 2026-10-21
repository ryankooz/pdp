"""How deep a pain goes: four levels, matched sentence by sentence.

  L1 surface      the symptom              "my back hurts"
  L2 physical     what the body can't do   "I can't bend over anymore"
  L3 life         what it takes from life  "I can't run with my kids anymore"
  L4 identity     what that means about    "...I'm missing their childhood, they see me
                  who they are                as the lame mom while the other parents run"

L4 is split into the forms it takes: missing out, how others see me, comparison,
failing a role, identity loss, relationships at risk, shame and hiding,
self-worth, future dread. Text is lowercased with apostrophes removed before
matching, so patterns are written as "cant", "im", "dont".

Sentences about self-harm or suicide are flagged as crisis and excluded from
everything this module outputs: those people need help, not marketing.
"""

import re

_PEOPLE = (r"(?:kids?|children|childrens|son|sons|daughter|daughters|baby|babies|toddler|family|husband|wife|"
           r"partner|boyfriend|girlfriend|bf|gf|fiance|fiancee|friends?|parents?|mom|dad|grandkids|"
           r"grandchildren|coworkers|team|students|patients|dog|dogs)")
_ROLE = (r"(?:mom|mother|mum|dad|father|parent|wife|husband|partner|girlfriend|boyfriend|friend|daughter|son|"
         r"sister|brother|employee|teacher|nurse|boss|coworker|owner|man|woman|person|human|adult)")
_NEG = r"(?:cant|cannot|can no longer|can barely|couldnt|unable to|no longer|dont|never)"

CRISIS = re.compile(r"\b(?:kill myself|killing myself|suicid\w*|end it all|end my life|want to die|wanna die|"
                    r"unalive|self harm|self-harm|cutting myself|dont want to (?:be here|live|exist)|"
                    r"better off dead|not want to live|take my (?:own )?life)\b")

L2 = {
    "can't do with my body": rf"\b(?:{_NEG}|struggle to|hard to|difficult to|painful to|hurts to|impossible to) "
                             r"(?:bend|walk|stand|sit|lift|sleep|eat|breathe|swallow|focus|concentrate|think "
                             r"straight|move|turn my|raise my|grip|open my|chew|talk|speak|hear|see|read|type|"
                             r"climb|kneel|squat|get up|get out of bed|fall asleep|stay asleep|wake up|pee|poop|"
                             r"go to the bathroom|function|exercise|run|hold (?:anything|things|my))\b",
    "it wakes me / takes hours": r"\b(?:wakes|woke|waking|keeps) me (?:up|awake)\b|\b(?:takes|took) me "
                                 r"(?:hours|forever|all day|\d+ (?:hours|minutes))\b|\bbarely (?:walk|sleep|eat|"
                                 r"function|move|stand|get out of bed)\b",
}

L3 = {
    "can't do it with people": rf"\b{_NEG}[a-z ]{{0,30}}\bwith my {_PEOPLE}\b",
    "had to quit / give up": r"\b(?:had to|forced to|going to have to) (?:quit|leave|stop|give up|drop out|cancel|"
                             r"take (?:leave|time off)|go part time|move back)\b|\b(?:gave up|giving up|quit|stopped) "
                             r"(?:on )?(?:my )?(?:job|career|hobby|hobbies|sport|running|the gym|dancing|school|"
                             r"college|degree|dream|travel(?:ing)?)\b",
    "ruining job / relationship": r"\b(?:affect|affects|affecting|ruin|ruins|ruining|ruined|destroying|hurting|"
                                  r"impacting|costing me|cost me|killing) (?:my )?(?:job|career|work|relationship|"
                                  r"marriage|social life|sex life|love life|friendships?|grades|studies|business|"
                                  r"family|confidence|life)\b",
    "missing work / events": r"\b(?:missed|miss|missing|skip|skipped|skipping|called in|calling in|call in sick) "
                             r"(?:work|school|class(?:es)?|events?|weddings?|parties|birthdays?|holidays|shifts?|"
                             r"days of work|so much work|family events|vacations?)\b",
    "avoiding life": r"\b(?:avoid|avoiding|cant go to|dont go to|stopped going to|scared to go to|never go to) "
                     r"(?:social|parties|events|restaurants|the gym|the beach|the pool|pools|dates|dating|public|"
                     r"crowds|work|school|church|friends|family|stores|the store|people)\b|\b(?:cant|dont|never) "
                     r"(?:leave|go out of) (?:the|my) house\b",
    "can't enjoy": r"\b(?:cant|cannot|dont|no longer) (?:enjoy|have fun|relax|be present|travel|date|have sex|"
                   r"be intimate)\b",
    "intimacy": r"\b(?:sex|intimacy|intimate)\b[a-z ]{0,30}\b(?:painful|impossible|avoid|cant|stopped|ruined|"
                r"hurts|scared)\b",
}

_GROUP = (r"(?:moms|mums|dads|parents|people|women|men|girls|guys|kids|couples|families|students|nurses|"
          r"wives|husbands|friends|coworkers|teens|adults)")
_TRAIT = (r"(?:so |really |very |such a |a |an |the |pretty |super )?(?:happy|fun|confident|outgoing|active|social|"
          r"energetic|strong|healthy|fit|independent|someone|the kind|the type|able|person|girl|guy|athlete|"
          r"runner|life of|carefree|bubbly|funny|smart|sharp|motivated|driven|beautiful|pretty|attractive|"
          r"care ?free|adventurous|productive|hard working|reliable|present|patient|loving|good at|known)")
L4 = {
    "missing out": r"\b(?:im|i am|i feel like im|i keep|ive been|i have been|i|ive|i feel like i)(?: \w+)? "
                   r"(?:missing|missed|miss) out\b|\bmissing (?:out on )?(?:my |their |his |her )(?:kids|"
                   r"childrens|sons|daughters|childhood|grandkids|life|twenties|20s|youth|wedding|best years|"
                   r"first|milestones)\b|\b(?:i |ive )?(?:wasted|lost|losing|wasting|throwing away) (?:my |the "
                   r"best )?(?:best years|twenties|20s|thirties|30s|youth|prime|years of my life|whole life)\b"
                   r"|\blife (?:is )?(?:passing|going) me by\b|\bon the sidelines\b|\b(?:never|cant|cannot|wont|"
                   r"ill never) get (?:those|these|that|the) (?:years|time|moments|days) back\b"
                   r"|\bwatch(?:ing)? (?:everyone|my friends|everybody|life) (?:else )?(?:live|go on|have fun|move "
                   r"on|grow up|pass)\b",
    "how others see me": r"\b(?:they|he|she|people|everyone|everybody|my \w+) (?:just |only |all |always |now |"
                         r"probably |still )?(?:see|sees|look at|looks at|think of|thinks of|treat|treats|view|"
                         r"views) me (?:as|like)\b|\b(?:people|everyone|they|others|my \w+) (?:probably |must |all "
                         r"|just )?(?:think|thinks|assume|assumes) (?:im|i am) (?:a |an |just |so |too )?(?:lazy|"
                         r"crazy|weird|gross|dirty|faking|making it up|exaggerating|dramatic|rude|stupid|dumb|"
                         r"boring|fat|ugly|disgusting|unhygienic|a joke|a loser|a failure|useless|pathetic|"
                         r"attention seeking|anti ?social|stuck up|drunk|high|on drugs)\b|\b(?:i |feel |felt |"
                         r"being |get |getting )judged\b|\b(?:people|everyone|they) (?:are |were |keep |always )?"
                         r"(?:stare|staring|stared|look|looking) at me\b|\bthe way (?:people|they|he|she|everyone) "
                         r"(?:look|looks|looked) at me\b|\bwhat (?:people|others|everyone) (?:think|will think|must "
                         r"think) of me\b|\b(?:im|i am|i was|im always|being) the (?:lame|weird|sick|fat|gross|"
                         r"smelly|lazy|boring|broken|crazy|annoying|flaky|unreliable|quiet|awkward|ugly|useless)\b"
                         r"|\b(?:im|i am|i was|i feel like im) the only (?:one|person|mom|dad|girl|guy|woman|man)"
                         r"(?: \w+){0,4} (?:who|that) (?:cant|can not|doesnt|isnt|wasnt|didnt|has to|struggles|"
                         r"deals|still|never|has|is)\b|\bthe only one (?:my age|in my (?:family|friend group|class|"
                         r"office|group)|left|without)\b",
    "comparison": rf"\b(?:(?:the |all the )?other|normal|regular) {_GROUP}(?: \w+){{0,3}} (?:can|get to|are able|"
                  r"dont have to|seem to|have no (?:problem|trouble|issue)|run|play|enjoy|are enjoying|get married|"
                  r"are married|have kids|are having|are living|go out|have fun|are getting)\b"
                  r"|\bwhile (?:everyone|everybody|my friends|other people|they all|all of them|(?:the |all the )?"
                  rf"other {_GROUP}|others) (?:else )?(?:can|get to|are|is|have|has|enjoy|seem|go|run|play|move|"
                  r"live|get)\b|\beveryone else (?:my age )?(?:gets|can|seems|gets to|is (?:able|happy|enjoying|"
                  r"living|moving|getting|having|married|out))\b|\b(?:people|everyone|friends|girls|guys|women|"
                  r"men) my age (?:are|have|can|get|seem|go|do)\b|\bunlike (?:other|everyone|most|normal) "
                  rf"(?:{_GROUP}|people)\b|\bcompared to (?:other|everyone|my friends|normal|most) (?:{_GROUP}|"
                  r"people)\b|\ball my friends (?:are|have|can) (?:married|engaged|buying|moving|having|getting|"
                  r"traveling|travelling|out|able|enjoying|living|dating|doing)\b",
    "failing a role": rf"\b(?:im|i am|i feel like|feel like|i was|being) (?:a |such a |the )?(?:bad|terrible|"
                      rf"horrible|awful|shitty|crappy|useless|failure of a|worse|worst|lazy) {_ROLE}\b"
                      rf"|\b(?:failing|let(?:ting)? down|disappointing) (?:my |our )?{_PEOPLE}\b"
                      r"|\b(?:im|i am|feel like|being|become|becoming|turned into) (?:such |just |a huge |nothing "
                      r"but )?a burden\b"
                      rf"|\b(?:they|he|she|my {_PEOPLE}) deserves? (?:better|more|a better)\b"
                      rf"|\b(?:cant|not) be the {_ROLE}\b|\bthe {_ROLE} i (?:want|wanted|used|should|need) to be\b"
                      r"|\bless of a (?:man|woman|mom|dad|person|wife|husband)\b|\bnot a real (?:man|woman|mom|dad)\b",
    "identity loss": rf"\bi used to be {_TRAIT}|\bnot (?:the same|myself) (?:person )?(?:anymore|again)\b|\bnot "
                     r"the same person\b|\bi (?:dont|do not|no longer) recogni[sz]e (?:myself|who i am|the person)\b"
                     r"|\b(?:shell|shadow|fraction) of (?:myself|my self|who i|the person|my former)\b|\b(?:lost|"
                     r"losing) (?:myself|my identity|who i (?:am|was)|my sense of self|my independence|my spark|my "
                     r"personality)\b|\bthe (?:old|real) me\b|\bwho i used to be\b|\bi miss (?:the old me|who i "
                     r"was|being able to|my old life|being normal|feeling normal|being me)\b",
    "relationship at risk": r"\b(?:hes|shes|he is|she is|theyre|my \w+ is) (?:getting )?(?:tired|sick|fed up) of "
                            r"(?:me|it|my|dealing)\b|\b(?:afraid|scared|worried|terrified) (?:that )?(?:hell|shell|"
                            r"he will|she will|they will|my \w+ will|hes going to|shes going to) (?:leave|cheat|give "
                            r"up|get tired|find someone)\b|\b(?:no one|nobody|no man|no woman|no guy|no girl) "
                            r"(?:will|would|is going to) (?:ever )?(?:want|love|date|marry) (?:me|someone like me)\b"
                            r"|\b(?:ill|i will|im going to) never (?:find|have|get) (?:someone|a partner|a "
                            r"relationship|love|a boyfriend|a girlfriend|married)\b|\b(?:stopped|stop|dont) "
                            r"(?:inviting|asking|calling|texting) me\b|\bi (?:keep |always |have to )?(?:cancel|bail)"
                            r"(?:ling|ing)? (?:on )?(?:plans|people|friends|dates)\b",
    "shame and hiding": r"\b(?:hide|hiding|hid) (?:it|this) from\b|\bhid(?:e|ing) my (?:face|body|arms|legs|"
                        r"hands|feet|skin|hair|teeth|smile|stomach|belly|scars)\b|\b(?:pretend|pretending) "
                        r"(?:to be (?:ok|okay|fine|normal|happy)|im (?:ok|okay|fine)|everything is)\b|\bfake "
                        r"(?:smile|a smile|being (?:ok|okay|happy|fine))\b|\bi (?:make|keep making|always make|"
                        r"made) excuses\b|\b(?:no one|nobody) knows (?:that i|about my|how (?:bad|much))\b"
                        r"|\b(?:i|im|i am|i feel|i felt|i look|i smell) (?:so |really |absolutely |just )?"
                        r"(?:disgusting|gross|repulsive|hideous|humiliated|mortified)\b|\bdisgusted (?:with|by) "
                        r"myself\b|\bhate (?:how i look|my body|looking in the mirror|the way i look)\b|\b(?:avoid|"
                        r"cant look at|hate) (?:mirrors|the mirror|photos of me|pictures of me|cameras)\b|\b(?:too|"
                        r"so) (?:ashamed|embarrassed) to\b",
    "self-worth": r"\b(?:i |i just |makes me |made me )feel (?:so |completely |really )?(?:worthless|useless|"
                  r"pathetic|broken|defective|like a failure|like garbage|like a loser|unlovable|less than|like a "
                  r"freak|like a joke|inadequate|like a burden)\b|\bi hate myself\b|\bwhat kind of (?:mom|dad|"
                  r"parent|wife|husband|person) (?:am i|cant|doesnt)\b",
    "future dread": r"\bis this (?:my life now|it for me|how (?:its|it is) going to be|what my life)\b|\b(?:will i|"
                    r"am i going to) (?:ever )?(?:be (?:normal|happy|able|ok|okay)|get better|feel (?:normal|"
                    r"better|like myself)|find|recover|stop|enjoy|have a)\b|\b(?:for|spend|deal with this|live "
                    r"like this|stuck like this|suffer) (?:for )?the rest of my life\b|\b(?:ill|i will|im) never "
                    r"(?:be able to|going to be|get to|be normal|be happy)\b|\bwhats the point (?:of (?:living|"
                    r"trying|anything|going on|it all|even trying|life)|anymore|in trying)\b",
}

# Openers that introduce a Level 4 feeling. What comes after them is the deep content.
FRAMES = {
    "makes me feel like ___": r"\b(?:makes|made|making) me feel (?:like )?((?:a |an |the |im |i am )?[a-z' ]{3,50})",
    "I feel like a ___": r"\bi (?:just |really |honestly )?feel like (?:a|an|such a|the) ([a-z' ]{3,40})",
    "I just want to ___": r"\bi just want to (?:be able to )?((?:be|feel|have|go|live|enjoy|wear|eat|play|sleep|"
                          r"look|stop|get|do)[a-z' ]{2,50})",
    "I'm the only one who ___": r"\b(?:im|i am|i feel like im) the only (?:one|person|mom|dad|girl|guy) "
                                r"(?:who|that|in|my age)([a-z' ]{3,50})",
    "everyone else ___": r"\beveryone else (?:my age )?((?:is|has|can|gets|seems)[a-z' ]{3,50})",
    "I used to ___": r"\bi used to ((?:be|love|go|run|play|enjoy|have|wear|work|travel|dance|hike|lift|swim)"
                     r"[a-z' ]{2,50})",
    "I can't even ___ anymore": r"\bi cant even ([a-z' ]{3,45}) (?:anymore|without)\b",
    "I'm scared that ___": r"\b(?:im|i am) (?:so |really )?(?:scared|afraid|terrified|worried) (?:that |ill |i will "
                           r")?([a-z' ]{3,50})",
}
_FRAMES = {k: re.compile(v) for k, v in FRAMES.items()}

_L2 = {k: re.compile(v) for k, v in L2.items()}
_L3 = {k: re.compile(v) for k, v in L3.items()}
_L4 = {k: re.compile(v) for k, v in L4.items()}
LEVELS = {2: _L2, 3: _L3, 4: _L4}
_ME = re.compile(r"\b(?:i|im|ive|id|ill|me|my|myself|mine)\b")
_SENT = re.compile(r"(?<=[.!?])\s+|\n+")


def _norm(s):
    s = (s or "").lower().replace("’", "'").replace("‘", "'").replace("'", "")
    return re.sub(r"\s+", " ", s).strip()


def sentences(text):
    return [s.strip() for s in _SENT.split(text or "") if len(s.strip()) > 8]


def classify(sentence):
    """[(level, type, matched text)] for one sentence; [] for crisis sentences."""
    n = _norm(sentence)
    if CRISIS.search(n):
        return []
    hits = []
    about_me = _ME.search(n) is not None
    for level, groups in LEVELS.items():
        if level == 4 and not about_me:
            continue  # Level 4 is always about what the problem means for *me*
        for name, rx in groups.items():
            m = rx.search(n)
            if m:
                hits.append((level, name, m.group(0)))
    return hits


def profile(text):
    """Depth profile of a post: counts per level and type, deepest quotes, crisis flag."""
    out = {"depth": 1, "L2": 0, "L3": 0, "L4": 0, "types": {}, "quotes": [], "crisis": False}
    for s in sentences(text):
        if CRISIS.search(_norm(s)):
            out["crisis"] = True
            continue
        hits = classify(s)
        if not hits:
            continue
        top = max(h[0] for h in hits)
        out["depth"] = max(out["depth"], top)
        for level, name, _ in hits:
            out[f"L{level}"] += 1
            out["types"][name] = out["types"].get(name, 0) + 1
        if top >= 3 and len(s) < 400:
            out["quotes"].append({"level": top, "types": sorted({h[1] for h in hits if h[0] == top}),
                                  "text": " ".join(s.split())})
    out["quotes"].sort(key=lambda q: -q["level"])
    if out["crisis"]:  # never surface anything from a crisis post
        out.update(depth=0, L2=0, L3=0, L4=0, types={}, quotes=[])
    return out


# --- Corpus analysis ----------------------------------------------------------------

_EDGE = {"and", "or", "but", "the", "a", "an", "to", "of", "so", "that", "with", "in", "on", "for", "is", "it"}


def _clip(x, max_words=6):
    """Trim a frame completion to its first clause and at most six words."""
    x = re.split(r"\b(?:but|because|and then|so i|which|when|since|although|though)\b", x)[0]
    w = x.split()[:max_words]
    while w and w[-1] in _EDGE | {"i", "my", "me", "im", "is", "was", "are", "be", "just", "really"}:
        w.pop()
    return " ".join(w) if len(w) >= 1 and len(" ".join(w)) > 2 else None


def analyse(posts, problems=None, top_learned=200):
    """Depth across a corpus: level mix, L4 types and their wordings, learned L4
    phrases, deepest communities, and (given problems from a run) each problem's
    L4 share and quotes."""
    from collections import Counter, defaultdict
    by_id = {}
    levels = Counter()
    type_posts = Counter()
    type_variants = defaultdict(Counter)
    frames = defaultdict(Counter)
    frame_subs = defaultdict(set)
    frame_example = {}
    n_sent = n_l4_sent = crisis = 0
    sub_posts, sub_l4 = Counter(), Counter()
    quotes = []
    for p in posts:
        text = p["title"] + ". " + (p.get("body") or "")
        prof = profile(text)
        for q in prof["quotes"]:
            q.update(subreddit=p["subreddit"], title=p["title"][:120],
                     permalink=p.get("permalink", ""), score=p.get("score", 0))
        by_id[p["id"]] = prof
        if prof["crisis"]:
            crisis += 1
            continue
        levels[prof["depth"]] += 1
        sub_posts[p["subreddit"]] += 1
        if prof["depth"] == 4:
            sub_l4[p["subreddit"]] += 1
        for t in prof["types"]:
            type_posts[t] += 1
        quotes.extend(prof["quotes"])
        for s in sentences(text):
            n = _norm(s)
            hits = classify(s)
            n_sent += 1
            l4 = [h for h in hits if h[0] == 4]
            for _, name, matched in l4:
                type_variants[name][matched] += 1
            if l4:
                n_l4_sent += 1
            for fname, rx in _FRAMES.items():
                for m in rx.finditer(n):
                    x = _clip(m.group(1))
                    if x:
                        frames[fname][x] += 1
                        frame_subs[(fname, x)].add(p["subreddit"].lower())
                        frame_example.setdefault((fname, x), " ".join(s.split())[:220])
    learned = []
    for fname, counts in frames.items():
        for x, k in counts.most_common():
            if k < 2:
                break
            learned.append({"frame": fname, "completion": x, "count": k,
                            "subreddits": len(frame_subs[(fname, x)]), "example": frame_example[(fname, x)]})
    learned.sort(key=lambda r: (-r["subreddits"], -r["count"]))
    pruned = learned[:top_learned]

    deepest_subs = sorted(((s, sub_l4[s], sub_posts[s], sub_l4[s] / sub_posts[s])
                           for s in sub_posts if sub_posts[s] >= 50),
                          key=lambda x: -x[3])[:30]
    problem_rows = []
    for prob in problems or []:
        profs = [by_id[i] for i in prob["thread_ids"] if i in by_id and not by_id[i]["crisis"]]
        if not profs:
            continue
        l4 = [x for x in profs if x["depth"] == 4]
        tcount = Counter(t for x in profs for t, lv in _type_levels(x) if lv == 4)
        qs = [q for x in profs for q in x["quotes"] if q["level"] == 4]
        problem_rows.append({"problem": prob["problem"], "threads": len(profs),
                             "l4_share": round(len(l4) / len(profs), 2),
                             "l3_share": round(sum(x["depth"] >= 3 for x in profs) / len(profs), 2),
                             "l4_types": tcount.most_common(5), "quotes": qs[:6]})
    problem_rows.sort(key=lambda r: -r["l4_share"] * r["threads"] ** 0.5)
    return {"posts": len(posts), "crisis_excluded": crisis, "levels": dict(levels),
            "type_posts": type_posts.most_common(),
            "type_variants": {k: v.most_common(15) for k, v in type_variants.items()},
            "learned": pruned, "deepest_subreddits": deepest_subs, "problems": problem_rows,
            "quotes": sorted(quotes, key=lambda q: (-q["level"], -len(q["types"]), -q["score"]))}


_TYPE_LEVEL = {**{k: 2 for k in L2}, **{k: 3 for k in L3}, **{k: 4 for k in L4}}


def _type_levels(prof):
    return [(t, _TYPE_LEVEL[t]) for t in prof["types"]]


def write_report(out, res, meta):
    import csv
    import json
    out.mkdir(parents=True, exist_ok=True)
    (out / "depth.json").write_text(json.dumps({"meta": meta, **res}, indent=2, default=str))
    with open(out / "deep_quotes.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["level", "types", "quote", "subreddit", "post_title", "upvotes", "link"])
        for q in res["quotes"]:
            w.writerow([q["level"], "; ".join(q["types"]), q["text"], q["subreddit"], q["title"],
                        q["score"], q["permalink"]])
    with open(out / "level4_keywords.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "type_or_phrase", "wording", "count", "lift", "subreddits", "example"])
        for name, vs in res["type_variants"].items():
            for v, n in vs:
                w.writerow(["pattern", name, v, n, "", "", ""])
        for r in res["learned"]:
            w.writerow(["frame", r["frame"], r["completion"], r["count"], "", r["subreddits"], r["example"]])

    lv = res["levels"]
    total = sum(lv.values()) or 1
    L = ["# Pain depth report", "",
         f"{res['posts']:,} posts · {res['crisis_excluded']:,} crisis posts excluded · {meta['run_at']}", "",
         "| Deepest level reached | Posts | Share |", "|---|---|---|"]
    names = {1: "L1 symptom only", 2: "L2 physical limit", 3: "L3 life impact", 4: "L4 identity / meaning"}
    for k in (1, 2, 3, 4):
        L.append(f"| {names[k]} | {lv.get(k, 0):,} | {lv.get(k, 0) / total:.1%} |")
    L += ["", "## Level 4: how it shows up", ""]
    for name, n in res["type_posts"]:
        if _TYPE_LEVEL.get(name) != 4:
            continue
        variants = ", ".join(f"“{v}” ({c})" for v, c in res["type_variants"].get(name, [])[:8])
        L.append(f"- **{name}** · {n:,} posts · {variants}")
    L += ["", "## What comes after the deep openers", "",
          "The words people write after *makes me feel like*, *I just want to*, *I'm the only one who* … "
          "Sorted by how many different communities use the same wording.", ""]
    by_frame = {}
    for r in res["learned"]:
        by_frame.setdefault(r["frame"], []).append(r)
    for fname, rows in by_frame.items():
        L.append(f"- **{fname}**: " + ", ".join(f"“{r['completion']}” ({r['count']})" for r in rows[:14]))
    if res["problems"]:
        L += ["", "## Problems by depth", "",
              "| Problem | Threads | Reach L3+ | Reach L4 | Main L4 forms |", "|---|---|---|---|---|"]
        for r in res["problems"]:
            L.append(f"| **{r['problem']}** | {r['threads']} | {r['l3_share']:.0%} | {r['l4_share']:.0%} | "
                     + ", ".join(f"{t} ({n})" for t, n in r["l4_types"][:3]) + " |")
        for r in res["problems"]:
            if not r["quotes"]:
                continue
            L += ["", f"### {r['problem']}: in their words", ""]
            L += [f"> {q['text']}  \n> — r/{q['subreddit']}, *{', '.join(q['types'])}*\n" for q in r["quotes"][:5]]
    L += ["", "## Communities with the deepest pain", "", "| Subreddit | L4 posts | Posts | L4 share |",
          "|---|---|---|---|"]
    for s, a, b, share in res["deepest_subreddits"]:
        L.append(f"| r/{s} | {a} | {b} | {share:.0%} |")
    (out / "depth.md").write_text("\n".join(L) + "\n")
    return out
