#!/usr/bin/env node
/** Single Meta Ads Library read (keyword or full Ads Library / page URL) in an isolated headless browser. */
import path from 'node:path';
import { launch, harvest, writeJson, stateDir } from './lib_browser.mjs';

const input = process.argv[2];
if (!input) {
  console.error('Usage: node meta_ads_library_probe.mjs "<keyword-or-full-URL>" [out.json]');
  process.exit(2);
}
const out = process.argv[3] || path.join(stateDir, 'meta-probe.json');

let context;
try {
  context = await launch();
  const page = context.pages()[0] || await context.newPage();
  const result = await harvest(page, input, { settleMs: 8000, scrolls: 6, scrollWaitMs: 2500 });
  writeJson(out, result);
  console.log(JSON.stringify({
    ok: result.ok, title: result.title, chars: result.body_text.length, links: result.links.length,
    library_ids: result.library_ids.length, destinations: result.destinations.length,
    login_wall: result.login_wall, no_ads_match: result.no_ads_match, out,
  }));
} catch (e) {
  console.error(JSON.stringify({ ok: false, error: String(e), out }));
  process.exitCode = 1;
} finally {
  if (context) await context.close();
}
