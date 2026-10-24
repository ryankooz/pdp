"""pain-finder: find validated, unsolved problems on Reddit and check them on Google Trends.

  discover   search Reddit for pain phrases ("i wish there was", "tried
             everything", ...) and surface the problems behind them
  topic      deep-dive one problem area ("hair loss", "toddler sleep")
  trends     check keywords on Google Trends only
  recluster  regroup a saved run (results.json) without scraping again
  mine       learn new pain phrases and pull named problems out of collected posts
  suggest    what people type into Google about a problem (autocomplete)
  depth      score how deep the pain goes (symptom → physical → life → identity)
  desires    what people want back, by level (body → life → identity)
  cj         search CJ Dropshipping for products that fit each validated problem
  phrases    print the pain-phrase library
"""

import argparse
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

from . import analyze, phrases, report, subreddits
from .reddit import Reddit, log
from .trends import VERDICT_MULTIPLIER, Trends

TOPIC_SEEDS = [
    "tried everything", "nothing works", "i wish there was", "at my wits end",
    "ruining my life", "doctors", "still", "desperate", "how do i fix", "anyone else",
]


def _common(p):
    p.add_argument("--time", default="year", choices=["day", "week", "month", "year", "all"],
                   help="how far back to search Reddit (default year)")
    p.add_argument("--sort", default="relevance", choices=["relevance", "top", "comments", "new"])
    p.add_argument("--per-query", type=int, default=100, help="posts per search query (default 100)")
    p.add_argument("--scan-posts", type=int, default=300,
                   help="arcticshift discovery: newest posts to scan per subreddit (default 300)")
    p.add_argument("--read-comments", type=int, default=40,
                   help="before grouping, read comments on the N most painful threads (default 40)")
    p.add_argument("--nsfw", action="store_true", help="include NSFW posts")
    _grouping(p)


