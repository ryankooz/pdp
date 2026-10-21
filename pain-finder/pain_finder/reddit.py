"""Reddit fetching with three interchangeable backends.

oauth     Official API (oauth.reddit.com). Needs REDDIT_CLIENT_ID and
          REDDIT_CLIENT_SECRET from https://www.reddit.com/prefs/apps (free,
          pick "script"). 100 requests/minute. Most reliable.
public    The anonymous .json endpoints. No setup, ~10 requests/minute, and
          Reddit blocks it from most cloud/VPN IPs (works from home internet).
pullpush  The PullPush archive (api.pullpush.io). No setup and searchable
          years back, but scores/comment counts can lag behind live Reddit.

`auto` picks oauth when credentials are set, otherwise tries public and falls
back to pullpush if Reddit refuses.
"""

import hashlib
import json
import os
import sys
import time
from pathlib import Path

import requests

USER_AGENT = os.environ.get(
    "REDDIT_USER_AGENT", "pain-finder/1.0 (problem research script)"
)
TIME_WINDOWS = {"day": 86400, "week": 604800, "month": 2_592_000,
                "year": 31_536_000, "all": None}


class RedditBlocked(Exception):
    pass


def log(msg):
    print(msg, file=sys.stderr, flush=True)


class _Cache:
    def __init__(self, root, ttl_hours):
        self.root = Path(root)
        self.ttl = ttl_hours * 3600
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key):
        return self.root / (hashlib.sha1(key.encode()).hexdigest() + ".json")

    def get(self, key):
        p = self._path(key)
        if self.ttl > 0 and p.exists() and time.time() - p.stat().st_mtime < self.ttl:
            return json.loads(p.read_text())
        return None

    def put(self, key, value):
        self._path(key).write_text(json.dumps(value))


class _Http:
    def __init__(self, min_interval, cache):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.min_interval = min_interval
        self.cache = cache
        self._last = 0.0

    def get_json(self, url, params=None, headers=None):
        key = url + "?" + json.dumps(params or {}, sort_keys=True)
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        for attempt in range(5):
            wait = self.min_interval - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            try:
                r = self.session.get(url, params=params, headers=headers, timeout=30)
            except requests.RequestException as e:
                log(f"  network error ({e.__class__.__name__}), retrying")
                time.sleep(2 ** attempt * 2)
                continue
            if r.status_code == 429 or r.status_code >= 500:
                delay = float(r.headers.get("Retry-After") or min(15 * 2 ** attempt, 120))
                log(f"  {r.status_code} from {url.split('/')[2]}, waiting {delay:.0f}s")
                time.sleep(delay)
                continue
            if r.status_code in (401, 403):
                raise RedditBlocked(f"{r.status_code} from {url}")
            r.raise_for_status()
            if "json" not in r.headers.get("Content-Type", ""):
                raise RedditBlocked(f"non-JSON response from {url}")
            data = r.json()
            self.cache.put(key, data)
            return data
        raise RuntimeError(f"giving up on {url} after retries")


def _post_from_listing(d):
    return {
        "id": d["id"],
        "title": d.get("title") or "",
        "body": d.get("selftext") or "",
        "subreddit": d.get("subreddit") or "",
        "score": d.get("score") or 0,
        "num_comments": d.get("num_comments") or 0,
        "created_utc": int(d.get("created_utc") or 0),
        "permalink": "https://www.reddit.com" + (d.get("permalink") or f"/comments/{d['id']}"),
        "over_18": bool(d.get("over_18")),
    }


def _flatten_comments(children, out, depth=0):
    for c in children:
        if c.get("kind") != "t1":
            continue
        d = c["data"]
        body = d.get("body") or ""
        if body and body not in ("[deleted]", "[removed]"):
            out.append({"body": body, "score": d.get("score") or 0, "depth": depth})
        replies = d.get("replies")
        if isinstance(replies, dict):
            _flatten_comments(replies["data"]["children"], out, depth + 1)


class _RedditListingBackend:
    """Shared code for oauth and public: same JSON shape, different host/auth."""

    base = ""

    def _headers(self):
        return None

    def search(self, query, subreddit=None, sort="relevance", time_filter="year", limit=100):
        path = f"/r/{subreddit}/search" if subreddit else "/search"
        posts, after = [], None
        while len(posts) < limit:
            params = {"q": query, "sort": sort, "t": time_filter, "limit": 100,
                      "type": "link", "raw_json": 1}
            if subreddit:
                params["restrict_sr"] = 1
            if after:
                params["after"] = after
            data = self.http.get_json(self.base + path + self._suffix, params, self._headers())
            children = data["data"]["children"]
            posts.extend(_post_from_listing(c["data"]) for c in children if c["kind"] == "t3")
            after = data["data"].get("after")
            if not after or not children:
                break
        return posts[:limit]

    def comments(self, post_id, limit=200):
        data = self.http.get_json(
            f"{self.base}/comments/{post_id}{self._suffix}",
            {"limit": limit, "depth": 3, "sort": "top", "raw_json": 1},
            self._headers(),
        )
        out = []
        if isinstance(data, list) and len(data) > 1:
            _flatten_comments(data[1]["data"]["children"], out)
        return out[:limit]


