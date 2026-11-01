"""Glossary, prompts, AI tools, LLMs, comparisons, use cases, tutorials, tool finder, community, 404."""
import json
import social
from layout import page, hero, card, grid, faq_html, faq_ld, e, slugify, BASE
from reference import G, CATS, P
from directory import AI_TOOLS, TOOL_CATS, LLMS, COMPARE, USE_CASES, TUTORIALS, CHECKED

def glossary(tools):
    terms = [dict(term=t, cat=c, d=d, ex=x, href=h, slug=slugify(t)) for t, c, d, x, h in G]
    assert len({t['slug'] for t in terms}) == len(terms)
    for t in terms:
        related = [r for r in terms if r['cat'] == t['cat'] and r is not t][:6]
        body = hero(f'AI GLOSSARY · {CATS[t["cat"]].upper()}', t['term'], t['d'])
        body += f'<section class="hub-section callout"><h2>Example</h2><p>{e(t["ex"])}</p></section>'
        body += f'<section class="hub-section"><h2>Learn it by doing</h2><p>Reading a definition is a start; using the idea makes it stick.</p><p><a class="primary" href="{t["href"]}">Try it in practice →</a></p></section>'
        body += '<section class="hub-section"><h2>Related terms</h2>' + grid([card(f'/glossary/{r["slug"]}/', r['term'], r['d'][:120] + ('…' if len(r['d']) > 120 else ''), CATS[r['cat']].upper()) for r in related]) + '</section>'
        body += '<p><a href="/glossary/">← All AI terms</a></p>'
        ld = [{'@context': 'https://schema.org', '@type': 'DefinedTerm', 'name': t['term'], 'description': t['d'], 'url': f'{BASE}/glossary/{t["slug"]}/', 'inDefinedTermSet': {'@type': 'DefinedTermSet', 'name': 'Open Practice AI glossary', 'url': BASE + '/glossary/'}}]
        desc = f'{t["term"]}: {t["d"]}'
        if len(desc) > 170:
            desc = desc[:167].rsplit(' ', 1)[0] + '…'
        if len(desc) < 50:
            desc = (desc + ' Plain-language definition, example and a hands-on way to try it.')[:170]
        page(f'/glossary/{t["slug"]}/', f'What is {t["term"]}? Plain-language definition', desc, body, crumbs=[('Glossary', '/glossary/'), (t['term'], None)], ld=ld, active='Learn', priority=0.6)
    letters = sorted({t['term'][0].upper() for t in terms})
    body = hero('LEARN · AI GLOSSARY', f'AI glossary: {len(terms)} terms in plain language', 'Every term has a one-line definition, a real example and a link to try the idea yourself — because you understand AI words best by using them.')
    for cat, name in CATS.items():
        items = sorted([t for t in terms if t['cat'] == cat], key=lambda t: t['term'].lower())
        body += f'<section class="hub-section" id="{cat}"><h2>{e(name)} <small>{len(items)}</small></h2><dl class="glossary-list">' + ''.join(f'<div><dt><a href="/glossary/{t["slug"]}/">{e(t["term"])}</a></dt><dd>{e(t["d"])}</dd></div>' for t in items) + '</dl></section>'
    ld = [{'@context': 'https://schema.org', '@type': 'DefinedTermSet', 'name': 'Open Practice AI glossary', 'url': BASE + '/glossary/', 'hasDefinedTerm': [{'@type': 'DefinedTerm', 'name': t['term'], 'url': f'{BASE}/glossary/{t["slug"]}/'} for t in terms]}]
    page('/glossary/', f'AI Glossary: {len(terms)} AI terms explained simply', f'{len(terms)} AI terms explained in plain language — LLM, token, RAG, hallucination, embeddings and more — each with an example and a way to try it.', body, crumbs=[('Glossary', None)], ld=ld, active='Learn', priority=0.85)

