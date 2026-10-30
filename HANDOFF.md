# HANDOFF: Veltia Labs "Collagen Cushion Support" launch + product research system

> **For the next chat:** this file holds everything decided and built so far. Read it top to bottom before doing anything.
> - Repo: `ryankooz/pdp`, branch `claude/great-dijkstra-a6qa7k`.
> - Every file referenced here is in that repo unless it says otherwise.
> - The current date when this was written: **Oct 30, 2026**. The user launches **~Oct 31 – Nov 3, 2026**.

---

## 0. TL;DR: what to do next
1. **Launch:** hemorrhoid supplement, brand **Veltia Labs**, product **Collagen Cushion Support** ("Cacao-Powered Support").
   - Swipe the winning competitor **Venalys** (venalyslab.com).
   - **3 ad sets × 3 creatives = 9 creatives, 3 copies (2 native + 1 static).** Final copy and creatives are in section 6.
2. **Before launch, fix the store so it matches the ads** (section 7):
   - a 150-day / 5-bottle "Buy 3 Get 2 Free" offer
   - a refund guarantee
   - a formula that really contains cacao and collagen support
   - Copy B only from a **real** licensed surgeon
3. **Backup product to watch:** **Rare Nutrition** (rarenutrition-us.com, saw palmetto prostate formula, first ad Oct 29). Re-check around Nov 3 with your rules (section 9).
4. **Rules that must never be broken:**
   - no invented doctors or credentials
   - no cure claims ("gone forever", "stay free", "rebuild")
   - FDA disclaimer on every claim
   - Two rule-clean competitors (Cirae and KrakenSupps) **vanished from the Meta Ads Library this week**, most likely banned for exactly these things.

---

## 1. Who the user is and how they work
- Runs supplement / health dropshipping brands on Shopify, sold through **Meta (Facebook/Instagram) ads**, **native and advertorial style**, with buyers mostly **40+**.
- Has already run **Biora** (IBS/SIBO). Don't suggest it again ("biora bad i already did it").
- Sources from **CJ Dropshipping**.
- Their research method is the **"Meta Ads Library rabbit-hole"**: find a *fresh* store that is clearly scaling right now, then **swipe it 1:1 with their own brand**. The user said: *"we're not reinventing the wheel or iterating, just putting my brand instead."*
- Communication style: short messages, wants direct answers, tables, and final copy they can paste.

### The user's rabbit-hole rules (use these to judge any competitor)
1. **Every ad**, active or inactive, must have **started within the last 28 days**. Any old ad for the same product means skip.
2. **New ads every 1–3 days.** **3+ quiet days = fail.**
3. **A high ad count is fine if the ads are fresh.**
4. **Validate** by searching the store's **domain token** in the Ads Library with **STATUS=all** (active + inactive), "keyword unordered". Look at the first ad, the newest ad, new ads per day, and cuts.
5. **Native persona ads** (first-person posts from persona pages) are the priority signal.
6. **A falling total ad count** means the store is cutting ads, which is bad.
7. **The 7-row playbook score, only test at 28+/35:**
   - pain moment
   - tried 3+ fixes
   - mechanism in 10 words
   - margin
   - felt in 7–14 days
   - private problem for a 40+ buyer
   - proven demand + weak competitor messaging

### The user's 4 pain levels (used for hooks and keywords)
| Level | What it is | Example |
|---|---|---|
| L1 | Surface | "my back hurts" |
| L2 | Physical | "I can't bend over anymore" |
| L3 | Emotional | "I can't run with my kids anymore" |
| L4 | The true feeling under L3 | "…I'm missing their childhood, they see me as the lame mom" |

**Winning ads hit L3–L4.**

---

## 2. Research tools built (where and how)

### 2a. Pain Finder (Reddit + Google Trends): `pain-finder/`
A Python package that finds validated, painful, unsolved, **product-solvable** problems.
- **Reddit backends:** `oauth`, `public`, `arcticshift`, `pullpush`.
  - **Use `arcticshift` scan mode.** Reddit and PullPush were blocked from the cloud.
