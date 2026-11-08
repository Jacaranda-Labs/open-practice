# Open Practice
## Practical AI Engineering

Free practical learning. Independent, non-degree and non-accredited. One portable repository; no runtime package dependencies.

## Curriculum 2.0
- **6 build paths / 36 substantial activities / 36 worked examples.**
- **18 knowledge-review questions / 6 capstones / 30 rubric criteria.**
- **31 library resources**, including six foundation handbooks/packs and ten new five-activity visual packs.
- **37 fictional fixture files**, including dirty datasets, reference outputs, templates, an offline quote calculator and an offline lexical-retrieval lab.
- Approximately **24 guided hours**, an editorial estimate not yet validated with learners.

Paths: prompting and evidence; support replies; spreadsheet cleaning; browser applications; automation and human review; cloud AI and retrieval. These are practical foundations, not complete professional AI-engineering preparation. Each activity has outcomes, explanation, a worked example, guided steps, expected evidence, common mistakes, a self-check and an offline alternative. Independent subject-matter review remains pending.

Browse `/curriculum.html`. Original sources live in `curriculum/courses/` and `curriculum/fixtures/`. Generated public JSON, handbooks, fixture copies and deterministic ZIPs come from `scripts/build-curriculum.py`.

## The 50-activity practice studio
A further **50 standalone guided activities** now extend the 36 foundation activities: **86 total**, across six foundation paths plus ten five-activity collections. Visit `/activities.html`. Each new activity has an original input, copyable prompt, worked reference, five guided steps, three test checks, a four-stage illustrated guide, common mistakes, an offline route and an evidence workspace.

The release adds **50 individual covers, 50 visual guides, 50 handbooks, 50 input sheets, ten collection workbooks and ten deterministic practice packs**, plus original CSV datasets and a three-page fictional report PDF. A new editorial illustration introduces the collection. Estimated additional guided practice is 1,985 minutes (about 33 hours); combined estimated guided practice is about 57 hours. These are not learner-tested timings.

Search/filter by collection; keep local evidence; explicitly save/load account copies; record the actual route (manual fixture, design-only or hosted AI run); download a self-contained illustrated HTML workspace; reimport its progress JSON. The learner dashboard shows standalone-activity records separately from foundation progress. Existing foundation IDs and notes are unchanged.

Small deterministic tools help check JSON structure, limited regex policies (in a time-bounded worker), script-disabled HTML, basic Markdown hierarchy and actual colour contrast. They are not AI inference or complete correctness/accessibility certification. SQL/formula activities include known-reference CSV fixtures, not automatic execution against production data.

Canonical sources: `curriculum/activities/`, `curriculum/activity-collections.json`, `curriculum/activity-fixtures/`. Build with `scripts/build-activities.py` after the foundation builder. See `curriculum/ACTIVITY-AUTHORING.md` for scope, source links and corrections to unsafe/outdated claims in the original exercise drafts.

## Run and verify
Requires Node 22.13+ for native SQLite accounts, and Python 3 for the content build.
```sh
cp config/env.example .env
npm run build:assets
npm run dev
npm run check
```
The default local port is 3001. For remote preview, bind to the supplied public origin and serve over HTTPS. Node SQLite currently emits an experimental-runtime warning.

## Working platform
- Username/password accounts, hashed recovery codes, secure sessions, export and deletion; **email magic links are not implemented**.
- Explicit cloud save/load, stale-write detection, visible empty/error/retry states.
- Local progress and notes without an account. Existing first-three-activity notes/completions retain their indices; the expanded review is versioned separately.
- Standalone native HTML workspaces with all six activities, review questions, capstone rubric and editable notes. Download an updated copy to preserve edits; export JSON for online import. Fixture packs are separate downloads.
- Completion and rubric scores are **learner self-reports**, not verified credentials. Capstone threshold: at least 8/10 and 2/2 on the critical safety criterion.
- First-party named learning events, no advertising trackers. No keystrokes, private prompts or keys in event payloads; daily 90-day retention cleanup.
- Temporary learner-owned Groq, Google AI Studio/Gemini and Cloudflare connections. Activity credentials are separate from the optional company tutor. Do not put secrets in notes.
- Company tutor receives only the selected activity, not every lesson in the path. Approved fallback order: Groq → Cloudflare → Pollinations; no local/browser inference.
- Free library and three dated source-linked News Drops; these are not an automated news feed.

