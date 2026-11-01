"""Earn by Doing deliverables: 12 starter-build workshops, 12 practice packs, 40 method starter kits and the offer contract.

Called from pages_earn.build(). Everything is generated from content/earn/builds.py and content/earn/methods.json:
  /earn/builds/                      index of the 12 workshops, the 40 kits and the contract
  /earn/builds/<slug>/               brief → make (guided template or the learner's own key) → check → improve → ship
  /earn/builds.json                  manifest (checks + worked example) used by test/earn-builds.test.mjs
  /resources/earn/packs/NN-slug.zip  practice pack: README, blank template, worked example, logs, the offer contract
  /resources/earn/methods/NN-slug.md one starter kit per method, prefilled from the directory
  /resources/earn/offer-contract.md  the 10-artifact contract as a fill-in template
Zips use a fixed timestamp so rebuilding never changes them."""
import io, json, re, sys, zipfile
from pathlib import Path
from layout import page, hero, card, grid, faq_html, faq_ld, e, BASE, P
import pages_tools

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'content/earn'))
from builds import BUILDS, BY_SLUG  # noqa: E402

ROOT = '/earn/builds/'
RES = '/resources/earn/'
# Methods that no starter-build card lists still get the closest build to practise with.
NEAREST = {7: 'article-refresh', 10: 'article-refresh', 15: 'article-refresh', 22: 'workflow-map', 28: 'customer-reply-kit', 37: 'content-month'}
STAMP = (2026, 11, 1, 0, 0, 0)

CONTRACT = [('Buyer', 'One specific customer and a painful job worth solving.', ['Buyer:', 'The painful, repeated job:', 'Where I can reach five of them this week:']),
            ('Bounded offer', 'Exact deliverables, exclusions, timeline and revision limit.', ['Deliverables:', 'Exclusions:', 'Timeline (days):', 'Revisions (rounds):']),
            ('Free stack', 'Primary tool plus an offline or free alternative; note current limits.', ['Primary tool:', 'Free or offline alternative:', 'Limits checked on (date):']),
            ('Evidence', 'Source log, inputs, outputs, tests and acceptance checklist.', ['Where the evidence log lives:', 'Acceptance checklist:']),
            ('Human gate', 'Approval before publishing, messaging, spending or deletion.', ['Who approves what, and how (in writing):']),
            ('Privacy', 'Synthetic practice data; permission and minimisation for real data.', ['Practice data used:', 'Real data, with whose permission, and what I removed:']),
            ('Rights', 'Provenance and commercial-use check for text, image, audio and code.', ['Every asset, where it came from and whether it may be used commercially:']),
            ('Honesty', 'No fake proof, invented testimonials or guaranteed-income claims.', ['Claims I make, and the evidence for each:']),
            ('Sales practice', 'Five personalised prospects, not mass messages.', ['Five prospects are in sales-practice.csv, each with a reason that is specific to them.']),
            ('Economics', 'Time log, free-tier limits, delivery cost, price and a reinvestment trigger.', ['Hours per delivery:', 'Free-tier limits that could bite:', 'Delivery cost:', 'Price:', 'I will reinvest when:'])]
SALES_CSV = 'prospect (role or business, no private data),where I found them (public),why them specifically,personal first line,date sent,reply,next step\n' + ''.join(f'{i},,,,,,\n' for i in range(1, 6))
EVIDENCE_CSV = 'date,what I did,input,output,check run,result,who approved\n'
ECON_CSV = 'item,value,notes\nhours per delivery,,\nfree-tier limits that could bite,,\ndelivery cost (US$),,\nprice (US$),,\npayment fees (US$),,\nreinvestment trigger,,"e.g. after 3 paid deliveries, buy a domain"\n'
HONEST_FAQ = ('Will this make me money?', 'Nobody can promise that, and Open Practice never does. This workshop helps you make work that is worth paying for and keep the evidence. Whether anyone buys depends on your market, your outreach and your work.')


def contract_md(prefill=None):
    prefill = prefill or {}
    out = ['# The offer contract', '', 'Every Earn by Doing build ends with these 10 artifacts. They make very different businesses measurable, reviewable and safe to practise. Fill in one contract per offer.', '']
    for i, (name, why, lines) in enumerate(CONTRACT, 1):
        out += [f'## {i:02d} · {name}', f'_{why}_', '']
        out += [f'- {ln} {prefill.get(ln, "")}'.rstrip() for ln in lines] + ['']
    out += ['---', 'Open Practice · Earn by Doing · CC BY 4.0 · ' + BASE + '/earn/', '']
    return '\n'.join(out)


