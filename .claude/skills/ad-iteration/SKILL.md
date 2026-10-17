---
name: ad-iteration
description: Set up the Iteration Playbook (FigJam board + Growth Guide sheet) and ingest one ad batch at a time (screenshots, hooks, outcome and spend, 9-question learnings interview, hypothesis written back to the Growth Guide, card on the board). Use when logging ad results, running a learnings interview, or planning iterations on losers, spend winners, KPI winners or breakthroughs.
---

# Ad Iteration — Iteration Playbook Setup & Batch Ingestion

This skill sets up the Iteration Playbook (a FigJam board + a Growth Guide sheet) from scratch and walks you through ingesting one ad batch at a time: screenshots in, hooks extracted, outcome + spend logged, a structured 9-question learnings interview, a hypothesis written back to your Growth Guide, and a visual card built on the FigJam board.

**Hard rule: never reference any real NDA'd client or agency-client brand by name in this skill's own instructions.** This file is shared with the whole team, so it must not name specific client brands, client folders, or client FigJam boards as examples anywhere in this document. When you (Claude) run this skill for a specific person, treat whatever brand they name as private to that conversation, never carry it into another person's session or into this file.

This skill writes to a screenshots folder scoped to the brand being worked on (see Step 1 for how that path is chosen) and never assumes any other project's folder structure. A FigJam file + Growth Guide sheet are connected or created live in each session. Do not reuse a node ID, file key, or sheet ID from a prior session's memory unless the person running this explicitly confirms they want the same one reused — see the note on stale cloud data below.

## Pre-flight

1. **Model check.** This is mechanical MCP work. If on Opus, mention it and offer a Sonnet swap to save credits.
2. **Confirm the two things this run means, out loud, before touching anything:**
> "Confirming before we start: we're setting up your Iteration Playbook, whether that's brand new or picking up one you already have. We're going to connect the MCPs live (Figma for the board, Google Drive for the Growth Guide). Let's verify both are actually working before we go further, not just installed."
3. **Live-verify MCP connectivity — do not skip, do not assume from a prior session:**
   - Call `mcp__claude_ai_Figma__whoami`. If it errors or returns no user, STOP and say: "Figma MCP isn't authenticated. Open Claude Code settings → Integrations → Figma and reconnect before we go further." Do not proceed to Step 2 until this returns a valid user.
   - Call `mcp__claude_ai_Google_Drive__list_recent_files` with a small page size. If it errors, STOP and say: "Google Drive MCP isn't authenticated. Reconnect it in Integrations before we go further." Do not proceed to Step 3 until this succeeds.
   - Report both results plainly: "Figma: connected as [handle]. Google Drive: connected, can see your files." This is the moment to catch a dead connection.
4. **Stale cloud data check — an empty local folder does NOT mean the FigJam board or Growth Guide sheet are empty.** Deleting local screenshot files has zero effect on any existing Figma file or Google Sheet from prior sessions. Before Step 2 or Step 3, ask:
> "Quick check: for the FigJam board and the Growth Guide sheet, do you want a genuinely brand new file, or are you intentionally reusing an existing one? If you paste a link to a board or sheet that already has batches on it, that data will be visible the moment it loads. Just want to confirm that's expected before we go further."
Do not assume a new brand implies a brand new file, the person running this may intentionally reuse an existing FigJam/Sheet. Only proceed once they've explicitly said which they want.
5. **Set the Growth Guide write-back expectation correctly, before it comes up later:** the connected Google Drive MCP can READ a Google Sheet but it CANNOT write or update individual cells, there's no update-cell tool in that connector. Real write-back requires a separate Google Sheets service account, checked for in Step 3 below. Say:
> "One thing to flag now: the standard Google Drive connection can read your Growth Guide but can't write learnings back into it automatically. For that we need a small one-time setup, a Google Sheets service account. I'll check if you already have one set up, and if not, walk you through creating it. Takes about five minutes, one time only."

## Step 0 — Brand name + screenshots folder

Ask:
> "What brand or product is this for? And where do you want the screenshots folder created, an absolute or relative path is fine. If you're not sure, I can create it at `iteration-playbook/screenshots/<brand>/` relative to your current directory."

Slugify the brand name (lowercase, hyphenated) and lock it in as `<brand>` for the rest of the session. Lock in the chosen base path as `<screenshots-root>` (defaulting to `iteration-playbook/screenshots` if the person has no preference). Never assume a specific team's existing folder layout, always ask or default to the generic path above.

## Step 1 — Folder structure

