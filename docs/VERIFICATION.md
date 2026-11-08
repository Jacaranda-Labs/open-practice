# Verification — 0.8.0 / 2026-10-21

**Current status: deployed to https://open-practice.open-practice.workers.dev.** The final automated suite has 45 passing tests; the production browser suite also passes. Earlier local-only sections below are retained as a chronological record. The production-deployment section contains the final migration evidence.

## Earlier local verification phase
38 automated tests pass under Node 22 with no skips. Chromium checks use the local Node preview, not the production Worker. External namespace transfer, remote repository rename/push and production deployment have **not** been executed for this release.

## Automated checks
- Six canonical paths, 36 complete activities, 18 review questions, six capstones, 30 rubric criteria; guided-time totals reconcile to 1,440 estimated minutes.
- Every activity includes outcomes, explanation, example, guided steps, evidence, common mistakes, understanding check and offline alternative.
- Legacy first-three-activity indices and notes survive; prior knowledge checks do not silently pass the expanded review.
- A 9/10 capstone fails its threshold if the critical safety criterion is only 1/2.
- Eight calculator reference cases plus multiplication overflow; cleaned expense fixture reconciles to its documented category totals.
- Tutor context contains the selected activity rather than the full path.
- Six practice ZIPs rebuild deterministically, open without archive errors and include workbook, metadata and fixtures.
- Worker-packaged ZIP/image/font bytes equal the source bytes, with correct MIME types.
- Active authored text uses current identity; historical Git records and third-party licence files are excluded from rewriting.
- Native SQLite registration, persistence, recovery rotation, export/deletion behaviour and the existing security/provider/router suite remain passing.

## Chromium local browser
- Curriculum page renders six paths and accurate 36-activity/21-resource counts.
- A path shows six activity selectors, structured examples/evidence, three review questions and five rubric controls.
- Selecting the correct review responses updates progress; critical rubric scoring changes the displayed threshold status.
- Native HTML export contains all six activities, review questions and rubric. Notes containing script-like text remain text and never execute.
- Download → open from disk → edit final-activity note → download updated copy → reopen preserves both old and new notes.
- Offline JSON reimport restores the final-activity note to the online path.
- Library renders 21 downloads; dashboard uses eight completion units and a 36-activity denominator.
- Homepage, curriculum, active cloud-AI path, dashboard, library, News Drops and privacy have no horizontal overflow at 390px.
- Offline quote fixture calculates a fractional case; lexical-retrieval fixture renders sources and explicitly reports a no-overlap query.
- A temporary account saves and retrieves the final expanded activity through the local HTTP API, then is deleted.
- No uncaught browser JavaScript errors in the successful run.

The browser suite exercises one path's full review/export round trip; structural/unit checks cover all six. Mocked provider tests do not establish live provider availability. Earlier production Groq/account tests belong to the preceding release and are not proof that 0.6.0 is live.

## Remaining gates
Independent subject-matter review, learner-tested timing, full backup/restore rehearsal, namespace-transfer rehearsal, production account-preservation verification, external rename/push/deployment, authenticated Gemini/learner Cloudflare tests, abuse/load/security review and provider budget enforcement. No email-link sender is configured. Self-review scores are not independently verified assessment.

## Optional browser runner
Start the Node server, install Playwright in a separate QA environment, then run `PREVIEW_URL=http://127.0.0.1:3001 node scripts/browser-check.mjs`. If Playwright is not installed in the repository, set `PLAYWRIGHT_MODULE` to its module path. `QA_DIR` selects an output directory; otherwise temporary OS storage is used. Playwright is test tooling, not a runtime dependency.

## Editorial Collection / 0.7.0
44 automated tests pass. The reference page’s actual CSS was inspected for its cream, burgundy, terracotta and gold palette, serif headings, rounded cards and cover/detail layout. Public and learner pages were rebuilt locally in that format. Additional Chromium checks verify public collection arrows, six selectors, Home/End keyboard navigation, course entry, cream background, native serif heading, account-dialog theme, and seven public/learner routes at 360, 390, 768 and 1024px without horizontal overflow. Existing offline download/edit/reopen/import and final-activity account save/delete checks pass under the new theme. Screenshots were visually inspected; a collapsed catalogue-card column found during inspection was fixed before the final run.

No external push, hostname transfer, account-store migration or production deployment was performed. The running preview is the current verified build.

