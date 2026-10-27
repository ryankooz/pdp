"""One fetcher per source. Each returns a list of Job objects and never raises:
a source that's down just logs a warning so the rest of the run still works."""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone

import requests

UA = {"User-Agent": "Mozilla/5.0 (job-scraper; personal use)"}
TIMEOUT = 20

# Boards that only list remote jobs. Jobs from these are remote by definition;
# everything else has to prove it (see filters.is_remote).
REMOTE_ONLY_SOURCES = {
    "Remotive", "RemoteOK", "We Work Remotely", "Working Nomads", "Jobicy",
    "Himalayas", "Jobspresso",
}


@dataclass
class Job:
    title: str
    company: str
    url: str
    source: str
    location: str = ""
    posted: datetime | None = None
    salary: str = ""
    description: str = ""
    remote_flag: bool | None = None  # what the source itself says, if anything
    score: int = 0
    tier: str = ""
    why: list[str] = field(default_factory=list)
    is_new: bool = False


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def parse_date(value) -> datetime | None:
    if value in (None, ""):
        return None
    try:
        if isinstance(value, (int, float)) or str(value).isdigit():
            ts = int(value)
            if ts > 10**11:  # milliseconds
                ts //= 1000
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        s = str(value).replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(s)
        except ValueError:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def money(lo, hi, period="") -> str:
    def fmt(v):
        try:
            v = float(v)
        except (TypeError, ValueError):
            return ""
        if v <= 0:
            return ""
        return f"${v/1000:.0f}k" if v >= 1000 else f"${v:,.0f}"
    lo, hi = fmt(lo), fmt(hi)
    if not lo and not hi:
        return ""
    s = f"{lo}–{hi}" if lo and hi and lo != hi else (lo or hi)
    return f"{s}/{period}" if period and period not in ("year", "yearly", "annual") else s


def _get(url, **kw):
    for attempt in range(2):  # one retry: some APIs (Lever) time out now and then
        try:
            r = requests.get(url, headers=UA, timeout=TIMEOUT, **kw)
            r.raise_for_status()
            return r
        except requests.RequestException:
            if attempt:
                raise


# --------------------------------------------------------------------------
# Remote-only job boards
# --------------------------------------------------------------------------

def remotive(searches):
    jobs = []
    for cat in ("writing", "marketing"):
        for j in _get(f"https://remotive.com/api/remote-jobs?category={cat}").json()["jobs"]:
            jobs.append(Job(
                title=j["title"], company=j["company_name"], url=j["url"],
                source="Remotive", location=j.get("candidate_required_location", ""),
                posted=parse_date(j.get("publication_date")), salary=j.get("salary") or "",
                description=strip_html(j.get("description")), remote_flag=True,
            ))
    return jobs


def remoteok(searches):
    data = _get("https://remoteok.com/api").json()
    jobs = []
    for j in data[1:]:  # first item is the API legal notice
        jobs.append(Job(
            title=j.get("position", ""), company=j.get("company", ""), url=j.get("url", ""),
            source="RemoteOK", location=j.get("location", ""), posted=parse_date(j.get("date")),
            salary=money(j.get("salary_min"), j.get("salary_max")),
            description=strip_html(j.get("description")) + " " + " ".join(j.get("tags") or []),
            remote_flag=True,
        ))
    return jobs


def _rss_items(url):
    root = ET.fromstring(_get(url).content)
    for item in root.iter("item"):
        yield {child.tag.split("}")[-1]: (child.text or "") for child in item}


def weworkremotely(searches):
    jobs = []
    for cat in ("remote-sales-and-marketing-jobs", "all-other-remote-jobs"):
        for it in _rss_items(f"https://weworkremotely.com/categories/{cat}.rss"):
            company, _, title = it.get("title", "").partition(": ")
            jobs.append(Job(
                title=title or company, company=company if title else "", url=it.get("link", ""),
                source="We Work Remotely", location=it.get("region", ""),
                posted=parse_date(it.get("pubDate")), description=strip_html(it.get("description")),
                remote_flag=True,
            ))
    return jobs


def workingnomads(searches):
    jobs = []
    for j in _get("https://www.workingnomads.com/api/exposed_jobs/").json():
        jobs.append(Job(
            title=j["title"], company=j.get("company_name", ""), url=j["url"],
            source="Working Nomads", location=j.get("location", ""),
            posted=parse_date(j.get("pub_date")),
            description=strip_html(j.get("description")) + " " + (j.get("tags") or ""),
            remote_flag=True,
        ))
    return jobs


def jobicy(searches):
    jobs, seen = [], set()
    for tag in ("copywriter", "copywriting", "marketing", "content"):
        data = _get(f"https://jobicy.com/api/v2/remote-jobs?count=100&tag={tag}").json()
        for j in data.get("jobs", []):
            if j["id"] in seen:
                continue
            seen.add(j["id"])
            jobs.append(Job(
                title=html.unescape(j["jobTitle"]), company=j.get("companyName", ""), url=j["url"],
                source="Jobicy", location=j.get("jobGeo", ""), posted=parse_date(j.get("pubDate")),
                salary=money(j.get("annualSalaryMin"), j.get("annualSalaryMax")),
                description=strip_html(j.get("jobDescription")), remote_flag=True,
            ))
    return jobs


