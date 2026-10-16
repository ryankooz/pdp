# What's left on the PDP

Open items as of Oct 15, 2026 (end of day). Live theme: "Copy of Copy of Veltia Drops" (155590262982). Make changes on a duplicate of it, then publish. Do NOT publish "Copy of Veltia Drops" (built for deleted per-bundle plans) or "Veltia Drops" (bundle subscriptions with a mismatched checkout).

Preview: https://veltialabs.co/products/black-walnut-liquid-drops?preview_theme_id=155567358150

## Before ads go live

1. **Publish** "Copy of Veltia PDP preview (Dawn)" (Online Store → Themes). The header cleanup and home page redirect only reach visitors after this.
2. **Place a test order** (Settings → Payments → test mode, or a real order you refund): check the bundle price, free shipping, the checkout header and the confirmation email.
3. **Meta tracking:** the Facebook & Instagram channel is installed. In it, confirm the pixel is connected and data sharing is set to Maximum (Conversions API), then check a test purchase shows up in Events Manager.
4. **Privacy policy:** still the Sept 10 version. Make the 3 small edits in `policies/README.md`.
5. **Store address:** Settings → Store details still says Elgin. Change it to 2501 N Chatham Rd, Suite N, Springfield, IL 62704 so emails and invoices match the policies.
6. **Claims to be able to back up:** "100k+ customers" (page and checkout header), and the trust badges "Clinically Studied Ingredients", "Third-Party Tested", "Globally Trusted Facilities". Remove any you can't prove.

## Waiting on the store owner

1. **Business hours.** The footer's "Need to Get in Touch?" block now shows the email, phone (224) 484-9937 and the Springfield address. Add your hours there if you want them shown. Also update Settings → Store details to the Springfield address so order emails match the policies.
2. **Paste in the store policies.** All six are written in `policies/` (refund, shipping, terms, privacy update, contact, subscription). Follow `policies/README.md`: Settings → Policies, `<>` button, paste, save. The API connection can't save policies.
3. **Make the free gifts real before publishing.** The gift tiles under the bundles are live in the copy theme (Free Shipping on every tier, Gut Reset Guide from 2 bottles, Top Priority Order + Expedited Shipping from 3 bottles).
   - **Gut Reset Guide:** the guide itself doesn't exist yet, only the cover. Write it (or have it written), make it a $0 digital product (Shopify Digital Downloads app), and add it as a free gift on the 2- and 3-bottle tiers in Kaching so it's actually delivered.
   - **Crossed-out values ($19.99, $9.99):** only keep these if the guide is really sold at $19.99 and expedited shipping really costs $9.99 in the store. Otherwise clear the value fields in the theme editor (Free gifts block).
   - **Top Priority Order + Expedited Shipping:** set up a real faster shipping method or handling for 3-bottle orders (e.g. tag them in Kaching and ship first), or remove the tile.
   - Free shipping is already real: the shipping profile charges $0 on every order.
4. **Subscribe & save (live, working):** Kaching Subscriptions plan "every 4 weeks, 15% off" is the only plan. Subscribe is offered on Buy 1 only ($38.24, renews $38.24 every 4 weeks; checked at checkout Oct 15). Bundles are one-time ($69.99 / $99.99). Shopify Subscriptions plans were deleted. **Open question for Kaching support:** can a 3- or 5-bottle bundle subscription renew as 1 bottle? Message drafted in chat. Until they answer, keep it as is.
5. **Publish.** In Online Store → Themes, publish "Copy of Veltia PDP preview (Dawn)". For later changes, duplicate the live theme first and work in the copy, because theme files can't be written to the live theme.

## Sale timer

The Fall Sale countdown restarts every 8 hours at the same times for everyone: 12am, 8am and 4pm Central (11pm, 7am and 3pm Central after clocks change on Nov 1). The owner changes prices manually at those times. Settings: theme editor → promo bar → "Repeat the countdown every (hours)"; set to 0 to count down to a real end date instead.

## Housekeeping (optional)

- Use a domain email (e.g. support@veltialabs.co) instead of the Gmail address. Biora uses help@trybiora.com.
- Product SEO title and description are empty (Products → Black Walnut Liquid Drops → Search engine listing).

- In the copy theme's code editor, delete `sections/pdp-story.liquid` and `sections/pdp-how-to.liquid`. They're no longer used and the API can't delete theme files.
- Swap `veltia-logo.webp` for an official logo if one exists (Theme settings → Logo).
- More real reviews. Biora shows 6, the page shows 4, and "4 reviews" sits next to "100k+ customers". A reviews app such as Judge.me can collect them after each order.

## Native ads

- **D1 · The cruise ship doctor** (`natives/D1-cruise-ship-doctor.md`): copy approved Oct 14, 2026. Round 1 creatives made (3, in `natives/creatives/`). Before it runs, base it on a real customer's story or present it so it doesn't claim to be a real person's experience.
- **D2 · The Bible's bitter herbs** (`natives/D2-bible-bitter-herbs.md`): copy approved Oct 14, 2026. Round 1 creatives made (3). Same caveat as D1 about presenting the story.
- **D3 · "I never had IBS"** (`natives/D3-never-had-ibs.md`): copy approved Oct 15, 2026. Round 1 creatives made (3). Same caveat as D1 about presenting the story.

**Ad set plan (3 ad sets):** 1) cruise ship doctor: D1, plus a toned-down D4 from Biora #4 ("why do I need more pills every year?") if written; 2) Bible: D2; 3) misdiagnosis: D3.

## Oct 16: Kaching Subscriptions on all bundles
- Kaching Subscriptions plan 15422980294 (every 4 weeks, 15% off) has a product quantity policy: 1 bottle after cycle 1.
- Theme "Veltia Drops – Kaching Subs" (155630567622) = live theme + our Subscribe & Save block disabled. Kaching's Purchase Options widget is the only subscribe UI.
- Tested on preview: Buy 1 sub $38.24; Buy 2 Get 1 sub $59.49; Buy 3 Get 2 sub $84.99; Buy 2 Get 1 one-time $69.99.
- Checkout "Recurring subtotal" still reads plan price x bundle qty ($114.72 / $191.20). Shopify computes it, and it can't be changed from the theme. Kaching's policy should bill renewals at 1 bottle ($38.24). Verify on the first real renewal.
- Widget feature line "56% of all recurring orders" is wrong (renewals are 15% off). Edit it in Kaching Subscriptions → widget → How it works.
