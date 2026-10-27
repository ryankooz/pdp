#!/usr/bin/env python3
"""Remote job scraper tuned for Superpower-style DR / health / DTC copy roles.

    python scrape.py                    # full run, last 14 days
    python scrape.py --days 3           # only recent postings
    python scrape.py --no-indeed        # skip Indeed (fastest)
    python scrape.py --min-score 50     # only strong fits

Writes output/report.html (open in a browser) and output/jobs_<date>.csv.
"""

import argparse
import csv
import html
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import config
import sources
from filters import is_bs, is_remote, is_us_eligible, score

OUT = Path(__file__).parent / "output"
SEEN_FILE = OUT / "seen.json"
# When the same job shows up in several places, keep the most direct link.
SOURCE_RANK = ["Company board", "Himalayas", "Remotive", "We Work Remotely", "Jobicy",
               "RemoteOK", "Working Nomads", "Jobspresso", "Indeed"]


def collect(args):
    searches = config.PRIMARY_SEARCHES + config.SECONDARY_SEARCHES
    boards = {
        "Remotive": sources.remotive, "RemoteOK": sources.remoteok,
        "We Work Remotely": sources.weworkremotely, "Working Nomads": sources.workingnomads,
        "Jobicy": sources.jobicy, "Himalayas": sources.himalayas, "Jobspresso": sources.jobspresso,
    }
    jobs = []

    def run(name, fn):
        try:
            got = fn(searches)
            print(f"  {name}: {len(got)}")
            return got
        except Exception as e:
            print(f"  ! {name} failed: {e}")
            return []

    print("Remote job boards:")
    with ThreadPoolExecutor(8) as ex:
        for got in ex.map(lambda kv: run(*kv), boards.items()):
            jobs += got

    print("Company boards (health / wellness / DTC):")
    got = sources.company_boards(config.COMPANY_BOARDS)
    print(f"  {len(config.COMPANY_BOARDS)} companies: {len(got)} postings")
    jobs += got

    if not args.no_indeed:
        print("Indeed (remote filter on, this takes a minute):")
        got = sources.indeed(searches, days=args.days)
        print(f"  Indeed: {len(got)}")
        jobs += got
    return jobs


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def process(jobs, args):
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    counts = {"too old": 0, "not remote": 0, "non-US": 0, "BS filter": 0, "low score": 0}
    kept = {}
    for j in jobs:
        if not j.title or not j.url:
            continue
        # Company-board postings are live until the company pulls them, so age doesn't matter.
        if j.posted and j.posted < cutoff and j.source != "Company board":
            counts["too old"] += 1
            continue
        if not is_remote(j):
            counts["not remote"] += 1
            continue
        if not is_us_eligible(j):
            counts["non-US"] += 1
            continue
        if is_bs(j):
            counts["BS filter"] += 1
            continue
        score(j)
        if j.score < args.min_score:
            counts["low score"] += 1
            continue
        key = norm(j.company) + "|" + norm(j.title) if j.company else norm(j.url)
        prev = kept.get(key)
        rank = SOURCE_RANK.index(j.source) if j.source in SOURCE_RANK else 99
        if prev is None or rank < SOURCE_RANK.index(prev.source):
            kept[key] = j
    print("Dropped: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    return sorted(kept.values(), key=lambda j: (-j.score, -(j.posted.timestamp() if j.posted else 0)))


def mark_new(jobs):
    seen = json.loads(SEEN_FILE.read_text()) if SEEN_FILE.exists() else {}
    today = datetime.now().strftime("%Y-%m-%d")
    for j in jobs:
        if j.url not in seen:
            j.is_new = True
            seen[j.url] = today
    SEEN_FILE.write_text(json.dumps(seen, indent=0))


def write_csv(jobs, path):
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["score", "tier", "new", "title", "company", "source", "location",
                    "salary", "posted", "url", "why"])
        for j in jobs:
            w.writerow([j.score, j.tier, "yes" if j.is_new else "", j.title, j.company, j.source,
                        j.location, j.salary, j.posted.strftime("%Y-%m-%d") if j.posted else "",
                        j.url, ", ".join(j.why)])


