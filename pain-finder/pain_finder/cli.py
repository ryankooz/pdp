"""pain-finder: find validated, unsolved problems on Reddit and check them on Google Trends.

  discover   search Reddit for pain phrases ("i wish there was", "tried
             everything", ...) and surface the problems behind them
  topic      deep-dive one problem area ("hair loss", "toddler sleep")
  trends     check keywords on Google Trends only
  phrases    print the pain-phrase library
"""

import argparse
import datetime as dt
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
    p.add_argument("--backend", default="auto", choices=["auto", "oauth", "public", "pullpush"],
                   help="Reddit source (default auto: oauth if REDDIT_CLIENT_ID is set, else public→pullpush)")
    p.add_argument("--time", default="year", choices=["day", "week", "month", "year", "all"],
                   help="how far back to search Reddit (default year)")
    p.add_argument("--sort", default="relevance", choices=["relevance", "top", "comments", "new"])
    p.add_argument("--per-query", type=int, default=100, help="posts per search query (default 100)")
    p.add_argument("--read-comments", type=int, default=60,
                   help="read comments on the N most painful threads (default 60)")
    p.add_argument("--max-comments", type=int, default=150, help="comments per thread (default 150)")
    p.add_argument("--problems", type=int, default=20, help="problems to report (default 20)")
    p.add_argument("--min-threads", type=int, default=2,
                   help="threads a problem needs to count as validated (default 2)")
    p.add_argument("--geo", default="", help="Google Trends country code, e.g. US, GB (default worldwide)")
    p.add_argument("--skip-trends", action="store_true", help="don't query Google Trends")
    p.add_argument("--nsfw", action="store_true", help="include NSFW posts")
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

    sub.add_parser("phrases", help="print the pain-phrase library")

    args = ap.parse_args(argv)
    if args.cmd == "phrases":
        return _print_phrases()
    if args.cmd == "trends":
        return _trends_only(args)
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
        ignore = ()
        label = "discover"
        if subs and len(queries) * len(subs) > 300:
            log(f"Note: {len(queries)} seeds × {len(subs)} subreddits = {len(queries) * len(subs)} "
                "searches. Fewer --seed values or packs will be faster.")
    else:
        topic = args.topic.strip()
        queries = [topic] + [f'{topic} "{s}"' for s in TOPIC_SEEDS]
        subs = subreddits.resolve(None, args.subreddit)
        ignore = analyze.normalise(topic).split() + [analyze.normalise(topic)]
        label = f"topic: {topic}"

    posts = _collect(reddit, args, queries, subs)
    log(f"Collected {len(posts)} unique posts. Scoring…")

    # First pass without comments, to decide which threads deserve a comment read.
    scored = [analyze.score_thread(p, []) for p in posts]
    if args.cmd == "discover":
        # Reddit search is fuzzy; keep only posts that really contain a pain phrase.
        scored = [t for t in scored if t["post_pain"] > 0]
    scored.sort(key=lambda t: -t["validation"])

    to_read = scored[:args.read_comments]
    for n, t in enumerate(to_read, 1):
        if t["num_comments"] == 0 and not reddit.stale_counts:
            continue
        try:
            comments = reddit.comments(t["id"], limit=args.max_comments)
        except SystemExit:
            raise
        except Exception as e:
            log(f"  comments for {t['id']} failed ({e})")
            continue
        if reddit.stale_counts:
            t = {**t, "num_comments": max(t["num_comments"], len(comments))}
        scored[n - 1] = analyze.score_thread(t, comments)
        if n % 10 == 0:
            log(f"  read comments on {n}/{len(to_read)} threads")
    scored = [_strip(t) for t in scored]
    scored.sort(key=lambda t: -t["validation"])

    problems = analyze.cluster_problems(scored, max_problems=args.problems,
                                        min_threads=args.min_threads, ignore=ignore)
    log(f"Found {len(problems)} problems.")

    if not args.skip_trends and problems:
        tr = Trends(geo=args.geo, cache_hours=0 if args.no_cache else 72)
        for n, p in enumerate(problems, 1):
            kw = p["problem"] if args.cmd == "discover" else _topic_keyword(args.topic, p["problem"])
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
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")[:40]
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