def _grouping(p):
    p.add_argument("--backend", default="auto",
                   choices=["auto", "oauth", "public", "arcticshift", "pullpush"],
                   help="Reddit source (default auto: oauth if REDDIT_CLIENT_ID is set, "
                        "else public, falling back to arcticshift)")
    p.add_argument("--comments-per-problem", type=int, default=5,
                   help="after grouping, read comments on each problem's top N threads to count "
                        "me-too replies and stories (default 5, 0 to skip)")
    p.add_argument("--max-comments", type=int, default=150, help="comments per thread (default 150)")
    p.add_argument("--problems", type=int, default=20, help="problems to report (default 20)")
    p.add_argument("--min-threads", type=int, default=3,
                   help="threads a problem needs to count as validated (default 3)")
    p.add_argument("--geo", default="", help="Google Trends country code, e.g. US, GB (default worldwide)")
    p.add_argument("--skip-trends", action="store_true", help="don't query Google Trends")
    p.add_argument("--out", default="runs", help="output folder (default runs/)")
    p.add_argument("--no-cache", action="store_true", help="ignore cached Reddit/Trends responses")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pain-finder", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("discover", help="find problems from pain phrases across Reddit")
    d.add_argument("--seed", action="append", help="pain phrase to search (repeatable; default: built-in list)")
    d.add_argument("--pack", action="append",
                   help=f"subreddit pack: {', '.join(subreddits.PACKS)}, all (repeatable; default: all of Reddit)")
    d.add_argument("--subreddit", "-r", action="append", help="extra subreddit (repeatable)")
    _common(d)

    t = sub.add_parser("topic", help="deep-dive one problem area")
    t.add_argument("topic", help='e.g. "tinnitus", "hair loss", "toddler won\'t sleep"')
    t.add_argument("--subreddit", "-r", action="append", help="limit to these subreddits")
    _common(t)

    g = sub.add_parser("trends", help="Google Trends check for keywords")
    g.add_argument("keywords", nargs="+")
    g.add_argument("--geo", default="")
    g.add_argument("--timeframe", default="today 5-y", help='pytrends timeframe (default "today 5-y")')

    c = sub.add_parser("recluster", help="regroup a saved run without scraping again")
    c.add_argument("results", help="path to a run's results.json")
    _grouping(c)

    m = sub.add_parser("mine", help="learn pain phrases and named problems from collected posts")
    m.add_argument("sources", nargs="*", default=[".cache/reddit"],
                   help="cache folders or results.json files (default .cache/reddit)")
    m.add_argument("--min-posts", type=int, default=12, help="posts a learned phrase needs (default 12)")
    m.add_argument("--phrases", type=int, default=150, help="learned phrases to keep (default 150)")
    m.add_argument("--problems", type=int, default=200, help="named problems to keep (default 200)")
    m.add_argument("--out", default="runs")

    q = sub.add_parser("suggest", help="Google autocomplete for problems, plus Trends on the top ones")
    q.add_argument("keywords", nargs="+")
    q.add_argument("--no-alphabet", action="store_true", help="skip the a-z expansion (faster)")
    q.add_argument("--trends", type=int, default=0, help="run Google Trends on the top N suggestions")
    q.add_argument("--geo", default="")
    q.add_argument("--out", default="runs")

    dp = sub.add_parser("depth", help="pain depth: symptom → physical → life → identity (Level 4)")
    dp.add_argument("sources", nargs="*", default=[".cache/reddit"],
                    help="cache folders or results.json files (default .cache/reddit)")
    dp.add_argument("--problems-from", help="a run's results.json, to rank its problems by depth")
    dp.add_argument("--out", default="runs")

    ds = sub.add_parser("desires", help="what people want back: body, life, identity (Level 2-4)")
    ds.add_argument("sources", nargs="*", default=[".cache/reddit"])
    ds.add_argument("--problems-from", help="a run's results.json, to show each problem's desires")
    ds.add_argument("--out", default="runs")

    c2 = sub.add_parser("cj", help="search CJ Dropshipping for products per problem (needs CJ_API_KEY)")
    c2.add_argument("--problem", action="append", help="problem name from cj.PROBLEMS (repeatable; default all)")
    c2.add_argument("--keyword", action="append", help="extra keyword, searched under 'custom'")
    c2.add_argument("--pages", type=int, default=1, help="result pages of 100 per keyword (default 1)")
    c2.add_argument("--country", help="only products stocked in this warehouse country, e.g. US")
    c2.add_argument("--list-problems", action="store_true")
    c2.add_argument("--formats", action="store_true",
                    help="search each problem's ingredients in every format (powder, gummy, spray, patch…)")
    c2.add_argument("--out", default="runs")

    sub.add_parser("phrases", help="print the pain-phrase library")

    args = ap.parse_args(argv)
    if args.cmd == "phrases":
        return _print_phrases()
    if args.cmd == "trends":
        return _trends_only(args)
    if args.cmd == "recluster":
        return _recluster(args)
    if args.cmd == "mine":
        return _mine(args)
    if args.cmd == "suggest":
        return _suggest(args)
    if args.cmd == "depth":
        return _depth(args)
    if args.cmd == "desires":
        return _desires(args)
    if args.cmd == "cj":
        return _cj(args)
    return _run(args)


def _print_phrases():
    for name, c in phrases.PAIN_CATEGORIES.items():
        print(f"\n[{name}] weight {c['weight']}")
        print("  " + " · ".join(c["phrases"]))
    print("\n[comment agreement]\n  " + " · ".join(phrases.AGREEMENT_PHRASES))
    print("\n[comment stories]\n  " + " · ".join(phrases.STORY_PHRASES))
    print("\n[fix claims]\n  " + " · ".join(phrases.SOLUTION_CLAIM_PHRASES))
    print("\n[default discovery seeds]\n  " + " · ".join(phrases.DISCOVERY_SEEDS))


def _trends_only(args):
    tr = Trends(geo=args.geo, timeframe=args.timeframe)
    print(f"{'keyword':32} {'verdict':12} {'YoY':>6} {'slope/yr':>9}  last 2 years")
    for kw in args.keywords:
        r = tr.check(kw)
        print(f"{kw[:32]:32} {r['verdict']:12} {r.get('yoy', ''):>6} "
              f"{(str(r['slope_pct']) + '%') if 'slope_pct' in r else '':>9}  {r.get('spark', '')}")
        for q, v in r.get("rising_queries", [])[:6]:
            print(f"    rising: {q} ({v})")