Check whether `<screenshots-root>/<brand>/` already exists.
- If it doesn't exist, create it fresh:
```
mkdir -p "<screenshots-root>/<brand>/📦-added"
mkdir -p "<screenshots-root>/<brand>/patterns"
```
- If it already exists, treat this as a returning brand: do not wipe or recreate `📦-added/` or `patterns/`, just confirm they're present.

Confirm:
> "Done. `<screenshots-root>/<brand>/` is ready. Drop ad screenshots in there before each batch. I'll archive them to `📦-added/` automatically after ingestion. The `patterns/` folder builds a running dataset of every batch you process. After 10-15 batches it becomes your most valuable reference."

## Step 2 — FigJam board (live creation, Claude creates the file directly)

Say:
> "This step is optional. Your learnings still get stored in your Growth Guide regardless. The FigJam board is purely visual: it lets you see all your ads side by side, compare losers against breakthroughs, and spot patterns at a glance. Want me to create the board for you?"

If yes:

**1. Determine which Figma team to create it under.** Call `mcp__claude_ai_Figma__whoami`. That returns a `plans` array of every team/org the person belongs to, each with a `key` (e.g. `team::123...`), a `tier`, and a `seat`. Only a paid-tier team with a Full seat can actually get write access later in this skill, a free/starter-only account won't be able to use the board-building step at all.
   - If exactly one plan qualifies (paid tier, Full seat), use it without asking.
   - If more than one qualifies, list the qualifying team names and ask which one to use. Do not guess.
   - If none qualify, say: "None of your connected Figma teams are on a paid plan, so I can't create a board with write access. You can still do the whole learnings process without the visual board, or upgrade a team first." and skip to Step 3.

**2. Load the required guidance before calling `create_new_file`:** try the `/figma-create-new-file` skill if it's in the available skills list; otherwise call `ReadMcpResourceTool` with `server: "Figma"` and `uri: "skill://figma/figma-create-new-file/SKILL.md"`. Do not skip this even if it looks unnecessary.

**3. Create the file:** call `mcp__claude_ai_Figma__create_new_file` with `editorType: "figjam"`, a `fileName` like `"Iteration Playbook — <brand>"`, and the chosen `planKey`. This returns the new file's key and URL. Share the URL so the person can open it: "Created: [URL]."

**4. Before calling `mcp__claude_ai_Figma__use_figma` for the first time this session**, load its separate required guidance: try the `/figma-use` skill if it's in the available skills list; otherwise call `ReadMcpResourceTool` with `server: "Figma"` and `uri: "skill://figma/figma-use/SKILL.md"`. Skipping this step is the single most common cause of silent, hard-to-debug `use_figma` failures, do not skip it even if the first call looks like it might work without it. This is a separate guidance load from Step 2's `create_new_file` guidance, both are required, neither substitutes for the other.

Then build the four sections via `mcp__claude_ai_Figma__use_figma`, using the file key returned in step 3, passing `skillNames: "figma-use"` (or `"resource:figma-use"` if loaded via the MCP resource). Each section is a FRAME, 1800px wide, tall enough to hold many batches (~40000px):

| Section | x | y | w | h |
|---------|---|---|---|---|
| ❌ LOSERS | 0 | 800 | 1800 | 40000 |
| 🔍 COMPARE (Losers) | 1850 | 800 | 600 | 40000 |
| 💸 SPEND WINNERS | 0 | 41600 | 1800 | 12000 |
| 🔍 COMPARE (Spend) | 1850 | 41600 | 600 | 12000 |
| 🎯 KPI WINNERS | 0 | 54400 | 1800 | 12000 |
| 🔍 COMPARE (KPI) | 1850 | 54400 | 600 | 12000 |
| 🏆 BREAKTHROUGHS | 2500 | 800 | 1800 | 64000 |

If the board already exists (reused from a prior session), skip creation and instead discover these section node IDs by inspecting the file, never assume fixed IDs from a previous session. Sections are top-level FRAME nodes named after their emoji label. Run this read-only inspection first:
```js
const page = figma.currentPage;
const sections = page.children.filter(n => n.type === 'FRAME');
return sections.map(s => ({ id: s.id, name: s.name, x: s.x, y: s.y, width: s.width, height: s.height }));
```
Match each returned section to the labels above by name (e.g. the frame named `❌ LOSERS`). If a page has multiple top-level frames, pages can load lazily, if the returned list looks incomplete, call `await figma.setCurrentPageAsync(page)` first.

Capture the returned or discovered node IDs and hold them in-session only.

## Step 3 — Growth Guide (live connection)

