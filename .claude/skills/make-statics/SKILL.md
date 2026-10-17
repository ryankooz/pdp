---
name: make-statics
description: One-command static ad batch. Reads the brand's standing brief, drafts the concepts, headlines, image prompts and primary text, asks once for approval and credit spend, then generates the images on Higgsfield, inspects them and saves a launch-ready batch. Use when someone says /make-statics, "make statics", "generate a batch", or "run the ads".
---

# Make Statics

Automated runner for the `native-first-statics` process. The person types one command, approves once, and gets a finished batch. All creative rules (natives first, funnel, headlines, prompt order, variation, retyping) come from `.claude/skills/native-first-statics/SKILL.md`. Read it at the start of every run and follow it. This file only decides the order and where the person is asked.

**Usage:** `/make-statics [count] [funnel] [brand]`, e.g. `/make-statics 6 BOF gut-complex`. Missing arguments fall back to the brief's defaults. With only one brief in `ads/`, the brand is that one.

**Spend rule:** nothing that costs Higgsfield credits runs without an explicit yes for that exact batch and cost. There is no standing approval and no schedule. Runs happen only when the person asks.

## 1. Load the brief

Read `ads/<brand>/brief.md`. If it doesn't exist, create it with the same headings as `ads/gut-complex/brief.md`, fill what the repo or the person can tell you, and stop for the `TO FILL` fields.

Check, without asking questions unless something is blocking:

| Check | If it fails |
|-------|-------------|
| Native winner filled in | Stop with the natives-first message from `native-first-statics` Step 1. Continue only on an explicit "break the rule", and mark the batch as an exception. |
| Real product photos listed | Build only TOF concepts and say which MOF/BOF ads were held back. |
| Photos show the current label | Warn and ask before using old-label photos. |
| Landing page filled in | Draft anyway, flag it in the approval message. |
| `mcp__Higgsfield__balance` works | Draft concepts and prompts only. Say Higgsfield is disconnected. |

## 2. Draft the batch (no questions)

Batch ID: `S<last batch number + 1>`. Ad IDs: `<brand>-S<N>-<n>`.

Following `native-first-statics` Steps 3, 4, 5 and 7:
1. Write about 9 headlines from the brief's VOC and the native winner's angle. Pick the best `count`, rotating mechanics. Review-style ads use only exact VOC lines from the brief.
2. Check every headline and primary text against the brief's Claims section. Drop anything on the "Do not use" list or marked VERIFY.
3. Give each ad a different palette, type and layout from the one before it.
4. Write each image prompt in the 7-part order.
5. Write the primary text for each ad.

## 3. Ask once

Preflight cost with `mcp__Higgsfield__generate_image` and `get_cost: true` for one job. Then send one message with:

- The batch matrix (ad ID, funnel, mechanic, headline, visual, palette, hypothesis)
- Primary text for each ad
- Anything held back or flagged in step 1
- Cost: `[count] jobs x [cost] = [total] credits`, plus up to `[count] x [cost]` more only if jobs fail and need their one retry. Current balance: `[N]`.

End with:
> "Reply **go** to generate all of these, or tell me which rows to change or drop."

Edits to rows mean redraft those rows and ask again. Only "go" (or a clear equivalent) for the batch as shown counts as approval.

## 4. Generate

1. **Photos:** for each product photo without a Higgsfield media ID in the brief, `mcp__Higgsfield__media_upload`, PUT the file with curl, `media_confirm`. Write the new media IDs back into the brief so later runs skip this.
2. **Submit** with `mcp__Higgsfield__generate_image_batch` (12 per call max). Every request: `model: "gpt_image_2"`, `quality: "high"`, `resolution: "2k"`, `aspect_ratio: "1:1"`, product photos in `medias` with role `image`, and the brief's Higgsfield folder ID if set. If any setting is rejected, stop and report the error. Do not switch settings.
3. **Wait** with `mcp__Higgsfield__jobs_wait` until every job is terminal. Keep every returned job ID. On a timeout, never resubmit until the original job's outcome is known.
4. **Retry** each failed job once with the same request (covered by the approval). A second failure is reported, not retried.
5. **Show** all jobs with one `mcp__Higgsfield__show_generation_by_ids` call.

## 5. Inspect

Download every result to `ads/<brand>/batches/S<N>/<ad id>.png` and look at each one. Check product fidelity, packaging, label and brand spelling, headline text, implied claims, contrast at phone size and cropping.

Mark each ad `pass` or `fail` with a one-line reason. A failed image is not regenerated automatically. List the failures and offer a fix batch with its own cost and approval.

## 6. Save

1. Write `ads/<brand>/batches/S<N>/manifest.json`, one entry per ad:
```json
{
  "ad_id": "gut-complex-S1-1",
  "batch": "S1",
  "parent": "<native winner ad ID or swipe>",
  "funnel": "BOF",
  "desire": "", "avatar": "", "angle": "",
  "mechanic": "",
  "hypothesis": "",
  "headline": "",
  "primary_text": "",
  "cta": "Shop Now",
  "landing_url": "",
  "image": "gut-complex-S1-1.png",
  "higgsfield_job_id": "",
  "prompt": "",
  "inspection": "pass",
  "status": "generated",
  "meta_ad_id": null,
  "results": null
}
```
   `status` moves through `generated`, `retyped`, `launched`, `measured`. `meta_ad_id` and `results` stay null until launch. Keep this shape stable: later automation reads it.
2. Write `ads/<brand>/batches/S<N>/batch.md`: the matrix, primary text and prompts in readable form.
3. **Images:** if the brief has a Drive folder ID, upload each passing image there with `mcp__Google_Drive__create_file` (`base64Content`, `contentMimeType: "image/png"`, `parentId`, `disableConversionToGoogleType: true`), record the Drive file IDs in the manifest, and don't commit the images. Without a Drive folder, commit the images with the batch.
4. Update the brief's "Last batch number" and Higgsfield media IDs.
5. Append one row per ad to `ads/<brand>/log.md`: date, ad ID, headline, mechanic, status.
6. Commit and push to the current branch. This environment is temporary, so an unpushed batch is a lost batch.

## Done state

End with:
> "Batch S[N]: [X] passed, [Y] failed, [Z] held back, [C] credits used. Images: [Drive folder or repo path]. Before launch: retype each headline in Canva or Photoshop. Verdict due [launch date + 7 days]. When results are in, run `/ad-iteration` on this batch."

## Voice + style rules

- ZERO em-dashes anywhere.
- No AI filler phrases.
- Never invent testimonials, stats, authority, scarcity or discounts.
