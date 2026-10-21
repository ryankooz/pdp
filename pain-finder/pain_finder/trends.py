"""Google Trends checks via pytrends (unofficial, rate-limited by Google).

For each keyword we pull 5 years of weekly interest and compute:

  yoy          last 12 weeks vs the same 12 weeks a year earlier (cancels
               seasonality, so a winter-only problem isn't flagged as rising)
  slope_pct    linear trend over the last 2 years, % of average per year
  growth_5y    last 26 weeks vs the first 26 weeks of the window
  verdict      rising fast / rising / stable / declining / no data

and the "rising" related queries, which are often the sharpest sub-problems
(anything marked Breakout grew more than 5000%).
"""

import json
import sys
import time

import numpy as np

from .reddit import _Cache

VERDICT_MULTIPLIER = {"rising fast": 1.6, "rising": 1.3, "stable": 1.0,
                      "declining": 0.7, "no data": 0.9, "error": 1.0}
_BLOCKS = " ▁▂▃▄▅▆▇█"


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def sparkline(values):
    if not values:
        return ""
    hi = max(values) or 1
    return "".join(_BLOCKS[min(8, round(v / hi * 8))] for v in values)


def analyse_series(values):
    """values: weekly interest (0-100), oldest first, partial week removed."""
    v = np.asarray(values, dtype=float)
    if len(v) < 60 or v.mean() < 1:
        return {"verdict": "no data", "mean": round(float(v.mean()), 1) if len(v) else 0}
    recent, year_ago = v[-12:].mean(), v[-64:-52].mean()
    yoy = recent / year_ago if year_ago > 0 else (2.0 if recent > 0 else 1.0)
    last2 = v[-104:]
    slope = np.polyfit(np.arange(len(last2)), last2, 1)[0] * 52
    slope_pct = slope / max(last2.mean(), 1e-9) * 100
    first = v[:26].mean()
    growth_5y = v[-26:].mean() / first if first > 0 else None

    if yoy >= 1.25 and slope_pct > 0:
        verdict = "rising fast"
    elif yoy >= 1.08 or slope_pct >= 10:
        verdict = "rising"
    elif yoy <= 0.85 and slope_pct < 0:
        verdict = "declining"
    else:
        verdict = "stable"
    monthly = [round(float(v[i:i + 4].mean())) for i in range(max(0, len(v) - 104), len(v), 4)]
    return {
        "verdict": verdict,
        "yoy": round(float(yoy), 2),
        "slope_pct": round(float(slope_pct), 1),
        "growth_5y": round(float(growth_5y), 2) if growth_5y else None,
        "mean": round(float(v.mean()), 1),
        "recent": round(float(recent), 1),
        "spark": sparkline(monthly),
    }


class Trends:
    def __init__(self, geo="", timeframe="today 5-y", cache_dir=".cache/trends",
                 cache_hours=72, pause=6.0):
        from pytrends.request import TrendReq
        self.req = TrendReq(hl="en-US", tz=0, timeout=(10, 30))
        self.geo, self.timeframe, self.pause = geo, timeframe, pause
        self.cache = _Cache(cache_dir, cache_hours)
        self._last = 0.0

    def _throttled(self, fn):
        for attempt in range(4):
            wait = self.pause - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            try:
                return fn()
            except Exception as e:  # pytrends raises a variety of errors on 429
                msg = str(e)
                if "429" in msg or "TooManyRequests" in type(e).__name__:
                    delay = 30 * (attempt + 1)
                    log(f"  Google Trends rate limit, waiting {delay}s")
                    time.sleep(delay)
                    continue
                raise
        raise RuntimeError("Google Trends kept rate-limiting; try again later or use --skip-trends")

    def check(self, keyword, related=True):
        key = json.dumps([keyword, self.geo, self.timeframe, related])
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        try:
            def fetch():
                self.req.build_payload([keyword], timeframe=self.timeframe, geo=self.geo)
                return self.req.interest_over_time()
            df = self._throttled(fetch)
            if df is None or df.empty or keyword not in df:
                result = {"keyword": keyword, "verdict": "no data"}
            else:
                if "isPartial" in df:
                    df = df[~df["isPartial"].astype(bool)]
                result = {"keyword": keyword, **analyse_series(df[keyword].tolist())}
            result["rising_queries"] = []
            if related and result["verdict"] != "no data":
                rq = self._throttled(self.req.related_queries).get(keyword, {}).get("rising")
                if rq is not None and not rq.empty:
                    result["rising_queries"] = [
                        [row["query"], "Breakout" if row["value"] >= 5000 else f"+{int(row['value'])}%"]
                        for _, row in rq.head(10).iterrows()
                    ]
        except RuntimeError:
            raise
        except Exception as e:
            log(f"  trends error for '{keyword}': {e}")
            return {"keyword": keyword, "verdict": "error", "error": str(e)[:200]}
        self.cache.put(key, result)
        return result