Say:
> "Now connect wherever you're tracking ad batches, concepts, desires, angles, and results. That could be a Google Sheet, ClickUp, Notion, or something else. Drop the link and I'll connect to it.
>
> If you don't have one at all, that's worth fixing before you scale ad testing. Get one set up before continuing."

- **Google Sheet:** extract the Sheet ID, hold it in-session, then continue to **Step 3A — Growth Guide write-back setup** below before moving on.
- **Other tools:** note the tool, ask the person to paste the relevant batch row manually, and skip Step 3A entirely.

### Step 3A — Growth Guide write-back setup (Google Sheet only)

This is what lets Claude actually write the confirmed learnings back into the sheet instead of just reading it. Never skip the check, never assume it's already done.

**1. Check whether the credential already exists:**
```
test -f ~/.config/sheets-mcp/service-account.json && echo EXISTS || echo MISSING
```

**If EXISTS:** say "Found an existing Sheets service account on this machine. I'll use it, but you still need to confirm this specific Growth Guide sheet is shared with it." Read the file to get its `client_email` (do not print the rest of the file, only the email), and say:
> "Share your Growth Guide sheet with **[client_email from the file]** as Editor (Share button, top right of the sheet, paste that email, set to Editor). Let me know once it's done."

**If MISSING:** walk through first-time setup:

> "You'll need a Google Cloud service account, a one-time five-minute setup. Here's how:
>
> 1. Go to console.cloud.google.com and create a new project (any name, e.g. 'sheets-mcp').
> 2. In the search bar, find and enable the **Google Sheets API** for that project.
> 3. Go to IAM & Admin → Service Accounts → Create Service Account. Name it something like 'claude-sheets-access'. No roles needed at the project level, skip that step.
> 4. Open the new service account → Keys tab → Add Key → Create new key → JSON. This downloads a .json file, keep it private, never share it or commit it anywhere.
> 5. Move that downloaded file to `~/.config/sheets-mcp/service-account.json` on this machine. I can create the folder for you: `mkdir -p ~/.config/sheets-mcp`, then you move the file in.
> 6. Once it's there, tell me and I'll confirm it's readable."

Once the person confirms the file is in place, re-run the check. Read the `client_email` field from the file and say:
> "Got it. Now share your Growth Guide sheet with **[client_email]** as Editor, same as above."

**Never** print, log, or say the contents of the private key fields in the JSON. Only the `client_email` value is ever surfaced, and only so the person can paste it into a Share dialog.

**2. Install the script dependencies once per machine** (the scripts need `googleapis`; `node_modules/` is git-ignored):
```
npm ci --prefix "<this skill's base directory>"
```

**3. Verify the round trip before relying on it later — do not skip, this is the check that catches "sheet not shared yet" before you get to the learnings step:**
```
node "<this skill's base directory>/scripts/check-connection.js" --sheet <SHEET_ID>
```
Use the skill's own base directory (shown at the top of this skill's invocation context) to build `<this skill's base directory>`, do not guess or hardcode a path. This script only reads spreadsheet metadata (title + tab names), it never touches cell data. If it prints `OK: connected to "..."`, sharing worked. If it prints `FAILED`, the sheet isn't shared with the right email yet, go back, re-confirm the `client_email`, re-share, and re-run this check before moving on.

**4. Once the check passes, this is the write-back tool used later in Step 7:**
```
node "<this skill's base directory>/scripts/write-learnings.js" \
  --sheet <SHEET_ID> --tab "<tab name>" \
  --key-column "BATCH #" --batch <N> \
  --column "LEARNINGS" --text "<confirmed hypothesis>" \
  --append-if-missing
```
Neither script contains or requires any hardcoded credentials or secrets. Both only ever read whatever service account file the person running this set up locally at `~/.config/sheets-mcp/service-account.json`, on their own machine.

## Step 4 — The learnings-first principle

Say, before asking for screenshots:
> "Quick note before we start: the most common mistake with iterations is skipping the learnings step. People see a winner and immediately spin off 10 variations without understanding why it won. This playbook forces the learnings process first. Every batch builds evidence. After 10-15 batches, patterns show up in the COMPARE column, and iterations stop being guesses and start being directional bets."

## Step 5 — Screenshots

Say:
> "Drop your ad screenshots now:
> 1. Screenshot the ad on Facebook (full page view, page name visible at top)
> 2. Save to desktop
> 3. Drag into `<screenshots-root>/<brand>/`, one file per variation
> 4. Label by batch and variation: `1a.png`, `1b.png`, `1c.png`. Single variation, just `1a.png`."

