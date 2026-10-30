import json, subprocess, time, os, datetime as dt
from collections import Counter
P=lambda s: dt.datetime.strptime(s,"%b %d, %Y").date()
ENV=dict(os.environ, NODE_PATH=subprocess.check_output(["npm","root","-g"],text=True).strip(), SCROLLS="1", STATUS="all", TYPE="keyword_unordered")
toks=["cladeprotocol","try-voke","tryfemvia","trycirae","noverly","krakensupps","savayabotanicals","vibriance","fineroot","try-odysseus","holistichealthlabs","sky-nutrition","inflairskin","gloalabs","venalyslab"]
out={}
for t in toks:
    for attempt in range(2):
        subprocess.run(["timeout","250","node","scrape.js",f"v3_{t}.json",t],env=ENV,capture_output=True)
        try: r=json.load(open(f"v3_{t}.json"))[t]
        except Exception: r={"ads":[],"total":None}
        if r.get("ads"): break
        time.sleep(150)
    key=t.replace("try-","").replace("try","") if t not in ("trycirae","tryfemvia") else t
    ads=[a for a in r["ads"] if a.get("started") and any(key in u for u in a["dest"])]
    if ads:
        act=[a for a in ads if a["active"]]
        out[t]=dict(total=r["total"],captured=len(ads),active=len(act),cut=len(ads)-len(act),first=str(min(P(a["started"]) for a in ads)),
            newest=str(max(P(a["started"]) for a in ads)),pages=sorted({a["page"] for a in ads}),
            by_day=sorted(Counter(a["started"] for a in act).items(),key=lambda x:P(x[0])),
            landing=Counter(u.split("?")[0].split("/")[-1] for a in ads for u in a["dest"] if key in u).most_common(2),
            hook=max(ads,key=lambda a:len(a["body"]))["body"][:240])
    else: out[t]={"total":r.get("total"),"captured":0}
    json.dump(out,open("v3_summary.json","w"),indent=1)
    time.sleep(60)
print("V3DONE")
