"""Remote verification, region check, BS filter and fit scoring."""

import re

import config
from sources import REMOTE_ONLY_SOURCES, Job

US_STATES = set("""AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS
MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC""".split())


def _has(text: str, phrase: str) -> bool:
    # Whole-word match so "uk" doesn't hit "ukulele" and "seo" doesn't hit "seoul".
    return re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", text) is not None


def is_remote(job: Job) -> bool:
    head = f"{job.title} {job.location}".lower()
    if any(_has(head, p) for p in config.NOT_REMOTE_PHRASES):
        return False
    desc = job.description.lower()
    if any(p in desc for p in config.NOT_REMOTE_DESC_PHRASES):
        return False
    if job.source in REMOTE_ONLY_SOURCES:
        return True
    # Indeed / company boards must explicitly say remote.
    return bool(job.remote_flag) or "remote" in head


def is_us_eligible(job: Job) -> bool:
    loc = job.location.lower().strip()
    if not loc or loc == "remote":
        return True
    if any(_has(loc, t) for t in config.US_OK):
        return True
    # US city/state locations from Indeed, e.g. "Austin, TX, USA" or "Remote, TX".
    if US_STATES & set(re.findall(r",\s*([A-Z]{2})\b", job.location)):
        return True
    return "remote" in loc and not any(_has(loc, t) for t in config.NON_US_ONLY)


def is_bs(job: Job) -> bool:
    company = job.company.lower().strip()
    if company in config.COMPANY_BLOCKLIST:
        return True
    head = f"{job.title} {job.company}".lower()
    if any(flag in head for flag in config.OFFSHORE_FLAGS):
        return True
    text = f"{head} {job.description}".lower()
    return any(flag in text for flag in config.RED_FLAGS)


def score(job: Job) -> None:
    title = job.title.lower()
    desc = job.description.lower()
    pts, why = 0, []

    for kw, w in config.TITLE_WEIGHTS.items():
        if _has(title, kw):
            pts += w
            why.append(kw)
    for kw, w in config.TITLE_PENALTIES.items():
        if _has(title, kw):
            pts += w
            why.append(f"-{kw}")
    # Description only adds once the title is in the right family, so a
    # wellness-brand engineer doesn't float up on industry words alone.
    if pts > 0:
        desc_hits = [kw for kw in config.DESC_WEIGHTS if _has(desc, kw)]
        pts += min(sum(config.DESC_WEIGHTS[k] for k in desc_hits), 45)
        why += desc_hits

    job.score = max(0, min(100, pts))
    job.why = list(dict.fromkeys(why))
    job.tier = next((name for cutoff, name in config.TIERS if job.score >= cutoff), "")
