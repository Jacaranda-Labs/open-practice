import {allowedGrowthActivities} from './ids.mjs';
import {readJSON,equal,randomToken,digest} from '../accounts/api.mjs';
export const growthEvents=new Set(['page_view','activity_started','artifact_saved','self_reviewed','share_created','referral_opened','challenge_started','challenge_completed','return_7d']);
export const growthSources=new Set(['direct','devto','mastodon','blogger','bluesky','nostr','facilitator','share','challenge','discord','facebook','pinterest','tumblr','other']);
const reply=(data,status=200)=>Response.json(data,{status,headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
export async function growthAPI(request,env){
 const path=new URL(request.url).pathname,db=env.DB;if(!db)return reply({error:'Analytics storage unavailable.'},503);
 if(path==='/api/growth/summary'){
  if(request.method!=='GET')return reply({error:'GET required.'},405);
  const supplied=request.headers.get('Authorization')?.replace(/^Bearer /,'')||'';
  if(!env.GROWTH_ADMIN_KEY||!equal(supplied,env.GROWTH_ADMIN_KEY))return reply({error:'Operator authorization required.'},401);
  const since=Date.now()-30*86400000;
  const [events,sources,daily]=await Promise.all([db.prepare('SELECT event, COUNT(DISTINCT visitor) AS visitors FROM growth_events WHERE created_at >= ? GROUP BY event').bind(since).all(),db.prepare('SELECT source,event,COUNT(DISTINCT visitor) AS visitors FROM growth_events WHERE created_at >= ? GROUP BY source,event').bind(since).all(),db.prepare('SELECT day,event,COUNT(DISTINCT visitor) AS visitors FROM growth_events WHERE created_at >= ? GROUP BY day,event ORDER BY day').bind(since).all()]);
  return reply({windowDays:30,retentionDays:90,events:events.results,sources:sources.results,daily:daily.results,note:'Optional-consent browser IDs, not all traffic or unique people. Saved artifacts and self-reviews are learner reports, not verified outcomes. No conversion percentage is inferred across unmatched cohorts.'});
 }
 if(!['/api/growth/event','/api/growth/erase'].includes(path))return reply({error:'Not found.'},404);
 if(request.method!=='POST')return reply({error:'POST required.'},405);
 if(request.headers.get('Origin')!==new URL(request.url).origin)return reply({error:'Same-origin requests only.'},403);
 if(!request.headers.get('Content-Type')?.includes('application/json'))return reply({error:'JSON required.'},415);
 const allowed=env.LEARNING_LIMITER&&await env.LEARNING_LIMITER.limit({key:'growth:'+(request.headers.get('CF-Connecting-IP')||'unknown')});if(!allowed?.success)return reply({error:'Analytics rate limit reached.'},429);
 let b;try{b=await readJSON(request,1200)}catch{return reply({error:'Invalid or oversized analytics request.'},400)}
 if(!b||typeof b!=='object'||!/^([a-f0-9]{32})$/.test(b.visitor||''))return reply({error:'Valid browser identifier required.'},400);
 if(path==='/api/growth/erase'){await db.batch([db.prepare('INSERT OR REPLACE INTO growth_optouts(visitor_hash,expires_at) VALUES(?,?)').bind(await digest(b.visitor),Date.now()+90*86400000),db.prepare('DELETE FROM growth_events WHERE visitor = ?').bind(b.visitor)]);return reply({ok:true})}
 if(b.consent!==true||!growthEvents.has(b.event)||!growthSources.has(b.source)||typeof b.activity!=='string'||!allowedGrowthActivities.has(b.activity))return reply({error:'Explicit consent and allowed event, source and activity required.'},400);
 const now=Date.now();await db.prepare('INSERT OR IGNORE INTO growth_events(id,visitor,event,activity,source,day,created_at) SELECT ?,?,?,?,?,?,? WHERE NOT EXISTS(SELECT 1 FROM growth_optouts WHERE visitor_hash = ? AND expires_at > ?)').bind(randomToken(),b.visitor,b.event,b.activity,b.source,Math.floor(now/86400000),now,await digest(b.visitor),now).run();return reply({ok:true});
}
