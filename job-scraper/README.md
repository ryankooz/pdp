# Remote job scraper

Finds verified-remote jobs that look like the Superpower Copywriter role (direct response / conversion copy for health, wellness and DTC brands), plus the secondary roles from the shortlist: creative strategist, short-form copywriter, growth marketing, ecommerce manager, and content creator.

## Run it

```bash
cd job-scraper
pip3 install -r requirements.txt   # needs Python 3.10+
python3 scrape.py
```

Then open `output/report.html` in a browser. A full run takes about a minute.

| Option | What it does |
|---|---|
| `--days 3` | Only postings from the last 3 days (default 30) |
| `--min-score 50` | Only strong fits (default 20, which includes Stretch roles) |
| `--no-indeed` | Skip Indeed, which takes ~15 seconds instead of ~1 minute |

Each run also writes `output/jobs_<date>.csv`. It remembers what you've already seen (`output/seen.json`), so jobs that are new since your last run get a **NEW** tag. Use the "New only" button to see just those.

## Where it looks

**Remote-only boards.** These boards only list remote jobs and screen their posts:
Himalayas, Remotive, We Work Remotely, Jobicy, RemoteOK, Working Nomads, Jobspresso.

**Indeed.** Searched through [JobSpy](https://github.com/speedyapply/JobSpy) with Indeed's own "Remote" filter on, and then re-checked here.

**Company boards.** First-party listings pulled straight from the Ashby, Greenhouse or Lever boards of about 30 health, wellness and DTC brands in Superpower's lane: Superpower, AG1, Oura, Ro, Eight Sleep, WHOOP, Grüns, Olipop, Liquid I.V., Ritual, Seed, Momentous, Hone Health, Maven Clinic, and others. These can't be reposts or ghost jobs. They're kept regardless of posting date, because they stay up only while the role is open. You can add companies in `config.py → COMPANY_BOARDS`.

**Not included:**
- Monster, ZipRecruiter and Glassdoor all block automated access with a 403.
- LinkedIn has no reliable remote flag, so remote couldn't be verified there.
- FlexJobs is paywalled.

## How it filters

1. **Remote verified.** The job must come from a remote-only board or be explicitly marked remote. Anything with hybrid, on-site or in-office in the title or location is dropped, and so are descriptions saying things like "3 days a week in the office".
2. **US-eligible.** Jobs restricted to other regions (EMEA, UK only, LATAM, Sri Lanka, …) are dropped.
3. **BS filter.** This drops commission-only, MLM, Telegram/WhatsApp recruiting and pay-for-training posts, offshore outsourcing and VA shops, AI-training gig sites (Outlier, DataAnnotation, …), and anything in `COMPANY_BLOCKLIST`.
4. **Fit score (0–100).**
   - Title matches carry most of the weight: copywriter, direct response, creative strategist, scriptwriter, and so on.
   - Description keywords add points for the Superpower profile: DR, VSL, sales pages, DTC, health, wellness, supplements, longevity, hooks, UGC.
   - Technical, grant, medical, legal and SEO writing roles are penalized.

| Score | Tier |
|---|---|
| 70+ | **Superpower match** |
| 50–69 | **Strong fit** |
| 30–49 | **Worth a look** |
| 20–29 | **Stretch**: adjacent roles (content, lifecycle, social, marketing manager) |

Each row shows the keywords that drove its score.

All tuning (searches, weights, red flags, blocklist, company boards) lives in `config.py`.

## Run it daily (Mac)

```bash
crontab -e
# every weekday at 8:10am:
10 8 * * 1-5 cd ~/path/to/pdp/job-scraper && /usr/bin/python3 scrape.py --days 2 >> output/cron.log 2>&1
```
