# Paced rabbit-hole sweep: newest-first discovery, then STATUS=all domain validation.
import json, subprocess, time, re, os, datetime as dt
from collections import Counter, defaultdict
T = dt.date(2026, 10, 25); P = lambda s: dt.datetime.strptime(s, "%b %d, %Y").date()
NEW = '&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped'
ENV = dict(os.environ, NODE_PATH=subprocess.check_output(["npm", "root", "-g"], text=True).strip(), SCROLLS="1")
PHRASES = ["I was skeptical", "my doctor never mentioned", "nobody told me", "what I wish I knew", "I used to be able to",
  "feel like myself again", "I finally stopped", "after menopause", "women over 50", "over 60", "my husband noticed",
  "my wife noticed", "I refused to take", "instead of surgery", "my urologist", "my gastroenterologist", "my rheumatologist",
  "my cardiologist", "my neurologist", "my dermatologist said", "my pharmacist", "as a nurse", "retired nurse",
  "20 years as a", "root cause", "tests came back normal", "ruining my life", "I tried everything", "nothing worked until",
  "the real reason", "Japanese doctor", "German doctor", "doctors hate"]
KILL = set(open("killlist.txt").read().split()) if os.path.exists("killlist.txt") else set()
def run(out, phrases, status, typ, extra=""):
    env = dict(ENV, STATUS=status, TYPE=typ, EXTRA=extra)
    subprocess.run(["timeout", "250", "node", "scrape.js", out] + phrases, env=env, capture_output=True)
    try: return json.load(open(out))
    except Exception: return {}
def dom(u):
    h = u.split("/")[2].lower() if u.startswith("http") else ""
    return re.sub(r"^(www|shop|try|get|go|secure|order|trk|track|lp|info)\.", "", h)
groups = defaultdict(dict); log = open("sweep.log", "a")
for i, ph in enumerate(PHRASES):
    d = run(f"sw_{i}.json", [ph], "active", "keyword_exact_phrase", NEW)
    r = d.get(ph, {}); n = len(r.get("ads", []))
    if n == 0:  # throttled: back off once and retry
        time.sleep(180); d = run(f"sw_{i}.json", [ph], "active", "keyword_exact_phrase", NEW); r = d.get(ph, {})
    for a in r.get("ads", []):
        dm = next((dom(u) for u in a["dest"] if dom(u)), "")
        if dm and a.get("started"): groups[dm][a["id"]] = {**a, "phrase": ph}
    print(f"{ph}: {r.get('total')} / {len(r.get('ads', []))}", file=log, flush=True)
    time.sleep(45)
BIG = re.compile(r"amazon|walmart|target|instagram|facebook|youtube|cvs|reelshort|drama|realt|insur|bank|casino|\.gov|\.edu|google|apple|tiktok", re.I)
cands = []
for dm, ads in groups.items():
    ads = list(ads.values()); ds = sorted(P(a["started"]) for a in ads); pages = {a["page"] for a in ads}
    if BIG.search(dm) or any(k in dm for k in KILL): continue
    if ds[0] >= dt.date(2026, 10, 4) and (len(ads) >= 6 or len(pages) >= 2):
        cands.append((dm, len(ads), len(pages), str(ds[0]), ads[0]["body"][:160]))
cands.sort(key=lambda c: (-c[2], -c[1]))
json.dump(cands, open("sweep_cands.json", "w"), indent=1)
print(f"CANDIDATES {len(cands)}", file=log, flush=True)
val = {}
for dm, *_ in cands[:14]:
    tok = dm.split(".")[0]
    d = run(f"swv_{tok}.json", [tok], "all", "keyword_unordered")
    ads = [a for a in d.get(tok, {}).get("ads", []) if a.get("started") and any(tok in u for u in a["dest"])]
    if ads:
        act = [a for a in ads if a["active"]]
        val[dm] = dict(total=d[tok]["total"], captured=len(ads), active=len(act), cut=len(ads) - len(act),
                       first=str(min(P(a["started"]) for a in ads)), newest=str(max(P(a["started"]) for a in ads)),
                       pages=sorted({a["page"] for a in ads}), by_day=sorted(Counter(a["started"] for a in act).items(), key=lambda x: P(x[0])),
                       landing=Counter(u.split("?")[0].split("/")[-1] for a in ads for u in a["dest"] if tok in u).most_common(2),
                       hook=max(ads, key=lambda a: len(a["body"]))["body"][:260])
    print(f"validated {dm}: {len(ads)}", file=log, flush=True)
    time.sleep(60)
json.dump(val, open("sweep_val.json", "w"), indent=1)
print("SWEEPDONE", file=log, flush=True)