## Four-component ceiling / portability
Source and CI on GitHub; hosting on Cloudflare Workers; storage in a SQLite Durable Object; cloud inference. The Node/SQLite adapter and Dockerfile support migration without application rewrites. Do not add more infrastructure merely to duplicate existing functions.

```text
curriculum/              Canonical activities, fixture sources and base library
apps/web/public/         Website, generated curriculum, resources, offline exporter
packages/                Portable accounts, tutor and learner-provider APIs
adapters/cloudflare/     Worker and SQLite Durable Object adapter
adapters/node/           Node server and native SQLite adapter
migrations/              Portable SQL account schema
scripts/                 Content/assets builders, transfer preparation, secret scan
 test/                   Automated functional and curriculum tests
 docs/                   Operations, deployment, security and verification
branding/                Original artwork and licensed display font
```

## Live release / 0.8.0
- Platform: https://open-practice.open-practice.workers.dev
- My learning: https://open-practice.open-practice.workers.dev/dashboard.html
- Curriculum: https://open-practice.open-practice.workers.dev/curriculum.html
- Library: https://open-practice.open-practice.workers.dev/library.html
- Repository: https://github.com/king-kunta-cpu/open-practice

The editorial-collection interface and expanded curriculum are deployed. The existing Durable Object namespace was transferred without changing its ID or original database object selector. A pre-transfer account and saved workspace were successfully retrieved on the new hostname. The previous address redirects; sign in again on the new hostname because sessions are host-scoped. Existing browser-local drafts on the former origin do not automatically move; cloud-saved work is retained. Keep exported files if you still have unsynced local work.

`adapters/cloudflare/wrangler.jsonc` is now the production configuration. It preserves the original object selector and completed migration tag. **Do not replace it with fresh-install defaults on this deployment.** A separate `wrangler.fresh-install.jsonc` keeps company AI off and creates a new store for a genuinely new installation in another account. Use `npm run deploy:fresh` only for that case. Secrets remain in Cloudflare, not source.

See `docs/LIVE-ACCESS.md`, `docs/VERIFICATION.md` and `docs/IDENTITY-TRANSFER.md` for deployment evidence and remaining gates.

## Pilot boundaries
No accreditation, verified assessment, automatic background sync, autonomous publishing, OAuth, payment checkout or admin analytics dashboard. Before wider launch: security review, backup/restore rehearsal, stronger abuse limits, budget controls and independent content review. Prior production account/provider checks do not establish that this release is deployed.

## Licensing
Code: MIT. Original learning/library material: CC BY 4.0. Archivo Black: included, unchanged SIL Open Font License. Third-party services have separate terms. No legal clearance, professional status or vulnerability-free certification is claimed. See `docs/OPERATING-NOTES.md`, `docs/SECURITY.md` and `docs/MONETISATION.md`.

## Editorial Collection interface / 0.7.0
The public and learner interfaces now follow the requested reference’s actual cream/burgundy format: #FDF7EE canvas, #7C1F16 serif headings, #A8321F terracotta actions, white rounded cards, miniature cover selectors and a two-column collection browser. Native Georgia and Arial replace the heavy dark interface. The theme covers the homepage, dashboard, lessons, reviews/rubrics, account dialogs, curriculum, library/news, practice labs and standalone offline exports. No fabricated reader statistics, urgency, reviews, advertisements or reference-site content were copied.

45 automated tests and local/production Chromium checks cover the curriculum, retained account/offline functionality, new public collection interactions and responsive layouts. Production transfer and deployment are verified; see the live release section above.

## Verification / 0.8.0
57 automated tests pass. The new browser suite visits all 50 detailed activities, checks cover/guide loading, search/filter, evidence recording, offline edit/reopen/import, verification tools, activity account save/restore, dashboard visibility and responsive layouts. The existing foundation suite remains passing. See `docs/VERIFICATION.md` for the final production status.

## Tool field desk / 0.8.1

