# Pain Finder

Finds **validated, unsolved problems** on Reddit and checks whether demand is **rising on Google Trends**.

It searches for the phrases people use when something hurts and nothing has fixed it ("I wish there was…", "I've tried everything", "at my wits end", "doctors can't figure out why", "nobody talks about…"). It reads the comments to measure how many others say "same here" and tell their own story, pulls out what people have **already tried that failed**, groups the threads into problems, and runs each problem through Google Trends.

No topic is off limits. By default it searches all of Reddit, so problems surface from any age, gender, job, body type, hobby or life situation.

## Setup

```bash
cd pain-finder
pip install -r requirements.txt
```

### Reddit access (recommended: 2 minutes, free)

Reddit blocks anonymous scraping from many networks (cloud servers, VPNs, some ISPs). The official API is free and much faster:

1. Go to https://www.reddit.com/prefs/apps and click **create another app**
2. Pick **script**, give it any name, and put `http://localhost` as the redirect URI
3. Copy the ID under the app name and the **secret**, then:

```bash
export REDDIT_CLIENT_ID=xxxxxxxx
export REDDIT_CLIENT_SECRET=yyyyyyyyyyyy
```

Without keys, the tool tries Reddit's public JSON and falls back to the **PullPush** archive automatically. PullPush works anywhere, but it saves posts when they're created, so upvote and comment counts there are often stale. The comments themselves are still read. Force a source with `--backend oauth|public|pullpush`.

## Usage

### 1. Discover problems from pain phrases (all of Reddit)

```bash
python -m pain_finder discover
```

This searches 18 built-in pain phrases over the past year. Narrow or widen it:

```bash
# your own phrases
python -m pain_finder discover --seed "i'm so embarrassed" --seed "why does no one make"

# only certain life areas (packs: health, body, mental, family, relationships,
# work, money, home, pets, age, lifestyle, all)
python -m pain_finder discover --pack health --pack body

# specific communities
python -m pain_finder discover -r nursing -r Teachers -r Truckers

# go back further, read more threads
python -m pain_finder discover --time all --read-comments 150 --problems 40
```

### 2. Deep-dive one problem

```bash
python -m pain_finder topic "tinnitus"
python -m pain_finder topic "toddler won't sleep" -r toddlers -r sleeptrain
```

This searches the topic combined with pain phrases. The problems it returns are the **sub-problems** inside that area, and each one is checked on Trends as `topic + sub-problem`.

### 3. Google Trends only

```bash
python -m pain_finder trends "tinnitus" "bloating after eating" "jaw clenching" --geo US
```

### 4. See or edit the phrase library

```bash
python -m pain_finder phrases
```

All phrases and their weights are in `pain_finder/phrases.py`. Add your own freely.

## Output

Each run writes a folder in `runs/`:

| File | What's in it |
|---|---|
| `report.md` | Ranked leaderboard, then for every problem: subreddits, pain types, Google Trends verdict and sparkline, rising related searches, **what people already tried**, top threads with links, "me too" quotes and personal stories |
| `problems.csv` | One row per problem, ready for a spreadsheet |
| `threads.csv` | Every scored thread with all score components |
| `results.json` | Everything, for your own analysis |

The **Next searches** section at the end lists rising Google queries found along the way. Feed them back into `topic` to go deeper.

## How a problem is scored

**Thread validation**: each thread is scored on:

- **Pain phrases** in the post, by category and weight:
  `wish_for_solution` ×4 (the gap), `tried_everything` ×3, `desperation` ×3, `unknown_cause` ×3 (people who don't know the real cause), `unspoken` ×2.5 (embarrassing or isolating), `help_seeking` ×1.5
- **Pain in the comments** at 40% weight
- **Agreement**: comments like "same here", "thought I was the only one", "following for answers"
- **Stories**: commenters describing their own experience
- **Engagement**: upvotes and comment count

**Problems**: threads are grouped by the most specific key phrase they share. A problem needs at least 2 threads (`--min-threads`). It scores higher when it spans several subreddits, meaning different kinds of people have the same problem.

**Gap**: the gap phrases ("wish there was", "tried everything", "unknown cause") divided by comments claiming a fix ("what worked for me", "cured it"). High gap with few fix claims means the problem is still unsolved.

**Opportunity** = problem score × Trends multiplier: rising fast ×1.6, rising ×1.3, stable ×1.0, declining ×0.7, no data ×0.9.

**Trends verdict** compares the last 12 weeks with the same 12 weeks a year earlier, so seasonal problems don't look like growth. It also uses the 2-year slope. "No data" means the term is too specific for Google to chart. Try a broader wording with the `trends` command.

## Tips

- The best opportunities usually combine a **high gap**, **many me-too comments**, a **long already-tried list**, several subreddits, and a **rising** trend.
- Read the top threads yourself before acting. The scores point you to them, and the people in them tell you what to build and how to say it.
- Results are cached for 24h (Reddit) and 72h (Trends) in `.cache/`, so re-runs are fast. Use `--no-cache` to refresh.
- Google Trends rate-limits heavily. The tool waits and retries. If it keeps failing, run with `--skip-trends` and check the best problems later with the `trends` command.
- Follow Reddit's API terms. Use this for research, not for mass-messaging the people you find.