def write_html(jobs, path):
    e = html.escape
    rows = []
    for j in jobs:
        tier_cls = {"Superpower match": "t1", "Strong fit": "t2"}.get(j.tier, "t3")
        rows.append(
            f'<tr data-tier="{tier_cls}" data-new="{int(j.is_new)}">'
            f'<td><span class="score {tier_cls}">{j.score}</span></td>'
            f'<td><a href="{e(j.url)}" target="_blank" rel="noopener">{e(j.title)}</a>'
            f'{" <span class=new>NEW</span>" if j.is_new else ""}'
            f'<div class="why">{e(", ".join(j.why))}</div></td>'
            f'<td>{e(j.company)}</td><td>{e(j.salary)}</td><td>{e(j.location or "Remote")}</td>'
            f'<td>{e(j.source)}</td><td>{j.posted.strftime("%b %d") if j.posted else ""}</td></tr>'
        )
    n1 = sum(j.tier == "Superpower match" for j in jobs)
    n2 = sum(j.tier == "Strong fit" for j in jobs)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Remote Job Matches</title>
<style>
:root{{--bg:#fafaf9;--fg:#1c1917;--mut:#78716c;--line:#e7e5e4;--card:#fff;--t1:#047857;--t2:#1d4ed8;--t3:#78716c;--acc:#b45309}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1c1917;--fg:#f5f5f4;--mut:#a8a29e;--line:#44403c;--card:#292524;--t1:#34d399;--t2:#93c5fd;--t3:#a8a29e;--acc:#fbbf24}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}}
main{{max-width:1200px;margin:0 auto;padding:24px 16px}}
h1{{margin:0 0 4px;font-size:22px}} .sub{{color:var(--mut);margin-bottom:16px}}
.bar{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}}
button,input{{font:inherit;padding:6px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg)}}
button.on{{border-color:var(--fg);font-weight:600}} input{{flex:1;min-width:180px}}
.wrap{{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:12px}}
table{{border-collapse:collapse;width:100%}} th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--mut)}}
a{{color:var(--fg);font-weight:600}} .why{{color:var(--mut);font-size:12px;margin-top:2px}}
.score{{font-weight:700;font-variant-numeric:tabular-nums}} .t1{{color:var(--t1)}} .t2{{color:var(--t2)}} .t3{{color:var(--t3)}}
.new{{color:var(--acc);font-size:11px;font-weight:700}}
</style></head><body><main>
<h1>Remote Job Matches</h1>
<div class="sub">{len(jobs)} verified-remote jobs · {n1} Superpower matches · {n2} strong fits · generated {datetime.now().strftime("%b %d, %Y %H:%M")}</div>
<div class="bar"><button class="on" data-f="all">All</button><button data-f="t1">Superpower match</button>
<button data-f="t2">Strong fit</button><button data-f="t3">Worth a look</button><button data-f="new">New only</button>
<input id="q" placeholder="Filter by title, company, keyword…"></div>
<div class="wrap"><table><thead><tr><th>Fit</th><th>Role</th><th>Company</th><th>Pay</th><th>Location</th><th>Source</th><th>Posted</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div></main>
<script>
let f='all';const q=document.getElementById('q');
function apply(){{const s=q.value.toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>{{
const ok=(f==='all'||(f==='new'?r.dataset.new==='1':r.dataset.tier===f))&&r.textContent.toLowerCase().includes(s);
r.style.display=ok?'':'none'}})}}
document.querySelectorAll('[data-f]').forEach(b=>b.onclick=()=>{{document.querySelectorAll('[data-f]').forEach(x=>x.classList.remove('on'));b.classList.add('on');f=b.dataset.f;apply()}});
q.oninput=apply;
</script></body></html>"""
    path.write_text(page)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--days", type=int, default=config.DEFAULT_DAYS)
    p.add_argument("--min-score", type=int, default=config.DEFAULT_MIN_SCORE)
    p.add_argument("--no-indeed", action="store_true", help="skip Indeed (faster)")
    args = p.parse_args()

    OUT.mkdir(exist_ok=True)
    jobs = process(collect(args), args)
    mark_new(jobs)
    stamp = datetime.now().strftime("%Y-%m-%d")
    write_csv(jobs, OUT / f"jobs_{stamp}.csv")
    write_html(jobs, OUT / "report.html")

    print(f"\n{len(jobs)} jobs kept → {OUT/'report.html'}\n")
    for j in jobs[:15]:
        flag = "NEW " if j.is_new else "    "
        print(f"{flag}{j.score:>3}  {j.title[:55]:<55} {j.company[:22]:<22} {j.source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