def prompts():
    cats = list(dict.fromkeys(c for c, *_ in P))
    for cat in cats:
        items = [(t, p, tip) for c, t, p, tip in P if c == cat]
        body = hero(f'PROMPT LIBRARY · {cat.upper()}', f'{len(items)} {cat.lower()} prompts to practise with', 'Copy a prompt, replace the [BRACKETS] with your details, run it in any AI tool, then check the result. Each prompt includes the habit that makes it reliable.')
        for n, (t, p, tip) in enumerate(items, 1):
            pid = f'p-{slugify(t)}'
            body += f'<section class="hub-section ws-step" id="{pid}"><h2><span>{n}</span>{e(t)}</h2><pre class="prompt-box" id="{pid}-text">{e(p)}</pre><p><button type="button" class="secondary" data-copy="{pid}-text">Copy prompt</button></p><p class="hub-meta"><b>Make it reliable:</b> {e(tip)}</p></section>'
        body += '<section class="hub-section"><h2>Other categories</h2>' + grid([card(f'/prompts/{slugify(c)}/', c + ' prompts', f'{sum(1 for x in P if x[0] == c)} prompts', 'PROMPTS') for c in cats if c != cat]) + '</section>'
        page(f'/prompts/{slugify(cat)}/', f'{len(items)} free {cat} prompts (copy and adapt)', f'Free {cat.lower()} AI prompts you can copy and adapt, each with a tip that makes results more reliable. Works with any AI tool.', body, crumbs=[('Prompts', '/prompts/'), (cat, None)], scripts=('/copy.js',), active='Tools', priority=0.7)
    body = hero('TOOLS · PROMPT LIBRARY', f'{len(P)} prompts to practise with', 'Proven prompt patterns for writing, business, marketing, learning, careers, data, coding and everyday life. Copy one, fill the brackets, run it, check it.')
    body += grid([card(f'/prompts/{slugify(c)}/', c, f'{sum(1 for x in P if x[0] == c)} prompts · ' + ', '.join(t for cc, t, *_ in P if cc == c)[:90] + '…', 'CATEGORY') for c in cats])
    body += '<section class="hub-section callout"><h2>Want a prompt built for you?</h2><p>The <a href="/free-tools/prompt-generator/">Prompt Generator</a> turns your brief into a structured prompt with role, context, format and checks.</p></section>'
    page('/prompts/', f'AI Prompt Library: {len(P)} free prompts', f'{len(P)} free AI prompts for writing, business, marketing, learning, careers, data, coding and everyday tasks — each with a reliability tip.', body, crumbs=[('Prompts', None)], active='Tools', priority=0.9)

def ai_tools():
    body = hero('TOOLS · DIRECTORY', 'AI tools directory: what each is good for', f'{len(AI_TOOLS)} widely used AI tools with what they do, the free option, what they are best for and what to watch out for. Plans and limits change often — always check the official site. Last reviewed {CHECKED}.')
    for cat, name in TOOL_CATS.items():
        items = [t for t in AI_TOOLS if t[1] == cat]
        if not items:
            continue
        rows = ''.join(f'<tr><th scope="row"><a href="{e(u)}" rel="noopener nofollow" target="_blank">{e(n)} ↗</a></th><td>{e(w)}</td><td>{e(f)}</td><td>{e(b)}</td><td>{e(x)}</td></tr>' for n, c, w, f, b, x, u in items)
        body += f'<section class="hub-section" id="{cat}"><h2>{e(name)} <small>{len(items)}</small></h2><div class="table-wrap"><table class="hub-table"><thead><tr><th>Tool</th><th>What it does</th><th>Free option</th><th>Best for</th><th>Watch out</th></tr></thead><tbody>{rows}</tbody></table></div></section>'
    body += '<section class="hub-section callout"><h2>Not sure which to use?</h2><p>Take the <a href="/tool-finder/">tool finder quiz</a>, or test two tools side by side with our <a href="/compare/">comparison protocols</a>.</p></section>'
    faq = [('Are these tools free?', 'Each has a free option, usually with limits. Paid plans add higher limits or features. Check the official site before relying on any plan.'), ('Do you get paid for listing tools?', 'No. There are no affiliate links or sponsored placements on this page.')]
    body += faq_html(faq)
    page('/ai-tools/', f'AI Tools Directory: {len(AI_TOOLS)} tools with free options', f'{len(AI_TOOLS)} popular AI tools for chat, research, coding, design, video, audio and automation — what each does, the free option and what to watch.', body, crumbs=[('AI tools', None)], ld=[faq_ld(faq)], active='Tools', priority=0.85, wide=True)

