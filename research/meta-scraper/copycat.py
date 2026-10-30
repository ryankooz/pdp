import json, subprocess, time, os, re, datetime as dt
from collections import defaultdict, Counter
P=lambda s: dt.datetime.strptime(s,"%b %d, %Y").date()
ENV=dict(os.environ, NODE_PATH=subprocess.check_output(["npm","root","-g"],text=True).strip(), SCROLLS="1", STATUS="active", TYPE="keyword_exact_phrase")
NEW='&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped'
PHRASES=["rectal cushion","collagen cushion","anal cushions","cushion support","cacao hemorrhoid","non-alkalized cacao",
 "1% less collagen","Freedom Guarantee","150 days","built to be finished","most dangerous sign of hemorrhoids",
 "words flare up","grade 3 hemorrhoids","dangerous foods for your hemorrhoids","hot peppers are poison",
 "hemorrhoids after 40","donut cushion","I paid a colorectal surgeon","colorectal surgeon","hemorrhoid supplement",
 "stay hemorrhoid free","hemorrhoid free","rebuilds the tissue","pushing a hemorrhoid back"]
groups=defaultdict(dict); log=open("copycat.log","w")
for i,ph in enumerate(PHRASES):
    for sort in ("", NEW):
        out=f"cc_{i}_{'n' if sort else 'd'}.json"
        for attempt in range(2):
            subprocess.run(["timeout","250","node","scrape.js",out,ph],env=dict(ENV,EXTRA=sort),capture_output=True)
            try: r=json.load(open(out)).get(ph,{})
            except Exception: r={}
            if r.get("ads") or r.get("total") not in (None,"0"): break
            time.sleep(120)
        for a in r.get("ads",[]):
            d=next((re.sub(r"^(www|shop|try|get|go|secure|order)\.","",u.split('/')[2]) for u in a["dest"] if u.startswith("http")),"page:"+a["page"])
            if a.get("started"): groups[d][a["id"]]={**a,"phrase":ph}
        print(f"{ph} [{'new' if sort else 'top'}]: {r.get('total')} / {len(r.get('ads',[]))}",file=log,flush=True)
        time.sleep(40)
rows=[]
for d,ads in groups.items():
    ads=list(ads.values()); ds=sorted(P(a["started"]) for a in ads)
    rows.append(dict(domain=d,n=len(ads),pages=sorted({a["page"] for a in ads}),first=str(ds[0]),newest=str(ds[-1]),
        phrases=sorted({a["phrase"] for a in ads}),by_day=sorted(Counter(a["started"] for a in ads).items(),key=lambda x:P(x[0]))[-8:],
        landing=Counter(u.split('?')[0] for a in ads for u in a["dest"]).most_common(1), hook=max(ads,key=lambda a:len(a["body"]))["body"][:220]))
rows.sort(key=lambda r:(-len(r["phrases"]),-r["n"]))
json.dump(rows,open("copycat_rows.json","w"),indent=1)
print("CCDONE",file=log,flush=True)