def blank_template(b):
    labels = {f['id']: f['label'] for f in b['fields']}
    return re.sub(r'\{(\w+)\}', lambda m: f'[[{labels[m.group(1)]}]]' if m.group(1) in labels else m.group(0), b['template'])


def readme(b):
    url = f'{BASE}{ROOT}{b["slug"]}/'
    steps = ['Read worked-example.md first. It shows a finished deliverable for an invented business.',
             f'Open the workshop at {url} or use template.md offline. Replace every [[blank]] with your own work.',
             'Do the real-world part: the interviews, tests, approvals or hand counts the template asks for. Log each one in evidence-log.csv.',
             'Run the checks in the workshop, or go through checklist.md by hand. Fix one thing at a time.',
             'Fill in offer-contract.md and pick five personalised prospects in sales-practice.csv. No mass messages.',
             'Record time and costs in economics.csv. Keep everything: it is your evidence.']
    return '\n'.join([f'# Build {b["num"]:02d} · {b["h1"]}', '', b['intro'], '', '## You will make', *[f'- {m}' for m in b['makes']], '',
                      '## Steps', *[f'{i}. {s}' for i, s in enumerate(steps, 1)], '', '## What is in this pack',
                      '- template.md: the blank deliverable', '- worked-example.md: a finished example (invented business, labelled)', '- checklist.md: the same checks the workshop runs, in plain words',
                      *[f'- {n}: a blank log for this build' for n in sorted(b.get('files', {}))],
                      '- offer-contract.md: the 10 artifacts every build ends with', '- sales-practice.csv, evidence-log.csv, economics.csv', '',
                      '## Honest limits', 'This pack teaches a way of working. It does not promise income. Use invented practice data until you have a real client, and get permission before using anyone else\'s data, media or name.', '',
                      f'Open Practice · Earn by Doing · CC BY 4.0 · {url}', ''])


def checklist(b):
    rows = []
    for c in b['checks']:
        if c.get('label'):
            rows.append(c['label'])
        elif c['t'] == 'blanks':
            rows.append('Every [[blank]] is replaced with your own words')
        elif c['t'] == 'lines':
            rows.append(f'At least {c["min"]} {c["what"]}')
        elif c['t'] == 'has':
            rows.append(f'Mentions the {c["name"]} from your brief')
        elif c['t'] == 'words':
            rows.append(f'Between {c["min"]} and {c["max"]} words')
    rows += b['selfcheck']
    return f'# Checklist · Build {b["num"]:02d} · {b["name"]}\n\n' + ''.join(f'- [ ] {r}\n' for r in rows)


def write_zip(path, entries):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = buf.getvalue()
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text() != text:
        path.write_text(text)


def pack_url(b):
    return f'{RES}packs/{b["num"]:02d}-{b["slug"]}.zip'


def method_slug(m):
    return f'{m["n"]:02d}-' + re.sub(r'[^a-z0-9]+', '-', m['title'].lower()).strip('-')


def kit_url(m):
    return f'{RES}methods/{method_slug(m)}.md'


def best_build(n):
    for b in BUILDS:
        if n in b['methods']:
            return b
    return BY_SLUG[NEAREST[n]]


