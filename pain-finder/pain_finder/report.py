"""Writes results.json, problems.csv, threads.csv and report.md to the run folder."""

import csv
import datetime as dt
import json
from pathlib import Path


def _quote(text, n=220):
    text = " ".join((text or "").split())
    return (text[:n] + "…") if len(text) > n else text


def _cell(text):
    return str(text).replace("|", "\\|")


def write_all(out_dir, meta, problems, threads):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(
        {"meta": meta, "problems": problems, "threads": threads}, indent=2, default=str))
    _write_problems_csv(out / "problems.csv", problems)
    _write_threads_csv(out / "threads.csv", threads)
    (out / "report.md").write_text(_markdown(meta, problems))
    return out


def _write_problems_csv(path, problems):
    cols = ["rank", "problem", "opportunity", "reddit_score", "trend_verdict", "trend_yoy",
            "trend_slope_pct", "threads", "subreddits", "agreement", "stories",
            "solution_claims", "gap_signal", "total_upvotes", "total_comments",
            "already_tried", "rising_queries", "top_thread"]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for i, p in enumerate(problems, 1):
            t = p.get("trend") or {}
            w.writerow([
                i, p["problem"], p["opportunity"], p["reddit_score"], t.get("verdict", ""),
                t.get("yoy", ""), t.get("slope_pct", ""), p["threads"],
                "; ".join(f"r/{s} ({n})" for s, n in p["subreddits"]),
                p["agreement"], p["stories"], p["solution_claims"], p["gap_signal"],
                p["total_upvotes"], p["total_comments"],
                "; ".join(f"{k} ({n})" for k, n in p["already_tried"]),
                "; ".join(f"{q} ({v})" for q, v in t.get("rising_queries", [])),
                p["top_threads"][0]["permalink"] if p["top_threads"] else "",
            ])


def _write_threads_csv(path, threads):
    cols = ["validation", "post_pain", "comment_pain", "agreement", "stories", "solutions",
            "gap_signal", "score", "num_comments", "subreddit", "title", "categories",
            "matched_phrases", "tried", "permalink", "created"]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for t in threads:
            w.writerow([
                t["validation"], t["post_pain"], t["comment_pain"], t["agreement"], t["stories"],
                t["solutions"], t["gap_signal"], t["score"], t["num_comments"], t["subreddit"],
                t["title"], "; ".join(t["categories"]), "; ".join(t["matched_phrases"]),
                "; ".join(f"{k} ({n})" for k, n in t["tried"]), t["permalink"],
                dt.datetime.fromtimestamp(t["created_utc"], dt.UTC).date() if t["created_utc"] else "",
            ])


