// The "make-mula" path was renamed "earn-by-doing" (curriculum/renames.json). Learner work, cloud rows and old links must follow it,
// and the retired name must not appear in public copy.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, readdirSync, statSync} from 'node:fs';
import {join} from 'node:path';
import {ALIASES, LAYOUT, migrateLocal, migrateRows, resolveCourse} from '../apps/web/public/course-aliases.js';
import {REDIRECTS, COURSE_ALIASES} from '../packages/core/redirects.mjs';

const OLD = 'make' + '-mula';
const store = init => { const m = new Map(Object.entries(init)); return {getItem: k => m.has(k) ? m.get(k) : null, setItem: (k, v) => m.set(k, String(v)), m}; };
const courses = JSON.parse(readFileSync(new URL('../apps/web/public/courses.json', import.meta.url)));
const earn = courses.find(c => c.id === 'earn-by-doing');

test('the renamed path exists and the old id resolves to it', () => {
  assert.ok(earn, 'earn-by-doing course');
  assert.ok(!courses.some(c => c.id === OLD));
  assert.equal(earn.title, 'Earn by Doing: useful work, honest offers');
  assert.equal(resolveCourse(OLD), 'earn-by-doing');
  assert.equal(COURSE_ALIASES[OLD], 'earn-by-doing');
  assert.equal(COURSE_ALIASES['campaign-evidence'], 'earn-by-doing');
  assert.ok(LAYOUT >= 3);
});

test('a browser that already ran the merge keeps its lesson order (identity map) and review fields', () => {
  const n = earn.lessons.length;
  const progress = {
    [OLD]: {done: [0, 7, n - 1], notes: {7: 'module two note'}, quiz: {q1: 'b'}, layout: 2},
    'campaign-evidence': {done: [0], mergedInto: OLD},
    sheets: {done: [1, 6], notes: {6: 'kept'}, layout: 2},
  };
  const s = store({'op-merge-layout': '2'});
  assert.equal(migrateLocal(progress, s), true);
  assert.deepEqual(progress['earn-by-doing'].done.sort((a, b) => a - b), [0, 7, n - 1]);
  assert.equal(progress['earn-by-doing'].notes[7], 'module two note');
  assert.deepEqual(progress['earn-by-doing'].quiz, {q1: 'b'});
  assert.equal(progress[OLD].mergedInto, 'earn-by-doing');
  assert.deepEqual(progress.sheets.done, [1, 6], 'already-merged records are never remapped twice');
  assert.equal(progress.sheets.notes[6], 'kept');
  assert.equal(s.getItem('op-merge-layout'), String(LAYOUT));
  assert.equal(migrateLocal(progress, s), false, 'runs once');
});

test('a browser from before the merge maps both old paths into the new one', () => {
  const head = ALIASES[OLD].map;
  const progress = {[OLD]: {done: [0, head.length - 1], notes: {}}, 'campaign-evidence': {done: [0], notes: {0: 'evidence'}}};
  migrateLocal(progress, store({}));
  const done = progress['earn-by-doing'].done;
  assert.ok(done.includes(0) && done.includes(head[head.length - 1]), 'own lessons and capstone');
  const start = ALIASES['campaign-evidence'].map[0];
  assert.ok(done.includes(start), 'absorbed module lesson');
  assert.equal(progress['earn-by-doing'].notes[start], 'evidence');
});

test('cloud rows under the old id are folded into the new id', () => {
  const rows = [{course_id: OLD, content: JSON.stringify({done: [3, 8], layout: 2}), updated_at: 'x'}, {course_id: 'sheets', content: JSON.stringify({done: [2], layout: 2})}];
  const out = migrateRows(rows);
  const row = out.find(r => r.course_id === 'earn-by-doing');
  assert.deepEqual(JSON.parse(row.content).done, [3, 8]);
  assert.deepEqual(JSON.parse(out.find(r => r.course_id === 'sheets').content).done, [2]);
});

test('old links redirect permanently', () => {
  assert.equal(REDIRECTS[`/builds/${OLD}.html`], '/builds/earn-by-doing.html');
  assert.equal(REDIRECTS[`/resources/handbooks/${OLD}-handbook.md`], '/resources/handbooks/earn-by-doing-handbook.md');
  assert.equal(REDIRECTS[`/resources/packs/${OLD}-practice-pack.zip`], '/resources/packs/earn-by-doing-practice-pack.zip');
  assert.equal(REDIRECTS[`/brand/covers/${OLD}.svg`], '/brand/covers/earn-by-doing.svg');
  assert.equal(REDIRECTS[`/resources/curriculum/${OLD}/hosted-lab.ipynb`], '/resources/curriculum/earn-by-doing/hosted-lab.ipynb');
});

test('the /earn/ category page renders 40 methods, the live path and the nav entry', () => {
  const html = readFileSync(new URL('../apps/web/public/earn/index.html', import.meta.url), 'utf8');
  assert.equal((html.match(/class="card method-card"/g) || []).length, 40);
  assert.equal((html.match(/data-methods="/g) || []).length, 12);
  assert.match(html, /href="\/earn\/" aria-current="page">Earn</);
  assert.match(html, /<link rel="stylesheet" href="\/earn.css">/);
  assert.match(html, /src="\/earn.js"/);
  assert.match(html, new RegExp(`BUILD PATH ${Number(earn.num)} OF ${courses.length}`));
  assert.match(html, new RegExp(earn.time));
  assert.doesNotMatch(html, /\{(num|total|time|hm|lessons|methods)\}/);
  const home = readFileSync(new URL('../apps/web/public/index.html', import.meta.url), 'utf8');
  assert.match(home, /href="\/earn\/"/);
});

test('the retired name appears nowhere in public files except the alias tables', () => {
  const root = new URL('../apps/web/public/', import.meta.url).pathname;
  const allowed = new Set(['course-aliases.js']);
  const bad = [];
  const walk = dir => { for (const f of readdirSync(dir)) { const p = join(dir, f); if (statSync(p).isDirectory()) walk(p); else if (/\.(html|js|json|md|svg|txt|xml|css|py|ipynb|csv)$/.test(f) && !allowed.has(f) && /make[-_ ]?mula|\bmula\b/i.test(readFileSync(p, 'utf8'))) bad.push(p.slice(root.length)); } };
  walk(root);
  assert.deepEqual(bad, []);
});
