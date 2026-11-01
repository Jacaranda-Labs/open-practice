"""Merge overlapping build paths (36 → 20) without losing learner work.
Used by build-curriculum.py. Also writes the browser alias module and the Worker redirect table."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / 'apps/web/public'
MERGES = {k: v for k, v in json.loads((ROOT / 'curriculum/merges.json').read_text()).items() if not k.startswith('_')}
RENAMES = {k: v for k, v in json.loads((ROOT / 'curriculum/renames.json').read_text()).items() if not k.startswith('_')}
# 3: renamed paths (curriculum/renames.json). Records saved at layout >= 2 are already in merged lesson order.
LAYOUT = 3

def _minutes(lessons):
    return sum(l.get('estimatedMinutes', 0) for l in lessons)

def _time(mins):
    h, m = divmod(mins, 60)
    return f'{h}h {m:02d}m estimated' if m else f'{h}h estimated'

def merge(courses):
    by = {c['id']: c for c in courses}
    absorbed = {a for v in MERGES.values() for a in v}
    for p, items in MERGES.items():
        assert p in by and p not in absorbed, p
        for a in items:
            assert a in by and a not in MERGES, a
    for i, c in enumerate([c for c in courses if c.get('sourceListingNumber')]):
        c['expansionIndex'] = i
    aliases, out = {}, []
    for c in courses:
        if c['id'] in absorbed:
            continue
        items = [by[a] for a in MERGES.get(c['id'], [])]
        if not items:
            out.append(c)
            continue
        c = json.loads(json.dumps(c))
        head, ship = c['lessons'][:-1], c['lessons'][-1]
        lessons = list(head)
        modules = [{'id': c['id'], 'title': c['title'], 'start': 0, 'count': len(head)}]
        for n, a in enumerate(items, start=2):
            start = len(lessons)
            part = [dict(l, module=a['title'], moduleId=a['id']) for l in a['lessons'][:-1]]
            part[0] = dict(part[0], text=f'Module {n}: {a["title"]}. {a["description"]}\n\n' + part[0]['text'])
            lessons += part
            modules.append({'id': a['id'], 'title': a['title'], 'start': start, 'count': len(part)})
            aliases[a['id']] = {'to': c['id'], 'map': list(range(start, start + len(part))) + [-1]}
        ext = '; '.join(f'“{a["title"]}”' for a in items)
        ship = dict(ship, steps=list(ship['steps']) + [f'Combined capstone: include one checked artefact from each extra module ({ext}) and say what it proved.'])
        lessons.append(ship)
        modules.append({'id': c['id'] + '-capstone', 'title': 'Combined capstone', 'start': len(lessons) - 1, 'count': 1})
        aliases[c['id']] = {'to': c['id'], 'map': list(range(len(head))) + [len(lessons) - 1]}
        c['lessons'] = lessons
        c['modules'] = modules
        c['mergedFrom'] = [a['id'] for a in items]
        c['description'] = c['description'].rstrip() + f' Includes {len(items)} extra module{"s" if len(items) > 1 else ""}: {ext}.'
        seen = set(); c['outcomes'] = [x for x in c['outcomes'] + [o for a in items for o in a['outcomes'][:2]] if not (x in seen or seen.add(x))]
        seen = set(); c['prerequisites'] = [x for x in c['prerequisites'] + [p for a in items for p in a['prerequisites']] if not (x in seen or seen.add(x))]
        urls = set(); c['references'] = [r for r in c['references'] + [r for a in items for r in a['references']] if not (r['url'] in urls or urls.add(r['url']))]
        c['estimatedMinutes'] = _minutes(lessons)
        c['time'] = _time(c['estimatedMinutes'])
        c['capstone'] = dict(c['capstone'], brief=c['capstone']['brief'].rstrip() + f'\n\nCombined capstone: your evidence must also include one checked artefact from each extra module ({ext}).')
        out.append(c)
    for i, c in enumerate(out, start=1):
        c['num'] = f'{i:02d}'
        ids = [l['id'] for l in c['lessons']]
        assert len(ids) == len(set(ids)), c['id']
    final = {c['id']: c for c in out}
    renamed = {}
    for old, new in RENAMES.items():
        assert new in final and old not in final and old not in aliases, (old, new)
        n = len(final[new]['lessons'])
        # 'map' reads a record saved before the merge; 'merged' reads one saved after it (layout >= 2).
        aliases[old] = {'to': new, 'map': aliases[new]['map'] if new in aliases else list(range(n)), 'merged': list(range(n))}
        renamed[old] = new
    redirects = {}
    for old, a in aliases.items():
        if old == a['to']:
            continue
        redirects[f'/builds/{old}.html'] = f'/builds/{a["to"]}.html' + ('' if old in renamed else f'#{old}')
        redirects[f'/resources/handbooks/{old}-handbook.md'] = f'/resources/handbooks/{a["to"]}-handbook.md'
        redirects[f'/resources/packs/{old}-practice-pack.zip'] = f'/resources/packs/{a["to"]}-practice-pack.zip'
    for old, new in renamed.items():
        redirects[f'/brand/covers/{old}.svg'] = f'/brand/covers/{new}.svg'
        lab = PUBLIC / 'resources/curriculum' / new
        for f in sorted(lab.iterdir()) if lab.is_dir() else []:
            redirects[f'/resources/curriculum/{old}/{f.name}'] = f'/resources/curriculum/{new}/{f.name}'
    write_modules(aliases, redirects)
    cleanup(absorbed)
    return out, aliases

def write_modules(aliases, redirects):
    data = json.dumps(aliases, separators=(',', ':'), sort_keys=True)
    js = ("// Generated by scripts/course_merge.py. Maps retired/renumbered build paths to their merged home.\n"
          f"export const LAYOUT={LAYOUT};\nexport const ALIASES={data};\n"
          "export const resolveCourse=id=>ALIASES[id]?.to||id;\n"
          "// A renamed path's record saved after the merge (layout >= 2) is already in the new lesson order.\n"
          "const pick=(a,r)=>a.merged&&r&&r.layout>=2?a.merged:a.map;\n"
          "function remap(r,map,keepReview){const out={done:[],notes:{}};for(const i of Array.isArray(r?.done)?r.done:[]){const j=map[i];if(Number.isInteger(j)&&j>=0)out.done.push(j)}"
          "for(const [k,v] of Object.entries(r?.notes&&typeof r.notes==='object'?r.notes:{})){const j=map[Number(k)];if(/^\\d+$/.test(k)&&Number.isInteger(j)&&j>=0&&typeof v==='string')out.notes[j]=v}"
          "if(keepReview)for(const key of ['quiz','quizAnswers','assessmentVersion','rubricScores','legacyReview'])if(r&&key in r)out[key]=r[key];return out}\n"
          "function union(target,extra,label){const t=target&&typeof target==='object'?{...target}:{};t.done=[...new Set([...(Array.isArray(t.done)?t.done:[]),...extra.done])];const notes={...(t.notes&&typeof t.notes==='object'?t.notes:{})};"
          "for(const [k,v] of Object.entries(extra.notes)){if(!notes[k]||!String(notes[k]).trim())notes[k]=v;else if(notes[k]!==v&&!String(notes[k]).includes(v))notes[k]=notes[k]+'\\n\\n— Earlier notes from '+label+' —\\n'+v}t.notes=notes;"
          "for(const key of ['quiz','quizAnswers','assessmentVersion','rubricScores','legacyReview'])if(key in extra&&!(key in t))t[key]=extra[key];t.layout=LAYOUT;return t}\n"
          "// Local records: run once per browser. The original object is kept in op-progress-premerge; old keys are never deleted.\n"
          "export function migrateLocal(progress,storage=globalThis.localStorage){if(!progress||typeof progress!=='object')return false;let flag=null;try{flag=storage?.getItem('op-merge-layout')}catch{}if(flag===String(LAYOUT))return false;"
          "try{if(!storage.getItem('op-progress-premerge'))storage.setItem('op-progress-premerge',JSON.stringify(progress))}catch{}let changed=false;"
          "for(const [id,a] of Object.entries(ALIASES))if(id===a.to&&progress[id]&&!(progress[id].layout>=2)){progress[id]={...progress[id],...remap(progress[id],a.map,true),layout:LAYOUT};changed=true}"
          "for(const [id,a] of Object.entries(ALIASES))if(id!==a.to&&progress[id]&&!progress[id].mergedInto){progress[a.to]=union(progress[a.to],remap(progress[id],pick(a,progress[id]),!!a.merged),'the former “'+id+'” path');progress[id]={...progress[id],mergedInto:a.to};changed=true}"
          "for(const id of Object.keys(progress))if(progress[id]&&typeof progress[id]==='object'&&!progress[id].mergedInto)progress[id].layout=LAYOUT;try{storage.setItem('op-merge-layout',String(LAYOUT))}catch{}return changed}\n"
          "// Cloud rows: old rows stay on the server untouched; this view folds them into the merged course until the learner saves.\n"
          "export function migrateRows(rows){if(!Array.isArray(rows))return rows;const parse=r=>{try{return JSON.parse(r.content)}catch{return null}};const out=rows.map(r=>({...r}));const byId=new Map(out.map(r=>[r.course_id,r]));"
          "for(const r of out){const a=ALIASES[r.course_id];if(a&&a.to===r.course_id){const w=parse(r);if(w&&!(w.layout>=2))r.content=JSON.stringify({...w,...remap(w,a.map,true),layout:LAYOUT})}}"
          "for(const r of rows){const a=ALIASES[r.course_id];if(!a||a.to===r.course_id)continue;const w=parse(r);if(!w)continue;const m=pick(a,w),k=!!a.merged;const target=byId.get(a.to);if(target){target.content=JSON.stringify(union(parse(target),remap(w,m,k),'the former “'+r.course_id+'” path'))}"
          "else{const row={course_id:a.to,content:JSON.stringify(union(null,remap(w,m,k),'the former “'+r.course_id+'” path')),updated_at:r.updated_at,migratedFrom:r.course_id};out.push(row);byId.set(a.to,row)}}return out}\n")
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (ROOT / 'packages/core').mkdir(parents=True, exist_ok=True)
    (PUBLIC / 'course-aliases.js').write_text(js)
    (ROOT / 'packages/core/redirects.mjs').write_text("// Generated by scripts/course_merge.py: retired URLs → their new home (301).\n"
        f"export const REDIRECTS={json.dumps(redirects, indent=1, sort_keys=True)};\n"
        f"export const COURSE_ALIASES={json.dumps({k: v['to'] for k, v in aliases.items() if k != v['to']}, sort_keys=True)};\n")

def cleanup(absorbed):
    """Remove generated public artefacts of absorbed paths (their URLs now redirect). Fixture folders stay: lesson text links to them.
    Covers stay when another library resource uses them as artwork."""
    used = (ROOT / 'curriculum/library-base.json').read_text()
    for a in absorbed:
        for p in [PUBLIC / 'builds' / f'{a}.html', PUBLIC / 'resources/handbooks' / f'{a}-handbook.md', PUBLIC / 'resources/packs' / f'{a}-practice-pack.zip'] + ([] if f'covers/{a}.svg' in used else [PUBLIC / 'brand/covers' / f'{a}.svg']):
            if p.exists():
                p.unlink()