def method_kit(m):
    b = best_build(m['n'])
    val = lambda k: (m.get(k) or '').strip()
    offer = val('offer') or m['title'][0].lower() + m['title'][1:] + ', scoped to one buyer'
    stack = val('start') or 'the free tiers of the tools used in the workshop below. Check current limits before you rely on them.'
    proof = val('proof') or val('evidence')
    checks = [p.strip().rstrip('.') for p in re.split(r',\s*(?![^()]*\))', proof.rstrip('.')) if p.strip()] if proof else []
    checks += [f'The work delivers what the offer says: {offer.rstrip(".")}']
    if val('boundary'):
        checks.append(f'Boundary kept: {val("boundary").rstrip(".")}')
    first = val('firstSale') or f'make one private sample of the deliverable ({offer.rstrip(".")}) for one real prospect (buyer: {val("buyer")}) and send it to them personally.'
    pre = {'Buyer:': val('buyer'), 'Deliverables:': offer, 'Primary tool:': val('start'), 'Acceptance checklist:': proof,
           'Claims I make, and the evidence for each:': 'only what the acceptance checklist proves.'}
    lines = [f'# Starter kit · Method {m["n"]:02d} · {m["title"]}', '',
             f'> Strength: {m["strength"]}. That is our screening judgement of how well this method holds up for a beginner with $0, not an earnings forecast. Typical first-sale window: {m["speed"]}.', '',
             '## The offer in one look', f'- Buyer: {val("buyer")}', f'- Deliverable: {offer}', f'- What AI does: {val("ai")}', f'- $0 start: {stack}']
    for k, label in (('boundary', 'Boundary'), ('recurring', 'Recurring model'), ('model', 'Business model'), ('why', 'Why it holds up'), ('note', 'Note')):
        if val(k):
            lines.append(f'- {label}: {val(k)}')
    lines += ['', '## Practise it first', f'Best starter build: Build {b["num"]:02d} · {b["h1"]}', f'- Workshop: {BASE}{ROOT}{b["slug"]}/', f'- Practice pack: {BASE}{pack_url(b)}', '',
              '## First sale, step by step', f'Start here: {first}', '',
              '1. Write your offer sheet for one narrow buyer (Build 01 helps). Name five real prospects you can reach without buying a list.',
              '2. Make one private sample with invented or public information. Never use someone\'s private data without permission.',
              '3. Send five personalised messages, one at a time, each with a reason that is specific to that person. No mass messages.',
              '4. Offer a small, bounded first job with a clear price, timeline and revision limit.',
              '5. Deliver, run the acceptance checks below, get written approval, and ask for an honest testimonial only after real work.', '',
              '## Acceptance checks (proof to keep)', *[f'- [ ] {c[0].upper() + c[1:]}' for c in checks],
              '- [ ] The client approved the work in writing', '- [ ] No invented reviews, numbers or guarantees anywhere', '',
              '## Five prospects (sales practice)', '| # | prospect (role or business) | why them specifically | personal first line | sent | reply |', '|---|---|---|---|---|---|', *[f'| {i} | | | | | |' for i in range(1, 6)], '',
              '## Economics', '- Hours per delivery:', '- Free-tier limits that could bite:', '- Price, and why:', '- I will reinvest when:', '', '---', '',
              contract_md(pre)]
    text = '\n'.join(lines)
    assert not re.search(r'^- [^:\n]+: *$', text.split('## Five prospects')[0], re.M) and ': \n' not in text.split('## Five prospects')[0], ('empty field in kit', m['n'])
    return text


def ship_fix(html):
    return re.sub(r'<a href="/free-tools/">See all 39 tools →</a>', f'<a href="{ROOT}">See all 12 starter builds →</a>', html)


def methods_by_n():
    return {m['n']: m for m in json.loads((R / 'content/earn/methods.json').read_text())}