def llms():
    rows = ''.join(f'<tr><th scope="row">{e(n)}</th><td>{e(m)}</td><td>{e(w)}</td><td>{e(t)}</td><td>{e(g)}</td><td>{e(x)}</td></tr>' for n, m, w, t, g, x in LLMS)
    body = hero('TOOLS · LLM GUIDE', 'Large language models, explained for builders', 'Which model families exist, who makes them, whether you can download them, and where to try them free. Then test them yourself — that is the only benchmark that matters for your work.')
    body += f'<div class="table-wrap"><table class="hub-table"><thead><tr><th>Family</th><th>Maker</th><th>Weights</th><th>Try free</th><th>Good at</th><th>Note</th></tr></thead><tbody>{rows}</tbody></table></div>'
    body += '<section class="hub-section"><h2>How to choose a model in 20 minutes</h2><ol class="key-steps"><li>Write three prompts from your real work.</li><li>Run each on two or three models (free keys from <a href="/api-keys/">our guides</a>).</li><li>Score each answer: correct, complete, clear, follows format (0–2 each).</li><li>Note speed and any errors or refusals.</li><li>Pick the cheapest model that scores well — not the most famous.</li></ol></section>'
    body += '<section class="hub-section"><h2>Key ideas</h2>' + grid([card('/glossary/large-language-model-llm/', 'What is an LLM?', 'The basics in plain language.', 'GLOSSARY'), card('/glossary/context-window/', 'Context window', 'How much text a model can consider at once.', 'GLOSSARY'), card('/glossary/open-weight-model/', 'Open-weight models', 'Models you can download and run yourself.', 'GLOSSARY'), card('/free-tools/token-counter/', 'Token counter', 'Estimate prompt size and cost.', 'TOOL')]) + '</section>'
    page('/llms/', 'LLM guide: model families and where to try them free', 'A plain-language guide to large language models — Llama, Gemini, GPT, Claude, Mistral, Qwen, DeepSeek and more — with where to try each free.', body, crumbs=[('LLMs', None)], active='Tools', priority=0.8, wide=True)