class OAuthBackend(_RedditListingBackend):
    name = "oauth"
    base = "https://oauth.reddit.com"
    _suffix = ""

    def __init__(self, cache):
        self.http = _Http(0.7, cache)
        self._token, self._expires = None, 0

    def _headers(self):
        if time.time() > self._expires - 60:
            r = requests.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=(os.environ["REDDIT_CLIENT_ID"], os.environ["REDDIT_CLIENT_SECRET"]),
                data={"grant_type": "client_credentials"},
                headers={"User-Agent": USER_AGENT}, timeout=30,
            )
            if r.status_code != 200:
                raise SystemExit(f"Reddit OAuth failed ({r.status_code}): check REDDIT_CLIENT_ID / SECRET")
            tok = r.json()
            self._token, self._expires = tok["access_token"], time.time() + tok.get("expires_in", 3600)
        return {"Authorization": f"bearer {self._token}"}


class PublicBackend(_RedditListingBackend):
    name = "public"
    base = "https://www.reddit.com"
    _suffix = ".json"

    def __init__(self, cache):
        self.http = _Http(6.5, cache)


class PullPushBackend:
    name = "pullpush"
    # The archive snapshots posts when they're created, so score/num_comments
    # are often near zero. Comments are still archived; read them regardless.
    stale_counts = True
    base = "https://api.pullpush.io/reddit/search"

    def __init__(self, cache):
        self.http = _Http(6.0, cache)

    def search(self, query, subreddit=None, sort="relevance", time_filter="year", limit=100):
        sort_type = {"top": "score", "comments": "num_comments", "new": "created_utc"}.get(sort, "score")
        params = {"q": query, "size": min(limit, 100), "sort_type": sort_type, "sort": "desc"}
        if subreddit:
            params["subreddit"] = subreddit
        window = TIME_WINDOWS.get(time_filter)
        if window:
            params["after"] = int(time.time()) - window
        posts = []
        while len(posts) < limit:
            data = self.http.get_json(self.base + "/submission/", params)
            rows = data.get("data") or []
            posts.extend(_post_from_listing(d) for d in rows)
            if len(rows) < params["size"] or sort_type != "created_utc":
                break
            params["before"] = rows[-1]["created_utc"]
        return posts[:limit]

    def comments(self, post_id, limit=200):
        data = self.http.get_json(self.base + "/comment/", {
            "link_id": post_id, "size": min(limit, 100), "sort_type": "score", "sort": "desc",
        })
        return [{"body": d.get("body") or "", "score": d.get("score") or 0, "depth": 0}
                for d in data.get("data") or []
                if d.get("body") not in (None, "", "[deleted]", "[removed]")]


class Reddit:
    """Facade that picks a backend and transparently falls back."""

    def __init__(self, backend="auto", cache_dir=".cache/reddit", cache_hours=24):
        cache = _Cache(cache_dir, cache_hours)
        has_creds = os.environ.get("REDDIT_CLIENT_ID") and os.environ.get("REDDIT_CLIENT_SECRET")
        if backend == "oauth" or (backend == "auto" and has_creds):
            if not has_creds:
                raise SystemExit("--backend oauth needs REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
            self.chain = [OAuthBackend(cache)]
        elif backend == "public":
            self.chain = [PublicBackend(cache)]
        elif backend == "pullpush":
            self.chain = [PullPushBackend(cache)]
        else:
            self.chain = [PublicBackend(cache), PullPushBackend(cache)]
        log(f"Reddit backend: {self.chain[0].name}"
            + (f" (fallback: {self.chain[1].name})" if len(self.chain) > 1 else ""))

    def _call(self, method, *args, **kwargs):
        while True:
            try:
                return getattr(self.chain[0], method)(*args, **kwargs)
            except RedditBlocked as e:
                if len(self.chain) == 1:
                    raise SystemExit(
                        f"Reddit refused the request ({e}). Set REDDIT_CLIENT_ID/SECRET "
                        "for the official API, or use --backend pullpush."
                    )
                log(f"  {self.chain[0].name} blocked ({e}); switching to {self.chain[1].name}")
                self.chain.pop(0)

    def search(self, *args, **kwargs):
        return self._call("search", *args, **kwargs)

    def comments(self, *args, **kwargs):
        return self._call("comments", *args, **kwargs)

    @property
    def stale_counts(self):
        return getattr(self.chain[0], "stale_counts", False)

    @property
    def backend_name(self):
        return self.chain[0].name