def _markdown(meta, problems):
    L = [f"# Pain Finder report: {meta['mode']}", ""]
    L.append(f"*{meta['run_at']}* · Reddit backend `{meta['backend']}` · "
             f"{meta['posts_collected']} posts found · {meta['threads_scored']} pain threads scored · "
             f"{meta['comment_threads']} with comments read · window: {meta['time_filter']}")
    if meta.get("queries"):
        L.append("")
        L.append("Searched: " + ", ".join(f"`{q}`" for q in meta["queries"][:25])
                 + (" …" if len(meta["queries"]) > 25 else ""))
    if meta.get("subreddits"):
        L.append("")
        L.append(f"Subreddits ({len(meta['subreddits'])}): "
                 + ", ".join(f"r/{s}" for s in meta["subreddits"][:40])
                 + (" …" if len(meta["subreddits"]) > 40 else ""))
    L += ["", "## Leaderboard", "",
          "Opportunity = Reddit validation × Google Trends multiplier "
          "(rising fast ×1.6, rising ×1.3, stable ×1.0, declining ×0.7, no data ×0.9).",
          "",
          "| # | Problem | Opportunity | Trend (2y) | YoY | Threads | Subs | Me-too | Stories | Gap | Fix claims | L4 |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, p in enumerate(problems, 1):
        t = p.get("trend") or {}
        trend = t.get("verdict", "skipped")
        if t.get("spark"):
            trend += f" `{t['spark']}`"
        L.append(f"| {i} | **{_cell(p['problem'])}** | {p['opportunity']} | {trend} | "
                 f"{t.get('yoy', '–')} | {p['threads']} | {len(p['subreddits'])} | {p['agreement']} | "
                 f"{p['stories']} | {p['gap_signal']} | {p['solution_claims']} | "
                 f"{p.get('level4_share', 0):.0%} |")
    L += ["", "**Gap** = gap phrases (wish / tried everything / unknown cause) per thread, divided "
          "by people claiming a fix. High gap + low fix claims = unsolved.", ""]

    for i, p in enumerate(problems, 1):
        t = p.get("trend") or {}
        L += ["---", "", f"## {i}. {p['problem']}", ""]
        L.append(f"**Opportunity {p['opportunity']}** · {p['threads']} threads · "
                 f"{p['total_upvotes']:,} upvotes · {p['total_comments']:,} comments · "
                 f"{p['agreement']} me-too comments · {p['stories']} personal stories · "
                 f"{p['solution_claims']} fix claims")
        L.append("")
        L.append("Subreddits: " + ", ".join(f"r/{s} ({n})" for s, n in p["subreddits"]))
        L.append("")
        L.append("Pain types: " + ", ".join(f"{c.replace('_', ' ')} ({n})" for c, n in p["pain_categories"]))
        if t:
            L.append("")
            if t.get("verdict") in ("no data", "error"):
                L.append(f"Google Trends for `{t['keyword']}`: {t['verdict']}"
                         + (" (search volume too low to chart, or term too specific: try a broader wording "
                            "with `pain-finder trends`)" if t["verdict"] == "no data" else ""))
            else:
                L.append(f"Google Trends for `{t['keyword']}`: **{t['verdict']}** `{t.get('spark', '')}` · "
                         f"YoY ×{t['yoy']} · 2-year slope {t['slope_pct']:+}%/yr · "
                         f"5-year ×{t.get('growth_5y') or '–'}")
            if t.get("rising_queries"):
                L.append("")
                L.append("Rising related searches: "
                         + ", ".join(f"`{q}` ({v})" for q, v in t["rising_queries"]))
        if p["already_tried"]:
            L.append("")
            L.append("**Already tried, and still struggling:** "
                     + ", ".join(f"{k} ×{n}" for k, n in p["already_tried"]))
        L += ["", "Top threads:", ""]
        for th in p["top_threads"][:6]:
            phrases = ", ".join(f"“{x}”" for x in th["matched_phrases"][:4])
            L.append(f"- [{_cell(_quote(th['title'], 140))}]({th['permalink']}) · r/{th['subreddit']} · "
                     f"{th['score']} upvotes · {th['num_comments']} comments · validation {th['validation']}"
                     + (f" · {phrases}" if phrases else ""))
        quotes = [q for th in p["top_threads"] for q in th["agree_examples"]][:3]
        stories = [q for th in p["top_threads"] for q in th["story_examples"]][:3]
        if quotes:
            L += ["", "People agreeing:", ""] + [f"> {_quote(q, 200)}" + "\n" for q in quotes]
        if stories:
            L += ["", "Their stories:", ""] + [f"> {_quote(q, 320)}" + "\n" for q in stories]
        if p.get("level4_quotes"):
            L += ["", f"Deepest pain, Level 4 ({p.get('level4_share', 0):.0%} of threads go this deep):", ""]
            L += [f"> {_quote(q, 320)}" + "\n" for q in p["level4_quotes"][:4]]
        L.append("")

    rising = sorted({q for p in problems for q, v in (p.get("trend") or {}).get("rising_queries", [])})
    if rising:
        L += ["---", "", "## Next searches", "",
              "Rising Google queries from the problems above. Feed them back in with "
              "`pain-finder topic \"<query>\"` to go deeper:", "",
              ", ".join(f"`{q}`" for q in rising), ""]
    return "\n".join(L)
