// Outreach v2 (owner, 2026-11-04). T1 is plain text with NO links or attachments; the kit link goes out when an
// organisation replies (a short answer in the same thread, from the same box), or on day 7 if they don't (T2).
// Day 14 is one short last note (T3), then silence. Two personal Gmail boxes; each organisation stays on one.
// Daily = ramp 10/25/50 from 5 Nov 2026; the brake stops new first touches when a week shows >5% bounces or >3%
// stops (from 20 sends). Recipients are public organisational role inboxes on the organisation's own domain only.
// Organisations that received the v1 pilot invitation were promised no automatic follow-ups: they are never in here.
import {digest,randomToken} from '../accounts/api.mjs';
import {smtpMail} from './smtp.mjs';
import {ImapSession,imapDate} from './imap.mjs';
import {decodeBody,ownWords,boxIndex,classifyInbound} from './replies.mjs';

export const outreachV2Schema=`CREATE TABLE IF NOT EXISTS outreach_seq (domain TEXT PRIMARY KEY, organisation TEXT NOT NULL, relevance TEXT NOT NULL, source TEXT NOT NULL, email TEXT, box INTEGER NOT NULL, touches INTEGER NOT NULL DEFAULT 0, first_at INTEGER, next_at INTEGER, msgid TEXT, unsubscribe_token TEXT, unsubscribe_hash TEXT UNIQUE, link_owed INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL, updated_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS outreach_tally (day TEXT PRIMARY KEY, sent INTEGER NOT NULL DEFAULT 0, bounced INTEGER NOT NULL DEFAULT 0, stops INTEGER NOT NULL DEFAULT 0);
`;
const BASE='https://open-practice.zlnew.workers.dev',DAY=86400000;
const V1_DONE=['suppressed','smtp_accepted','recipient_rejected','delivery_unknown','transport_blocked','sending'];

export function boxes(env){
 return [[env.OUTREACH_SMTP_USER,env.OUTREACH_SMTP_PASSWORD],[env.OUTREACH_SMTP2_USER,env.OUTREACH_SMTP2_PASSWORD]]
  .filter(([u,p])=>u&&p).map(([user,pass])=>({user:String(user).trim(),pass:String(pass).replace(/\s+/g,'')}));
}
export function ramp(now,start='2026-11-05'){const d=Math.floor((now-Date.parse(start+'T00:00:00Z'))/DAY);return d<0?0:d<7?10:d<14?25:50}
export function brake({sent=0,bounced=0,stops=0}={}){if(sent<20)return '';if(bounced/sent>0.05)return 'bounces';if(stops/sent>0.03)return 'stops';return ''}
export const inWindow=(now)=>{const d=new Date(now),h=d.getUTCHours(),w=d.getUTCDay();return w>0&&w<6&&h>=7&&h<17};

/** kind: 'first' (T1, no links) | 'follow' (T2, day 7) | 'nudge' (T3, day 14) | 'link' (answer to a reply). */
export function compose(lead,kind,postal=''){
 const post=postal?`\n${postal}`:'',stop='\n\nIf you would rather not hear from me again, just reply "stop".';
 const subj='A free, hands-on AI hour for the adults you serve?',re='Re: '+subj;
 const kit=`${BASE}/facilitators.html?src=facilitator`,demo=`${BASE}/demonstrations/valid-json-wrong-facts.html?src=facilitator`;
 if(kind==='first')return {subject:subj,text:`Hello ${lead.organisation} team,\n\nI came across your work while looking for adult learning communities: I noticed ${lead.relevance}.\n\nMany adults are told AI matters for their work, but have never had a calm, safe hour to actually try it and see where it goes wrong. I run Open Practice, an independent, non-accredited collection of free practical AI learning materials, built for exactly that hour. Could a small, optional 60-minute taster complement an existing session?\n\nIn the taster, people do three real things with fictional inputs: test an editor, inspect JSON, and measure colour contrast. They leave having done it, not just watched it. No paid AI plan, account signup or mailing list is needed, and there are manual fixtures for rooms without AI access. This is an invitation, not a claim of partnership or pilot results.\n\nWould it help if I sent the free facilitator kit? Just reply and I will. If this is not relevant, no reply is needed, and thank you for reading.\n\nOpen Practice, a Jacaranda Labs venture${post}\n\nYour public organisational inbox was found on your own website. No personal contact list or tracking pixel is used.${stop}`};
 if(kind==='follow')return {subject:re,text:`Hello again,\n\nIn case it is useful, here is the free facilitator kit and instructions: ${kit}\n\nAnd a short example of the kind of thing adults practise (valid JSON, wrong facts): ${demo}\n\nIf a 60-minute taster could fit an existing session, I would be glad to hear which cohort and date might work.\n\nOpen Practice${post}${stop}`};
 if(kind==='nudge')return {subject:re,text:`Last note from me, and thank you for reading. If a hands-on AI hour for adults ever becomes useful to ${lead.organisation}, the free kit stays here: ${kit}\n\nI will not write again.\n\nOpen Practice${post}`};
 return {subject:re,text:`Thank you for writing back. Here is the free facilitator kit and instructions: ${kit}\n\nA short example adults can try first (valid JSON, wrong facts): ${demo}\n\nNo signup or paid AI plan is needed. Happy to answer anything here.\n\nOpen Practice`};
}