def build_page(b, methods, tools, courses):
    url = f'{ROOT}{b["slug"]}/'
    cfg = dict(b, slug='earn-' + b['slug'], ext='md')
    ws = ship_fix(pages_tools.workshop_write(cfg))
    makes = ''.join(f'<li>{e(x)}</li>' for x in b['makes'])
    chips = ''.join(f'<li>{e(x)}</li>' for x in b['skills'])
    extra = (f'<p class="hub-meta">⏱ About 20–30 minutes to draft · the real-world steps take days · Works with or without AI · No signup</p>'
             f'<div class="hub-skills"><h2>You will make</h2><ul>{makes}</ul></div><div class="hub-skills"><h2>You will practise</h2><ul>{chips}</ul></div>'
             f'<p class="earn-pack-bar"><a class="primary" href="{pack_url(b)}" download>Download the practice pack (.zip)</a>'
             f'<a class="secondary" href="#example">See a finished example</a><a class="secondary" href="{RES}offer-contract.md" download>Offer contract (.md)</a></p>')
    body = hero(f'EARN BY DOING · BUILD {b["num"]:02d} · {b["track"].upper()}', b['h1'], b['intro'], extra) + ws
    body += (f'<section class="hub-section" id="example"><h2>A finished example</h2><p>The business, people and numbers are invented. It passes every check above, so you can see what “done” looks like before you start.</p>'
             f'<details class="earn-example"><summary>Show the worked example</summary><pre>{e(b["example"])}</pre></details></section>')
    body += '<section class="hub-section"><h2>Pro moves</h2><ul class="hub-list">' + ''.join(f'<li>{e(x)}</li>' for x in b['tips']) + '</ul></section>'
    ms = [methods[n] for n in b['methods']]
    body += ('<section class="hub-section"><h2>Methods this build practises</h2><p>Each method in the directory has a starter kit: the offer prefilled, first-sale steps, proof checks and the offer contract.</p>'
             + grid([card(f'/earn/#method-{m["n"]}', m['title'], 'Buyer: ' + m['buyer'], f'METHOD {m["n"]:02d}') for m in ms])
             + '<ul class="hub-list">' + ''.join(f'<li><a href="{kit_url(m)}" download>Starter kit ↓ Method {m["n"]:02d} · {e(m["title"])}</a></li>' for m in ms) + '</ul></section>')
    faq = list(b['faq']) + [HONEST_FAQ] + pages_tools.SHARED_FAQ
    body += faq_html(faq)
    nxt = BUILDS[b['num'] % 12]
    rel = [card(f'{ROOT}{nxt["slug"]}/', f'Build {nxt["num"]:02d} · {nxt["h1"]}', 'You’ll make: ' + ', '.join(nxt['makes']), 'NEXT BUILD', nxt['emoji'])]
    rel += [card(f'/free-tools/{s}/', tools[s]['name'], tools[s]['h1'], 'FREE TOOL', tools[s].get('emoji', '')) for s in b.get('extra_tools', []) if s in tools]
    if 'earn-by-doing' in courses:
        c = courses['earn-by-doing']
        rel.append(card(f'/builds/{c["id"]}.html', c['title'], 'The full build path: guided activities, a hosted lab and a combined capstone.', 'ACADEMY COURSE', '🎓'))
    body += '<section class="hub-section"><h2>Keep building</h2>' + grid(rel) + '</section>'
    steps = [('Brief', 'Answer the questions about your buyer and situation.'), ('Make', 'Fill in the guided template or draft with your own AI key.'), ('Check', 'Run the automatic checks.'),
             ('Improve', 'Fix failing items one at a time.'), ('Ship', 'Download the deliverable and do the real-world steps.')]
    ld = [{'@context': 'https://schema.org', '@type': 'HowTo', 'name': b['h1'], 'description': b['desc'], 'totalTime': 'PT30M', 'estimatedCost': {'@type': 'MonetaryAmount', 'currency': 'USD', 'value': '0'},
           'step': [{'@type': 'HowToStep', 'position': i + 1, 'name': n, 'text': x, 'url': BASE + url + '#workshop'} for i, (n, x) in enumerate(steps)]},
          {'@context': 'https://schema.org', '@type': 'LearningResource', 'name': b['name'], 'url': BASE + url, 'learningResourceType': 'Workshop', 'isAccessibleForFree': True,
           'teaches': b['skills'], 'license': 'https://creativecommons.org/licenses/by/4.0/', 'publisher': {'@type': 'Organization', 'name': 'Open Practice', 'url': BASE + '/'}},
          faq_ld(faq)]
    title = b['name'] + ' — free Earn by Doing workshop'
    if len(title) + 16 > 90:
        title = b['name'] + ' — free workshop'
    page(url, title, b['desc'], body, crumbs=[('Earn by Doing', '/earn/'), ('Starter builds', ROOT), (b['name'], None)], ld=ld,
         scripts=('/workshop.js',), styles=('/earn.css',), active='Earn', priority=0.8)


