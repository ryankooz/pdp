"""CJ Dropshipping catalog search for the validated problems (official API).

Setup: in CJ, install the API app (Apps), then Personal Center > API > Add API >
API Key, and export it:  export CJ_API_KEY="CJ1234567@api@..."

The API allows 1 request/second; free accounts get about 1000 product-list
calls a day (100 products per call). Results are cached for a week.

For each problem we search a set of product keywords, keep products whose name
actually matches, and report count, price range, and listedNum (how many CJ
stores already list it: a demand signal, but also competition).
"""

import json
import os
import statistics
import time
from pathlib import Path

import requests

from .reddit import _Cache, log

BASE = "https://developers.cjdropshipping.com/api2.0/v1"

# Product keywords per validated problem. Names match the pain-finder findings.
PROBLEMS = {
    "body odor": ["chlorophyll", "internal deodorant", "body odor", "deodorant", "antiperspirant", "underarm",
                  "armpit", "sweat pads", "body wash odor", "zinc supplement", "digestive enzyme",
                  "probiotic", "magnesium", "feminine odor", "ph balance"],
    "gut / bloating / IBS": ["probiotic", "prebiotic", "digestive enzyme", "bloating", "gut health", "fiber",
                             "psyllium", "colon", "detox", "peppermint oil", "ginger capsule",
                             "apple cider vinegar", "berberine", "l-glutamine", "constipation"],
    "brain fog / focus": ["lions mane", "nootropic", "magnesium glycinate", "magnesium l-threonate", "l-theanine",
                          "creatine", "omega 3", "fish oil", "vitamin b12", "focus supplement", "memory supplement",
                          "ginkgo", "rhodiola"],
    "PCOS / hormones": ["inositol", "myo-inositol", "spearmint", "berberine", "hormone balance", "dim supplement",
                        "vitex", "chasteberry", "evening primrose"],
    "histamine / MCAS": ["quercetin", "dao enzyme", "nettle", "histamine", "vitamin c", "bromelain"],
    "dandruff / scalp": ["dandruff", "anti dandruff", "ketoconazole", "scalp serum", "scalp massager",
                         "scalp scrub", "seborrheic", "zinc pyrithione", "tea tree shampoo"],
    "excessive sweating": ["sweat pads", "antiperspirant", "iontophoresis", "sweat", "hyperhidrosis",
                           "underarm pads"],
    "incontinence / pelvic floor": ["incontinence", "kegel", "pelvic floor", "leak proof underwear",
                                    "bladder", "adult diaper"],
    "bruxism / jaw": ["night guard", "mouth guard", "teeth grinding", "jaw exerciser", "tmj"],
    "plantar fasciitis / feet": ["plantar fasciitis", "night splint", "arch support", "orthotic insoles",
                                 "heel pain"],
    "eczema / dry skin": ["eczema", "colloidal oatmeal", "ceramide cream", "itch relief", "wet wrap",
                          "psoriasis"],
    "acne": ["acne patch", "pimple patch", "acne", "blue light acne", "benzoyl", "salicylic"],
    "sleep": ["sleep supplement", "melatonin", "magnesium spray", "sleep mask", "mouth tape", "white noise"],
}


class CJ:
    def __init__(self, api_key=None, cache_hours=24 * 7, cache_dir=".cache/cj"):
        self.api_key = api_key or os.environ.get("CJ_API_KEY")
        # Without a key, assume a network secret injects the CJ-Access-Token header for us.
        self.injected = not self.api_key
        self.cache = _Cache(cache_dir, cache_hours)
        self.token_file = Path(cache_dir) / "token.json"
        self.s = requests.Session()
        self._last = 0.0
        self.calls = 0

    def _token(self):
        if self.token_file.exists():
            t = json.loads(self.token_file.read_text())
            if t.get("apiKey") == self.api_key[-8:] and t.get("expires", 0) > time.time() + 3600:
                return t["accessToken"]
        r = self._post("/authentication/getAccessToken", {"apiKey": self.api_key})
        data = r.get("data") or {}
        if not data.get("accessToken"):
            raise SystemExit(f"CJ login failed: {r.get('message')}")
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        self.token_file.write_text(json.dumps({"accessToken": data["accessToken"], "apiKey": self.api_key[-8:],
                                               "expires": time.time() + 170 * 86400}))
        return data["accessToken"]

    def _wait(self):
        gap = 1.1 - (time.time() - self._last)
        if gap > 0:
            time.sleep(gap)
        self._last = time.time()

    def _post(self, path, body):
        self._wait()
        return self.s.post(BASE + path, json=body, timeout=30).json()

    def get(self, path, params):
        key = json.dumps([path, params], sort_keys=True)
        hit = self.cache.get(key)
        if hit is not None:
            return hit
        headers = {} if self.injected else {"CJ-Access-Token": self._token()}
        for attempt in range(4):
            self._wait()
            self.calls += 1
            r = self.s.get(BASE + path, params=params, headers=headers, timeout=30)
            try:
                data = r.json()
            except ValueError:
                data = {"result": False, "message": r.text[:200]}
            if r.status_code in (402, 406, 429) or data.get("code") in (1600200, 1600300):
                log(f"  CJ rate limit ({r.status_code} {data.get('message')}), waiting")
                time.sleep(5 * (attempt + 1))
                continue
            if self.injected and data.get("code") == 1600002:
                raise SystemExit(
                    "No CJ credentials. Set CJ_API_KEY (environment variable), or add a network secret for "
                    "developers.cjdropshipping.com with header CJ-Access-Token = your CJ access token.")
            if not data.get("result", data.get("success", False)):
                raise RuntimeError(f"CJ {path}: {data.get('code')} {data.get('message')}")
            self.cache.put(key, data)
            return data
        raise RuntimeError(f"CJ {path}: still rate limited")

    def categories(self):
        return self.get("/product/getCategory", {}).get("data") or []

    def search(self, keyword=None, pages=1, size=100, category_id=None, country=None):
        """Products for a keyword (or a whole category when keyword is None)."""
        out = []
        for page in range(1, pages + 1):
            params = {"page": page, "size": size}
            if keyword:
                params["keyWord"] = keyword
            if category_id:
                params["categoryId"] = category_id
            if country:
                params["countryCode"] = country
            data = self.get("/product/listV2", params).get("data") or {}
            rows = []
            for block in data.get("content") or []:
                rows += block.get("productList") or []
            out += [_product(p) for p in rows]
            if len(rows) < size:
                break
        return out