/** File a verified organisation (official domain, robots allowed, role inbox on that domain) for the sequence. */
export async function enqueue(db,lead,now,nBoxes){
 const v1=await db.prepare('SELECT status FROM outreach_leads WHERE domain=?').bind(lead.domain).first();
 if(v1&&V1_DONE.includes(v1.status))return false;
 const r=await db.prepare('INSERT OR IGNORE INTO outreach_seq (domain,organisation,relevance,source,email,box,touches,status,updated_at) VALUES (?,?,?,?,?,?,0,?,?)')
  .bind(lead.domain,lead.organisation,lead.relevance,lead.source,lead.email,boxIndex(lead.email,Math.max(1,nBoxes)),'ready',now).run();
 return !!r.meta?.changes;
}

async function tally(db,now,field){const day=new Date(now).toISOString().slice(0,10);await db.prepare(`INSERT INTO outreach_tally (day,${field}) VALUES (?,1) ON CONFLICT(day) DO UPDATE SET ${field}=${field}+1`).bind(day).run()}
async function week(db,now){return (await db.prepare('SELECT COALESCE(SUM(sent),0) sent,COALESCE(SUM(bounced),0) bounced,COALESCE(SUM(stops),0) stops FROM outreach_tally WHERE day>=?').bind(new Date(now-7*DAY).toISOString().slice(0,10)).first())||{}}

/** One message for one box: a link answer, then a due T2/T3, then a fresh T1. */
export async function sendOne(env,{now=Date.now(),mail=smtpMail,box=0,force=false}={}){
 const db=env.DB,bx=boxes(env);if(!db||!bx[box])return {sent:false,why:'no_box'};
 if(env.OUTREACH_SEND_ENABLED!=='true')return {sent:false,why:'sender_disabled'};
 if(!force&&!inWindow(now))return {sent:false,why:'outside_window'};
 const day=new Date(now).toISOString().slice(0,10);
 const today=(await db.prepare('SELECT sent FROM outreach_tally WHERE day=?').bind(day).first())?.sent||0;
 const daily=Math.min(Number(env.OUTREACH_DAILY)||50,ramp(now,env.OUTREACH_START||undefined));
 let row=await db.prepare("SELECT *,'link' kind FROM outreach_seq WHERE link_owed=1 AND box=? LIMIT 1").bind(box).first();
 if(!row&&today<daily)row=await db.prepare("SELECT *,CASE touches WHEN 1 THEN 'follow' ELSE 'nudge' END kind FROM outreach_seq WHERE status='contacted' AND touches<3 AND next_at<=? AND box=? ORDER BY next_at LIMIT 1").bind(now,box).first();
 if(!row&&today<daily&&!brake(await week(db,now)))row=await db.prepare("SELECT *,'first' kind FROM outreach_seq WHERE status='ready' AND box=? ORDER BY updated_at LIMIT 1").bind(box).first();
 if(!row)return {sent:false,why:today>=daily?'daily_cap':'nothing_owed'};
 let token=row.unsubscribe_token;
 if(!token){token=randomToken();await db.prepare('UPDATE outreach_seq SET unsubscribe_token=?,unsubscribe_hash=? WHERE domain=?').bind(token,await digest(token),row.domain).run()}
 const m=compose(row,row.kind,env.POSTAL_ADDRESS||'');
 const id=randomToken();
 try{
  const r=await mail(env,{to:row.email,id,box:bx[box],subject:m.subject,text:m.text,inReplyTo:row.kind==='first'?'':(row.msgid||''),
   unsubscribe:row.kind==='link'?'':BASE+'/api/outreach/unsubscribe?t='+token});
  const msgid=(r&&r.messageId)||`<${id}@gmail.com>`;
  if(row.kind==='link')await db.prepare("UPDATE outreach_seq SET link_owed=0,status='replied',updated_at=? WHERE domain=?").bind(now,row.domain).run();
  else{
   const touches=row.touches+1,done=touches>=3;
   await db.prepare('UPDATE outreach_seq SET touches=?,status=?,first_at=COALESCE(first_at,?),msgid=COALESCE(msgid,?),next_at=?,email=?,updated_at=? WHERE domain=?')
    .bind(touches,done?'finished':'contacted',now,msgid,now+7*DAY,done?null:row.email,now,row.domain).run();
   await tally(db,now,'sent');
  }
  return {sent:true,kind:row.kind,organisation:row.organisation};
 }catch(error){
  if(error.code==='recipient_rejected'){
   // a full / temporarily refusing mailbox is not a bounce (owner 2026-11-04)
   const soft=/\b(5\.2\.2|4\.\d\.\d+)\b|mailbox (is )?full|over (the )?quota|quota exceeded|insufficient (storage|space)|temporar/i.test(String(error.message||''));
   await db.prepare("UPDATE outreach_seq SET status=?,email=NULL,updated_at=? WHERE domain=?").bind(soft?'undeliverable':'bounced',now,row.domain).run();if(!soft)await tally(db,now,'bounced');return {sent:false,why:soft?'undeliverable':'recipient_rejected'}}
  // the server may have taken it: never risk a second copy; the owner sees it in the summary
  if(error.uncertain){await db.prepare("UPDATE outreach_seq SET status='delivery_unknown',updated_at=? WHERE domain=?").bind(now,row.domain).run();return {sent:false,why:'delivery_unknown'}}
  return {sent:false,why:error.code||'mail_failed'};
 }
}

