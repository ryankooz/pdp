# Oct 30 pre-launch check: (1) refresh comparison, (2) fresh backup discovery Oct 16-30, (3) validate.
import json, subprocess, time, re, os, datetime as dt
from collections import Counter, defaultdict
P=lambda s: dt.datetime.strptime(s,"%b %d, %Y").date()
NEW="&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped"
BASE=dict(os.environ, NODE_PATH=subprocess.check_output(["npm","root","-g"],text=True).strip(), SCROLLS="1")
log=open("pre30.log","w")
def L(*a): print(*a,file=log,flush=True)
def run(fn,ph,status,typ,extra=""):
    for k in range(3):
        subprocess.run(["timeout","250","node","scrape.js",fn,ph],env=dict(BASE,STATUS=status,TYPE=typ,EXTRA=extra),capture_output=True)
        try: r=json.load(open(fn))[ph]
        except Exception: r={"ads":[],"total":None}
        if r.get("ads"): return r
        time.sleep(120)
    return r
def summ(ads):
    act=[a for a in ads if a["active"]]
    return dict(captured=len(ads),active=len(act),cut=len(ads)-len(act),first=str(min(P(a["started"]) for a in ads)),
        newest=str(max(P(a["started"]) for a in ads)),pages=sorted({a["page"] for a in ads}),
        by_day=sorted(Counter(a["started"] for a in act).items(),key=lambda x:P(x[0])),
        landing=Counter(u.split("?")[0].split("/",3)[-1] for a in ads for u in a["dest"]).most_common(3),
        hook=max(ads,key=lambda a:len(a["body"]))["body"][:260])
# 1. comparison
cmp={}
for t in ["gloalabs","venalyslab","venalyn","krakensupps","trylevoria","trycirae"]:
    ra=run(f"p30c_{t}_all.json",t,"all","keyword_unordered"); time.sleep(45)
    rn=run(f"p30c_{t}_new.json",t,"active","keyword_unordered",NEW); time.sleep(45)
    ads=list({a["id"]:a for a in ra["ads"]+rn["ads"] if a.get("started") and any(t in u for u in a["dest"])}.values())
    cmp[t]=dict(total_all=ra.get("total"),total_active=rn.get("total"),**(summ(ads) if ads else {"captured":0}))
    json.dump(cmp,open("p30_cmp.json","w"),indent=1); L("cmp",t,len(ads))
# 2. discovery
PH=["I used to be able to","feel like a burden","too embarrassed to","nobody knows","make excuses","play with my grandkids",
 "is this my life now","bloodwork came back normal","brushed me off","feel normal again","travel without worrying","for the rest of my life",
 "I begged my doctor","my colonoscopy","my bloodwork","sold out again","final batch","I prescribe every day",
 "UTI","bladder leaks","urinary tract","my urologist","D-mannose","leak when I laugh","up all night to pee",
 "after menopause","women over 40","women over 50","hot flashes","vaginal dryness"]
KILL=set(open("killlist.txt").read().split())|{"gloalabs","venalys","venalyn","trycirae","krakensupps","cladeprotocol","getbottomsup","trylevoria","shopdazara","dermanouriva","lanural","bottomsup"}
try: KILL|={c[0].split(".")[0] for c in json.load(open("sweep_cands.json"))}
except Exception: pass
BIG=re.compile(r"amazon|walmart|target|instagram|facebook|youtube|cvs|walgreens|reelshort|drama|insur|bank|casino|\.gov|\.edu|google|apple|tiktok|hims|hers|ro\.co|poise|always|tena|azo",re.I)
def dom(u):
    h=u.split("/")[2].lower() if u.startswith("http") else ""
    return re.sub(r"^(www|shop|try|get|go|secure|order|trk|track|lp|info)\.","",h)
groups=defaultdict(dict)
for i,ph in enumerate(PH):
    r=run(f"p30d_{i}.json",ph,"active","keyword_exact_phrase",NEW)
    for a in r.get("ads",[]):
        dm=next((dom(u) for u in a["dest"] if dom(u)),"")
        if dm and a.get("started"): groups[dm][a["id"]]={**a,"phrase":ph}
    L("disc",ph,r.get("total"),len(r.get("ads",[]))); time.sleep(45)
cands=[]
for dm,ads in groups.items():
    ads=list(ads.values()); ds=sorted(P(a["started"]) for a in ads); pages={a["page"] for a in ads}
    if BIG.search(dm) or any(k in dm for k in KILL): continue
    if ds[0]>=dt.date(2026,10,16) and (len(ads)>=3 or len(pages)>=2):
        cands.append((dm,len(ads),len(pages),str(ds[0]),str(ds[-1]),sorted({a["phrase"] for a in ads}),ads[0]["body"][:200]))
cands.sort(key=lambda c:(-c[2],-c[1]))
json.dump(cands,open("p30_cands.json","w"),indent=1); L("CANDS",len(cands))
# 3. validate
val={}
for dm,*_ in cands[:10]:
    tok=dm.split(".")[0]
    r=run(f"p30v_{tok}.json",tok,"all","keyword_unordered")
    ads=[a for a in r.get("ads",[]) if a.get("started") and any(tok in u for u in a["dest"])]
    val[dm]=dict(total=r.get("total"),**(summ(ads) if ads else {"captured":0}))
    json.dump(val,open("p30_val.json","w"),indent=1); L("val",dm,len(ads)); time.sleep(60)
L("P30DONE")