## Production deployment / 21 October 2026
The 0.7.0 release is now live at https://open-practice.open-practice.workers.dev. The previous local-only notes above describe earlier verification stages, not the final deployment status.

- Rehearsed cross-Worker SQLite transfer on disposable Workers; identical namespace ID and retained row verified. Test Workers were then removed.
- Captured an encrypted, transaction-consistent snapshot of account/session/workspace/event tables before transfer. Recovery material is kept out of source and release ZIPs; a complete snapshot-restore rehearsal is still pending.
- Production namespace and original object ID preserved. Pre-transfer login and exact workspace retrieval succeeded on the new host, including the final expanded-activity note. No replacement account was used as a substitute.
- Stale saved-work update correctly returned 409. The company tutor returned an actual Groq response using its privately transferred credential.
- Temporary migration-proof account deleted. The former address redirects, and its Worker has no database/secret binding or cron. Destination retention cron runs daily at 03:00 UTC.
- The maintained Chromium suite passed against the real production hostname: public collection, curriculum, rich activities/review/rubric, native offline edit/download/reopen, JSON reimport, library count, dynamic dashboard, local tools, account save/retrieve/delete and mobile layout. A QA race was corrected by waiting for the activity UI before setting a file input; no application import defect was found.
- Existing remote repository renamed to `king-kunta-cpu/open-practice`; no second source repository was created.

No accreditation, audited-security status, guaranteed provider budget, email-link sender or complete operator restore drill is claimed.

## The 50-activity studio / 0.8.0
57 automated tests pass with no skips. Tests verify all 50 unique activity numbers, ten collections with five members each, substantive unique inputs/prompts/references, five guided steps per activity, 50 original covers, 50 four-stage visual guides, 50 handbooks/input sheets, deterministic collection packs, original CSV/PDF fixtures and byte-accurate Worker binary packaging. New tests cover self-review evidence requirements, bounded record normalization, contrast reference values, JSON syntax/shape errors and standalone HTML escaping.

The activity Chromium suite visits all 50 detailed views and confirms that their guides load. It exercises catalogue pagination/search/category filters; explicit manual/hosted/design route labels; local evidence/self-review; offline HTML download/edit/reopen and JSON reimport; regex, JSON, contrast and script-disabled HTML tools; temporary-account activity save/restore; dashboard activity records; and 360/390/768/1024px layouts. A long-account-name overflow found in the first run was corrected with wrapping before the passing run. Temporary accounts are deleted. The existing foundation browser suite also passes with the 31-item library.

Timing and independent subject-matter review remain pending. No paid tool access, custom model training, image generation entitlement, real-user research, accessibility certification or professional advice is implied by reading an activity. Learner-recorded completion is not independently verified.


## Tool field desk / 0.8.1

The 0.8.0 studio was published and its all-50 activity suite plus foundation suite passed on the live host. GitHub CI passed for `efa4c303ef9e`.

The 0.8.1 tool directory adds ten provider options with official access-reference links, four track filters and two access labels, reusing existing illustrated exercises rather than inventing independent mastery claims. It does not save keys or add provider bindings. The free-tier label is not a guarantee of model/feature/region availability. Canva editing alone is explicitly design-only; a Zapier manual handoff is not an automated AI run. The source list's local-training/simulation recommendations are replaced and Lobe's maintenance status is disclosed.

Local verification: 61 automated tests; ten challenge inputs/prompts/guides and related covers; directory search/track/access/reset/empty state; clipboard failure fallback; linked evidence workspace; account dialog; 360/390/768/1024px responsive layouts. No new account/workspace schema or database migration is needed.


## Artwork refresh / 0.8.2 — first ten only

Activities 01–10 have original colorful AI-generated editorial illustrations with dimensional lighting, shading and material textures. Their ten visual guides now have artwork headers, color-coded steps and shaded process diagrams. The remaining 40 activity covers/guides are not yet replaced: generation was limited to ten images in this turn. The catalogue uses larger edge-to-edge artwork instead of padded book thumbnails. The linked tools directory, dashboard, collection selectors and ZIP downloads consume the same updated assets.