Visit `/tools.html` for ten external practice options linked to existing illustrated activity workspaces. Search by skill, filter by track or access route, inspect a fictional input and copy the activity prompt. Notes, tests, self-review, explicit account save/restore and standalone HTML export remain in the linked activity workspace; opening an external tool never records completion.

The directory is plain HTML/CSS/JavaScript plus `tools.json`, in this same repository and Worker. No React, Tailwind CDN, new backend, key collection or local-model runtime is introduced. Groq, AI Studio and Workers AI replace local training/simulation and unmaintained Lobe recommendations. Provider access is distinguished from learning-material access: free tiers/allocations have limits; Spaces, Canva AI and Zapier AI are conditional. No paid entitlement or commercial media license is promised.

61 automated tests pass. `scripts/tools-browser-check.mjs` checks all ten tool assignments, guide/cover loading, search/filters/empty state/reset, clipboard-denial fallback, linked workspace, account dialog and four responsive widths. Use `PREVIEW_URL` and `QA_DIR` as in the activity browser suite. The existing activity/foundation browser suites remain applicable.

## Artwork refresh / 0.8.3 — 20 of 50

Activities 01–20 now have distinct colorful AI-generated editorial art, full-bleed covers and matching illustrated workflow guides. Thirty covers/guides (21–50) still await later batches. Existing IDs, learner records and curriculum are unchanged.

To preserve image quality while keeping the deployed Worker small, public files now use the native Cloudflare **ASSETS binding on the same Worker**. No extra service, bucket or third-party image host is introduced. All requests still pass through the Worker for security headers; `.html` URLs, root mapping, API routing and learner database binding are preserved. Self-contained SVGs keep downloadable guides, collection ZIPs and offline HTML independent of network access.

`npm run build:assets` still generates a portable `static.mjs` fixture for integration tests, but production must not import it. `npm run deploy` uses Wrangler's native asset upload through the existing config. For an **existing** deployment, `scripts/deploy-cloudflare-assets.py` provides a standard-library REST uploader with explicit production database-selector and namespace checks and existing-secret retention. Run `python3 scripts/deploy-cloudflare-assets.py --check` for an offline manifest/module-budget check. Actual upload reads `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` privately from the environment, never from command arguments or source code. Do not use the fresh-install configuration on production.

67 automated tests cover artwork embedding, module budget, root and exact-HTML handling, security/cache headers, HEAD/304/404 behavior, API isolation and existing learning features. The all-50 activity and ten-tool browser suites also pass locally with the twenty refreshed covers/guides.


## Artwork refresh / 0.8.4 — activities 21–30

Ten new original AI-generated editorial illustrations and matching self-contained visual guides now cover reasoning checks, prompt frameworks, concept maps, feedback classification, résumé evidence, simulated interviews, visual priorities, outpainting, controlled automation and jargon translation. Total refreshed: **30 covers and 30 guides**. Remaining: **20 covers and guides, activities 31–50**. The gallery, tool directory, dashboard and downloadable collection packs reuse the updated art without changing activity IDs or saved work.

67 automated tests pass, including the exact artwork-batch scope, offline embedding and production module budget. Production retains the existing native same-Worker static-assets binding, original database namespace/object selector and existing secrets. No runtime, schema or infrastructure changes are needed for this batch.


## Artwork refresh / 0.8.5 — activities 31–40

Ten new original AI-generated editorial illustrations and matching self-contained guides now cover cross-topic connections, source verification, framing audits, email-thread actions, paper interpretation, audience rewrites, skeptical FAQs, plain language, fair mock interviews and contract questions. Total refreshed: **40 covers and 40 guides**. Remaining: **10 covers and guides, activities 41–50**. The updated artwork flows into the gallery, directory, dashboard and downloadable packs without changing activity IDs or learner workspaces.

67 automated tests cover artwork scope, offline embedding, existing learning features and production packaging. This artwork-only batch retains native static assets on the same Worker and requires no database, runtime or infrastructure changes.


## Artwork refresh complete / 0.8.6 — activities 41–50

The final ten original AI-generated editorial illustrations and matching self-contained guides cover Markdown structure, regex testing, validated JSON, SQL reference totals, API success/failure paths, visual prompt chaining, negative-space composition, storyboard continuity, measured contrast and synthetic focus groups. **All 50 standalone activity covers and all 50 illustrated guides are now refreshed. No activity artwork remains pending.** The minimalist composition deliberately preserves negative space, using a subject-aware crop and shorter shade behind the caption.