def _mine(args):
    from . import mine
    started = dt.datetime.now(dt.UTC)
    posts = mine.load_posts(args.sources)
    if not posts:
        raise SystemExit(f"No posts found in {', '.join(args.sources)}. Run discover or topic first.")
    log(f"Loaded {len(posts):,} posts. Learning phrases…")
    phrases_ = mine.learn_phrases(posts, min_posts=args.min_posts, top=args.phrases)
    log(f"Learned {len(phrases_)} phrases. Extracting named problems…")
    problems = mine.extract_problems(posts, top=args.problems)
    n_pain = sum(1 for p in posts if any(c in analyze.pain_hits(analyze.normalise(mine._text(p)))
                                         for c in mine.STRONG))
    meta = {"run_at": started.strftime("%Y-%m-%d %H:%M UTC"), "posts": len(posts),
            "pain_posts": n_pain, "sources": args.sources}
    out = mine.write_mine_report(Path(args.out) / f"{started:%Y%m%d-%H%M%S}-mine", meta, phrases_, problems)
    print(f"\nReport: {out / 'mine.md'}\nSpreadsheets: {out / 'named_problems.csv'}, "
          f"{out / 'learned_phrases.csv'}\n")
    print("Top named problems:")
    for r in problems[:15]:
        print(f"  {r['problem'][:32]:32} {r['posts']:4} posts  median {r['median_years'] or '-'} yrs  "
              f"${r['max_money'] or '-'}  {r['mention_doctors']} doctor mentions")
    print("\nTop learned phrases:")
    for r in phrases_[:15]:
        print(f"  “{r['phrase']}”  {r['pain_posts']} pain posts, ×{r['lift']}")
    return 0


def _depth(args):
    from . import depth, mine
    started = dt.datetime.now(dt.UTC)
    posts = mine.load_posts(args.sources)
    if not posts:
        raise SystemExit(f"No posts found in {', '.join(args.sources)}.")
    problems = json.loads(Path(args.problems_from).read_text())["problems"] if args.problems_from else None
    log(f"Reading {len(posts):,} posts sentence by sentence…")
    res = depth.analyse(posts, problems)
    meta = {"run_at": started.strftime("%Y-%m-%d %H:%M UTC"), "sources": args.sources}
    out = depth.write_report(Path(args.out) / f"{started:%Y%m%d-%H%M%S}-depth", res, meta)
    lv = res["levels"]
    print(f"\nReport: {out / 'depth.md'}\nQuotes: {out / 'deep_quotes.csv'}\n"
          f"Keywords: {out / 'level4_keywords.csv'}\n")
    print("Deepest level reached: " + ", ".join(f"L{k} {lv.get(k, 0):,}" for k in (1, 2, 3, 4)))
    for r in res["learned"][:25]:
        print(f"  {r['frame']:28} “{r['completion']}”  ×{r['count']} in {r['subreddits']} subs")
    return 0


def _desires(args):
    from . import desire, mine
    started = dt.datetime.now(dt.UTC)
    posts = mine.load_posts(args.sources)
    if not posts:
        raise SystemExit(f"No posts found in {', '.join(args.sources)}.")
    problems = json.loads(Path(args.problems_from).read_text())["problems"] if args.problems_from else None
    log(f"Reading {len(posts):,} posts for desires…")
    res = desire.analyse(posts, problems)
    meta = {"run_at": started.strftime("%Y-%m-%d %H:%M UTC"), "sources": args.sources}
    out = desire.write_report(Path(args.out) / f"{started:%Y%m%d-%H%M%S}-desires", res, meta)
    print(f"\nReport: {out / 'desires.md'}\nQuotes: {out / 'desires.csv'}\n")
    for r in res["themes"]:
        print(f"  L{r['level']} {r['theme']:34} {r['posts']:5} posts  e.g. “{r['top_wants'][0][0]}”")
    return 0