def compare():
    for c in COMPARE:
        diff = ''.join(f'<li>{e(x)}</li>' for x in c['diff'])
        tests = ''.join(f'<li>{e(x)}</li>' for x in c['tests'])
        body = hero('COMPARE · TEST IT YOURSELF', f'{c["a"]} vs {c["b"]}', c['desc'])
        body += f'<section class="hub-section"><h2>What is actually different</h2><ul class="hub-list">{diff}</ul><p class="hub-meta">Plans and features change often. Checked {CHECKED} — confirm on each official site.</p></section>'
        body += f'<section class="hub-section ws-step"><h2>The 20-minute test</h2><p>Run the same three tasks on both. Use your own real material where you can.</p><ol class="key-steps">{tests}</ol><h3>Score each answer (0–2 each)</h3><table class="hub-table"><thead><tr><th>Criterion</th><th>{e(c["a"])}</th><th>{e(c["b"])}</th></tr></thead><tbody>' + ''.join(f'<tr><th scope="row">{k}</th><td></td><td></td></tr>' for k in ['Correct (facts check out)', 'Complete (nothing important missing)', 'Clear (easy to use as is)', 'Followed the format', 'Speed / reliability']) + '</tbody></table><p class="hub-meta">Print this page or copy the table into a sheet. The higher total on your tasks wins — for you.</p></section>'
        body += f'<section class="hub-section callout"><h2>Quick decision</h2><p><b>Choose {e(c["a"])}</b> if {e(c["pick"][0])}.</p><p><b>Choose {e(c["b"])}</b> if {e(c["pick"][1])}.</p></section>'
        body += '<section class="hub-section"><h2>More comparisons</h2>' + grid([card(f'/compare/{o["slug"]}/', f'{o["a"]} vs {o["b"]}', o['desc'][:110] + '…', 'COMPARE') for o in COMPARE if o is not c][:4]) + '</section>'
        faq = [(f'Is {c["a"]} better than {c["b"]}?', f'It depends on your tasks. Run the 20-minute test with your own material: the one that scores higher on your work is better for you.'), ('Are these results sponsored?', 'No. There are no affiliate links, and the method is designed so you get your own evidence.')]
        body += faq_html(faq)
        page(f'/compare/{c["slug"]}/', f'{c["a"]} vs {c["b"]}: a 20-minute hands-on test', c['desc'], body, crumbs=[('Compare', '/compare/'), (f'{c["a"]} vs {c["b"]}', None)], ld=[faq_ld(faq)], active='Tools', priority=0.75)
    body = hero('TOOLS · COMPARE', 'Compare AI tools with your own evidence', 'No rankings bought by affiliates. Each comparison gives you the real differences plus a 20-minute test with a scoring table, so you decide on your own work.')
    body += grid([card(f'/compare/{c["slug"]}/', f'{c["a"]} vs {c["b"]}', c['desc'], 'TEST PROTOCOL') for c in COMPARE])
    page('/compare/', 'Compare AI tools: hands-on test protocols', 'Compare ChatGPT, Gemini, Claude, Groq, OpenRouter, free vs paid and open vs closed AI with hands-on tests and a reusable scoring table.', body, crumbs=[('Compare', None)], active='Tools', priority=0.8)

def use_cases():
    for slug, who, desc, tasks, project in USE_CASES:
        body = hero('USE CASES', f'AI for {who.lower()}', desc)
        body += '<section class="hub-section"><h2>Start with these tasks</h2>' + grid([card(h, t, 'Hands-on: do it with real material, then check it.', 'DO IT') for t, h in tasks]) + '</section>'
        body += f'<section class="hub-section callout"><h2>Your 30-minute starter project</h2><p>{e(project)}</p><p class="hub-meta">Tip: keep a note of the time it took and what you would change. That record is your proof that AI helped.</p></section>'
        body += '<section class="hub-section"><h2>Ground rules</h2><ul class="hub-list"><li>Check every fact, number and claim before it reaches a customer.</li><li>Remove private details before pasting anything into an AI tool.</li><li>Keep a human responsible for anything involving money, health or legal matters.</li></ul></section>'
        page(f'/use-cases/{slug}/', f'AI for {who}: practical, free use cases', desc, body, crumbs=[('Use cases', '/use-cases/'), (who, None)], active='Learn', priority=0.7)
    body = hero('LEARN · USE CASES', 'What can AI do for you?', 'Practical, honest use cases by role — each with tasks you can do today using free tools, and a 30-minute starter project.')
    body += grid([card(f'/use-cases/{s}/', who, d, 'USE CASE') for s, who, d, *_ in USE_CASES])
    page('/use-cases/', 'AI use cases by role: practical and free', 'Practical AI use cases for small businesses, farmers, teachers, students, job seekers, freelancers, NGOs, creators, developers and office staff.', body, crumbs=[('Use cases', None)], active='Learn', priority=0.8)

