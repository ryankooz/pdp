# Customer research swipe file

Collects what customers have already said: 1–3 star competitor reviews plus Reddit, X/Twitter and forum posts. Everything goes into **one sheet**, and hooks are pulled from that sheet on demand.

```
research/
  voc.py              scraper + sheet + hook puller (Python 3.11+, requests, openpyxl, bs4)
  gut-complex.toml    what to scrape for Gut Complex: competitor ASINs, subreddits, queries, themes
  data/swipe.csv      the sheet (source of truth, one row per review/post)
  data/swipe.xlsx     same rows, with tabs: All · Reviews 1-3 star · Forums & social
  data/*.jsonl        raw research batches gathered by Claude with web search
```

## Two ways to fill the sheet

### 1. Bulk scrape (300+ reviews in one run)

Uses [Apify](https://apify.com). One token covers every source:

| Source | Apify actor | What it pulls |
| --- | --- | --- |
| Amazon | `junglee/amazon-reviews-scraper` | 1, 2 and 3 star reviews for each competitor ASIN |
| Reddit | `trudax/reddit-scraper-lite` | posts and comments matching pain queries in each subreddit |
| X / Twitter | `apidojo/tweet-scraper` | tweets matching pain queries |
| Google | `apify/google-search-scraper` | forum threads outside Reddit (HealingWell, Mayo Connect, Patient.info, Quora); with `fetch_pages` it keeps the emotional paragraphs from each page |

```bash
pip install requests openpyxl beautifulsoup4
export APIFY_TOKEN=apify_api_xxx                     # console.apify.com → Settings → Integrations
python research/voc.py collect                        # all sources in gut-complex.toml
python research/voc.py collect --only amazon          # one source
python research/voc.py stats
```

Cost: Apify bills per result. A full run of the default config (about 1,800 reviews and 900 Reddit items at most) usually lands at a few dollars. Lower `max_reviews_per_product` / `max_items_*` to try it cheaply first.

Re-running is safe: rows are deduplicated by URL and text, so new runs only add new rows.

### 2. Claude research (no API keys)

In Claude Code, run the `/voc` skill (`.claude/skills/voc/SKILL.md`):

```
/voc research Gut Complex Drops https://yourstore.com/products/gut-complex
```

Claude searches the web the way a researcher would, saves verbatim quotes with their URLs to `research/data/*.jsonl`, and imports them into the same sheet. It's slower and smaller than the bulk scrape, but it finds long, emotional forum stories that keyword scrapers miss.

Anything else can be imported too, such as a CSV exported from a reviews app, a review-export browser extension, or a hand-copied list. It needs a `text` (or `quote`/`body`/`review`) column, and `url`, `rating`, `product` and `author` columns are used when present:

```bash
python research/voc.py import ~/Downloads/reviews.csv --source judgeme
```

## Pulling hooks

```bash
python research/voc.py hooks --theme urgency --n 30
python research/voc.py hooks --theme relapse --kind reviews       # only competitor reviews
python research/voc.py hooks --kind forums --contains "doctor"    # only problem posts, not product complaints
python research/voc.py hooks --theme bloating --out research/data/hooks-bloating.md
```

The output is a ranked list of **exact customer sentences**: first person, 4–22 words, scored for emotional language (fear, shame, despair, anger), each with its source link. They're raw material: tighten them into hooks, but keep the customer's words.

Or ask Claude: *"/voc hooks urgency, 20 for TikTok"*. It reads the sheet and writes hooks built from those quotes, with each one tied back to the source row.

Themes: `urgency`, `bloating`, `relapse`, `dismissal`, `food-fear`, `social`, `rock-bottom`, `probiotics`. Edit `[themes]` in the config to add your own. `--theme` also accepts any plain word.

## Another product

Copy `gut-complex.toml`, then change the ASINs, subreddits, queries, `product_terms` and themes:

```bash
python research/voc.py collect --config research/other-product.toml
```

## Rules for using what's in here

- Reviews and posts are other people's words. Use them as **research and inspiration for hooks**. Don't present a competitor's reviewer or a Reddit user as your customer, and don't publish their text as a testimonial.
- Health claims written in a hook still have to follow the FDA structure/function rules in the main README.
- Respect each platform's terms. Apify and the official APIs are the supported ways to collect this data.