- **Pain phrase library** (`phrases.py`, plus the user's own `my_phrases.txt`):
  - "I wish there was", "I've tried everything", "I can't take this anymore", cause unknown, help seeking
  - agreement and story signals ("same here", "this is me")
- **Depth model** (`depth.py`): L2/L3/L4 regexes. L4 requires first-person self-reference.
- **Desires** (`desire.py`), **keyword mining** (`mine.py`), **Google autocomplete** (`suggest`), **Google Trends** via pytrends (YoY, slope, rising queries).
- **CJ search** (`cj.py`): searches CJ by problem, ingredient and format (`--formats` finds the same ingredient as powder, gummy, spray, patch…). Results are in `pain-finder/cj-results/`.
- **CLI commands:** `discover`, `topic`, `trends`, `recluster`, `mine`, `suggest`, `depth`, `desires`, `cj`, `phrases`. See `pain-finder/README.md`.

### 2b. Meta Ads Library scraper: `research/meta-scraper/`
- `scrape.js`, a headless Playwright Chromium script. Usage: `node scrape.js out.json "phrase1" "phrase2"`.
- **Environment variables:**
  - `STATUS=active|all`
  - `TYPE=keyword_exact_phrase|keyword_unordered`
  - `SCROLLS=1`
  - `MEDIA=all|video|image`
  - `EXTRA=` (appended to the URL)
- **Captures:** library ID, start date (or the start of the date range if inactive), end date, active, page name, body, landing URL, versions, and media type.
- **Newest-first sort:** `EXTRA='&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped'`
- **Gotchas:**
  - Logged-out view only shows about 30 ads per search.
  - **"~0 results" usually means Meta throttling.** Space searches 40–90s apart and retry after a back-off.
  - To confirm a real zero, run a control search (a known store) in the same run.
- **Scripts:**
  - `chk28.py` / `pre30.py`: competitor comparison plus discovery sweep
  - `val30.py` / `val3.py`: domain validation
  - `copycat.py`: finds who is swiping a competitor's phrases
  - `sweep.py`: phrase discovery
  - `killlist.txt`: stores the user has already rejected. **Always exclude them.**

### 2c. Reports and data: `research/reports/`, `research/data/`
- `combined-product-research.md`: Reddit × Google × Meta × CJ cross-reference.
- `level3-4-desires-deep-dive.md`, `desires-report.md`, `pain-depth-report.md`: deep pain language for hooks.
- `cirae-venalys-funnels.md`: full offer and funnel breakdown of Venalys vs Cirae.
- `venalys-top10-ads.md`: Venalys's top ads, with copy.
- `data/oct30-*.json`: latest comparison, discovery candidates, backup validation.
- `data/level4-keywords.csv`, `desire-quotes.csv`: L3–L4 phrases to search Meta and to write hooks.

---

## 3. What the research found (why hemorrhoids / Venalys)

**Reddit (about 68,000 posts):**
- Strongest product-fit pains:
  - **Body odor** "even with good hygiene": best product-vs-prescription ratio and the deepest L4. The user doubted it. Meta showed a big persimmon-soap "aging odor" market for women 40+. **Set aside.**
  - **Bloating/gut** (+39% YoY)
  - **Neuropathy** (products beat prescriptions)
  - **MCAS**
- **Hemorrhoids on Reddit/Google:** flat overall, *but* female searches are rising fast:
  - "external hemorrhoids in females" +2,900%
  - "hemorrhoids symptoms female" +300%

  The win is **ad-driven**: weak competitor messaging, and a supplement in a category full of creams.

**Venalys is the clearest proof of scaling found:**
- **venalys.shop:** Sep 24–Oct 9, 29 ads, all cut.
- **venalyslab.com:** from Oct 10, about 720 ads, **0 cut**.
- **venalyn.com:** from Oct 10, 190 ads. A second domain, same operator, same persona pages. **Still adding ads every 1–2 days as of Oct 30.**
- **Rules it breaks:** the 28-day rule (its first ads go back to Sep 24) and old ads for the same product. The user knowingly accepted this, because no other store shows this much proof of scaling.

**No real outside copycats of Venalys yet.**
- **Levoria** (trylevoria.com) tried a cushion and surgeon swipe with a diosmin product. By Oct 30 it had cut about 57 of 64 ads, so it's dying.
- Getbottomsup (gay-men angle), Sculptique (lymphatic) and Nutraful are not true copies.

---

## 4. Venalys's offer and funnel (what we copy)
- **Product:** "Collagen Cushion Support Capsules", hero ingredient **non-alkalized cacao flavanols**, 2 capsules a day.
- **Mechanism:** "Everyone has 3 rectal cushions held up by a collagen mesh. After 40 you lose about 1% of collagen a year and the cushions slip. Bleeding and itching are symptoms; the collapsed cushion is the cause." **Collagen, not veins.**
- **Villains:**
  - creams (hydrocortisone is only labeled for 7 days)
  - fiber, wipes, donut cushions
  - **vein supplements (diosmin, hesperidin, horse chestnut): "tone the vessels, ignore the mesh"**
  - banding and surgery
- **Offer:**
  - $39.90 for 1 bottle ("30-day trial")
  - $119.70 for 3 (Buy 2 Get 1)
  - **$179.50 for 5 (Buy 3 Get 2), labeled "MOST POPULAR • FREEDOM PROGRAM"**, a 150-day program
  - **12-month "Freedom Guarantee"** (refund if hemorrhoids come back after finishing)
  - "40% OFF ends at 11:59pm"
- **Funnel:** ad → product page (most ads) or a "Top 5 hemorrhoid solutions" listicle by "Dr. Matthew Hayes" → product page.
- **Pages:** 7+ persona or publisher pages: Venalys, Dr. Matthew Hayes, David Miller, Better Gut Living, Digestive Wellness Network, The Naked Truth on Health, The Fourth Trimester Relief (postpartum); on Venalyn: Dr. Fabian Liebscher, Gary Whitmore, Susan Rhodes.
- **Risk:** they use **invented doctors and cure claims**. **We do not copy those parts.**

### Venalys's 16 angles, by ad volume (from about 420 ads)

| # | Angle | Ads |
|---|---|---|
| 1 | Surgeon confession: "surgery doesn't fix it" | ~66 |
| 2 | Collagen, not veins (the mechanism) | ~63 |
| 3 | Finish line: "they want you buying forever" | ~52 |
| 4 | Patient vs surgeon (refusing banding) | ~46 |
| 5 | Flare-ups mean it was never fixed | ~45 |
| 6 | Life loss (L3–4) | ~30 |
| 7 | Nurse insider | ~17 |
| 8 | Postpartum | ~16 |
| 9 | Urgency | ~14 |
| 10 | Symptom self-check | ~14 |
| 11 | Ranking / takedown of competitors | ~11 |
| 12 | Sex and intimacy | ~9 |
| 13 | "My husband is a surgeon" | ~8 |
| 14 | Shock / home fixes | ~5 |
| 15 | Foods to avoid | ~5 |
| 16 | Relief testimonial | ~3 |

**Top 3 performing angles:**
1. **Finish line**: 4 of the top 10, about 52 ads, 3+ pages, video and image, live since Oct 10.
2. **Surgeon confession**: the largest angle, 15+ scripts, still adding new versions.
3. **Flare-ups**: one script running on 4 pages.

### The user's Venalys top 10 (from their Ads Library screenshots)
Positions: top row 1–5, bottom row 6–10.

| # | Library ID | Page | Hook | Creative | Link headline | Angle |
|---|---|---|---|---|---|---|
| 1 | 3859877310819123 | Dr. Matthew Hayes | "I recommended the same hemorrhoid protocol to 89 patients…" | Orange background + bottle, "doctors issue a warning?" | This will confirm your suspicions. | Surgeon confession |
| 2 | 2422274331910009 | Digestive Wellness Network | "💸 Every hemorrhoid supplement wants you to keep buying it forever" | Video, bottle in a store aisle | Hemorrhoids aren't just forever? | Finish line |
| 3 | 1087161883929270 | Better Gut Living | same as #2 | "The official 5-bottle offer, Buy 3 Get 2 Free" | 40% OFF ends at 11:59pm | Finish line |
| 4 | 1088313590757998 | Dr. Matthew Hayes | same as #1 | Black, "SCAM EXPOSED", red arrow, "SCAM?" | This will confirm your suspicions. | Surgeon confession |
| 5 | 1614565426810529 | Better Gut Living | "The most dangerous sign of hemorrhoids isn't the pain…" | Doctor at a whiteboard: "The 'hemorrhoid killer' protein is called…" | Hemorrhoids Or Collagen Failure? | Flare-ups |
| 6 | 2003014067054566 | David Miller | "So sick of people in my group swearing Collinsonia and Diosmin…" | Red grapes on a tape measure | Colorectal surgeon: hemorrhoids aren't varicose veins | Competitor takedown |
| 7 | 1097904886428753 | Venalys | same as #2 | "THIRD FLARE THIS YEAR? Try Venalys", cushion icons, Buy 3 Get 2 | 40% OFF ends at 23h59 | Finish line |
| 8 | 28941504235485744 | Digestive Wellness Network | "My new boyfriend… 'Babe, is this a hemorrhoid?'" | Pencil-sketch illustration | Hemorrhoids Are Collagen Failure? | Sex and intimacy |
| 9 | 2105520263439478 | Venalys | same as #2 | Text-heavy "FINAL NOTICE: WE ARE CLOSING THE OFFER" | 40% OFF ends at 23h59 | Finish line + urgency |
| 10 | 1655557989247292 | Better Gut Living | "Honestly thought I'd have hemorrhoids for the rest of my life" | "F*CK YOU, HEMORRHOIDS." + bottle | Finally hemorrhoids you can actually forget | Relief testimonial |

### Why they work
- **Finish line:**
  - It names a villain the buyer already suspects (the business model).
  - It flips the "subscription forever" objection into the selling point.
  - It justifies the 5-bottle bundle.
  - One script runs under many creatives.
- **Surgeon confession:**
  - An insider turns on their own industry.
  - Specific numbers (89 / 31) make it believable.
  - It hits the L4 fear of surgery.
  - Skeptic images ("warning", "scam exposed") stop the scroll.
- **Flare-ups:**
  - A curiosity gap ("isn't… isn't… isn't…").
  - It reframes the buyer's own words.
  - "Failing 1% a year since forty" turns "managing it" into losing.
- **Shared by all of them:**
  - one mechanism (collagen) under every angle
  - the hook confirms frustration before any selling
  - L3–4 pain
  - specific details
  - an offer built into the angle
  - many pages, one script, many creatives

---

## 5. Brand assets (already made by the user)
- **Brand:** Veltia Labs. **Product:** Collagen Cushion Support, label subtitle "Cacao-Powered Support".
- **Label art:** cacao pod, beans and leaves line art; Non-GMO / Alcohol Free / GMP Compliant badges; "Herbal Dietary Supplement, 100% Plant-Based, 60 Capsules, Net Wt 35 g".
- **9 final creatives (PNG, 1122×1402):** the user has them in `veltia-nine-ad-creatives_1.zip` (the second, final zip). Filenames are listed in section 6.
- **Shopify product page template:** `templates/product.cushion-support.json`.
  - Current bundles: 1 month $44.99 / 3 months $89.99 / 5 months $129.99.
  - Current ingredient list: diosmin/hesperidin, collagen, vitamin C, horse chestnut, butcher's broom, cocoa flavanols. **Must be updated** (section 7).
- **Older ad packs:**
  - `ads/cushion-support-launch-ads.md`: the first draft, superseded.
  - `ads/cushion-support-natives.md`: the launch plan. Section 6 below is the latest version and overrides it where they differ.

---

## 6. FINAL LAUNCH SET: 3 ad sets, 3 copies, 9 creatives
Each copy keeps **Venalys's exact hook, lead and headline**. Only the body is rewritten, keeping what makes it work. Fill in the `[brackets]` with **true** numbers. `*` = FDA disclaimer.

| Ad set | Copy | Type | Funnel | Creatives (files) |
|---|---|---|---|---|
| 1 | A: Finish line | Static | BOF | `1A-five-bottle-offer.png`, `1B-third-flare.png`, `1C-before-you-buy.png` (Final Notice) |
| 2 | B: Expert confession | Expert native | MOF | `2A-orange-label-check.png` (doctors warning), `2B-scam-or-substance.png` (scam exposed), `2C-grapes-and-tape.png` |
| 3 | C: Flare-ups | Customer native | TOF | `3A-collagen-whiteboard.png`, `3B-two-am-sketch.png`, `3C-orange-statement.png` (F*CK YOU, HEMORRHOIDS.) |

**Creative sources:** 1A ← #3, 1B ← #7, 1C ← #9, 2A ← #1, 2B ← #4, 2C ← #6, 3A ← #5, 3B ← #8, 3C ← #10.
- 1A–1C, 2A, 2B and 3A ran under the same copy at Venalys.
- 2C, 3B and 3C are borrowed from other winning top-10 ads.
- **Native creatives (2C, 3A, 3B) have no logo, no text overlay and no product.** That's deliberate: native images must not look like ads.

### Copy A: Finish line (static, BOF)
```
💸 Every hemorrhoid supplement wants you to keep buying it forever. Because they treat the symptom, not the collagen deficit underneath. That's the whole business model. You stop taking it, the flares come back. Every time.

🍫 Veltia Labs Collagen Cushion Support is different. You take it for [150 days] to support the collagen your rectal cushions have been losing since you turned 40.* Then you stop.

✅ If your flares come back within [12 months] of finishing, full refund. 🛡️

⭐ [2,148] people have already finished the program.

No other hemorrhoid brand puts an end date on it. There's a reason.

[Offer line, e.g. "40% OFF ends at 11:59pm"]
```
- **Headline:** 40% OFF ends at 11:59pm
- **Description:** Veltia Labs Collagen Cushion Support is a daily plant-based capsule formulated with cacao and botanical extracts, traditionally used to support collagen and comfort.*
- **Warning:** "[2,148] people" must be a real number. At launch you have none, so **delete that line** until it's true.

### Copy B: Expert confession (native, MOF). ONLY from a real, licensed colorectal surgeon posting from their own page.
```
I recommended the same hemorrhoid protocol to [89] patients last year. [31] of them still ended up on my surgery schedule. Same protocol. Same explanation. Same instructions. But more than a third of the people I was trying to keep out of my operating room walked right back into it.

I'm [Dr. Full Name, credentials]. I've been a colorectal surgeon in [city] for [X] years. I don't recommend anything I haven't watched work.

Creams calm the surface. Fiber takes pressure off. Banding removes what's already there. None of them do anything about the collagen that holds your cushions in place, and that support has been thinning since you turned 40. That's why they walk back in.

So before I recommended anything to my patients, I tried Veltia Labs Collagen Cushion Support with [12] of them first. [Six months], in my own clinic. [True observation in the doctor's own words.]* Two capsules a day. It's a [150-day] program, not a forever product.

I'm not telling you to skip your doctor. I'm telling you what I now ask my patients to try before we talk about the operating room.
```
- **Headline:** This will confirm your suspicions.
- **Description:** same as Copy A.
- **No real surgeon? Don't run ad set 2.** Launch ad sets 1 and 3 only. Running it under an invented doctor is what likely got Cirae removed.

### Copy C: Flare-ups (customer native, TOF)
```
The most dangerous sign of hemorrhoids isn't the pain when you sit. It isn't the itching. It isn't even the blood on the toilet paper. It's the words flare up. A flare up means it comes and it goes, and something that goes away is something you're allowed to wait out. Nothing has gone away. The thing underneath has been failing at about one percent a year since you turned forty, straight through every good week you've had. The flare ups are just the weeks you can see it.

A colorectal nurse said that in a video I watched at 2am, and I cried. Because I'd been waiting mine out for [9] years.

"It's just flaring up again." I said it to my husband when I bailed on the road trip. I said it to myself when I picked the aisle seat at every wedding. Every time it calmed down, I thought I'd won. I'd stop the cream, forget about it, and three weeks later I'd be planning my whole day around where I could sit.

Nobody told me the cream only calms the surface. The thing underneath is collagen, the support that holds your cushions in place, and it keeps thinning whether you're having a good week or a bad one.

That's what Veltia Labs Collagen Cushion Support is for. Two capsules a day, [150 days], supporting the collagen underneath instead of the surface on top.* I'm in month [4]. [Real result in her words, e.g. "I haven't said the words 'flare up' since August."]*

If you're still waiting yours out, this is for you.
```
- **Headline:** Hemorrhoids Or Collagen Failure?
- **Description:** same as Copy A.
- **Option for the sketch creative (3B):** "A cacao capsule that supports collagen in the rectal cushion.* Two capsules a day for [150] days, then you stop."
- It must be posted by a **real customer or creator** (as a partnership ad) whose story and results are true.

**Footer for every ad and page:**
> \*These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.

### How to run it
- **Day 1:** all 9 ads. Every ad goes to the product page with the **5-bottle bundle preselected**.
- **Pages:** brand page + real customer or creator pages (partnership ads). Venalys spreads winners across 4–7 pages.
- **Days 2–4:** in each ad set, kill the weakest creative and put a new image under the **same copy** (Venalys's pattern: one script, many creatives).
- **Scale:** duplicate the winning creative onto another real person's page.
- **Next wave (later):** the smaller angles that still made Venalys's top 10:
  - sex and intimacy ("Babe, is this a hemorrhoid?")
  - relief testimonial
  - postpartum: their newest page, and it matches the rising female searches
- **Unused but available:** Venalys #2, a video of the bottle in a store aisle under Copy A. Make it as a 4th creative for ad set 1 if you want video.

---

## 7. PRE-LAUNCH CHECKLIST (the store must match the ads)
- [ ] **Offer:** create a **150-day / 5-bottle "Buy 3 Get 2 Free"** bundle and make it the default or most popular option. Venalys charges $179.50; the current template has $129.99 for 5. Decide the price. The 3-bottle and 1-bottle options stay.
- [ ] **Guarantee:** add the refund guarantee the copy promises: a refund if flares come back within [12 months] of finishing. If you won't honor 12 months, change the copy to your real terms (e.g. 90 days).
- [ ] **Formula:** confirm with the supplier that the product contains **cacao (flavanols)** and supports **collagen**, to match the label and copy.
  - Update the ingredient cards in `templates/product.cushion-support.json`. They currently lead with diosmin and horse chestnut, which is exactly what Venalys calls the villain.
  - Remove anything you don't actually source.
- [ ] **Discount:** use "40% OFF ends at 11:59pm" only if you really run that discount.
- [ ] **Numbers:** every `[bracket]` must be true or deleted ("2,148 people", patient numbers, months).
- [ ] **Copy B:** only with a real licensed surgeon. Otherwise skip ad set 2.
- [ ] **Label wording:** keep "Cacao-Powered **Support**", not "Rebuild".
- [ ] **Product page:** add the FDA disclaimer and discreet shipping. Use the same mechanism language as the ads (collagen, cushions, surface vs underneath).
- [ ] **Reviews:** the template has placeholders. **Never fabricate reviews.**
- [ ] **CJ:** source the capsule. Results are in `pain-finder/cj-results/`. A child session was set up to search CJ for hemorrhoid, collagen, cacao, diosmin, horse chestnut, butcher's broom, witch hazel, sitz bath and rutin, with output going to `pain-finder/cj-results/hemorrhoid/`. It was waiting for the user's "yes", so check whether it ran.

---

## 8. Compliance rules (why they matter)
| Don't | Do instead | Why |
|---|---|---|
| Invented doctors, nurses or credentials | Real people only; a customer quoting their own doctor; a real licensed expert using their real name | FTC deceptive endorsements. **Cirae and KrakenSupps disappeared from the Ads Library** this week after running fake personas and aggressive claims. |
| "Cures", "gone forever", "stay hemorrhoid free", "rebuild" | "Supports", "program", "routine"; let the **guarantee** carry the promise | Disease claims are illegal for supplements and get ad accounts banned |
| Fake testimonials or review counts | Real, typical results only | FTC, chargebacks |
| Claims with no disclaimer | Asterisk + FDA disclaimer | Required |

---

## 9. Competitor status (latest: Oct 30, 2026)
| Store | Product | Total ads | First → newest | Recent days with new ads | Cut | Verdict |
|---|---|---|---|---|---|---|
| **Venalyn** (venalyn.com) | Same as Venalys | 190 | Oct 10 → **Oct 30** | Oct 21, 23, 24, 26, 27, 29, 30 | 19 | ✅ Still scaling |
| **Venalys** (venalyslab.com) | Hemorrhoid cacao/collagen | 720 | Oct 10 → Oct 29 | Oct 22, 23, 24, 29 | 0 | ✅ Active; the new ads are on Venalyn |
| **Gloa Labs** (gloalabs.com) | UTI cranberry softgels, $32.95 Buy 1 Get 1 | 30 | Oct 20 → Oct 29 | Oct 20, 22, 26, 28, 29 | 0 | ❌ Final no-go: a 3-day gap and low volume |
| **Levoria** (trylevoria.com) | Diosmin "vein" hemorrhoid | 64 | → Oct 29 | Oct 29 only | 57 inactive | ❌ Cutting, dying |
| **Cirae** (trycirae.com) | Gout tart cherry | **0** | — | — | everything gone | ❌ Banned or removed |
| **KrakenSupps** | Constipation | **0** | — | — | everything gone | ❌ Banned or removed |

### Backup candidates (discovery run Oct 30, 30 phrases, L3–4 + UTI/bladder/women 40+)
- **Rare Nutrition** (rarenutrition-us.com): **the best backup to watch.**
  - Product: saw palmetto prostate formula, men 50+.
  - First ad **Oct 29**, 39 total, 26 launched Oct 30, 3 pages (American Prostate Support Group, David Hart, Dr. Paul Miller).
  - Funnel: German-doctor advertorial → product.
  - **Re-check around Nov 3:** if it's still adding ads every 1–3 days with no falling total, it passes the rules.
- **Kaira Wellness** (kairawellness.com): transdermal **bladder patches** for women 50+ with overactive bladder (a new format, a plus). First ad Oct 14, 61 ads, 0 cut, 3 pages, a burst Oct 24–27. **Quiet since Oct 28, so cadence is breaking.** Fails today.
- **Rejected** (old ads, wrong product or no data): Dermiqua (July), Lovy/trylovy (April), Her Vitality (June), Bioma (2025), Fortis Health (Sep 26, a wrap), Auniva (no new ads since Oct 9), Amala Health / Lovi Health (no data; Lovi is probably "trylovi" from the kill list).

### Set aside (not dead, just not now)
- **Body odor, women 40+** (persimmon soap / "2-nonenal" market): Orchard & Root was fresh on Oct 19. Older proof: Kaori, Swarva, Kakiyu, Mirai.
- **Neuropathy** (Nervalley), **bloating/gut**, **MCAS**, **UTI** (CJ has cranberry + vitamin C softgels for $1.74, chlorophyll drops for $0.92).

---

## 10. How to repeat the research yourself
1. **Find candidates:** in the Ads Library, run an exact-phrase search on L3–L4 phrases (`research/data/level4-keywords.csv`, `desire-quotes.csv`), sorted newest first. Phrases with fewer than about 300 results surface fresh stores.
2. **Group by landing domain.** Drop the kill list, big brands, and non-supplements (dramas, novels and gadgets show up a lot).
3. **Validate:** search the domain token with STATUS=all, keyword unordered. Apply the rules in section 1.
4. **Score** with the 7-row playbook. Only test at 28+/35.
5. **Swipe 1:1:**
   - top 3 angles by top-10 slots + ad count + run time
   - exact hook, lead and headline
   - body that keeps the structure
   - 3 creatives per copy taken from their winners
   - the brand swapped in
   - fake doctors and cure claims removed
6. **Pace searches** 40–90s apart. A "~0 results" means throttling unless a control search in the same run returns results.

---

## 11. Scheduled check-ins
- Oct 28 (comparison) and Oct 30 (pre-launch + backups) have **both fired and are complete**. Results are in section 9. No more check-ins are scheduled.
- **Suggested next check:** around **Nov 3**. Re-validate Rare Nutrition and Venalyn with `research/meta-scraper/pre30.py`, or with `val30.py` after editing its token list.