def _cj(args):
    from . import cj
    if args.list_problems:
        for k, v in cj.PROBLEMS.items():
            print(f"{k}: {', '.join(v)}")
        return 0
    started = dt.datetime.now(dt.UTC)
    if args.keyword:
        cj.PROBLEMS["custom"] = args.keyword
    problems = args.problem or list(cj.PROBLEMS)
    unknown = [p for p in problems if p not in cj.PROBLEMS]
    if unknown:
        raise SystemExit(f"Unknown problem(s): {unknown}. See --list-problems.")
    client = cj.CJ()
    if args.formats:
        problems = [p for p in problems if p in cj.INGREDIENTS] or list(cj.INGREDIENTS)
        res = cj.scan_formats(client, problems, country=args.country)
        meta = {"run_at": started.strftime("%Y-%m-%d %H:%M UTC"), "api_calls": client.calls}
        out = cj.write_formats_report(Path(args.out) / f"{started:%Y%m%d-%H%M%S}-cj-formats", res, meta)
        print(f"\nReport: {out / 'cj_formats.md'}\nSpreadsheet: {out / 'cj_formats.csv'}")
        return 0
    res = cj.scan(client, problems, pages=args.pages, country=args.country)
    meta = {"run_at": started.strftime("%Y-%m-%d %H:%M UTC"), "api_calls": client.calls,
            "country": args.country}
    out = cj.write_report(Path(args.out) / f"{started:%Y%m%d-%H%M%S}-cj", res, meta)
    print(f"\nReport: {out / 'cj.md'}\nSpreadsheet: {out / 'cj_products.csv'}\n")
    for prob, r in res.items():
        top = r["products"][0] if r["products"] else None
        print(f"  {prob:30} {len(r['products']):4} products"
              + (f"  top: {top['name'][:50]} ({top['listed']} stores)" if top else ""))
    return 0