def himalayas(searches):
    jobs, seen = [], set()
    for q in searches:
        data = _get("https://himalayas.app/jobs/api/search", params={"q": q}).json()
        for j in data.get("jobs", []):
            url = j.get("applicationLink") or j.get("guid")
            if url in seen:
                continue
            seen.add(url)
            jobs.append(Job(
                title=j["title"], company=j.get("companyName", ""), url=url, source="Himalayas",
                location=", ".join(j.get("locationRestrictions") or []) or "Anywhere",
                posted=parse_date(j.get("pubDate")),
                salary=money(j.get("minSalary"), j.get("maxSalary"), j.get("salaryPeriod") or ""),
                description=strip_html(j.get("description")), remote_flag=True,
            ))
    return jobs


def jobspresso(searches):
    jobs = []
    for it in _rss_items("https://jobspresso.co/feed/?post_type=job_listing"):
        jobs.append(Job(
            title=html.unescape(it.get("title", "")), company="", url=it.get("link", ""),
            source="Jobspresso", posted=parse_date(it.get("pubDate")),
            description=strip_html(it.get("encoded") or it.get("description")), remote_flag=True,
        ))
    return jobs


# --------------------------------------------------------------------------
# Indeed (via JobSpy, using Indeed's own "Remote" filter)
# --------------------------------------------------------------------------

def indeed(searches, days=14, per_search=40):
    from jobspy import scrape_jobs

    jobs = []
    for q in searches:
        try:
            df = scrape_jobs(
                site_name=["indeed"], search_term=q, is_remote=True,
                results_wanted=per_search, hours_old=days * 24, country_indeed="USA",
                verbose=0,
            )
        except Exception as e:
            print(f"  ! Indeed '{q}': {e}")
            continue
        for _, r in df.iterrows():
            def val(k):
                v = r.get(k)
                return "" if v is None or (isinstance(v, float) and v != v) else v
            jobs.append(Job(
                title=str(val("title")), company=str(val("company")), url=str(val("job_url")),
                source="Indeed", location=str(val("location")), posted=parse_date(str(val("date_posted"))),
                salary=money(val("min_amount"), val("max_amount"), str(val("interval"))),
                description=str(val("description")), remote_flag=bool(val("is_remote")),
            ))
    return jobs


# --------------------------------------------------------------------------
# Company boards (Ashby / Greenhouse / Lever): first-party listings from
# health, wellness and DTC brands. Remote is checked per job.
# --------------------------------------------------------------------------

def _ashby(name, slug):
    data = _get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true").json()
    out = []
    for j in data.get("jobs", []):
        comp = (j.get("compensation") or {}).get("compensationTierSummary") or ""
        out.append(Job(
            title=j["title"], company=name, url=j.get("jobUrl", ""), source="Company board",
            location=j.get("location", ""), posted=parse_date(j.get("publishedAt")), salary=comp,
            description=strip_html(j.get("descriptionHtml")),
            remote_flag=bool(j.get("isRemote")) or j.get("workplaceType") == "Remote",
        ))
    return out


def _greenhouse(name, slug):
    data = _get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true").json()
    out = []
    for j in data.get("jobs", []):
        loc = (j.get("location") or {}).get("name", "")
        out.append(Job(
            title=j["title"], company=name, url=j.get("absolute_url", ""), source="Company board",
            location=loc, posted=parse_date(j.get("updated_at")),
            description=strip_html(html.unescape(j.get("content") or "")),
            remote_flag="remote" in loc.lower() or None,
        ))
    return out


def _lever(name, slug):
    data = _get(f"https://api.lever.co/v0/postings/{slug}?mode=json").json()
    out = []
    for j in data:
        cats = j.get("categories") or {}
        loc = cats.get("location") or ", ".join(cats.get("allLocations") or [])
        sal = j.get("salaryRange") or {}
        out.append(Job(
            title=j["text"], company=name, url=j.get("hostedUrl", ""), source="Company board",
            location=loc, posted=parse_date(j.get("createdAt")),
            salary=money(sal.get("min"), sal.get("max")),
            description=strip_html(j.get("descriptionPlain") or j.get("description")),
            remote_flag=(j.get("workplaceType") == "remote") or ("remote" in loc.lower()) or None,
        ))
    return out


def company_boards(boards):
    fetch = {"ashby": _ashby, "greenhouse": _greenhouse, "lever": _lever}
    jobs = []
    for name, ats, slug in boards:
        try:
            jobs.extend(fetch[ats](name, slug))
        except Exception as e:
            print(f"  ! {name} ({ats}): {e}")
    return jobs