def index_page(methods):
    cards = [card(f'{ROOT}{b["slug"]}/', f'{b["num"]:02d} · {b["h1"]}', 'You’ll make: ' + ', '.join(b['makes']), b['track'].upper(), b['emoji']) for b in BUILDS]
    packs = ''.join(f'<li><a href="{pack_url(b)}" download>Practice pack ↓ Build {b["num"]:02d} · {e(b["h1"])}</a></li>' for b in BUILDS)
    kits = ''.join(f'<li><a href="{kit_url(m)}" download>Method {m["n"]:02d} · {e(m["title"])}</a> <span>· practise with <a href="{ROOT}{best_build(m["n"])["slug"]}/">Build {best_build(m["n"])["num"]:02d}</a></span></li>' for m in methods.values())
    body = hero('EARN BY DOING · 12 STARTER BUILDS', 'Make the work before you sell it.',
                'Every starter build is a hands-on workshop: answer a short brief, fill in a guided template or draft with your own free AI key, run the checks, then download a deliverable you can show a buyer. Each comes with a practice pack and a worked example. No signup, no income promises.',
                f'<p class="earn-pack-bar"><a class="primary" href="{ROOT}{BUILDS[0]["slug"]}/">Start with Build 01 →</a><a class="secondary" href="{RES}offer-contract.md" download>Offer contract (.md)</a><a class="secondary" href="{RES}earn-method-kits.zip" download>All 40 starter kits (.zip)</a></p>')
    body += '<section class="hub-section"><h2>The 12 workshops</h2>' + grid(cards) + '</section>'
    body += f'<section class="hub-section"><h2>Practice packs</h2><p>Blank templates, a worked example, the checklist, the offer contract and logs for evidence, sales practice and economics. Works offline.</p><ul class="hub-list earn-downloads">{packs}</ul></section>'
    body += f'<section class="hub-section" id="kits"><h2>40 method starter kits</h2><p>One Markdown file per method in the <a href="/earn/#methods">directory</a>: the offer prefilled, first-sale steps, proof checks, five-prospect sales practice and the offer contract.</p><ul class="hub-list earn-downloads">{kits}</ul></section>'
    faq = [HONEST_FAQ, ('Which build should I start with?', 'Build 01, unless you already have a buyer who asked for something specific. An offer sheet tells you which of the other builds is worth your time.'),
           ('Can I use these files commercially?', 'Yes. The packs and kits are CC BY 4.0: use, change and share them with credit to Open Practice. Your filled-in work is yours.')]
    body += faq_html(faq)
    ld = [{'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Earn by Doing starter builds', 'numberOfItems': len(BUILDS),
           'itemListElement': [{'@type': 'ListItem', 'position': b['num'], 'url': f'{BASE}{ROOT}{b["slug"]}/', 'name': b['h1']} for b in BUILDS]}, faq_ld(faq)]
    page(ROOT, 'Earn by Doing starter builds: 12 free workshops',
         '12 free learn-by-doing workshops that turn a skill into a checked deliverable: offer sheet, reply kit, audit, report and more. Packs, examples, 40 kits.',
         body, crumbs=[('Earn by Doing', '/earn/'), ('Starter builds', None)], ld=ld, styles=('/earn.css',), active='Earn', priority=0.85)


def build_all(courses, tools):
    methods = methods_by_n()
    assert sorted(methods) == list(range(1, 41))
    for b in BUILDS:
        assert all(n in methods for n in b['methods']), b['slug']
        missing = [s for s in b.get('extra_tools', []) if s not in tools]
        assert not missing, (b['slug'], missing)
        build_page(b, methods, tools, courses)
    index_page(methods)
    res = P / RES.strip('/')
    shared = {'offer-contract.md': contract_md(), 'sales-practice.csv': SALES_CSV, 'evidence-log.csv': EVIDENCE_CSV, 'economics.csv': ECON_CSV}
    write_text(res / 'offer-contract.md', shared['offer-contract.md'])
    for b in BUILDS:
        entries = {'README.md': readme(b), 'template.md': blank_template(b), 'worked-example.md': b['example'], 'checklist.md': checklist(b), **shared, **b.get('files', {})}
        write_zip(P / pack_url(b).lstrip('/'), {f'{b["num"]:02d}-{b["slug"]}/{k}': v for k, v in entries.items()})
    kits = {}
    for m in methods.values():
        kits[f'earn-method-kits/{method_slug(m)}.md'] = text = method_kit(m)
        write_text(P / kit_url(m).lstrip('/'), text)
    write_zip(res / 'earn-method-kits.zip', kits)
    manifest = [dict(num=b['num'], slug=b['slug'], url=f'{ROOT}{b["slug"]}/', h1=b['h1'], name=b['name'], track=b['track'], makes=b['makes'], methods=b['methods'],
                     pack=pack_url(b), checks=b['checks'], template=b['template'], fields=[f['id'] for f in b['fields']], example=b['example'], exampleValues=b['example_values'])
                for b in BUILDS]
    kitmap = {m['n']: dict(kit=kit_url(m), build=best_build(m['n'])['slug']) for m in methods.values()}
    write_text(P / 'earn/builds.json', json.dumps(dict(builds=manifest, kits=kitmap, contract=f'{RES}offer-contract.md', allKits=f'{RES}earn-method-kits.zip'), ensure_ascii=False, indent=1) + '\n')
    return kitmap
