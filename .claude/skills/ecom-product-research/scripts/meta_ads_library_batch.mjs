#!/usr/bin/env node
/** Batch up to 5 Meta Ads Library keyword reads (one wave) in a single browser session. */
import { launch, harvest, writeJson } from './lib_browser.mjs';

const out = process.argv[2];
const keywords = process.argv.slice(3).filter(Boolean).slice(0, 5);
if (!out || keywords.length < 1) {
  console.error('Usage: node meta_ads_library_batch.mjs <out.json> <keyword...>  (max 5 per wave)');
  process.exit(2);
}

const results = [];
const context = await launch();
const page = context.pages()[0] || await context.newPage();
try {
  for (const query of keywords) {
    try {
      results.push(await harvest(page, query, { settleMs: 6000, scrolls: 4, scrollWaitMs: 1800 }));
    } catch (e) {
      results.push({ ok: false, observed_at: new Date().toISOString(), query, error: String(e) });
    }
  }
} finally {
  await context.close();
}
writeJson(out, { observed_at: new Date().toISOString(), count: results.length, results });
console.log(JSON.stringify({
  ok: results.filter(x => x.ok).length, count: results.length,
  summary: results.map(x => ({ query: x.query, ok: x.ok, ids: x.library_ids?.length ?? 0, login_wall: x.login_wall ?? null, no_ads_match: x.no_ads_match ?? null })),
  out,
}));
