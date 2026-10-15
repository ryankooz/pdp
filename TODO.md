# What's left on the PDP

Open items as of Oct 14, 2026. Work happens in the unpublished theme "Copy of Veltia PDP preview (Dawn)" (ID 155567358150).

Preview: https://veltialabs.co/products/black-walnut-liquid-drops?preview_theme_id=155567358150

## Waiting on the store owner

1. **Business hours.** The footer's "Need to Get in Touch?" block now shows the email, phone (224) 484-9937 and the Springfield address. Add your hours there if you want them shown. Also update Settings → Store details to the Springfield address so order emails match the policies.
2. **Paste in the store policies.** All six are written in `policies/` (refund, shipping, terms, privacy update, contact, subscription). Follow `policies/README.md`: Settings → Policies, `<>` button, paste, save. The API connection can't save policies.
3. **Make the free gifts real before publishing.** The gift tiles under the bundles are live in the copy theme (Free Shipping on every tier, Gut Reset Guide from 2 bottles, Top Priority Order + Expedited Shipping from 3 bottles).
   - **Gut Reset Guide:** the guide itself doesn't exist yet, only the cover. Write it (or have it written), make it a $0 digital product (Shopify Digital Downloads app), and add it as a free gift on the 2- and 3-bottle tiers in Kaching so it's actually delivered.
   - **Crossed-out values ($19.99, $9.99):** only keep these if the guide is really sold at $19.99 and expedited shipping really costs $9.99 in the store. Otherwise clear the value fields in the theme editor (Free gifts block).
   - **Top Priority Order + Expedited Shipping:** set up a real faster shipping method or handling for 3-bottle orders (e.g. tag them in Kaching and ship first), or remove the tile.
   - Free shipping is already real: the shipping profile charges $0 on every order.
4. **Subscribe & save.** The Subscriptions app embed is switched off because the product has no selling plans. To offer "Refills ship every 28 days · Cancel anytime", the owner picks a discount and creates the plan in the Shopify Subscriptions app. Then switch the embed back on and add that line under the button.
5. **Publish.** In Online Store → Themes, publish "Copy of Veltia PDP preview (Dawn)". For later changes, duplicate the live theme first and work in the copy, because theme files can't be written to the live theme.

## Housekeeping (optional)

- In the copy theme's code editor, delete `sections/pdp-story.liquid` and `sections/pdp-how-to.liquid`. They're no longer used and the API can't delete theme files.
- Swap `veltia-logo.webp` for an official logo if one exists (Theme settings → Logo).
- More real reviews. Biora shows 6, the page shows 4. A reviews app such as Judge.me can collect them after each order.

## Native ads

- **D1 · The cruise ship doctor** (`natives/D1-cruise-ship-doctor.md`): copy approved Oct 14, 2026. Round 1 creatives made (3, in `natives/creatives/`). Before it runs, base it on a real customer's story or present it so it doesn't claim to be a real person's experience.
- **D2 · The Bible's bitter herbs** (`natives/D2-bible-bitter-herbs.md`): copy approved Oct 14, 2026. Round 1 creatives made (3). Same caveat as D1 about presenting the story.
- **D3 · "I never had IBS"** (`natives/D3-never-had-ibs.md`): copy approved Oct 15, 2026. Round 1 creatives made (3). Same caveat as D1 about presenting the story.

**Ad set plan (3 ad sets):** 1) cruise ship doctor: D1, plus a toned-down D4 from Biora #4 ("why do I need more pills every year?") if written; 2) Bible: D2; 3) misdiagnosis: D3.