/** Hourly: read each box's inbox for replies from organisations in the sequence. Read-only (EXAMINE). */
export async function readReplies(env,{now=Date.now(),open=(o)=>ImapSession.open(o)}={}){
 const db=env.DB,bx=boxes(env),out={replied:0,stopped:0,bounced:0,undeliverable:0};if(!db||!bx.length)return out;
 const {results}=await db.prepare("SELECT * FROM outreach_seq WHERE status='contacted' AND email IS NOT NULL AND first_at>=?").bind(now-30*DAY).all();
 for(let i=0;i<bx.length;i++){
  const mine=(results||[]).filter(r=>r.box===i);if(!mine.length)continue;
  const s=await open({host:'imap.gmail.com',user:bx[i].user,pass:bx[i].pass});
  try{
   await s.examine('INBOX');
   const since=imapDate(new Date(Math.min(...mine.map(r=>r.first_at))-DAY));
   for(const r of mine){
    const uids=await s.uidSearch(`SINCE ${since} FROM "${r.email.replace(/"/g,'')}"`);if(!uids.length)continue;
    const text=decodeBody(((await s.fetchText(uids.slice(-1),6000))[0]||{}).text||'');
    // Owner 2026-11-04: full / unavailable / unmonitored / left is a delivery problem, never a stop.
    const kind=classifyInbound({from:r.email,text}).kind;
    if(kind==='auto')continue;
    if(kind==='soft'||kind==='gone'){await db.prepare("UPDATE outreach_seq SET status='undeliverable',email=NULL,link_owed=0,updated_at=? WHERE domain=?").bind(now,r.domain).run();out.undeliverable++;continue}
    if(kind==='stop'){await db.prepare("UPDATE outreach_seq SET status='suppressed',email=NULL,link_owed=0,updated_at=? WHERE domain=?").bind(now,r.domain).run();await tally(db,now,'stops');out.stopped++;continue}
    // a real reply: the kit link is owed only if they answered T1 (T2/T3 already carried it)
    await db.prepare("UPDATE outreach_seq SET status='replied',link_owed=?,updated_at=? WHERE domain=?").bind(r.touches===1?1:0,now,r.domain).run();out.replied++;
   }
   const b=(await s.uidSearch(`SINCE ${since} OR FROM "mailer-daemon" FROM "postmaster"`)).slice(-10);
   if(b.length){const reps=(await s.fetchText(b)).map(m=>{const t=decodeBody(m.text);return {t:t.toLowerCase(),kind:classifyInbound({from:'mailer-daemon@report',text:t}).kind}});
    for(const r of mine){const hit=reps.find(x=>x.t.includes(r.email.toLowerCase()));if(!hit)continue;
     if(hit.kind==='bounce'){const u=await db.prepare("UPDATE outreach_seq SET status='bounced',email=NULL,updated_at=? WHERE domain=? AND status='contacted'").bind(now,r.domain).run();if(u&&u.meta&&u.meta.changes===0)continue;await tally(db,now,'bounced');out.bounced++}
     else{await db.prepare("UPDATE outreach_seq SET status='undeliverable',email=NULL,updated_at=? WHERE domain=? AND status='contacted'").bind(now,r.domain).run();out.undeliverable++}}}
  }finally{await s.logout()}
 }
 return out;
}

/** The hourly cron's outreach part: replies on the hour's tick, then one send per box. */
export async function outreachHourly(env,{now=Date.now(),mail=smtpMail,open}={}){
 if(env.OUTREACH_ENABLED!=='true'||env.OUTREACH_SEND_ENABLED!=='true'||!env.DB)return {result:'disabled'};
 const out={};
 try{out.replies=await readReplies(env,{now,...(open?{open}:{})})}catch(e){out.replies={error:String(e&&e.message||e).slice(0,80)}}
 out.sends=[];for(let b=0;b<boxes(env).length;b++)out.sends.push(await sendOne(env,{now,mail,box:b}));
 return out;
}