Once confirmed, list the folder, read all screenshots via the Read tool, and:
1. Auto-detect batch number from filenames
2. Auto-detect variation count (a/b = 2 vars → varWidth=675; a/b/c = 3 vars → varWidth=440; a/b/c/d = 4 vars → varWidth=325; single = varWidth=1370)
3. Extract hook text (in-video text only, never Facebook primary copy above the video)
4. Confirm the page name shown belongs to the brand from Step 0

Present:
```
Brand: [brand]
Batch [N]: [X] variations detected.

Hooks:
- Var A: "[hook text]"
- Var B: "[hook text]"
...

Anything to add or correct?
```

## Step 6 — Outcome + Spend

Use `AskUserQuestion` for outcome:
- 🏆 Breakthrough
- 💸 Spend Winner
- 🎯 KPI Winner
- ❌ Loser

Then ask:
> "Two spend numbers:
> 1. How much did you spend on this specific ad in its first week?
> 2. What's the campaign's total spend for that same period?"

## Step 7 — Structured Ad Breakdown (Learnings Interview)

Walk through 9 questions sequentially. If a Google Sheet was connected in Step 3 and contains a row for this batch already (concept, desire, avatar, angle, planned awareness level, etc.), pull that row first and use it to inform each hypothesis instead of asking cold. Present each hypothesis against the planned data and ask the person to confirm or correct it. If no prior row exists, ask each question fresh.

**Tone:** everything is a hypothesis. Never state things as fact. Use "our hypothesis is...", "this looks like...", "likely...", "we think...". Avoid "yes exactly" or "correct", use "that tracks" or "noted, keeping that as our hypothesis."

1. **Market Awareness Level** — hook-level only (what awareness level does the hook itself speak to: Unaware / Problem Aware / Solution Aware / Product Aware / Most Aware). Do not ask whether it "stays consistent across the hook, bridge, and copy," awareness level is a hook-level classification, not a whole-ad one.
2. **Valence + Intensity** — hypothesis on zone from the hook/bridge tone. Confirm or correct.
3. **Desire** — what desire or outcome is the ad promising? Does it deliver?
4. **Avatar** — who specifically is this speaking to? Does the copy actually reach them?
5. **Angle** — what's the core reason someone buys after watching? Is it clear?
6. **Mechanism** — is a new/specific way the product delivers results shown, implied, or missing?
7. **Belief** — what builds trust here? Authority figure, credential, strategic copy, or nothing?
8. **Positioning** — what's different here vs. what the viewer has already seen? Skip if unclear, this one's advanced.
9. **Urgency** — what gets worse for the avatar if they don't act? Is that communicated?

**Brain dump (after Q9):**
> "Last thing. Raw brain dump. From a copy and creative standpoint, what do you think is actually driving performance? Don't overthink it."

**Synthesize** a 3-5 sentence hypothesis for the banner. Hypothesis-framed, no em-dashes, no "this clearly works because." Show it before locking in:
> "Anything to change before I lock this in and save it as learnings?"

**Write it back:**
- If a Google Sheet was connected in Step 3 and the write-back setup in Step 3A succeeded, run the `write-learnings.js` script (command shown in Step 3A) with the confirmed hypothesis text. Confirm success by reporting exactly what the script printed, don't assume it worked.
- If write-back setup was skipped, wasn't completed, or the sheet write fails, present the confirmed hypothesis as text and say "copy this into your Growth Guide's Learnings column for batch [N]," then move on.
- Always append the same row to the local `patterns/all-batches.md` tracker regardless of what happens with the Sheet, so nothing is lost.

## Step 8 — Iterations (Breakthroughs + Spend Winners only)

Skip for Losers and KPI Winners. Otherwise:
1. Flag any components from Step 7 that were absent or weak as natural iteration candidates.
2. Pull any explicit iteration signals from the brain dump ("we could try...", "an iteration where...").
3. Ask directly what iterations to run.

Compile and confirm before locking in.

## Step 9 — Video link

Ask for the ad video link (Frame.io, Drive, wherever). Use as the hyperlink on the FigJam card title.

## Build the card

**1. Compute baseY — always scan dynamically, never hardcode:** get the target section node by the ID captured/discovered in Step 2, scan all its children, `baseY = max(child.y + child.height) + 80` (or `820` if the section is empty).

**2. API notes:**
- STICKY nodes can't be resized via the plugin API. Use `createShapeWithText()` with `shapeType = 'ROUNDED_RECTANGLE'` for every card, then `.resize(w, h)`, not `resizeWithoutConstraints`.
- Always `section.appendChild(node)` BEFORE setting `node.x` / `node.y`, coordinates are section-relative and only apply once the node is a child of the section.
- Clear drop zone placeholder text after creation: `dropZone.text.characters = ''`.
- Section width in this spec is 1800px. If you're building into an existing board with a different section width, compute `scale = section.width / 1800` and multiply every x, width, and gap value in the tables below by `scale` before using them (heights and y-offsets stay as-is, they aren't width-dependent). Do not eyeball or approximate the scale.

