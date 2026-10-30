import json,subprocess,time,os,datetime as dt
from collections import Counter
P=lambda s: dt.datetime.strptime(s,"%b %d, %Y").date()
E=dict(os.environ,NODE_PATH=subprocess.check_output(["npm","root","-g"],text=True).strip(),SCROLLS="1",STATUS="all",TYPE="keyword_unordered")
out={}
for t in ["dermiqua","trylovy","fortishealth","rarenutrition","getamalahealth","lovi-health","hervitality","auniva","kairawellness","bioma"]:
    for k in range(3):
        subprocess.run(["timeout","250","node","scrape.js",f"v30_{t}.json",t],env=E,capture_output=True)
        try: r=json.load(open(f"v30_{t}.json"))[t]
        except Exception: r={"ads":[]}
        if r.get("ads"): break
        time.sleep(120)
    ads=[a for a in r.get("ads",[]) if a.get("started") and any(t in u for u in a["dest"])]
    if ads:
        act=[a for a in ads if a["active"]]
        out[t]=dict(total=r.get("total"),captured=len(ads),active=len(act),cut=len(ads)-len(act),first=str(min(P(a["started"]) for a in ads)),newest=str(max(P(a["started"]) for a in ads)),pages=sorted({a["page"] for a in ads}),by_day=sorted(Counter(a["started"] for a in act).items(),key=lambda x:P(x[0])),landing=Counter(u.split("?")[0].split("/",3)[-1] for a in ads for u in a["dest"] if t in u).most_common(2),hook=max(ads,key=lambda a:len(a["body"]))["body"][:300])
    else: out[t]={"total":r.get("total"),"captured":0}
    json.dump(out,open("v30_summary.json","w"),indent=1)
    time.sleep(60)
print("V30DONE")
