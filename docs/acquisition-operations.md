# Acquisition pilot operations — 0.9.0

## Delivered

- Fifty static, indexable activity guides, canonical URLs, social JPEGs and sitemap.
- Three-activity starter: 120 estimated minutes, not independently validated.
- Optional, local SVG/PNG share cards; no automatic identity or publication.
- Consent-first funnel counts, off by default and respecting GPC. Erasure suppresses delayed event recreation. Ninety-day event retention; operator-only aggregates.
- Adult facilitator kit: a 60-minute taster, not full starter completion.
- Two original demonstrations; constructed teaching examples, not observed model-performance evidence.

## Autonomous research / bounded invitations

The existing Worker cron runs daily at **03:00 UTC (05:00 Zimbabwe/South Africa)**. It uses the existing SQLite Durable Object; no new database, queue, hosting provider or paid search API.

`OUTREACH_ENABLED=true` enables the bounded daily job. **`OUTREACH_SEND_ENABLED=false` currently prevents all invitation sends.** On 2026-10-29 the SMTP binding was replaced with a Gmail app password that passed a live SMTP login and delivered test mail from four sibling Workers; sending stays off until this Worker's own `test-sender` check passes. Research and email sending have separate switches. Research-only runs can record eligible role inboxes from the three pre-researched organisations.

The initial pilot pool is Impact Hub Harare, Uncommon.org and BongoHive. Only their exact official domains and www aliases can be fetched for contacts. Robots restrictions, source response bounds, HTTPS-only requests and same-domain redirect checks apply. Only listed organisational role addresses on that exact domain qualify; never guessed or personal addresses. A rotating public search creates a separate, unreviewed research queue. Relevance filtering is coarse: search results are not automatically verified organisations, approved recipients or evidence of demand. New domains need deliberate addition to the reviewed pool.

Safety limits: **one job/attempt per UTC day; three approved organisations total; at most one invitation per domain; no follow-up sequence.** The SQLite daily claim prevents concurrent cron/manual duplication. SMTP acceptance is recorded separately from actual delivery, a reply, a booking or a completed pilot. Unknown delivery or interrupted sending pauses automation rather than retrying and risking a duplicate. Transport/authentication failures also pause sending. Opt-out URLs use opaque random tokens; addresses are removed on opt-out or after an attempt, with hashes/domain suppression retained. Unattempted addresses expire after 90 days.

This is a small initial pilot, not unlimited autonomous cold outreach or a promise of acquisition. No pilot or partnership should be announced until a host agrees, and no session outcome should be reported until it actually happens.

## Operator access

`/operator-metrics.html` displays consented funnel aggregates and private outreach status only after a Bearer operator key is entered. The key is not bundled, persisted in browser storage, or included in URLs. The deployment operator retains it outside the repository.

Server-only secret bindings:
- `GROWTH_ADMIN_KEY`
- `OUTREACH_SMTP_USER`
- `OUTREACH_SMTP_PASSWORD`

Authenticated operations:
- `GET /api/growth/summary`
- `GET /api/outreach/summary`
- `POST /api/outreach/test-sender` — authenticates only; **does not send**.
- `POST /api/outreach/run` — respects both switches and the daily claim.

To enable sending: run `curl -X POST -H "Authorization: Bearer $GROWTH_ADMIN_KEY" https://open-practice.open-practice.workers.dev/api/outreach/test-sender`. If it reports a successful login, set `OUTREACH_SEND_ENABLED` to `"true"` in `adapters/cloudflare/wrangler.jsonc` and deploy. The sender is a personal Gmail with an app password (2-Step Verification on, myaccount.google.com/apppasswords; no Google Cloud project): see [GMAIL.md](GMAIL.md) for limits and error codes.

No SMTP password, social token, Nostr key or publishing credential belongs in a static asset, repository, screenshot, log or URL. Credentials pasted into chat should be rotated. Social publishing is a separately authorised manual operator action, not an unattended posting bot.

## Secure reading fallback

GitHub Pages serves a clearly labelled reading/download mirror at:

https://king-kunta-cpu.github.io/open-practice/

The same repository builds it using `scripts/build-reading-mirror.py` and `.github/workflows/reading-mirror.yml`. Learning pages retain the original canonical URLs. No account API, cloud saving, browser progress or analytics runs on the mirror. Downloadable offline exercises retain their own local code. Interactive workspace links point honestly to the main site.

This provides another HTTPS route for reading and downloads; it is **not** proof that a reported laptop/network TLS issue has been repaired. Independent checks of the main host verified TLS 1.2/1.3 and a valid certificate; SSL Labs simulated modern Chrome/Edge successfully on IPv4 and IPv6 endpoints. Its B grade also reflects legacy TLS on the Cloudflare-managed workers.dev service. No TLS security settings were lowered for compatibility. Investigate the exact browser error, system date, browser updates and network differences without bypassing certificate warnings.

## Verification

Run on Node 22.13+:

```
npm run build:assets
npm run check
python3 scripts/build-reading-mirror.py
python3 scripts/deploy-cloudflare-assets.py --check
```

Production browser suites cover the starter/guides/consent/erasure/share downloads, all 50 editable activities, accounts/cloud round trips, the foundation curriculum, offline exports, tools and four responsive widths. Tests use temporary accounts and erase optional test analytics. Passing QA is not independent accessibility certification, learner validation or market traction.
