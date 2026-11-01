// Earn by Doing deliverables: every starter build is a real workshop with a practice pack, every method has a starter kit,
// and every worked example passes the same checks learners get in the browser.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, existsSync} from 'node:fs';
import {inflateRawSync} from 'node:zlib';
import {runChecks} from '../apps/web/public/checks.js';

const pub = p => new URL('../apps/web/public/' + p.replace(/^\//, ''), import.meta.url);
const read = p => readFileSync(pub(p), 'utf8');
const html = url => read(url.endsWith('/') ? url + 'index.html' : url);
const M = JSON.parse(read('/earn/builds.json'));
const methods = JSON.parse(readFileSync(new URL('../content/earn/methods.json', import.meta.url), 'utf8'));
const BANNED = [new RegExp('sch' + 'ool', 'i'), new RegExp('\\bmu' + 'la\\b|make[-_ ]?mu' + 'la', 'i'), new RegExp('black' + 'hat|\\bb' + 'hw\\b', 'i')];

// Minimal zip reader (central directory), enough to list and read our own deterministic packs.
function unzip(buf) {
  const files = {};
  let eocd = buf.length - 22;
  while (buf.readUInt32LE(eocd) !== 0x06054b50) eocd--;
  let off = buf.readUInt32LE(eocd + 16);
  const count = buf.readUInt16LE(eocd + 10);
  for (let i = 0; i < count; i++) {
    const method = buf.readUInt16LE(off + 10), csize = buf.readUInt32LE(off + 20), size = buf.readUInt32LE(off + 24), nlen = buf.readUInt16LE(off + 28), xlen = buf.readUInt16LE(off + 30), clen = buf.readUInt16LE(off + 32), local = buf.readUInt32LE(off + 42);
    const name = buf.toString('utf8', off + 46, off + 46 + nlen);
    const start = local + 30 + buf.readUInt16LE(local + 26) + buf.readUInt16LE(local + 28);
    const raw = buf.subarray(start, start + csize);
    files[name] = (method === 8 ? inflateRawSync(raw) : raw).toString('utf8');
    assert.equal(Buffer.byteLength(files[name]), size, name);
    off += 46 + nlen + xlen + clen;
  }
  return files;
}

test('12 starter builds, numbered in page order, each with its own workshop page', () => {
  assert.equal(M.builds.length, 12);
  assert.deepEqual(M.builds.map(b => b.num), [...Array(12)].map((_, i) => i + 1));
  const earn = html('/earn/');
  for (const b of M.builds) {
    const page = html(b.url);
    assert.match(page, /id="ws-config"/, b.slug + ' has a workshop');
    assert.ok(page.includes('<h1>' + b.h1.replace(/’/g, '’') + '</h1>') || page.includes(b.h1), b.slug + ' h1');
    assert.ok(earn.includes(b.h1), b.slug + ' card is on /earn/');
    assert.ok(earn.includes(`href="${b.url}"`), b.slug + ' card links to its workshop');
    assert.ok(earn.includes(`href="${b.pack}"`), b.slug + ' card links to its pack');
    assert.ok(page.includes(`href="${b.pack}"`), b.slug + ' page links to its pack');
    assert.match(page, /class="active"[^>]*>Earn|aria-current="page"[^>]*>Earn|>Earn<\/a>/, 'nav shows Earn');
    const cfg = JSON.parse(page.match(/<script type="application\/json" id="ws-config">(.*?)<\/script>/s)[1].replace(/<\\\//g, '</'));
    assert.equal(cfg.slug, 'earn-' + b.slug, 'progress key does not collide with a free tool');
    assert.equal(cfg.ext, 'md');
    assert.ok(cfg.prompt.length > 200 && cfg.template.includes('[['), b.slug + ' has both routes');
    assert.ok(!page.includes('See all 39 tools'), 'ship step points back to the builds, not the tools');
    for (const make of b.makes) assert.ok(page.includes(make), `${b.slug} names “${make}”`);
  }
  assert.ok(existsSync(pub('/earn/builds/index.html')));
});

test('every “You’ll make” promise on /earn/ is a section a workshop produces', () => {
  const earn = html('/earn/');
  for (const b of M.builds) {
    const card = earn.slice(earn.indexOf(`<span class="card-num">${String(b.num).padStart(2, '0')}</span>`));
    const made = card.match(/YOU’LL MAKE<\/b>([^<]+)</)[1].split(',').map(s => s.trim().toLowerCase());
    assert.deepEqual(made, b.makes.map(s => s.toLowerCase()), b.slug);
  }
});

test('every worked example passes all of its build’s checks; the blank template does not', () => {
  for (const b of M.builds) {
    const res = runChecks(b.checks, b.example, b.exampleValues);
    const failed = res.filter(r => !r.pass).map(r => r.label + (r.detail ? ' (' + r.detail + ')' : ''));
    assert.deepEqual(failed, [], b.slug + ' example');
    assert.ok(b.checks.length >= 8, b.slug + ' has a real rubric');
    const blank = runChecks(b.checks, b.template, {});
    assert.ok(blank.some(r => !r.pass && /blank/i.test(r.label)), b.slug + ' template still has blanks');
    assert.match(b.example, /^> Worked example\. The business, people and numbers are invented/, b.slug + ' example is labelled');
  }
});

test('the honesty check catches hype but allows saying what is not promised', () => {
  const rule = M.builds[0].checks.find(c => c.t === 'not' && /passive income/.test(c.re));
  const bad = ['Guaranteed results in a week', 'Earn passive income', 'risk-free', 'overnight success', 'guaranteed sales'];
  const ok = ['No guaranteed results, no invented testimonials.', 'There is never guaranteed income.'];
  for (const s of bad) assert.ok(!runChecks([rule], s)[0].pass, s);
  for (const s of ok) assert.ok(runChecks([rule], s)[0].pass, s);
  for (const b of M.builds) assert.ok(b.checks.some(c => c.t === 'not' && c.re === rule.re), b.slug + ' has the honesty check');
});

test('each practice pack is a complete, deterministic zip', () => {
  for (const b of M.builds) {
    const buf = readFileSync(pub(b.pack));
    const files = unzip(buf);
    const dir = `${String(b.num).padStart(2, '0')}-${b.slug}/`;
    for (const f of ['README.md', 'template.md', 'worked-example.md', 'checklist.md', 'offer-contract.md', 'sales-practice.csv', 'evidence-log.csv', 'economics.csv'])
      assert.ok(files[dir + f], `${b.slug} pack has ${f}`);
    assert.ok(Object.keys(files).length >= 9, b.slug + ' has a build-specific log');
    assert.equal(files[dir + 'worked-example.md'], b.example);
    assert.ok(!/\{\w+\}/.test(files[dir + 'template.md']), b.slug + ' blank template has no raw {field} placeholders');
    assert.match(files[dir + 'README.md'], /does not promise income/);
    assert.equal(buf.readUInt16LE(12), ((2026 - 1980) << 9) | (11 << 5) | 1, b.slug + ' fixed date');
  }
});

test('40 method starter kits: one per method, each pointing at a real build', () => {
  assert.equal(Object.keys(M.kits).length, 40);
  const earn = html('/earn/');
  const slugs = new Set(M.builds.map(b => b.slug));
  for (const m of methods) {
    const k = M.kits[m.n];
    assert.ok(k && slugs.has(k.build), 'method ' + m.n);
    const kit = read(k.kit);
    assert.ok(kit.includes(m.title) && kit.includes(m.buyer), 'kit ' + m.n + ' is prefilled');
    assert.match(kit, /not an earnings forecast/);
    const head = kit.split('## Five prospects')[0];
    assert.ok(!/^- [^:\n]+: *$/m.test(head) && !/: \n/.test(head), 'kit ' + m.n + ' has no empty prefilled field');
    assert.match(kit, /## 10 · Economics/);
    assert.ok(kit.includes('/earn/builds/' + k.build + '/'));
    const card = earn.slice(earn.indexOf(`id="method-${m.n}"`), earn.indexOf('</article>', earn.indexOf(`id="method-${m.n}"`)));
    assert.ok(card.includes(`href="${k.kit}"`) && card.includes(`href="/earn/builds/${k.build}/"`), 'card ' + m.n + ' links its kit and build');
  }
  const all = unzip(readFileSync(pub(M.allKits)));
  assert.equal(Object.keys(all).length, 40);
  for (const b of M.builds) for (const n of b.methods) assert.equal(typeof M.kits[n], 'object');
});

test('the offer contract is downloadable with all 10 artifacts and linked from /earn/', () => {
  const c = read(M.contract);
  for (const name of ['Buyer', 'Bounded offer', 'Free stack', 'Evidence', 'Human gate', 'Privacy', 'Rights', 'Honesty', 'Sales practice', 'Economics']) assert.match(c, new RegExp('## \\d\\d · ' + name));
  assert.ok(html('/earn/').includes(`href="${M.contract}"`));
});

test('the new pages are in the sitemap, and no banned word appears in any deliverable', () => {
  const sitemap = read('/sitemap.xml');
  for (const b of M.builds) assert.ok(sitemap.includes(b.url), b.url);
  assert.ok(sitemap.includes('/earn/builds/<'));
  const texts = [read('/earn/builds.json'), html('/earn/builds/'), read(M.contract), ...M.builds.map(b => html(b.url)), ...Object.values(M.kits).map(k => read(k.kit)),
    ...M.builds.flatMap(b => Object.values(unzip(readFileSync(pub(b.pack))))), readFileSync(new URL('../content/earn/builds.py', import.meta.url), 'utf8')];
  for (const t of texts) for (const re of BANNED) assert.ok(!re.test(t), 'banned word: ' + re + ' in ' + t.slice(0, 80));
});