68 automated tests cover all fifty artwork records, embedded cover/guide images, the negative-space caption treatment, offline behavior and existing account/curriculum functionality. Native static assets stay on the same Worker; learner IDs, saved work, database bindings and company tutor credentials are unchanged.

## Discover, practice and facilitate (0.9.0)

- [50 illustrated, readable activity guides](https://open-practice.open-practice.workers.dev/practice.html)
- [Three-activity starter challenge](https://open-practice.open-practice.workers.dev/starter.html) (120 estimated minutes)
- [Adult facilitator taster kit](https://open-practice.open-practice.workers.dev/facilitators.html) (60-minute taster, not full completion)
- [Useful worked demonstrations](https://open-practice.open-practice.workers.dev/demonstrations.html)
- [Alternate HTTPS reading/download mirror](https://king-kunta-cpu.github.io/open-practice/) — explicitly not an account/cloud-saving host

Consent-first funnel counts are off by default. Sharing is optional and local. The existing daily Worker schedule performs bounded research; invitation sending remains disabled until Gmail authentication succeeds. The three-organisation pilot has strict caps, public role contacts only, opt-out and no automatic follow-ups. Research results and SMTP acceptance are never represented as learner outcomes. See [operator instructions](docs/acquisition-operations.md).

## Cover-first shelves and site information (0.9.2)

Catalogue search now keeps an explicitly accepted user query separate from DOM values that a browser/password manager may autofill. Unsolicited events and unfocused input cannot drive filtering. Account credential controls are mounted only when the learner opens the Account dialog, then removed on close. Account autofill remains available inside that explicit dialog.

Home cards, both carousel thumbnail rails, curriculum entries and tool cards display large artwork. Every one of the 31 library resources has a cover; the full illustrated library and downloads are also rendered as HTML for JavaScript-free reading. Related downloads deliberately share their build-path artwork; these are not 31 newly generated illustrations.

Shared footer navigation links the privacy policy, cookies/storage explanation, terms, licensing, accessibility statement, about, contact and help pages. These describe the current independent adult pilot and actual features, not legal certification or an audited accessibility guarantee. The contact route is the public repository issue tracker; no private support inbox or contact form is invented.


## 0.10.0 — original projects for underserved regions

Thirty original six-activity project courses extend the six existing foundations. All eleven approved supporting inputs are embedded in related lessons; none of the twenty-seven conditional or six held topics is published as a course. The audience is people across regions underserved or excluded by mainstream AI/payment providers, not one country. Access guidance checks lawful country/account eligibility, language, identity, data, cost and connectivity; manual fixtures are never represented as live AI runs.

- **36 paths / 216 path activities**, plus the unchanged **50 standalone activities**: 266 activities in total.
- **91 library resources**, complete course handbooks and ZIP packs, 30 hosted notebooks, deterministic reference code and independent fixture targets.
- Full no-JavaScript reading guides: `/builds/index.html`; Earn by Doing: `/builds/earn-by-doing.html` or `/?course=earn-by-doing`.
- Earn by Doing includes original discovery prompts, offer/handoff templates, a regional access worksheet and before-tax economics; no income guarantee or mandatory marketplace.
- New covers reuse thirty distinct existing original Open Practice illustrations with new course typography; the original six foundation paintings/covers and course sources are unchanged. These are not claimed as thirty newly generated paintings.
- Exact scope: `curriculum/expansion/scope.json`; topic locators: `topic-index.json`. Subject areas informed the new briefs; no external course lessons were copied and no affiliation is implied.
- Reference validation: `python scripts/check-expansion.py` after installing test-only dependencies from `curriculum/expansion/requirements-test.txt`. It checks thirty synthetic references and executes 71 notebook code cells; it does not contact external AI providers or validate learner outcomes.
- End-to-end checks: `scripts/expansion-browser-check.mjs`; existing six regression suites retain coverage. Non-accredited, learner self-reviewed, estimates unvalidated and independent subject review pending.

Builds remain in one repository with the existing same-Worker assets, API and database architecture. Optional hosted learner exercises do not add production platform components.