def tutorials(tools):
    for slug, title, desc, tool, steps in TUTORIALS:
        t = tools.get(tool) if tool else None
        href = (t.get('href') or f'/free-tools/{t["slug"]}/') if t else '/api-keys/'
        label = f'Open the {t["name"]}' if t else 'Open the API key guides'
        body = hero('TUTORIAL · STEP BY STEP', title, desc)
        body += '<section class="hub-section ws-step"><h2>Steps</h2><ol class="key-steps">' + ''.join(f'<li>{e(s)}</li>' for s in steps) + f'</ol><p><a class="primary" href="{href}">{e(label)} →</a></p></section>'
        body += '<section class="hub-section callout"><h2>Why this works</h2><p>Every step ends with something you can check. AI speeds up the draft; your brief and your checks make the result good.</p></section>'
        ld = [{'@context': 'https://schema.org', '@type': 'HowTo', 'name': title, 'description': desc, 'estimatedCost': {'@type': 'MonetaryAmount', 'currency': 'USD', 'value': '0'}, 'step': [{'@type': 'HowToStep', 'position': i + 1, 'text': s} for i, s in enumerate(steps)]}]
        page(f'/tutorials/{slug}/', title, desc, body, crumbs=[('Tutorials', '/tutorials/'), (title, None)], ld=ld, active='Learn', priority=0.7)
    body = hero('LEARN · TUTORIALS', 'Step-by-step AI tutorials', 'Short, practical tutorials that end with something shipped: a letter sent, a site published, a bot running.')
    body += grid([card(f'/tutorials/{s}/', t, d, 'TUTORIAL') for s, t, d, *_ in TUTORIALS])
    page('/tutorials/', 'Free AI tutorials: step by step', 'Free step-by-step AI tutorials: cover letters, websites, Telegram bots, cold emails, YouTube planning, product descriptions and more.', body, crumbs=[('Tutorials', None)], active='Learn', priority=0.8)

FINDER = {
 'questions': [
  {'id': 'goal', 'q': 'What do you want to do first?', 'options': [['write', 'Write something (email, post, letter)'], ['build', 'Build something (website, bot, app)'], ['learn', 'Learn AI from the basics'], ['data', 'Work with data or spreadsheets'], ['earn', 'Find clients or earn with my skills']]},
  {'id': 'level', 'q': 'How comfortable are you with tech?', 'options': [['new', 'Brand new'], ['some', 'I use apps and email daily'], ['dev', 'I can write some code']]},
  {'id': 'time', 'q': 'How much time do you have today?', 'options': [['15', '15 minutes'], ['60', 'About an hour'], ['more', 'A few hours']]},
  {'id': 'key', 'q': 'Do you have an AI API key?', 'options': [['no', 'No'], ['yes', 'Yes'], ['what', 'What is that?']]},
 ],
 'results': {
  'write': [['/free-tools/email-writer/', 'Email Writer'], ['/free-tools/cold-email-writer/', 'Cold Email Writer'], ['/free-tools/blog-post-writer/', 'Blog Post Writer']],
  'build': [['/free-tools/website-generator/', 'Website Generator'], ['/free-tools/telegram-bot-creator/', 'Telegram Bot Creator'], ['/free-tools/chrome-extension-creator/', 'Chrome Extension Creator']],
  'learn': [['/learn/beginners/', 'Start here: 10 lessons'], ['/learn/beginners/first-prompt/', 'Write your first good prompt'], ['/glossary/', 'AI glossary']],
  'data': [['/builds/sheets.html', 'Make messy data useful'], ['/prompts/data/', 'Data prompts'], ['/free-tools/json-formatter/', 'JSON Formatter']],
  'earn': [['/builds/earn-by-doing.html', 'Earn by Doing: honest offers'], ['/free-tools/landing-page-generator/', 'Landing Page Generator'], ['/free-tools/cold-email-writer/', 'Cold Email Writer']],
  'new': [['/learn/beginners/what-is-ai/', 'What AI is — and is not']], 'dev': [['/builds/api-integration.html', 'Connect an AI API safely']],
  'more': [['/academy/', 'Pick a full project path']], 'no': [['/api-keys/groq/', 'Get a free Groq key (optional)']], 'what': [['/learn/beginners/free-ai-key/', 'What an AI key is, in 10 minutes']],
 },
}

