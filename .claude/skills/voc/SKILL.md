---
name: voc
description: Voice-of-customer research and hook pulling. Use when the user says "/voc", asks to research customers for a product, mine competitor 1–3 star reviews, find Reddit/forum posts about a pain point, add to the swipe file/sheet, or "pull hooks" from it.
---

# Voice-of-customer swipe file

The sheet lives at `research/data/swipe.csv` (plus `swipe.xlsx`). The tool is `research/voc.py` (see `research/README.md`). There are two modes.

## Mode 1: `research <product> <product page URL> [focus]`

1. Read the product page (WebFetch) and, if it's this repo's product, `templates/product.gut-complex.json`. Work out:
   the underlying problem, the dominant customer demographic, what they've already tried, and 6–10 direct and indirect competitors.
2. Research in parallel. Spawn 4 subagents with WebSearch/WebFetch:
   - **Forums A and B.** 25 posts each from Reddit and non-Reddit forums (HealingWell, Mayo Clinic Connect, Patient.info, Inspire, Quora, niche forums). They describe the *emotional* cost of the underlying problem (fear, shame, rock-bottom moments, tipping points, obsessive worry), **not** the product. Split the themes between the two agents so they don't overlap.
   - **Reviews A and B.** 1–3 star reviews of direct and indirect competitors from Amazon, iHerb, Trustpilot, Drugs.com/WebMD (for Rx alternatives) and Reddit complaint threads. Aim for 60+ each.
   Each agent writes JSONL to `research/data/<batch>-<YYYY-MM-DD>.jsonl` with keys
   `platform, community, product, brand, url, title, author, date, rating, theme, quote, emotion, key_phrases[], verified`.
3. Hard rules for every agent: quotes are **verbatim** from a page or snippet the agent actually saw, with the real URL, and `verified` is `fetched` or `snippet`. No paraphrasing inside quotes, no invented posts, no stitched fragments.
4. Import: `python research/voc.py import research/data/<batch>-*.jsonl --source claude`.
5. Reply **in chat** (not a file), grouped by theme. For each post give a bold one-line summary, the verbatim quote, and a link. After that come the recurring complaint patterns from the reviews, a "language bank" of exact phrases, and 10 starter hooks. Say how many rows the sheet now has.

For 300+ reviews at once, tell the user about the bulk scraper (`python research/voc.py collect`, needs `APIFY_TOKEN`).

## Mode 2: `hooks [theme] [count] [format]`

1. Run `python research/voc.py hooks --theme <theme> --n 60` (add `--kind reviews` or `--kind forums` if asked) to get ranked exact sentences, and read matching rows in `research/data/swipe.csv` for context.
2. Write the requested number of hooks (default 20) for the format asked (TikTok/Reels first line, Meta primary text opener, headline, email subject).
   Each hook must reuse the customer's own words or phrasing. Under it, put the source quote and URL in small text.
3. Group them by angle: callout of the pain, rock-bottom moment, "tried everything", enemy (rifaximin, probiotics, doctors), identity, and so on.
4. Compliance: supplement hooks can't claim to cure, treat or prevent a disease (no "cures SIBO"). Keep the pain in the customer's words, and make any benefit a structure/function claim.
   Don't present a competitor's reviewer or a Reddit user as our customer.