def _suggest(args):
    from . import mine
    from .reddit import _Cache
    started = dt.datetime.now(dt.UTC)
    ac = mine.Autocomplete(_Cache(".cache/autocomplete", 24 * 7), geo=(args.geo or "us").lower())
    tr = Trends(geo=args.geo) if args.trends else None
    results = {}
    for kw in args.keywords:
        log(f"Autocomplete: {kw}")
        rows = ac.expand(kw, alphabet=not args.no_alphabet)
        results[kw] = rows
        print(f"\n{kw}: {len(rows)} searches")
        for r in rows[:25]:
            print(f"  {r['query']}" + (f"  (×{r['hits']})" if r["hits"] > 1 else ""))
        if tr:
            for r in rows[:args.trends]:
                t = tr.check(r["query"], related=False)
                r["trend"] = t
                print(f"    trend: {r['query'][:50]:50} {t['verdict']:11} {t.get('yoy', '')} {t.get('spark', '')}")
    out = Path(args.out) / f"{started:%Y%m%d-%H%M%S}-suggest"
    out.mkdir(parents=True, exist_ok=True)
    (out / "suggest.json").write_text(json.dumps(results, indent=2, default=str))
    with open(out / "suggest.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["keyword", "search", "times_suggested", "template", "trend", "yoy"])
        for kw, rows in results.items():
            for r in rows:
                t = r.get("trend") or {}
                w.writerow([kw, r["query"], r["hits"], r["from"], t.get("verdict", ""), t.get("yoy", "")])
    print(f"\nSaved: {out / 'suggest.csv'}")
    return 0


def _scan(reddit, args, subs):
    """Archive mode: read each subreddit's recent posts and match phrases locally."""
    posts = {}
    for n, s in enumerate(subs, 1):
        try:
            found = reddit.scan(s, time_filter=args.time, limit=args.scan_posts)
        except SystemExit:
            raise
        except Exception as e:
            log(f"[{n}/{len(subs)}] r/{s}: failed ({e})")
            continue
        for p in found:
            if not ((p["over_18"] and not args.nsfw) or p["subreddit"].startswith("u_")):
                posts.setdefault(p["id"], p)
        log(f"[{n}/{len(subs)}] r/{s}: scanned {len(found)} posts")
    return list(posts.values())


def _collect(reddit, args, queries, subs):
    posts = {}
    jobs = [(q, s) for q in queries for s in (subs or [None])]
    for n, (q, s) in enumerate(jobs, 1):
        where = f"r/{s}" if s else "all of Reddit"
        try:
            found = reddit.search(q, subreddit=s, sort=args.sort, time_filter=args.time,
                                  limit=args.per_query)
        except SystemExit:
            raise
        except Exception as e:
            log(f"[{n}/{len(jobs)}] {q!r} in {where}: failed ({e})")
            continue
        new = 0
        for p in found:
            if (p["over_18"] and not args.nsfw) or p["subreddit"].startswith("u_"):
                continue
            if p["id"] not in posts:
                posts[p["id"]] = p
                new += 1
        log(f"[{n}/{len(jobs)}] {q!r} in {where}: {len(found)} posts, {new} new")
    return list(posts.values())


def _run(args):
    started = dt.datetime.now(dt.UTC)
    cache_hours = 0 if args.no_cache else 24
    reddit = Reddit(args.backend, cache_hours=cache_hours)

    if args.cmd == "discover":
        seeds = args.seed or phrases.DISCOVERY_SEEDS
        queries = [f'"{s}"' for s in seeds]
        subs = subreddits.resolve(args.pack, args.subreddit)
        label = "discover"

    else:
        topic = args.topic.strip()
        queries = [topic] + [f'{topic} "{s}"' for s in TOPIC_SEEDS]
        subs = subreddits.resolve(None, args.subreddit)
        label = f"topic: {topic}"

    reddit.probe()
    if reddit.needs_subreddit and args.cmd == "discover":
        if not subs:
            subs = subreddits.resolve(["all"], None)
            log(f"{reddit.backend_name} can't search all of Reddit; scanning all "
                f"{len(subs)} subreddits in the packs instead")
        queries = []
        label = f"discover (scanned {len(subs)} subreddits)"
        posts = _scan(reddit, args, subs)
    elif reddit.needs_subreddit and not subs:
        raise SystemExit(f"{reddit.backend_name} can only search inside subreddits: add -r <name>.")
    else:
        if subs and len(queries) * len(subs) > 300:
            log(f"Note: {len(queries)} seeds × {len(subs)} subreddits = {len(queries) * len(subs)} "
                "searches. Fewer --seed values or packs will be faster.")
        posts = _collect(reddit, args, queries, subs)
    log(f"Collected {len(posts)} unique posts. Scoring…")

    # First pass without comments, to decide which threads deserve a comment read.
    scored = [analyze.score_thread(p, []) for p in posts]
    if args.cmd == "discover":
        # Reddit search is fuzzy; keep only posts that really contain a pain phrase.
        scored = [t for t in scored if t["post_pain"] > 0]
    scored.sort(key=lambda t: -t["validation"])

    scored = [_strip(t) for t in scored]
    for n in range(min(args.read_comments, len(scored))):
        scored[n] = _read_comments(reddit, scored[n], args)
        if (n + 1) % 10 == 0:
            log(f"  read comments on {n + 1}/{args.read_comments} threads")
    scored.sort(key=lambda t: -t["validation"])

    meta = {
        "mode": label,
        "run_at": started.strftime("%Y-%m-%d %H:%M UTC"),
        "backend": reddit.backend_name,
        "time_filter": args.time,
        "queries": queries,
        "subreddits": subs,
        "posts_collected": len(posts),
        "threads_scored": len(scored),
        "comment_threads": sum(1 for t in scored if t["comments_analyzed"]),
    }
    topic = args.topic.strip() if args.cmd == "topic" else None
    return _finish(args, started, meta, scored, topic, reddit)


def _recluster(args):
    data = json.loads(Path(args.results).read_text())
    meta = data["meta"]
    topic = meta["mode"].removeprefix("topic: ") if meta["mode"].startswith("topic: ") else None
    meta["regrouped_at"] = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    log(f"Regrouping {len(data['threads'])} threads from {args.results}")
    reddit = Reddit(args.backend, cache_hours=0 if args.no_cache else 24 * 30) \
        if args.comments_per_problem else None
    return _finish(args, dt.datetime.now(dt.UTC), meta, data["threads"], topic, reddit)


def _read_comments(reddit, t, args):
    """Rescore one thread with its comments; returns the thread unchanged on failure."""
    if t["num_comments"] == 0 and not reddit.stale_counts:
        return t
    try:
        comments = reddit.comments(t["id"], limit=args.max_comments)
    except SystemExit:
        raise
    except Exception as e:
        log(f"  comments for {t['id']} failed ({e})")
        return t
    if reddit.stale_counts:
        t = {**t, "num_comments": max(t["num_comments"], len(comments))}
    return _strip(analyze.score_thread(t, comments))


def _finish(args, started, meta, scored, topic, reddit=None):
    """Group scored threads into problems, read their comments, check Trends, write the report."""
    ignore = analyze.normalise(topic).split() + [analyze.normalise(topic)] if topic else ()
    problems = analyze.cluster_problems(scored, max_problems=args.problems,
                                        min_threads=args.min_threads, ignore=ignore)
    log(f"Found {len(problems)} problems.")

    if reddit and args.comments_per_problem:
        # Agreement and stories live in the comments, so make sure every problem
        # has its strongest threads read, not just the global top N.
        by_id = {t["id"]: t for t in scored}
        todo = [(p, i) for p in problems for i in p["thread_ids"][:args.comments_per_problem]
                if not by_id[i]["comments_analyzed"]]
        log(f"Reading comments on {len(todo)} threads across {len(problems)} problems")
        for n, (p, i) in enumerate(todo, 1):
            by_id[i] = _read_comments(reddit, by_id[i], args)
            if n % 10 == 0:
                log(f"  read comments on {n}/{len(todo)} threads")
        for k, p in enumerate(problems):
            members = sorted((by_id[i] for i in p["thread_ids"]), key=lambda t: -t["validation"])
            problems[k] = analyze.summarise(p["problem"], members)
        scored = sorted(by_id.values(), key=lambda t: -t["validation"])
        meta["comment_threads"] = sum(1 for t in scored if t["comments_analyzed"])

    if not args.skip_trends and problems:
        tr = Trends(geo=args.geo, cache_hours=0 if args.no_cache else 72)
        for n, p in enumerate(problems, 1):
            kw = _topic_keyword(topic, p["problem"]) if topic else p["problem"]
            log(f"  Google Trends [{n}/{len(problems)}]: {kw}")
            try:
                p["trend"] = tr.check(kw)
            except RuntimeError as e:
                log(f"  {e}")
                break
    for p in problems:
        mult = VERDICT_MULTIPLIER.get((p.get("trend") or {}).get("verdict"), 1.0)
        p["opportunity"] = round(p["reddit_score"] * mult, 1)
    problems.sort(key=lambda p: -p["opportunity"])

    slug = re.sub(r"[^a-z0-9]+", "-", meta["mode"].lower()).strip("-")[:40]
    out = report.write_all(Path(args.out) / f"{started:%Y%m%d-%H%M%S}-{slug}", meta, problems, scored)
    print(f"\nReport: {out / 'report.md'}")
    print(f"Spreadsheets: {out / 'problems.csv'}, {out / 'threads.csv'}\n")
    for i, p in enumerate(problems[:10], 1):
        t = p.get("trend") or {}
        print(f"{i:2}. {p['problem'][:40]:40} opp {p['opportunity']:>8}  "
              f"{t.get('verdict', '-'):11} {t.get('spark', '')}  "
              f"{p['threads']} threads, {p['agreement']} me-too")
    return 0


def _topic_keyword(topic, problem):
    """In topic mode a sub-problem like 'ringing' is checked as 'tinnitus ringing'."""
    topic_words = set(analyze.normalise(topic).split())
    if set(problem.split()) <= topic_words:
        return topic
    return f"{topic} {problem}"


def _strip(t):
    # Bodies are long and already summarised; keep a preview in the outputs.
    t = dict(t)
    t["body"] = t["body"][:1500]
    return t


if __name__ == "__main__":
    sys.exit(main())
