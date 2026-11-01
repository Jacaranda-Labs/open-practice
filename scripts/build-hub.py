#!/usr/bin/env python3
"""Build the Open Practice hub: free tools, API keys, academy, learn, directory, prompts, glossary, community.
Then unify header/footer on every page and write sitemap.xml, robots.txt and llms.txt. No network."""
import json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / 'hub'), str(HERE.parent / 'content/hub')]
import layout
from layout import P, BASE, header, FOOTER, URLS, UPDATED, e
import pages_tools, pages_keys
from tools_write import WRITE
from tools_build import BUILD, DEV, SPECIAL

courses = {c['id']: c for c in json.loads((P / 'courses.json').read_text())}
TOOLS = BUILD + WRITE + DEV
assert len(TOOLS) + len(SPECIAL) == 39, len(TOOLS) + len(SPECIAL)
slugs = [t['slug'] for t in TOOLS + SPECIAL]
assert len(slugs) == len(set(slugs)), 'duplicate tool slug'
BY_SLUG = {t['slug']: t for t in TOOLS + SPECIAL}

# ---- sections ------------------------------------------------------------
import covers
print("tool covers:", covers.write_tool_covers(TOOLS + SPECIAL, pages_tools.CAT_NAME), "of", len(TOOLS) + len(SPECIAL))
# 0.11.5: a library item with its own illustration (branding/library-art/<id>.webp) points its image at
# /brand/library/<id>.svg in curriculum/library-base.json; the SVG is written here, and a pointer with no art fails.
_lib = [r for r in json.loads((HERE.parent / 'curriculum/library-base.json').read_text()) if str(r.get('image', '')).startswith('/brand/library/')]
for _r in _lib:
    assert covers._art('library', _r['id']), 'library item points at art that does not exist: ' + _r['id']
print("library covers:", covers.write_library_covers(_lib), "of", len(json.loads((HERE.parent / 'curriculum/library-base.json').read_text())))
pages_tools.index_page(TOOLS, SPECIAL)
for t in TOOLS:
    pages_tools.tool_page(t, all_by_slug=BY_SLUG, courses=courses)
pages_keys.build()

import importlib
for name in ['pages_academy', 'pages_learn', 'pages_directory', 'pages_earn']:
    try:
        mod = importlib.import_module(name)
    except ModuleNotFoundError as err:
        if err.name == name:
            continue
        raise
    mod.build(courses=courses, tools=BY_SLUG)


