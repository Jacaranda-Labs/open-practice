# Live access — 0.8.0 / 21 October 2026

- Platform: https://open-practice.open-practice.workers.dev
- My learning: https://open-practice.open-practice.workers.dev/dashboard.html
- Activity studio: https://open-practice.open-practice.workers.dev/activities.html
- Curriculum: https://open-practice.open-practice.workers.dev/curriculum.html
- Library: https://open-practice.open-practice.workers.dev/library.html
- News: https://open-practice.open-practice.workers.dev/news.html
- Privacy: https://open-practice.open-practice.workers.dev/privacy.html
- Repository: https://github.com/king-kunta-cpu/open-practice

The existing repository was renamed, not duplicated. The existing learner namespace/object were preserved during the Worker transfer. An account created before transfer signed in on the new host and retrieved the same notes and progress. A stale update was rejected with HTTP 409. The company tutor returned an actual Groq response. Daily retention cleanup is configured at 03:00 UTC.

The previous public address now redirects to the current hostname. The retired redirect has no database or tutor-secret binding and no scheduled task. The original host's sessions are not copied: sign in again. Account-saved work remains available; origin-local drafts do not automatically transfer. Restore an exported per-path progress JSON when needed. No whole-account automatic bulk import is claimed.

## Operator access
- GitHub: https://github.com/login
- Cloudflare: https://dash.cloudflare.com/
- Groq: https://console.groq.com/

No default administrator account/password exists. Content is managed in the repository. Credentials are managed in the hosting secret manager, never committed or added to downloads. Rotate the GitHub and Cloudflare tokens exposed in conversation after verification. Email magic-link login remains unimplemented; no verified sender/domain/service is configured.

## Tool field desk

The illustrated external-tools directory is at `/tools.html`. It links into the existing evidence/account/offline activity workflows; external accounts remain learner-owned and access/paid-feature caveats are shown on every card.


## Artwork batches / 0.8.3

The activity catalogue `/activities.html` now contains refreshed artwork for activities 01–20; activities 21–50 remain pending. Direct examples: `/activities.html?activity=voice-delivery` and `/activities.html?activity=debate-opponent`. Native Cloudflare static assets are attached to the same Worker, with security-header processing retained. Existing accounts and cloud progress use the unchanged database namespace and object selector.


## Artwork batch 3 / 0.8.4

Activities 01–30 have refreshed artwork and illustrated guides. Activities 31–50 remain pending. Examples: `/activities.html?activity=visual-priority`, `/activities.html?activity=concept-map` and `/activities.html?activity=automation-blueprint`.


## Artwork batch 4 / 0.8.5

Activities 01–40 have refreshed artwork and illustrated guides. Activities 41–50 remain pending. Examples: `/activities.html?activity=connection-graph`, `/activities.html?activity=source-verifier` and `/activities.html?activity=paper-decoder`.


## Artwork complete / 0.8.6

All 50 standalone activities have refreshed artwork and illustrated guides. Examples from the final batch: `/activities.html?activity=visual-prompt-chain`, `/activities.html?activity=storyboard-continuity` and `/activities.html?activity=contrast-check`. The complete set is available through `/activities.html` and the matching collection ZIPs; no activity artwork remains pending.


## HTTPS troubleshooting

If another device reports an unsupported protocol or certificate error, see [the safe HTTPS diagnostic procedure](HTTPS-TROUBLESHOOTING.md). It distinguishes a verified server response from an unverified client-specific failure; no certificate checks should be bypassed.
