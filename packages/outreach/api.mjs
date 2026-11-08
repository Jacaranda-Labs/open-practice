import {equal,digest,randomToken} from '../accounts/api.mjs';
import {smtpMail} from './smtp.mjs';
import {enqueue,boxes} from './v2.mjs';
export const outreachSchema=`CREATE TABLE IF NOT EXISTS outreach_leads (domain TEXT PRIMARY KEY, organisation TEXT NOT NULL, source TEXT NOT NULL, email_hash TEXT UNIQUE, email TEXT, unsubscribe_hash TEXT UNIQUE, status TEXT NOT NULL, detail TEXT NOT NULL, updated_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS outreach_runs (day TEXT PRIMARY KEY, created_at INTEGER NOT NULL, result TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS outreach_discovery (url TEXT PRIMARY KEY, title TEXT NOT NULL, found_at INTEGER NOT NULL);\n`;
export const pilotPool=[
 {domain:'impacthubharare.net',organisation:'Impact Hub Harare',path:'/contact-us/',relevance:'your community and entrepreneurship work in Harare'},
 {domain:'uncommon.org',organisation:'Uncommon.org',path:'/contact',relevance:'your adult technology bootcamp programme'},
 {domain:'bongohive.co.zm',organisation:'BongoHive',path:'/get-in-touch/',relevance:'your entrepreneurship and Data & AI work'}
];
const BASE='https://open-practice.open-practice.workers.dev',reply=(body,status=200)=>Response.json(body,{status,headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'}});
const agent='OpenPracticePilot/0.9 (+https://open-practice.open-practice.workers.dev/facilitators.html)';
export const relevantResearch=title=>/digital|skills|technolog|community|innovation|hub|entrepreneur|bootcamp|training|librar/i.test(title);
export function contactAddress(html,domain){
 // Public organisational role inboxes only: never infer or extract personal contacts.
 const allowed=new Set(['hello','info','contact','partnerships','community','programmes','programs','events','enquiries']);
 return [...html.toLowerCase().matchAll(/\b([a-z0-9._%+-]+)@([a-z0-9.-]+\.[a-z]{2,})\b/g)].map(m=>[m[1],m[2]]).find(([local,host])=>allowed.has(local)&&host===domain)?.join('@')||null;
}
export function robotsAllow(text,path){
 const groups=[];let agents=[],rules=[];
 const flush=()=>{if(agents.length)groups.push({agents,rules});agents=[];rules=[]};
 for(const raw of text.split(/\r?\n/)){const m=raw.split('#')[0].trim().match(/^([^:]+):\s*(.*)$/);if(!m)continue;const key=m[1].toLowerCase(),value=m[2].trim();if(key==='user-agent'){if(rules.length)flush();agents.push(value.toLowerCase())}else if(key==='disallow'||key==='allow')rules.push({key,value})}flush();
 for(const group of groups)if(group.agents.some(a=>a==='*'||a.includes('openpracticepilot')))for(const rule of group.rules){if(rule.key!=='disallow'||!rule.value)continue;const pattern=rule.value.replace(/\$$/,'').replace(/[.+?^${}()|[\]\\]/g,'\\$&').replace(/\*/g,'.*');if(new RegExp('^'+pattern).test(path))return false}return true;
}
async function pageFetch(url,domain,fetcher=fetch){
 for(let i=0;i<3;i++){
  const u=new URL(url);if(u.protocol!=='https:'||![domain,'www.'+domain].includes(u.hostname)||u.port||u.username||u.password)throw Error('source_not_allowed');
  const r=await fetcher(u,{redirect:'manual',headers:{'User-Agent':agent},signal:AbortSignal.timeout(10000)});
  if([301,302,307,308].includes(r.status)){url=new URL(r.headers.get('location'),u).href;continue}
  if(!r.ok&&r.status!==404)throw Error('source_unavailable');
  if(Number(r.headers.get('content-length'))>1000000)throw Error('source_too_large');
  // Stream a strict response bound; a misleading/missing Content-Length cannot bypass it.
  if(!r.body)return {status:r.status,text:'',url:u.href};const reader=r.body.getReader(),parts=[];let length=0;
  try{while(true){const c=await reader.read();if(c.done)break;length+=c.value.length;if(length>1000000)throw Error('source_too_large');parts.push(c.value)}}finally{await reader.cancel().catch(()=>{})}
  const bytes=new Uint8Array(length);let offset=0;for(const part of parts){bytes.set(part,offset);offset+=part.length}return {status:r.status,text:new TextDecoder().decode(bytes),url:u.href};
 }throw Error('too_many_redirects');
}
export function invitation(lead,optout){return {subject:'A free, hands-on AI hour for the adults you serve?',text:`Hello ${lead.organisation} team,\n\nI came across your work while looking for adult learning communities: I noticed ${lead.relevance}.\n\nMany adults are told AI matters for their work, but have never had a calm, safe hour to actually try it and see where it goes wrong. I run Open Practice, an independent, non-accredited collection of free practical AI learning materials, built for exactly that hour. Could a small, optional 60-minute taster complement an existing session?\n\nIn the taster, people do three real things with fictional inputs: test an editor, inspect JSON, and measure colour contrast. They leave having done it, not just watched it. No paid AI plan, account signup, public sharing or mailing-list enrolment is required, and there are manual fixtures for rooms without AI access. A 60-minute taster is not completion of the approximately 120-minute starter. This is an invitation, not a claim of partnership or pilot results.\n\nThe free kit and instructions: ${BASE}/facilitators.html?src=facilitator\nA useful example (valid JSON, wrong facts): ${BASE}/demonstrations/valid-json-wrong-facts.html?src=facilitator\n\nIf it feels useful, would your team look at the kit and suggest an adult cohort, facilitator and date? There are no automatic follow-ups. If this is not relevant, no reply is needed, and thank you for reading. You can suppress further invitations here: ${optout}\n\nOpen Practice\nReply directly to this email with any questions.\n\nYour public organisational inbox was found at ${lead.source}. No personal contact list or tracking pixel is used.`}}
async function discover(db,fetcher){
 // Search results create a research queue only. New domains cannot become send targets automatically.
 try{
  const q=['\"digital skills\" \"Zimbabwe\" community training contact','\"Zambia\" entrepreneurship hub community contact','\"Zimbabwe\" adult technology bootcamp contact'][Math.floor(Date.now()/86400000)%3];
  const r=await fetcher('https://www.bing.com/search?format=rss&q='+encodeURIComponent(q),{headers:{'User-Agent':agent},signal:AbortSignal.timeout(10000)});if(!r.ok||Number(r.headers.get('content-length'))>100000)return;
  const reader=r.body?.getReader();if(!reader)return;let xml='',size=0;try{while(true){const c=await reader.read();if(c.done)break;size+=c.value.length;if(size>100000)throw Error('search_too_large');xml+=new TextDecoder().decode(c.value)}}finally{await reader.cancel().catch(()=>{})}
  const decode=s=>s.replaceAll('&amp;','&').replaceAll('&lt;','<').replaceAll('&gt;','>').replaceAll('&quot;','"').replaceAll('&#39;',"'");
  for(const item of [...xml.matchAll(/<item>([\s\S]*?)<\/item>/g)].slice(0,5)){const url=decode(item[1].match(/<link>([^<]+)<\/link>/)?.[1]||''),title=decode(item[1].match(/<title>([^<]+)<\/title>/)?.[1]||'').slice(0,200);try{const u=new URL(url);if(u.protocol!=='https:'||url.length>1000||u.username||u.password||!relevantResearch(title))continue;await db.prepare('INSERT OR IGNORE INTO outreach_discovery (url,title,found_at) VALUES (?,?,?)').bind(url,title,Date.now()).run()}catch{}}
  await db.prepare('DELETE FROM outreach_discovery WHERE found_at < ?').bind(Date.now()-90*86400000).run();
 }catch{} // Search outages never broaden the send pool or block learning.
}
export async function runOutreach(env,{fetcher=fetch,mail=smtpMail,now=Date.now()}={}){
 const db=env.DB;if(!db)return {result:'storage_unavailable'};
 if(env.OUTREACH_ENABLED!=='true')return {result:'disabled'};
 const day=new Date(now).toISOString().slice(0,10);
 // Atomic SQLite claim prevents simultaneous cron/admin sends and caps attempts at one/day.
 const claim=await db.prepare('INSERT OR IGNORE INTO outreach_runs (day,created_at,result) VALUES (?,?,?)').bind(day,now,'running').run();if(!claim.meta?.changes)return {result:'daily_limit'};
 let result='no_eligible_contacts';
 try{
  await discover(db,fetcher);
  await db.prepare('UPDATE outreach_leads SET email=NULL WHERE updated_at < ?').bind(now-90*86400000).run();
  const paused=await db.prepare("SELECT domain FROM outreach_leads WHERE status IN ('sending','delivery_unknown','transport_blocked') LIMIT 1").first();if(paused){result='paused_transport_or_uncertain_delivery';return {result}}
  for(const lead of pilotPool){
   const prior=await db.prepare('SELECT status FROM outreach_leads WHERE domain=?').bind(lead.domain).first();if(prior&&prior.status!=='eligible')continue;
   let contact;try{
    const robots=await pageFetch('https://'+lead.domain+'/robots.txt',lead.domain,fetcher);if(robots.status!==404&&!robotsAllow(robots.text,lead.path))continue;
    contact=await pageFetch('https://'+lead.domain+lead.path,lead.domain,fetcher);if(contact.status!==200)continue;
   }catch{continue}
   const email=contactAddress(contact.text,lead.domain);if(!email)continue;
   const token=randomToken(),emailHash=await digest(email),unsubscribeHash=await digest(token),id=randomToken();
   if(env.OUTREACH_SEND_ENABLED!=='true'){
    await db.prepare('INSERT OR IGNORE INTO outreach_leads (domain,organisation,source,email_hash,email,status,detail,updated_at) VALUES (?,?,?,?,?,?,?,?)').bind(lead.domain,lead.organisation,contact.url,emailHash,email,'eligible','Official source and role inbox found; not contacted. Sender disabled.',now).run();result='research_only_sender_disabled';continue;
   }
   // outreach v2 (2026-11-04): a verified organisation joins the sequence (T1 without links, the kit on reply or day 7,
   // a last note on day 14). Sending happens on the hourly cron, one message per box at a time (v2.mjs).
   if(await enqueue(db,{domain:lead.domain,organisation:lead.organisation,relevance:lead.relevance,source:contact.url,email},now,boxes(env).length))result='queued';
  }
  if(env.OUTREACH_SEND_ENABLED==='true'){
   // Search results that pass the same bar as the approved pool (their own https domain, robots allowed, a public
   // organisational role inbox on that domain) become organisations in the sequence. Five a day at most.
   const {results:found}=await db.prepare('SELECT url,title FROM outreach_discovery WHERE found_at>=? ORDER BY found_at DESC LIMIT 5').bind(now-2*86400000).all();
   for(const f of found||[]){
    try{
     const u=new URL(f.url),domain=u.hostname.replace(/^www\./,'');
     if(await db.prepare('SELECT 1 FROM outreach_seq WHERE domain=? UNION SELECT 1 FROM outreach_leads WHERE domain=?').bind(domain,domain).first())continue;
     const robots=await pageFetch('https://'+domain+'/robots.txt',domain,fetcher);if(robots.status!==404&&!robotsAllow(robots.text,u.pathname))continue;
     const page=await pageFetch(f.url,domain,fetcher);if(page.status!==200)continue;
     const email=contactAddress(page.text,domain);if(!email)continue;
     const organisation=String(f.title).split(/\s[|\-\u2013\u2014:]\s/)[0].trim().slice(0,80)||domain;
     if(await enqueue(db,{domain,organisation,relevance:`your page "${String(f.title).slice(0,120)}"`,source:page.url,email},now,boxes(env).length))result='queued';
    }catch{}
   }
  }
  return {result};
 }finally{await db.prepare('UPDATE outreach_runs SET result=? WHERE day=?').bind(result,day).run()}
}
export async function outreachAPI(request,env){
 const url=new URL(request.url),db=env.DB;if(!db)return reply({error:'Storage unavailable.'},503);
 if(url.pathname==='/api/outreach/unsubscribe'){
  if(request.method!=='GET'&&request.method!=='POST')return reply({error:'GET or POST required.'},405);   // POST = RFC 8058 one-click
  const token=url.searchParams.get('t')||'';if(!/^[a-f0-9]{64}$/.test(token))return reply({error:'Invalid opt-out link.'},400);
  const h=await digest(token);
  await db.prepare('UPDATE outreach_leads SET status=?,email=NULL,detail=?,updated_at=? WHERE unsubscribe_hash=?').bind('suppressed','Opted out. Hash retained only to prevent recontact.',Date.now(),h).run();
  await db.prepare("UPDATE outreach_seq SET status='suppressed',email=NULL,link_owed=0,updated_at=? WHERE unsubscribe_hash=?").bind(Date.now(),h).run();
  if(request.method==='POST')return new Response('Done.',{headers:{'Cache-Control':'no-store'}});return new Response('You will not receive further Open Practice pilot invitations. No login is needed.',{headers:{'Content-Type':'text/plain; charset=utf-8','Cache-Control':'no-store','Referrer-Policy':'no-referrer'}});
 }
 if(!env.GROWTH_ADMIN_KEY||!equal(request.headers.get('Authorization')?.replace(/^Bearer /,'')||'',env.GROWTH_ADMIN_KEY))return reply({error:'Operator authorization required.'},401);
 if(request.method==='GET'&&url.pathname==='/api/outreach/summary'){
  const sequence=(await db.prepare('SELECT organisation,domain,status,touches,link_owed,updated_at FROM outreach_seq ORDER BY updated_at DESC LIMIT 100').all()).results;
  const [leads,runs,research]=await Promise.all([db.prepare('SELECT organisation,domain,source,status,detail,updated_at FROM outreach_leads ORDER BY updated_at DESC').all(),db.prepare('SELECT * FROM outreach_runs ORDER BY day DESC LIMIT 30').all(),db.prepare('SELECT * FROM outreach_discovery ORDER BY found_at DESC LIMIT 50').all()]);return reply({enabled:env.OUTREACH_ENABLED==='true',sendingEnabled:env.OUTREACH_SEND_ENABLED==='true',limits:'Outreach v2: first email has no links; the kit goes out on a reply or on day 7; a last note on day 14, then silence. Two boxes, one organisation per box, weekdays 07:00-17:00 UTC, ramp 10/25/50 a day, brake on >5% bounces or >3% stops. Public organisational role inboxes on the organisation\'s own domain only. v1 pilot invitations are never followed up.',leads:leads.results,runs:runs.results,research:research.results.filter(x=>relevantResearch(x.title)),sequence});
 }
 if(request.method==='POST'&&url.pathname==='/api/outreach/test-sender'){
  try{return reply(await (env.SEND_MAIL||smtpMail)(env,null))}catch(error){return reply({authenticated:false,sent:false,error:error.code||'transport_unavailable'},502)}
 }
 if(request.method==='POST'&&url.pathname==='/api/outreach/run')return reply(await runOutreach(env));
 return reply({error:'Unknown operator operation.'},404);
}