def _product(p):
    pid = p.get("id") or p.get("pid")
    price = p.get("nowPrice") or p.get("sellPrice") or p.get("discountPrice")
    try:
        price_num = float(str(price).split("-")[0])
    except (TypeError, ValueError):
        price_num = None
    return {
        "pid": pid, "name": p.get("nameEn") or p.get("productNameEn") or "",
        "sku": p.get("sku") or p.get("productSku"), "price": price, "price_num": price_num,
        "listed": int(p.get("listedNum") or 0),
        "category": p.get("threeCategoryName") or p.get("categoryName") or p.get("twoCategoryName") or "",
        "inventory": p.get("warehouseInventoryNum"), "supplier": p.get("supplierName"),
        "image": p.get("bigImage") or p.get("productImage"),
        "link": f"https://cjdropshipping.com/product/-p-{pid}.html" if pid else "",
    }


def _matches(name, keyword):
    n = name.lower()
    return all(w in n for w in keyword.lower().replace("-", " ").split() if len(w) > 2)


def scan(cj, problems, pages=1, country=None):
    """{problem: {"products": [...], "by_keyword": {kw: n}}} with name-matched, de-duplicated products."""
    out = {}
    for prob in problems:
        seen, prods, by_kw = set(), [], {}
        for kw in PROBLEMS[prob]:
            try:
                found = cj.search(kw, pages=pages, country=country)
            except RuntimeError as e:
                log(f"  {prob} / {kw}: {e}")
                continue
            hits = [p for p in found if _matches(p["name"], kw)]
            by_kw[kw] = len(hits)
            for p in hits:
                if p["pid"] not in seen:
                    seen.add(p["pid"])
                    prods.append({**p, "keyword": kw})
            log(f"  {prob} / {kw}: {len(found)} results, {len(hits)} matching")
        prods.sort(key=lambda p: -p["listed"])
        out[prob] = {"products": prods, "by_keyword": by_kw}
    return out


def write_report(out_dir, res, meta):
    import csv
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "cj.json").write_text(json.dumps({"meta": meta, "results": res}, indent=2, default=str))
    with open(out / "cj_products.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["problem", "keyword", "product", "price", "stores_listing", "category", "inventory",
                    "sku", "link"])
        for prob, r in res.items():
            for p in r["products"]:
                w.writerow([prob, p["keyword"], p["name"], p["price"], p["listed"], p["category"],
                            p["inventory"], p["sku"], p["link"]])
    L = ["# CJ Dropshipping: products for the validated problems", "",
         f"{meta['run_at']} · {meta['api_calls']} API calls · keywords per problem in `pain_finder/cj.py`", "",
         "**Stores listing** = how many CJ stores already list the product. High means proven demand "
         "and more competition; zero means untested.", "",
         "| Problem | Products found | Price range | Median | Most-listed product (stores) |",
         "|---|---|---|---|---|"]
    for prob, r in res.items():
        ps = r["products"]
        prices = [p["price_num"] for p in ps if p["price_num"]]
        top = ps[0] if ps else None
        L.append(f"| **{prob}** | {len(ps)} | "
                 + (f"${min(prices):.2f}–${max(prices):.2f} | ${statistics.median(prices):.2f}" if prices else "– | –")
                 + (f" | {top['name'][:60]} ({top['listed']})" if top else " | –") + " |")
    for prob, r in res.items():
        L += ["", f"## {prob}", "",
              "Searched: " + ", ".join(f"`{k}` ({n})" for k, n in r["by_keyword"].items()), ""]
        if not r["products"]:
            L.append("Nothing on CJ matched these keywords.")
            continue
        L += ["| Product | Price | Stores | Category |", "|---|---|---|---|"]
        for p in r["products"][:15]:
            L.append(f"| [{p['name'][:80].replace('|', '/')}]({p['link']}) | ${p['price']} | {p['listed']} | "
                     f"{p['category']} |")
    (out / "cj.md").write_text("\n".join(L) + "\n")
    return out