# ---- stamp live counts into hand-written pages so they never drift after merges
def _stamp():
    import re as _re
    cs = json.loads((P / 'courses.json').read_text())
    n = len(cs); hrs = round(sum(c.get('estimatedMinutes', 0) for c in cs) / 60)
    found = [c for c in cs if not c.get('sourceListingNumber') and c.get('expansionIndex') is None]
    fl = sum(len(c['lessons']) for c in found)
    words = {3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight'}
    subs = {'index.html': [(r'Explore \d+ practical AI build paths', f'Explore {n} practical AI build paths'),
                           (r'<strong>\d+</strong><span>Build paths', f'<strong>{n}</strong><span>Build paths'),
                           (r'<strong>~\d+h</strong>', f'<strong>~{hrs}h</strong>'),
                           (r'BUILD PATH 1 OF \d+', f'BUILD PATH 1 OF {n}'),
                           (r'\d+ BUILD PATHS / \d+ PRACTICAL ACTIVITIES', f'{len(found):02d} FOUNDATION PATHS / {fl} PRACTICAL ACTIVITIES')],
            'about.html': [(r'\w+ foundation build paths contain \d+ guided activities', f'{words.get(len(found), str(len(found)))} foundation build paths contain {fl} guided activities')]}
    for name, rules in subs.items():
        f = P / name
        if not f.exists():
            continue
        t = f.read_text()
        for pat, rep in rules:
            t = _re.sub(pat, rep, t)
        f.write_text(t)
_stamp()

if (P / '404/index.html').exists():
    (P / '404.html').write_text((P / '404/index.html').read_text())

# ---- unify chrome on every other page --------------------------------------
ACTIVE = {'curriculum.html': 'Academy', 'activities.html': 'Academy', 'library.html': 'Academy', 'dashboard.html': 'Academy', 'tools.html': 'Tools', 'news.html': 'News'}
generated = {str(p) for p in P.rglob('index.html')}
existing = []
for path in sorted(P.rglob('*.html')):
    rel = path.relative_to(P).as_posix()
    if rel.startswith('resources/') or str(path) in generated and '/' in rel:
        continue
    text = path.read_text()
    if '<header' not in text:
        continue
    active = ACTIVE.get(rel, 'Academy' if rel.startswith(('builds/', 'activities/')) else '')
    text = re.sub(r'<header[^>]*>.*?</header>', lambda m: header(active), text, count=1, flags=re.S)
    text = re.sub(r'<footer[^>]*>.*?</footer>', lambda m: FOOTER, text, count=1, flags=re.S)
    text = re.sub(r'Browse all \d+ paths', f'Browse all {len(courses)} paths', text)
    if '/hub.css' not in text:
        text = text.replace('<link rel="stylesheet" href="/style.css">', '<link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/hub.css">', 1)
    if '/nav.js' not in text:
        text = text.replace('</body>', '<script type="module" src="/nav.js"></script></body>', 1)
    path.write_text(text)
    if 'name="robots" content="noindex' not in text and rel != 'operator-metrics.html':
        existing.append(rel)

# ---- sitemap, robots, llms.txt -------------------------------------------
def prio(rel):
    if rel == 'index.html':
        return 1.0
    if rel.startswith('builds/'):
        return 0.8
    if rel.startswith('activities/'):
        return 0.6
    return 0.5
entries = {}
for rel in existing:
    url = '/' if rel == 'index.html' else '/' + rel
    entries[url] = prio(rel)
for url, pr in URLS:
    entries[url] = pr
assert len(entries) == len(set(entries))
xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for url, pr in sorted(entries.items(), key=lambda kv: (-kv[1], kv[0])):
    xml.append(f'<url><loc>{BASE}{url}</loc><lastmod>{UPDATED}</lastmod><priority>{pr:.1f}</priority></url>')
xml.append('</urlset>')
(P / 'sitemap.xml').write_text('\n'.join(xml) + '\n')
(P / 'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /operator-metrics.html\nDisallow: /api/\nDisallow: /settings/\n\nSitemap: ' + BASE + '/sitemap.xml\n')
sections = [('Free tools (learn by doing)', '/free-tools/'), ('Free AI API keys and guides', '/api-keys/'), ('Academy courses', '/academy/'), ('Learn: beginners, seniors, kids', '/learn/'), ('Earn by Doing: useful work, honest offers', '/earn/'), ('Earn by Doing starter builds (12 workshops, 40 starter kits)', '/earn/builds/'), ('AI glossary', '/glossary/'), ('Prompt library', '/prompts/'), ('AI tools directory', '/ai-tools/'), ('LLM guide', '/llms/'), ('Comparisons', '/compare/'), ('Tutorials', '/tutorials/'), ('Use cases', '/use-cases/'), ('Tool finder quiz', '/tool-finder/'), ('News', '/news.html'), ('Community', '/community/')]
llms = ['# Open Practice', '', '> Free, independent, practical AI learning. Every lesson and tool is learn-by-doing: brief → make → check → improve → ship. No signup needed; learners can bring their own free AI key or use guided templates without AI. Original lessons are CC BY 4.0; code is MIT.', '',
        '## Sections', *[f'- [{n}]({BASE}{u})' for n, u in sections if u.rstrip('/').split('/')[-1] and (u == '/news.html' or (P / u.strip('/') / 'index.html').exists())], '',
        '## Free tools', *[f'- [{t["name"]}]({BASE}/free-tools/{t["slug"]}/): {t["desc"]}' for t in TOOLS], '',
        '## Courses', *[f'- [{c["title"]}]({BASE}/builds/{c["id"]}.html): {c["project"]}' for c in courses.values()], '',
        '## Facts', '- Not accredited; self-review is not assessment.', '- Keys entered in tools stay in the learner\'s browser and go straight to the chosen provider.', f'- Content last updated {UPDATED}.', '']
(P / 'llms.txt').write_text('\n'.join(llms))
print(f'hub: {len(URLS)} generated pages, sitemap {len(entries)} URLs')