**3. Variation x positions (section-relative).** Components sidebar always at x=30, w=290. 60px gap to first variation.

| Var count | Each var width | Var A x | Var B x | Var C x | Var D x |
|-----------|---------------|---------|---------|---------|---------|
| 1 | 1370 | 380 | — | — | — |
| 2 | 675 | 380 | 1075 | — | — |
| 3 | 440 | 380 | 845 | 1310 | — |
| 4 | 325 | 380 | 725 | 1070 | 1415 |

**4. Vertical offsets from baseY (section-relative):**

| Element | y offset | x | w | h | Notes |
|---------|---------|---|---|---|-------|
| Divider line | baseY-40 | 0 | 1760 | 0 | LINE node |
| Title TEXT | baseY | 0 | — | — | Bold, blue `r:0.1 g:0.4 b:0.9`, hyperlinked to the video URL from Step 9 |
| Components sidebar | baseY+140 | 30 | 290 | 280 | SHAPE_WITH_TEXT ROUNDED_RECTANGLE, yellow `r:1 g:0.95 b:0.65` |
| Variation labels | baseY+140 | varX | — | — | TEXT nodes, Bold |
| Hook cards | baseY+170 | varX | varW | 240 | SHAPE_WITH_TEXT ROUNDED_RECTANGLE, blue `r:0.82 g:0.88 b:1` |
| Drop zones | baseY+430 | varX | varW | 360 | SHAPE_WITH_TEXT ROUNDED_RECTANGLE, light gray `r:0.9 g:0.9 b:0.9`. Clear text after creation. |
| "Your Take" banner | baseY+850 | 20 | 1760 | 180 | SHAPE_WITH_TEXT ROUNDED_RECTANGLE, orange `r:1 g:0.82 b:0.6` |
| Iterations | baseY+1070 | 20 | 1760 | 160 | SHAPE_WITH_TEXT ROUNDED_RECTANGLE, green `r:0.8 g:1 b:0.8`. Breakthroughs + Spend Winners only. |

**5. Work in 3 `use_figma` calls** (each needs `skillNames: "figma-use"` per the guidance loaded in Step 2):
- Call 1: Divider + Title + Components sidebar
- Call 2: Variation labels + Hook cards (all vars)
- Call 3: Drop zones + Take banner + Iterations (if applicable). Capture the drop zone node IDs, needed for Upload below.

**6. Text formats:**

Hook card:
```
🪝 HOOK:
[hook text from Step 5]

📊 Valence + Intensity:
Zone X (label)
```

Components sidebar (fill from whatever Growth Guide data is available, "—" for anything not connected):
```
Concept: [value or —]
Date: [value or —]
Desire: [value or —]
Avatar: [value or —]
Angle: [value or —]
Awareness: [value or —]
Ad Type: [value or —]
Mechanism: [value or —]
Belief: [value or —]
```

Iterations card:
```
🔁 Iterations:
1. [Short title]: [one sentence — what to test]
2. [Short title]: [one sentence]
```

Take banner text: the synthesized hypothesis from Step 7. Hypothesis-framed, no em-dashes.

## Upload + Archive

1. For each drop zone node ID captured above, call `mcp__claude_ai_Figma__upload_assets` with `nodeId=<drop zone id>`, `count=1`, `scaleMode=FIT`.
2. POST the returned upload URL: `curl -s -X POST -F "file=@<path>" "<submitUrl>"`.
3. **Run uploads sequentially, one at a time, not in parallel** — parallel POSTs cause the submit URLs to expire before they're used. Get the URL, POST it immediately, confirm `success:true`, then move to the next screenshot.
4. Only after every upload returns `success:true`, archive the batch's screenshots to `<screenshots-root>/<brand>/📦-added/`.

## Voice + style rules

- ZERO em-dashes anywhere.
- No AI filler phrases.
- V&I labels: `Zone X (label)` ONLY.
- Per-outcome emoji prefixes always: 🏆 💸 🎯 ❌
- **Never name a real client brand, real Growth Guide file, or real FigJam board in this skill's own instructions.** Whatever brand a person names when running the skill lives only in that session.

## Done state

End with: "Batch [N] ingested + [N] screenshots placed + archived. [FigJam link]. Ready for next."
