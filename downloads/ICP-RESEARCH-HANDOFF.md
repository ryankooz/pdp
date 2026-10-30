# HANDOFF: Customer / ICP Research (pain → keywords → desires)

> **For the next chat:** this file covers only the **customer research** done so far: how we find out what a buyer feels, in their own words, at every depth.
> - It does not cover how to find products or competitors.
> - Read it top to bottom. Every file referenced is in the repo `ryankooz/pdp`, branch `claude/great-dijkstra-a6qa7k`.
> - The tool that does this research is `pain-finder/`.

---

## 0. TL;DR
- **Goal:** find problems that are **validated** (many people share them), **painful** (deep emotion), **unsolved** (they've tried everything) and **solvable by a product** such as a supplement. Then capture the customer's **exact words** at 4 depth levels to write ads.
- **Core idea:** surface complaints ("my back hurts") don't sell. **Level 3–4 pain and desire do**: what the problem takes from their life, and what that means about who they are.
- **Sources:** Reddit (the venting communities are the richest), Google Trends, and Google autocomplete.
- **Main outputs so far:**
  - 5 universal level 4 desires
  - level 4 keyword banks
  - a condition-by-condition depth table
  - a detailed ICP for the current product (**hemorrhoids, women 40+**)

---

## 1. What counts as a validated, painful, unsolved problem

A problem passes when it has all six:

| Criterion | What we look for | How it's measured |
|---|---|---|
| **Painful** | Emotional intensity, not just symptoms | Pain phrase hits (section 2), share of posts reaching L3 or L4 (section 3) |
| **Unsolved** | People have tried many things and failed | "Tried everything" share, list of failed fixes, few "what finally worked" claims |
| **Validated / shared** | Others agree and tell their own story | "Me too" replies + story replies in the comments |
| **Unknown cause** | They don't understand why. That's room for a new mechanism or explanation | "Doctors don't know", "tests came back normal" |
| **Product-solvable** | People talk about supplements and OTC products, not just prescriptions and surgery | Product mentions vs prescription/surgery mentions (**product share should be ≥ prescription share**) |
| **Growing** | Search interest rising | Google Trends YoY, 2-year slope, rising and breakout queries |

**Bonus signals:**
- the problem is **private or embarrassing**, so people buy online to avoid a doctor
- the buyer is **40+**, the target buyer
- people use **throwaway accounts** to post about it

**Exclude:**
- **Crisis posts** (self-harm or suicide language) are excluded from everything. Those people need help, not marketing.
- **Recurring megathreads** (scheduled or copy-pasted) would skew counts.

---

## 2. Pain keyword library (the phrases that prove pain)

Each category has a weight. A post earns that weight once per distinct phrase. Matching is case-insensitive and treats apostrophes as optional. Full lists are in `pain-finder/pain_finder/phrases.py`; add your own in `pain-finder/my_phrases.txt` as `category: phrase`.

### wish_for_solution (weight 4, the strongest: the gap)
"I wish there was", "I wish someone made", "if only there was", "why is there no", "why doesn't anyone make", "someone should invent", "nobody makes", "is there a product", "is there anything that", "there has to be a better way", "can't find anything that", "nothing on the market", "I would pay anything", "I'd pay", "take my money", "I'd buy"

### tried_everything (weight 3: the market's current answers are failing)
"I've tried everything", "tried literally everything", "tried so many", "nothing has worked", "nothing works", "nothing helps", "didn't work for me", "made it worse", "only temporary relief", "band-aid", "keeps coming back", "always comes back", "spent thousands", "wasted so much money", "seen multiple doctors", "every doctor", "multiple specialists", "out of options", "last resort", "my last hope"

### desperation (weight 3: emotional intensity)
"I can't take this anymore", "at my wits end", "I'm desperate", "please help", "ruining my life", "destroying my life", "taking over my life", "losing my mind", "driving me insane", "so miserable", "I just want to feel normal", "sick and tired of", "I give up", "I don't know what else to do", "can't live like this", "I'm crying", "in tears", "affecting my job / relationship / marriage", "no quality of life", "suffered for years", "my whole life", "since I was a kid"

### unknown_cause (weight 3: room for a mechanism)
"no idea why", "can't figure out why", "what's causing this", "root cause", "nobody knows why", "doctors don't know", "no one can tell me", "tests came back normal", "bloodwork came back normal", "told me it's just", "it's all in my head", "dismissed me", "brushed me off", "doesn't take me seriously", "undiagnosed", "misdiagnosed"

### unspoken (weight 2.5: embarrassing, isolating, under-served)
"nobody talks about", "why does no one talk about", "too embarrassed", "embarrassing to admit", "ashamed to", "never told anyone", "can't tell anyone", "feel so alone", "thought I was the only one", "am I the only one", "is it just me", "no one understands", "throwaway account"

### help_seeking (weight 1.5: intent to act)
"how do I fix", "how do I get rid of", "how do I make it stop", "any advice", "what actually works", "what finally worked", "does anyone else", "anyone else struggle", "looking for a solution", "recommendations for"

### Validation signals in the comments
- **Agreement ("this is me too"):** "same here", "me too", "same boat", "this is me", "literally me", "I could have written this", "you just described my", "thought I was the only one", "glad I'm not the only one", "you're not alone", "I have the same", "following", "commenting to follow", "saving this", "bump"
- **Stories (depth across many people):** "I've been dealing", "I've had this", "I've struggled", "for years I", "my experience", "I went through", "I suffered", "it took me", "I spent", "I tried"
- **Fix claims (a lot of these = less untapped):** "what worked for me", "finally found", "finally fixed", "cured my", "game changer", "life changing", "holy grail", "completely gone", "never looked back"
- **What they tried** is captured from "I've tried / used / taken / been on ___". That list becomes the "tried everything" section of an ad.

### Discovery seed phrases (searched as exact phrases)
"i wish there was", "why is there no", "someone should invent", "i would pay anything", "i've tried everything", "nothing has worked", "at my wits end", "i can't take this anymore", "ruining my life", "doctors can't figure out", "tests came back normal", "nobody talks about", "thought i was the only one", "how do i fix", "has anyone found a solution", "spent thousands", "keeps coming back", "is there anything that actually works"

---

## 3. The 4 pain levels (the user's framework)

| Level | Name | What it is | Example |
|---|---|---|---|
| **L1** | Surface | The symptom | "my back hurts" |
| **L2** | Physical | What the body can't do anymore | "I can't bend over anymore" |
| **L3** | Emotional / life | What it takes from their life | "I can't run with my kids anymore" |
| **L4** | The true feeling under L3 | What that means about **who they are** | "I can't run with my kids anymore, and I'm missing their childhood. They just see me as the lame mom who doesn't do anything while the other parents run with their kids." |

**The rule:** ads, hooks and keywords must reach **L3–L4**. L1–L2 alone don't move buyers. In the data, about 94% of posts stop at L1, so **L3–L4 language is rare and valuable**.

### How each level is detected (`pain-finder/pain_finder/depth.py`)
Matching is sentence by sentence.

**L2: physical limits**
- "can't / struggle to / hurts to / impossible to" + bend, walk, sit, stand, sleep, eat, focus, lift, get out of bed, go to the bathroom, exercise, run…
- "wakes me up", "takes me hours", "barely walk / sleep / function"

**L3: what it takes from life**
- **Can't do it with people:** "can't ___ with my kids / husband / friends / grandkids"
- **Had to quit / give up:** "had to quit / cancel / take time off", "gave up my job / hobby / the gym / travel"
- **Ruining job or relationships:** "ruining my marriage / social life / sex life / confidence / career"
- **Missing events:** "missed work / weddings / birthdays / holidays / family events"
- **Avoiding life:** "avoid parties / the beach / the pool / dates / restaurants", "can't leave the house"
- **Can't enjoy:** "can't relax / travel / date / be present / be intimate"
- **Intimacy:** sex is painful, avoided, ruined or scary

**L4: identity (9 forms).** A sentence counts as L4 only if it's first person (about "me").

| L4 form | Typical wording (with counts from about 40,000 posts) |
|---|---|
| **Future dread** (the most common) | "for the rest of my life" (55), "spend the rest of my life" (17), "I'll never be able to" (15), "will I be able", "will I ever be able", "is this my life now", "what's the point" |
| **Failing a role** | "feel like a burden" (10), "the person I want to be" (7), "I feel like a terrible person", "being a bad mom", "I'm a burden", "the mom I want to be", "less of a woman", "they deserve better" |
| **How others see me** | "being judged" (15), "feel judged", "what people think of me", "they look at me", "they see me as", "people treat me like", "I'm the lame / weird / gross / smelly one", "I'm the only one who can't" |
| **Identity loss** | "I used to be able" (18), "lost myself" (12), "the real me" (9), "I miss being able to" (8), "the old me" (7), "shell of myself" (6), "who I used to be", "I don't recognize myself", "not the same person" |
| **Self-worth** | "I hate myself" (29), "I feel like a failure", "I feel like a burden", "I feel useless", "I feel pathetic", "I feel broken", "I feel like a freak" |
| **Shame and hiding** | "too embarrassed to" (9), "disgusted with myself", "I feel gross", "too ashamed to", "hate my body", "hate the way I look", "I make excuses", "nobody knows", "pretending I'm fine", "hide my arms / legs / face" |
| **Comparison** | "everyone else seems", "other people can", "compared to other people", "people my age are", "everyone else gets to", "all my friends are married / traveling / having kids" |
| **Missing out** | "I've missed out", "I feel like I'm missing out", "on the sidelines", "missing my kids' childhood", "wasted my 20s", "lost my best years", "life is passing me by", "I'll never get those years back" |
| **Relationship at risk** | "stopped calling me", "no one will ever love me", "stopped asking me", "I'll never find someone", "he's sick of it", "nobody will want me", "I always cancel plans" |

**Deep openers.** What comes after these is the gold, so collect the completions:
- "makes me feel like ___" (worse, guilty, insecure, **invisible**)
- "I feel like a ___" (**failure**, loser, **burden**, terrible person, **bad mom**, imposter, "walking brain instead of a woman")
- "I just want to ___" (**feel normal again**, be loved, be noticed)
- "I'm the only one who ___"
- "everyone else ___"
- "I used to ___"
- "I can't even ___ anymore"
- "I'm scared that ___" (I won't be able to function, of what the future holds)

### Level 4 keywords to search with (for finding content and ads, and writing hooks)
Apostrophes are removed because exact-phrase searches break on them.
- **Identity loss:** "I used to be able to", "shell of myself", "the old me", "I lost myself", "I dont recognize myself", "I miss being able to", "who I used to be", "not the same person"
- **Failing a role:** "feel like a burden", "feel like a bad mom", "the mom I want to be", "the dad I want to be", "keep up with my kids", "play with my grandkids"
- **Comparison / missing out:** "everyone else gets to", "people my age", "I lost my 20s", "missing out on", "on the sidelines"
- **Shame / hiding:** "too embarrassed to", "nobody knows", "make excuses", "being judged", "hide my arms", "even with good hygiene", "shower twice a day"
- **Future dread:** "for the rest of my life", "is this my life now", "will I ever be normal"
- **Cause unknown:** "bloodwork came back normal", "no one believes me", "doctors dont know", "brushed me off", "misdiagnosed for"
- **Desire:** "feel normal again", "wear shorts again", "go to the beach", "date again", "travel without worrying"
- **Proof / authority** (how buyers talk about trying things): "I begged my doctor", "my colonoscopy", "my bloodwork", "after just three days", "within two weeks", "after years of", "I noticed a difference"

Full lists with counts and example sentences: `research/data/level4-keywords.csv`.

---

## 4. Desires: what they want back (the mirror of pain)

Desires are pulled from sentences starting:
- "I just want to ___", "all I want is ___", "I want my ___ back"
- "I wish I could ___", "I'd give anything to ___", "I miss being able to ___"
- "I dream of ___", "one day I want to ___", "I want to be the ___ who", "if only I could ___"

Source: `pain-finder/pain_finder/desire.py`.

**Important:** in fewer than 5% of threads do people state a desire outright. Most desires are **implied**, read as the opposite of the L3–L4 pain. Always label them stated or implied.

### Desire themes by level
| Level | Theme |
|---|---|
| **L4 identity** | feel normal / like myself again · confidence / feel attractive · be a good parent / partner · be seen / believed / not judged · stop hiding / no shame · be loved / not alone · connect / make friends · feel happy / at peace / free · be independent / capable |
| **L3 life** | do things with my kids / family · intimacy / sex life · go out / social life / travel · work / career · active life / sport / hobbies · eat / wear what I want · "my life back" |
| **L2 body** | sleep · no pain / body works |

### The 5 universal L4 desires (they show up across every condition)
1. **"Feel like myself again" / "be normal, like how I used to be"**: the most common deep desire. It's about getting a self *back*, not becoming someone new.
2. **"Be the parent / partner I want to be"**: "a happy, present, playful mother", "the dad I want to be", "do things with my kids like I used to", "not a burden to my partner".
3. **"Be believed"**: doctors and family think they're "exaggerating", "making it up" or "lazy".
4. **"Stop being the one people notice"**: "people cover their nose", "think I don't take care of myself".
5. **"Stop losing my best years"**: "I lost my 20s", "wasting my teen years", "watched people my age move forward".

**The before → after pattern:** take their L4 pain sentence (before) and their L4 desire (after). For example: "people cover their nose in subtle ways" → "a happy, present, playful mother who enjoys life." That pair is the spine of an ad.

---

## 5. Where to listen

**Reddit communities (subreddit packs in `pain-finder/pain_finder/subreddits.py`):**
- **health:** ChronicPain, ChronicIllness, IBS, GERD, Constipation, SIBO, insomnia, POTS, Fibromyalgia, Gout, **Hemorrhoids**, Interstitialcystitis, HealthAnxiety, longcovid, **Perimenopause**, **Menopause**, PCOS, endometriosis, Hyperhidrosis, Neuropathy…
- **body:** HairLoss, FemaleHairLoss, acne, Rosacea, eczema, bodyodor, Halitosis, BingeEatingDisorder, Lipedema…
- **family:** Parenting, **beyondthebump** (postpartum), Mommit, AgingParents, CaregiverSupport…
- **age:** **AskWomenOver40**, over60, retirement, GenX, AskOldPeople
- **venting (the richest for L3–L4, where people say what they don't say out loud):** offmychest, TrueOffMyChest, Vent, confession, lonely, disability, **TwoXChromosomes**, AskMenAdvice, SingleParents, ChronicIllness, AskWomenOver30

**Google:**
- **Trends:** is the problem rising year on year? What are the rising and breakout queries?
- **Autocomplete:** how do people phrase it when searching alone? That's raw, private language. Example: "why do I smell bad even with good hygiene".

**Rule of thumb:** Reddit tells you **how deep** it goes, and Google tells you **whether it's growing** and **how people phrase it privately**.

---

## 6. What the research found across conditions
About 68,000 Reddit posts, over 3 runs, plus Google Trends.

| Condition | Posts | Pain | Tried everything | L3+ | L4 | Product vs Rx | Google YoY | Read |
|---|---|---|---|---|---|---|---|---|
| **Body odor (even with good hygiene)** | 266 | 25% | **11%, highest** | **12%, highest** | **7%, highest** | **31% vs 15%, best** | ×1.17; "why do I smell bad even with good hygiene" rising; "body odor after menopause / in older women" | The strongest product-fit pain found |
| IBS / SIBO | 665 | 23% | 8% | 8% | 4% | 25% vs 28% | SIBO +27%/yr | Biggest gut pain pool |
| Bloating | 454 | 23% | 8% | 7% | 3% | 28% vs 30% | **×1.39**; "why am I so bloated I look pregnant" +250% | Rising fast |
| Constipation | 500 | 23% | 9% | 6% | 2% | 30% vs 29% | ×1.14 | Big, product-friendly |
| Neuropathy | 155 | 20% | 7% | 6% | 3% | **24% vs 18%** | +38%/yr; "how I cured my neuropathy" +800% | Products beat Rx |
| MCAS / histamine | 358 | 17% | 5% | 4% | 2% | 27% vs 28% | MCAS ×1.42 | Possible gap |
| Excessive sweating | 238 | 20% | 7% | 9% | 4% | 24% vs 30% | severe hyperhidrosis ×2.0 | Deep |
| Lymphatic / puffy | 245 | 13% | 3% | 4% | 3% | 18% vs 31% | **×1.57, the fastest-growing** | Ad-made demand, shallow pain |
| **Hemorrhoids** | 73 | 23% | 4% | 7% | 5% | 19% vs 29% | ×0.96 flat overall; **female searches rising** | See section 7 |
| Blood sugar | 255 | 15% | 5% | 4% | 1% | 29% vs 33% | insulin resistance ×1.26 | Ozempic-driven |
| Breast-milk supply | 21 | 19% | 0% | 10% | 5% | 14% vs 19% | ×1.38 | Small; new moms |
| Endometriosis | 281 | 17% | 6% | 9% | 4% | **18% vs 56%** | ×1.12 | Doctor-dominated, skip |
| Pelvic floor | 518 | 21% | 8% | 8% | 3% | 19% vs **45%** | ×1.34 | Physical-therapy-dominated, skip |
| Reflux | 424 | 20% | 5% | 5% | 3% | 18% vs 36% | — | Prescription-dominated |

**Deepest L4 by condition** (from the level 3–4 deep dive, about 57,000 posts):
- invisible chronic illness, POTS / long COVID: **18% L4**
- panic / agoraphobia: 15%, with the most *stated* desires
- body odor / hyperhidrosis: 14%, and the biggest unsolved gap
- binge eating: 14%
- IBS: 9%
- PCOS / hair loss: 6%
- eczema and acne are big but shallow (2–3%)

Full quotes for each condition are in `research/reports/level3-4-desires-deep-dive.md`.

**Representative L3–L4 lines (real Reddit wording):**
- Body odor: "people always look at me sideways and cover their nose in subtle ways"; "I'm considering quitting school… so scared of being judged"; desire: "I want to be a happy, present, playful mother who enjoys life with her children."
- POTS / chronic illness: "I feel like a burden, to my work, to my mom, to my partner"; "I feel like a shell of myself"; "watched people my age move forward while I'm stuck"; desire: "I want to be able to go out and do things with my kids like I used to."
- IBS: "I can't make normal plans or travel without worrying about my stomach"; "I'm going to be like this for the rest of my life"; desire: "I miss being able to go out and have drinks with my friends", "I just want to feel like me again."
- PCOS: "I miss being beautiful and I miss who I was before this"; "Why do I feel like less of a woman"; "I'm getting married next year and I hate how I look."
- Menopause: "I've not really recognised who I am for a while"; "I feel like such a lazy person, but it's overwhelming tiredness"; "Why oh why are we not told just how debilitating menopause can be."
- Neuropathy: "neuropathy has stolen our marriage and I'm losing myself"; "I used to hike 10 miles, now I'm lucky to walk one."
- Binge eating: "I physically can't be the dad I want to be."
- Panic: "I wasted my 20s away"; desire: "I want to be able to go to the beach without having a panic attack."

---

## 7. ICP for the current product: hemorrhoids (Collagen Cushion Support)

### Who
- **Core buyer: women 40–65.** The secondary audience is men 50+.
  - Google data: "**external hemorrhoids in females +2,900%**", "**hemorrhoids symptoms female +300%**". Overall searches are flat (×0.96), so **the growth is in women**.
- **Sub-segment: postpartum / "it started after my kids"** (women 35–55). Pregnancy is a common origin that "never fully went away".
- **Sub-segment: 60+ / grandparents.** Missing out on grandkids, retirement and travel.
- A very **private, embarrassing** problem. People buy online to avoid talking about it.

### Their pain at each level
| Level | What it sounds like |
|---|---|
| **L1** | Itching, burning, bleeding ("blood on the toilet paper"), swelling, pain when sitting |
| **L2** | Can't sit for long, can't sit through a drive, has to "push it back in", checks the toilet paper every time, flares after straining |
| **L3** | Bailed on the road trip, picks the aisle seat at every wedding, plans the whole day around where they can sit, avoids intimacy, sits on a pillow or donut cushion (keeps one in the car under a towel), skips the gym, cancels plans when it flares |
| **L4** | "**For the rest of my life**", "**is this my life now**". The fear of surgery or banding ("I'll end up on the operating table"). Shame: "nobody knows", hiding it from a partner, "my husband thought I was avoiding him". Failing a role: missing time on the floor with the grandkids. "I used to…" / "the old me" |

### What they've already tried (the tried-everything list)
Creams (Preparation H, hydrocortisone, which is only labeled for 7 days of use), medicated wipes, suppositories, sitz baths, fiber, more water, stool softeners, donut cushions, witch hazel, vein supplements (diosmin, hesperidin, horse chestnut), banding, and surgery or being booked for surgery. **The common complaint:** "it works for a day or two, then it's back", "it keeps flaring up", and "I've spent hundreds on creams".

### What they don't understand (the mechanism gap)
- They think it's a vein or skin-surface problem. They don't know *why* it keeps coming back.
- **The education angle that lands:** the cushions and the support tissue underneath weaken with **age (collagen drops about 1% a year after 40) and pregnancy**, and creams only touch the surface.
- **The "flare up" reframe:** "something that comes and goes was never gone".

### What they want (desires)
| Level | Desire |
|---|---|
| L2 | Sit without thinking about it; no bleeding, no itch; stop checking the paper |
| L3 | Sit through a wedding, a recital or a graduation; take the road trip; get on the floor with the grandkids; intimacy without fear; stop planning around chairs |
| L4 | **"I don't plan around it anymore."** Forget it exists. Feel normal / like myself again. **Avoid surgery.** Stop hiding it. **Be done with it, with a finish line, not a forever product.** |

### Buyer psychology (what this ICP responds to)
- **Distrust of the category:** "every product wants you to keep buying forever". They are skeptical, even "this is a scam". Address the skepticism head-on.
- **Fear of surgery** is the deepest fear. A "surgery won't fix it / they end up back here" insight hits hard.
- **They want an end date.** A program (for example 150 days, then stop), not a lifelong subscription.
- **Specific, personal details beat claims:** receipts that add up to $612, "31 flare days last year", the aisle seat, the road trip.
- **Ages and life moments:** "since you turned 40", "after my second baby", "at 62".

---

## 8. How to turn the research into hooks and copy
1. **Pick the deepest pain sentence** (L4 if possible) in their exact words. That's the hook.
2. **Confirm their frustration before selling:** list what they already tried and why it failed.
3. **Give the reason they never heard** (the mechanism): this answers "unknown cause".
4. **Say the desire in their words** (stated if possible).
5. **Use specific details** (numbers, places, ages, objects) to make it feel true.
6. **Never write the result as a cure.** Write it as a feeling or routine in their words ("I don't plan around it anymore").

**Hook formulas built from the levels:**
- L3 life loss: "I chose the aisle seat at every wedding for six years so nobody would see me shift."
- L4 identity: "I stopped saying yes to road trips and blamed my back."
- Future dread: "I thought I'd have [problem] for the rest of my life."
- Failing a role: "My granddaughter asked why I sit on a pillow at the dinner table."
- Unknown cause / reframe: "The most dangerous sign of [problem] isn't the pain. It's the words *flare up*."
- Tried everything: "I added up every [problem] receipt from the last 3 years. $612."

---

## 9. Ethics and accuracy
- **Crisis exclusion:** any post with self-harm or suicide language is dropped from all outputs.
- **Accuracy:** the pattern matching is about 85% accurate, so **read the quotes yourself** before using them.
- **Level 4 is rare** (about 1.6% of posts). Treat quotes as real voices, not statistics.
- **Mark desires stated or implied.**
- **Use customer language for real customers:** testimonials must be real and typical. Never invent people, doctors or results from this research.

---

## 10. Files and how to run it
**Data and reports** (in the repo):
- `research/reports/level3-4-desires-deep-dive.md`: L3–L4 pain and desire by condition, with quotes
- `research/reports/desires-report.md`: all desire themes, with wording and quotes
- `research/reports/pain-depth-report.md`: level mix, L4 forms, deep openers, communities with the deepest pain
- `research/reports/combined-product-research.md`: the condition table (product vs Rx, Google trends) and the L3–L4 phrase bank
- `research/data/level4-keywords.csv`: every L4 wording with counts and examples
- `research/data/desire-quotes.csv`: desire sentences by theme
- `research/data/pain-finder-problems.csv`: problem leaderboard

**The tool:** `pain-finder/` (see `pain-finder/README.md`).
- Reddit backend: `arcticshift` (scan mode). Reddit's own API and PullPush were blocked from the cloud.
- **Commands:**
  - `python -m pain_finder discover --pack health --pack venting`: find pain problems
  - `python -m pain_finder topic "hemorrhoids"`: deep dive on one problem
  - `python -m pain_finder depth`: run the L1–L4 analysis
  - `python -m pain_finder desires`: run the desire extraction
  - `python -m pain_finder mine`: learn new pain phrases from the data
  - `python -m pain_finder suggest "hemorrhoids"`: Google autocomplete
  - `python -m pain_finder trends "hemorrhoids"`: Google Trends
  - `python -m pain_finder phrases`: show the phrase library
- **Add your own phrases** in `pain-finder/my_phrases.txt`, for example `desperation: i feel like im dying`.

**Next research to run for this ICP:**
- `topic` runs on r/Hemorrhoids, r/beyondthebump, r/AskWomenOver40, r/Menopause and r/TwoXChromosomes for the hemorrhoid keywords, to collect more first-person L3–L4 lines from women 40+ and postpartum mothers.
- Google autocomplete on "hemorrhoids after…", "hemorrhoids in women…" and "why do my hemorrhoids keep…".
