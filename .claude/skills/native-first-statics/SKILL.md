---
name: native-first-statics
description: Build static image ads from a proven native winner, then launch, read and iterate them. Covers the natives-first gate, funnel stage, swiping, VOC headlines, image prompts, Higgsfield generation, primary text, the 7-day verdict and Evolve-style static iteration. Use when someone asks for static ads, statics, image ads, a swipe, static headlines or static iterations.
---

# Native-First Static Ads

This skill turns a winning native ad into static image ads, generates them through the Higgsfield MCP, and logs the results so the next batch builds on evidence.

**House rule: natives come first.** The order is: find a native winner, iterate its images, and only then build statics from its angle. Do not build statics for an angle that has not won as a native, except in the one case allowed in Step 1.

**Evidence level.** Most of this process comes from one operator (kinnym), and the reported results are single tests. Present every number in this file as "reported once", never as a benchmark or a promise.

**Hard rule: never name a real NDA'd client or agency-client brand in this file.** Whatever brand the person names when running the skill lives only in that session.

## Pre-flight

1. **Model check.** Image generation is mechanical MCP work. If on Opus, mention it and offer a Sonnet swap to save credits.
2. **Brand and claims.** Ask which brand and product this is for. Look for an approved-claims source (brand brain, claim register, the PDP, or the compliance notes in this repo's `README.md` if the product is the one this repo builds). Supplements are held to FDA structure/function rules: no diagnose, treat, cure or prevent claims. If no approved-claims source exists, say so and keep copy to claims the PDP already makes.
3. **Inventory inputs, and name the gaps instead of inventing facts:**
   - The native winner (Step 1) and its results
   - Real product photos: straight on, three-quarter angle, packaging, in use
   - VOC: post-purchase survey responses, reviews, ad comments
   - Swipe file or swipe references
   - The person's own docs, if they use them: static bootstrap doc (TOF/MOF/BOF learnings), ideas doc, build prompt
4. **Live-verify Higgsfield.** Call `mcp__Higgsfield__balance` and report credits plainly: "Higgsfield: connected, [N] credits." If it errors, STOP and say: "The Higgsfield MCP isn't connected. Reconnect it before we generate anything. I can still write the concepts, headlines and prompts without it."
5. **Budget before spend.** Budget about 7 credits per ad, so 10 ads cost about 70 credits before revisions. Preflight the real cost with `get_cost: true` on one job, show the batch total, and get a yes before submitting. Never spend credits on an unapproved batch.

## Step 1: The natives-first gate

Ask:
> "Which native is the winner we're building from? I need the ad ID or screenshot, its desire, avatar and angle, and its results (spend, CPA, ROAS, date range)."

- **Native winner exists:** lock in its desire, avatar and angle for the whole batch. Statics reuse the native's angle; they do not invent a new one.
- **Native winner exists but its images haven't been iterated yet:** say so. The house order is to iterate the native's images first. Proceed only if the person confirms that's done or chooses to skip it.
- **Exception, a product whose top ads are statics:** swipe those statics (Step 3) and also make natives. Keep the same headline and change the style, or redo it with the GPT static workflow.
- **Neither:** STOP and say:
> "House rule is natives first. There's no native winner to take the angle from yet, so a static batch would be testing an untested angle. Want to work on natives first, or knowingly break the rule for this batch?"

Only continue past "Neither" on an explicit yes, and record the batch as an exception in the log.

## Step 2: Pick the funnel stage

Use `AskUserQuestion` with MOF, BOF and TOF. Present the reported pattern first:

- **TOF statics never hit** for kinnym. They seem to need a listicle or advertorial prelander. Only offer TOF if a prelander exists or the person wants to test that.
- **MOF and BOF statics worked.**
- **BOF works best when** TOF has been scaling for a while, or competitors have run a long time, so there is an audience to take. kinnym reports BOF statics at $100-200/day at about 4-5 ROAS.

Funnel labels describe creative intent. Do not create retargeting audiences because an ad is called BOF unless the person asks.

## Step 3: Get the winning static or angle

Pick one source per concept and record it:

1. **From the native winner (default):** a swipe-file layout + the native's angle + VOC headlines.
2. **Swipe a static:** static winners are often concepts ripped from big brands in other niches. Sources the operators used: a gallery of about 400 top statics pulled with the TrendTrack MCP, and an X search for brands people recommend swiping.

Borrow structure, never another brand's identity, logo, protected imagery, fabricated proof or discount. A swipe is inspiration, not performance evidence.

## Step 4: Write the headlines

1. Feed VOC (survey responses, reviews, ad comments) into the headline pass. Expect about 9 headlines; launch about 3. Ask the person for their own ideas too, and mix them in.
2. **Rules:**
   - 6-8 words
   - Assume the avatar doesn't know or care about the brand
   - The image must show what the headline says
   - Make the reader feel understood
   - Keep it simple
3. **Rotate mechanics** from the "11 famous ads" set. The notes name six; ask the person for the other five if they want the full set:
   - Price comparison
   - Self-demonstrating stat (only a real, sourced stat)
   - Before/after (only within approved claims)
   - Wordplay
   - Review-style: real customer words only. Never write a fake testimonial, even though the mechanic is nicknamed "fake review".
   - Exaggerated problem
4. **Quality bar:** would someone scrolling at 11pm with this exact problem stop? Cut anything that fails it.

## Step 5: Batch matrix and approval

Before generating, show one row per ad and get approval:

| Field | Content |
|-------|---------|
| Ad ID | `<brand>-S<batch>-<n>`, e.g. `acme-S3-2`. Never reuse an ID. |
| Parent | The native winner's ad ID, or the swipe source |
| Funnel | TOF / MOF / BOF |
| Desire / Avatar / Angle | From the native winner |
| Hypothesis | For [AVATAR], changing [VARIABLE] while holding [CONTROLS] fixed should improve [METRIC], because [EVIDENCE]. |
| Mechanic | From Step 4 |
| Headline | Exact on-image text |
| Layout source | Swipe reference |
| Palette / type / layout | Must differ from the previous ad in the batch |
| Product refs | Which real photos the job uses |

Approval of an earlier draft does not cover changed content.

## Step 6: Build the images (Higgsfield)

**Settings lock.** Every job uses `mcp__Higgsfield__generate_image` (or `generate_image_batch`) with:
- `model: "gpt_image_2"`, `quality: "high"`, `resolution: "2k"`, `aspect_ratio: "1:1"`
- Product photos passed in `medias` with role `image`. Upload local photos with `media_upload` first.

If any setting is rejected, STOP and report the exact error. Do not silently switch model, quality, size or ratio.

**Product photo gate.** MOF/BOF jobs run only with real product photos as references, so the product isn't invented. With no photos, build only the TOF jobs and say which MOF/BOF jobs were held back and why.

**Prompt order.** Write every image prompt in this order:
1. **Format:** what kind of ad this is (e.g. "1:1 static Facebook ad, review-style card")
2. **Layout:** where the text and image sit
3. **Exact headline text:** in quotes, spelled exactly
4. **Main visual:** the photo, with the product taken from the reference images
5. **Palette:** 2-3 colours
6. **Style:** TOF looks phone-shot and imperfect. MOF/BOF is clean with a plain background.
7. **Negative guards:** what must not appear (invented labels, extra products, distorted packaging, extra text, other brands)

**Variation rule.** Palette, type and layout must change between consecutive ads.

**Run in batches.** Submit independent jobs with `generate_image_batch`, wait with `jobs_wait`, then show them with one `show_generation_by_ids`. Retry a failed job once with the same prompt. If it fails again, report it and move on.

**Inspect every output** for product fidelity, packaging, brand spelling, headline accuracy, claims the image implies, contrast, mobile readability and cropping. Do not claim small label text is accurate without checking it.

**Retype the text.** AI text rendering is unreliable. Tell the person to reset the headline type in Canva or Photoshop before launch, even when the render looks right.

**Optional idea loop (the person's own docs):** if they paste a static bootstrap doc and ideas doc, the prompts are:
- Paste the bootstrap doc once per conversation.
- "I want you to create ADs for [FUNNEL]. This is for the desire: [DESIRE]. This is the amount of unique ideas I want: [AMOUNT]", with the ideas doc pasted each time.
- "I want you to change idea [#]. This is because [WHY]", so the same mistake isn't repeated.

Tip for the person: paste long prompts with Ctrl+Shift+V so they stay editable text and the placeholders can be filled in.

## Step 7: Primary text

Primary text matters less than on natives. Two options:
- **Advertorial:** tease the story the advertorial tells.
- **Short native intro:** a few lines in the native's voice, ending in "read more...".

Write it from the final static plus the research docs (VOC, avatar, survey). Same claims rules as the headline.

## Step 8: Launch and read results

- **Verdict timing:** 7 days for the official verdict. 3-6 days only if the ad has already spent a lot or was killed early.
- Low spend and immature data are not proof of failure. Label those results "inconclusive", not "loser".
- Record per ad ID: date range, attribution, spend, CTR, CPC, purchases, CPA, revenue, ROAS. Never invent a missing metric.

Reported reference points (single tests, kinnym):
- A static swiped from baz's file hit $23.80 per purchase and 3.90 ROAS on launch day.
- BOF statics hit 5.27 and 4.86 ROAS on the dashboard.

## Step 9: Iterate a winning static (Evolve order)

Change one thing per round, everything else identical:

1. **Images first:** three meaningfully different images (product in use, close-up, comparison, different context). Same headline, copy and offer.
2. **Headlines next,** on the best image.
3. **Then benefit and persona framings.**

Name and number every iteration (`acme-S3-2.i1`, `.i2`, `.i3`). In Evolve's example, the image showing the product in use vastly outperformed the others. Treat that as a hypothesis worth testing first, not a rule.

## Step 10: Close the loop

1. Log each ad by ID: hypothesis, variable changed, controls, outcome, learnings. If the `ad-iteration` skill is set up, run its learnings interview and Growth Guide write-back for the batch. Otherwise append the row to `iteration-playbook/statics/<brand>/all-batches.md` and give the person the row to paste into their tracker.
2. **80/20:** once something wins, put about 80% of the next batch into iterations of it and about 20% into new concepts.
3. **Keep the top of the funnel fed:** keep TOF natives with the same desire, angle and avatar running, so MOF/BOF statics have an audience to convert.

## Voice + style rules

- ZERO em-dashes anywhere.
- No AI filler phrases.
- Every result is a hypothesis until it has a 7-day verdict.
- Never invent testimonials, stats, authority, scarcity or discounts.

## Done state

End with: "Batch S[N]: [X] statics generated, [Y] held back, [Z] credits used. Retype headlines in Canva before launch. Verdict due [date + 7 days]."