Images remain self-contained in SVG data URIs, including offline HTML exports. Compressed source art and guide thumbnails live in `branding/activity-art`; the deterministic builder uses only Python's standard library. 63 automated tests cover the original functionality plus artwork embedding and the 3 MiB Worker payload ceiling. All 100 activity SVGs are XML-valid. The all-50 activity browser suite and ten-tool suite passed locally after the artwork update, including mobile layouts and offline edit/reopen.


## Artwork refresh / 0.8.3 — activities 11–20

Batch two adds ten distinct editorial scenes and ten corresponding illustrated field guides. Total refreshed: 20 covers plus 20 guides. Remaining: activities 21–50 (30 covers plus 30 guides). Every existing activity ID and learner workspace schema is preserved.

67 automated tests pass, with no skips. All 100 activity SVGs are valid XML. The all-50 activity browser suite verifies guide loading, account save/restore, self-review and offline edit/export/reopen; the ten-tool suite verifies reused covers and guides. Both pass locally at four responsive widths.

Production packaging now uses Cloudflare's native same-Worker assets binding, not inline artwork inside Worker code. Offline preflight reports 377 assets and six small Worker modules (about 7.4 KB gzip). The generated inline fixture remains available to unit tests only; it is not an additional service or production bundle. Both Wrangler configs route requests through the Worker first, preserving CSP and other security headers, exact `.html` URLs and an explicit `/` to `/index.html` mapping. Unit tests guard HEAD, 304, 404, API isolation, missing-binding failure and distinct public-page/downloadable-starter policy. The deployer checks the existing database selector before upload, retains existing secrets and checks namespace/selector/secret names afterward. No database migration is run.


Production verification for 0.8.3: root, exact `.html` pages, SVG artwork, ZIP and PDF returned expected content and headers from native assets; missing paths returned 404. The live company tutor remained configured. A first browser run exposed an image-readiness timing assumption and a request-scoped adapter accidentally retained in shared bindings during the packaging refactor. The image check now awaits decoding; per-request binding copies were restored and guarded by a new regression test before the final passing run. The repeated live all-50 activity and foundation suites passed, including temporary-account registration/save/restore/deletion and offline edit/reopen. The separate diagnostic account was recovered and deleted; no test account was retained. The ten-tool browser suite also passed on native assets.


## Artwork refresh / 0.8.4 — activities 21–30

Ten new original AI-generated editorial illustrations and matching self-contained visual guides now cover reasoning checks, prompt frameworks, concept maps, feedback classification, résumé evidence, simulated interviews, visual priorities, outpainting, controlled automation and jargon translation. Total refreshed: **30 covers and 30 guides**. Remaining: **20 covers and guides, activities 31–50**. The gallery, tool directory, dashboard and downloadable collection packs reuse the updated art without changing activity IDs or saved work.

67 automated tests pass, including the exact artwork-batch scope, offline embedding and production module budget. Production retains the existing native same-Worker static-assets binding, original database namespace/object selector and existing secrets. No runtime, schema or infrastructure changes are needed for this batch.


## Artwork refresh / 0.8.5 — activities 31–40

Ten new original AI-generated editorial illustrations and matching self-contained guides now cover cross-topic connections, source verification, framing audits, email-thread actions, paper interpretation, audience rewrites, skeptical FAQs, plain language, fair mock interviews and contract questions. Total refreshed: **40 covers and 40 guides**. Remaining: **10 covers and guides, activities 41–50**. The updated artwork flows into the gallery, directory, dashboard and downloadable packs without changing activity IDs or learner workspaces.

67 automated tests cover artwork scope, offline embedding, existing learning features and production packaging. This artwork-only batch retains native static assets on the same Worker and requires no database, runtime or infrastructure changes.


## Artwork refresh complete / 0.8.6 — activities 41–50

The final ten original AI-generated editorial illustrations and matching self-contained guides cover Markdown structure, regex testing, validated JSON, SQL reference totals, API success/failure paths, visual prompt chaining, negative-space composition, storyboard continuity, measured contrast and synthetic focus groups. **All 50 standalone activity covers and all 50 illustrated guides are now refreshed. No activity artwork remains pending.** The minimalist composition deliberately preserves negative space, using a subject-aware crop and shorter shade behind the caption.

68 automated tests cover all fifty artwork records, embedded cover/guide images, the negative-space caption treatment, offline behavior and existing account/curriculum functionality. Native static assets stay on the same Worker; learner IDs, saved work, database bindings and company tutor credentials are unchanged.
