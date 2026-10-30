import json, subprocess, time, os, datetime as dt
from collections import Counter
P=lambda s: dt.datetime.strptime(s,"%b %d, %Y").date()
BASE=dict(os.environ, NODE_PATH=subprocess.check_output(["npm","root","-g"],text=True).strip(), SCROLLS="1", TYPE="keyword_unordered")
NEW="&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped"
toks={"gloalabs":"gloalabs","venalyslab":"venalyslab","venalys.shop":"venalys.shop","venalyn":"venalyn","trycirae":"trycirae","krakensupps":"krakensupps","trylevoria":"trylevoria"}
out={}
def run(t,status,extra,fn):
    for attempt in range(3):
        subprocess.run(["timeout","250","node","scrape.js",fn,t],env=dict(BASE,STATUS=status,EXTRA=extra),capture_output=True)
        try: r=json.load(open(fn))[t]
        except Exception: r={"ads":[],"total":None}
        if r.get("ads"): return r
        time.sleep(120)
    return r
for t,key in toks.items():
    ra=run(t,"all","",f"k28_{t}_all.json"); time.sleep(50)
    rn=run(t,"active",NEW,f"k28_{t}_new.json"); time.sleep(50)
    ads={a["id"]:a for a in ra["ads"]+rn["ads"] if a.get("started") and any(key in u for u in a["dest"])}.values()
    ads=list(ads)
    if ads:
        act=[a for a in ads if a["active"]]
        out[t]=dict(total_all=ra.get("total"),total_active=rn.get("total"),captured=len(ads),active=len(act),cut=len(ads)-len(act),
            first=str(min(P(a["started"]) for a in ads)),newest=str(max(P(a["started"]) for a in ads)),
            pages=sorted({a["page"] for a in ads}),
            by_day=sorted(Counter(a["started"] for a in act).items(),key=lambda x:P(x[0])),
            landing=Counter(u.split("?")[0].split("/",3)[-1] for a in ads for u in a["dest"] if key in u).most_common(3))
    else: out[t]={"total_all":ra.get("total"),"total_active":rn.get("total"),"captured":0}
    json.dump(out,open("k28_summary.json","w"),indent=1)
print("K28DONE")