def tool_finder():
    body = hero('TOOLS · FINDER', 'Find the right free tool in 4 questions', 'Answer four quick questions and get a short, personal starting plan: one tool to use today, one lesson, and what to do next.')
    body += '<script type="application/json" id="finder-config">' + json.dumps(FINDER).replace('</', '<\\/') + '</script><section class="ws"><form id="finder" class="ws-step quiz">' + ''.join(
        f'<fieldset><legend>{n + 1}. {e(q["q"])}</legend>' + ''.join(f'<label><input type="radio" name="{q["id"]}" value="{v}" required> {e(t)}</label>' for v, t in q['options']) + '</fieldset>' for n, q in enumerate(FINDER['questions'])) + '<button class="primary">Show my plan</button></form><div id="finder-result" class="ws-step" hidden aria-live="polite"></div></section>'
    body += '<noscript><p>Without JavaScript: beginners start at <a href="/learn/beginners/">Start here</a>; builders at <a href="/free-tools/#build">Build apps</a>; writers at <a href="/free-tools/#writing">Writing tools</a>.</p></noscript>'
    page('/tool-finder/', 'AI tool finder quiz: what should I use?', 'Answer four quick questions to find the right free AI tool, lesson and next step for your goal, skill level and time — no signup.', body, crumbs=[('Tool finder', None)], scripts=('/finder.js',), active='Tools', priority=0.75)

def community():
    # Two halves, lengthwise: left = what you can do here (challenge, kit, contribute, ship + guidelines);
    # right = join buttons for the free communities (curriculum/social-links.json; empty link = "Opening soon").
    left = hero('COMMUNITY', 'Learn together, build in public', 'Open Practice is free and open. The community is how it gets better: share what you built, help someone stuck, run a session, or improve the lessons themselves.')
    left += grid([card('/starter.html', 'Starter challenge', 'A 120-minute challenge to run alone or with friends.', 'DO IT', '🏁'),
                  card('/facilitators.html', 'Facilitator kit', 'Run a free session for your class, club or team.', 'TEACH', '🧑‍🏫'),
                  card('https://github.com/king-kunta-cpu/open-practice', 'Improve the lessons', 'Report a mistake or suggest a lesson on GitHub.', 'CONTRIBUTE', '🛠️'),
                  card('/free-tools/', 'Ship something this week', 'Pick one tool, finish it, share the link.', 'SHIP', '🚀')], 'hub-grid-2')
    left += '<section class="hub-section"><h2>Community guidelines</h2><ul class="hub-list"><li>Share real work and honest results — including what did not work.</li><li>Never share API keys, passwords or other people’s private data.</li><li>Credit sources and tools you used.</li><li>Be kind to beginners; everyone started at lesson one.</li></ul></section>'
    body = '<div class="community-split"><div class="community-main">' + left + '</div>' + social.community_panel() + '</div>'
    page('/community/', 'Open Practice community: learn and build together', 'Join the free Open Practice communities on Whop, Discord, Telegram and Facebook: starter challenges, facilitator kits and ways to improve open AI lessons together.', body, crumbs=[('Community', None)], active='Community', priority=0.6, wide=True)

def not_found():
    body = hero('404 · PAGE NOT FOUND', 'That page has moved or never existed', 'Some courses were merged and old links now redirect. If you followed a link here, try one of these:')
    body += grid([card('/academy/', 'Academy', 'All project paths.', ''), card('/free-tools/', 'Free tools', '39 learn-by-doing tools.', ''), card('/learn/', 'Learn', 'Beginners, seniors and kids.', ''), card('/api-keys/', 'API keys', 'Free key guides.', '')])
    page('/404/', 'Page not found', 'The page you were looking for could not be found. Browse the Academy, free tools, Learn section or API key guides instead.', body, noindex=True, priority=0)

def build(tools, **_):
    glossary(tools); prompts(); ai_tools(); llms(); compare(); use_cases(); tutorials(tools); tool_finder(); community(); not_found()
