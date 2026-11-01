"""Earn by Doing: the category page at /earn/ (useful work, honest offers).

Body copy lives in content/earn/body.html and the 40-method directory in content/earn/methods.json.
The method cards are rendered here, so the directory works without JavaScript; /earn.js only searches and filters.
Live course numbers (path position, time, activities) are stamped from courses.json so they never drift."""
import json
from pathlib import Path
from layout import page, faq_ld, e
import re
import earn_builds

R = Path(__file__).resolve().parents[2]
COURSE = 'earn-by-doing'
CAT_LABEL = {'service': 'AI-ASSISTED SERVICE', 'automation': 'AUTOMATION', 'product': 'PRODUCT & MEDIA', 'build': 'TOOL & SAAS'}
POINTS = [('offer', 'Deliverable'), ('ai', 'AI role'), ('start', '$0 start'), ('boundary', 'Boundary'), ('firstSale', 'First sale'), ('proof', 'Proof to teach'), ('recurring', 'Recurring model'), ('evidence', 'Evidence'), ('model', 'Business model'), ('why', 'Why it holds up')]


def method_card(m, kit=None):
    pts = ''.join(f'<div><b>{e(label)}</b><span>{e(m[k])}</span></div>' for k, label in POINTS if m.get(k))
    words = ' '.join(str(m.get(k, '')) for k in ('title', 'buyer', 'offer', 'ai', 'start', 'boundary', 'firstSale', 'proof', 'recurring', 'model', 'cat')).lower()
    note = f'<p class="method-buyer">{e(m["note"])}</p>' if m.get('note') else ''
    return (f'<article class="card method-card" id="method-{m["n"]}" data-n="{m["n"]}" data-cat="{m["cat"]}" data-text="{e(words)}"><div class="card-body">'
            f'<div class="method-top"><span class="card-track">{CAT_LABEL[m["cat"]]}</span><span class="method-index">#{m["n"]:02d} · {e(m["speed"])}</span></div>'
            f'<h3>{e(m["title"])}</h3><p class="method-buyer"><b>BUYER</b>{e(m["buyer"])}</p><div class="method-points">{pts}</div>{note}'
            + (f'<p class="method-actions"><a class="text-link" href="{earn_builds.ROOT}{kit["build"]}/">Practise it: Build {earn_builds.BY_SLUG[kit["build"]]["num"]:02d} →</a><a class="text-link" href="{kit["kit"]}" download>Starter kit ↓</a></p>' if kit else '') +
            f'<div class="card-bottom"><span>Strength: {e(m["strength"])} · not an earnings forecast</span></div></div></article>')


def build(courses, tools=None, **_):
    methods = json.loads((R / 'content/earn/methods.json').read_text())
    kits = earn_builds.build_all(courses, tools or {})
    assert [m['n'] for m in methods] == list(range(1, 41)), 'the directory promises 40 numbered methods'
    c = courses[COURSE]
    ids = list(courses)  # every live build path
    h, mins = divmod(c['estimatedMinutes'], 60)
    body = (R / 'content/earn/body.html').read_text()
    for k, v in {'{num}': str(int(c['num'])), '{total}': str(len(ids)), '{time}': c['time'], '{hm}': f'{h}h {mins:02d}m' if mins else f'{h}h',
                 '{lessons}': str(len(c['lessons'])), '{methods}': ''.join(method_card(m, kits[m['n']]) for m in methods)}.items():
        assert k in body, k
        body = body.replace(k, v)
    def _actions(mt):
        b = earn_builds.BUILDS[int(mt.group(2)) - 1]
        return (mt.group(1) + f'<p class="path-actions"><a class="primary" href="{earn_builds.ROOT}{b["slug"]}/">Open the workshop →</a>'
                f'<a class="text-link" href="{earn_builds.pack_url(b)}" download>Practice pack ↓</a></p>' + mt.group(3))
    body, n = re.subn(r'(<span class="card-num">(\d\d)</span>.*?)(<div class="card-bottom">)', _actions, body, flags=re.S)
    assert n == 12, n
    faq = [('Does Earn by Doing promise income?', 'No. It teaches you to find a real buyer, deliver checked work and keep evidence. Results depend on your work, your market and current provider terms.'),
           ('Do I need money to start?', 'Every method can be tested with free tiers and organic outreach. Free to start is not costless: time, provider limits and transaction fees still matter.'),
           ('Where is the full course?', 'The Earn by Doing build path has guided activities, a hosted lab and a combined capstone. Open it from the Academy or the link on this page.')]
    body += '<section class="hub-faq"><h2>Questions people ask</h2>' + ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in faq) + '</section>'
    page('/earn/', 'Earn by Doing: useful work, honest offers',
         'Turn AI skills into a real service or small product. 40 screened methods, 12 starter builds, free tools, evidence and human review. No income promises.',
         body, crumbs=[('Academy', '/academy/'), ('Earn by Doing', None)], ld=[faq_ld(faq)], scripts=('/earn.js',), styles=('/earn.css',),
         active='Earn', priority=0.9, og='/brand/earn/earn-hero.webp', wide=True)
