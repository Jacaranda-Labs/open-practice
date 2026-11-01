"""/academy/: every build path grouped by goal, generated from courses.json (post-merge)."""
from layout import page, hero, faq_html, faq_ld, e, BASE

GOALS = [
    ('Start with AI', 'Use AI well in everyday work: prompts, checking, fieldwork and responsible use.', ['prompt', 'ai-fieldwork', 'responsible-ai', 'replies']),
    ('Data & spreadsheets', 'Clean, join, report and chart data you can defend.', ['sheets', 'data-wrangling', 'data-report']),
    ('Build with code & APIs', 'Pages, automations, API clients and reproducible cloud labs.', ['web', 'automation', 'api-integration', 'evidence-assistant', 'python-records', 'reproducible-cloud-lab']),
    ('Machine learning', 'Honest baselines, pipelines, classification and clustering.', ['measured-ml', 'sklearn-lab', 'text-classification', 'clustering-lab']),
    ('Plan, create & earn', 'Plans that obey constraints, creative briefs and honest offers.', ['project-planning', 'visual-brief', 'earn-by-doing']),
]

def course_card(c):
    mods = ''.join(f'<li>{e(m["title"])}</li>' for m in c.get('modules', [])[1:-1])
    extra = f'<details class="mods"><summary>Includes {len(c["modules"]) - 2} merged module(s)</summary><ul>{mods}</ul></details>' if mods else ''
    level = c.get('level') or 'Open entry'
    return (f'<article class="hub-card course-card"><a href="/builds/{c["id"]}.html" class="course-link"><img src="/brand/covers/{c["id"]}.svg?v=illustrated-20261021" alt="" width="205" height="260" loading="lazy">'
            f'<small>PATH {c["num"]} · {e(c["track"]).upper()}</small><b>{e(c["title"])}</b><span>{e(c["project"])}.</span></a>'
            f'<p class="hub-meta">{len(c["lessons"])} activities · {e(c["time"])} · {e(level)}</p>{extra}'
            f'<p><a class="primary" href="/?course={c["id"]}">Start building</a> <a href="{c["downloads"]["handbook"]}">Handbook</a></p></article>')

def build(courses, **_):
    listed, body_sections = set(), ''
    for title, blurb, ids in GOALS:
        items = [courses[i] for i in ids if i in courses]
        listed.update(c['id'] for c in items)
        body_sections += f'<section class="hub-section" id="{title.lower().split()[0]}"><h2>{e(title)} <small>{len(items)}</small></h2><p>{e(blurb)}</p><div class="hub-grid course-grid">' + ''.join(course_card(c) for c in items) + '</div></section>'
    rest = [c for i, c in courses.items() if i not in listed]
    if rest:
        body_sections += '<section class="hub-section"><h2>More paths</h2><div class="hub-grid course-grid">' + ''.join(course_card(c) for c in rest) + '</div></section>'
    total_lessons = sum(len(c['lessons']) for c in courses.values())
    body = hero('ACADEMY · FREE · NO SIGNUP', f'{len(courses)} project paths. {total_lessons} hands-on activities.',
                'Every path ends in something real you can show: a checked report, a working page, a tested model or an honest offer. Each activity follows the same loop — read a short explanation, do the task with real files, check it, then ship.',
                '<p class="hub-meta"><a href="/activities.html">50 short activities</a> · <a href="/free-tools/">39 free tools</a> · <a href="/curriculum.html">Curriculum map</a> · <a href="/dashboard.html">My learning</a></p>')
    body += '<section class="hub-how"><ol><li><b>Read</b>One idea, one worked example</li><li><b>Do</b>A task with real practice files</li><li><b>Check</b>Expected results and common mistakes</li><li><b>Review</b>Self-check questions</li><li><b>Ship</b>A capstone with a rubric</li></ol></section>'
    body += body_sections
    faq = [('Is the Academy really free?', 'Yes. Every path, handbook and practice pack is free to read and download, with no signup. An optional free account only syncs your progress between devices.'),
           ('Do I get a certificate?', 'No. Open Practice is not accredited, and self-review is not assessment. You leave with something better for most employers and clients: a finished project and the evidence that it works.'),
           ('Why did some courses disappear?', 'Overlapping paths were merged so nothing is taught twice. Your saved progress moved with them automatically, and old links redirect to the new module.'),
           ('Do I need an AI subscription?', 'No. Activities work with free tools, your own free API key, or no AI at all. The practice files and expected results let you check your work either way.')]
    body += faq_html(faq)
    ld = [{'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Open Practice Academy', 'numberOfItems': len(courses), 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'item': {'@type': 'Course', 'name': c['title'], 'description': c['description'][:300], 'url': f'{BASE}/builds/{c["id"]}.html', 'provider': {'@type': 'Organization', 'name': 'Open Practice', 'url': BASE + '/'}, 'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD', 'category': 'Free'}, 'hasCourseInstance': {'@type': 'CourseInstance', 'courseMode': 'online', 'courseWorkload': f'PT{c["estimatedMinutes"] // 60}H{c["estimatedMinutes"] % 60}M'}}} for i, c in enumerate(courses.values())]}, faq_ld(faq)]
    page('/academy/', f'Free AI Academy: {len(courses)} project paths', f'{len(courses)} free, project-based AI courses with {total_lessons} hands-on activities: prompts, data, code, APIs, machine learning and honest freelancing. No signup.', body, crumbs=[('Academy', None)], ld=ld, active='Academy', priority=0.95, wide=True)
