import {outreachAPI,runOutreach} from '../../packages/outreach/api.mjs';
import {outreachHourly} from '../../packages/outreach/v2.mjs';
import {growthAPI} from '../../packages/growth/api.mjs';
import {database} from './database.mjs';
export {LearnerDatabase} from './database.mjs';
import {accountAPI} from '../../packages/accounts/api.mjs';
import {practiceAPI} from '../../packages/ai/practice.mjs';
import {createAPI} from '../../packages/core/api.mjs';
import {REDIRECTS} from '../../packages/core/redirects.mjs';
export default {async scheduled(event,env){const db=database(env);
 // hourly cron (outreach v2): the cleanup, lead verification and discovery stay once a day at 03:00 UTC
 if(db)await outreachHourly({...env,DB:db}).catch(()=>{});
 if(new Date(event?.scheduledTime||Date.now()).getUTCHours()!==3)return;
 if(db)await db.batch([db.prepare('DELETE FROM sessions WHERE expires_at < ?').bind(Date.now()),db.prepare('DELETE FROM learning_events WHERE created_at < ?').bind(Date.now()-90*86400000),db.prepare('DELETE FROM growth_events WHERE created_at < ?').bind(Date.now()-90*86400000),db.prepare('DELETE FROM growth_optouts WHERE expires_at < ?').bind(Date.now())]);if(db)await runOutreach({...env,DB:db})},async fetch(request,env){
 // Redirect cleartext before routing; this does not repair a failed TLS handshake.
 {const url=new URL(request.url);if(url.protocol==='http:'){url.protocol='https:';return new Response(null,{status:301,headers:{Location:url.toString()}})}}
 env={...env}; // Keep request-scoped database adapters out of the shared binding object.
 env.DB=database(env);
 const path=new URL(request.url).pathname;
 try {
 if(path.startsWith('/api/outreach/'))return await outreachAPI(request,env);
 if(path.startsWith('/api/growth/'))return await growthAPI(request,env);
 if(path.startsWith('/api/account/')||path==='/api/workspaces'||path==='/api/events')return await accountAPI(request,env);
 if(path==='/api/practice')return await practiceAPI(request,env);
 }catch{return new Response(JSON.stringify({error:'Request could not be processed.'}),{status:400,headers:{'Content-Type':'application/json','Cache-Control':'no-store'}})}
 if(!new URL(request.url).pathname.startsWith('/api/')){
 if(!env.ASSETS)return new Response('Static assets are not configured.',{status:503,headers:{'Cache-Control':'no-store'}});
 if(REDIRECTS[path]){const to=new URL(REDIRECTS[path],request.url);return new Response(null,{status:301,headers:{Location:to.toString(),'Cache-Control':'public,max-age=3600'}})}
 const assetURL=new URL(request.url);if(path.endsWith('/'))assetURL.pathname=path+'index.html';
 let response=await env.ASSETS.fetch(new Request(assetURL,request));
 // Clean URLs: /free-tools/json-formatter → /free-tools/json-formatter/ when that directory page exists.
 if(response.status===404&&!/\.[a-z0-9]{1,8}$/i.test(path)){const dir=new URL(request.url);dir.pathname=path+'/index.html';const probe=await env.ASSETS.fetch(new Request(dir,{method:'GET'}));if(probe.ok){const to=new URL(request.url);to.pathname=path+'/';return new Response(null,{status:301,headers:{Location:to.toString()}})}}
 if(response.status===404&&(request.headers.get('accept')||'').includes('text/html')){const nf=await env.ASSETS.fetch(new Request(new URL('/404.html',request.url)));if(nf.ok)response=new Response(nf.body,{status:404,headers:nf.headers})}const output=new Response(response.body,response);output.headers.set('Strict-Transport-Security','max-age=31536000; includeSubDomains');output.headers.set('Referrer-Policy','strict-origin-when-cross-origin');output.headers.set('X-Content-Type-Options','nosniff');output.headers.set('Permissions-Policy','camera=(), microphone=(), geolocation=()');output.headers.set('Cache-Control',/\.(png|webp|jpg|ico|zip|pdf|woff2?)$/i.test(path)?'public,max-age=86400':'no-cache');
 if(path==='/'||path.endsWith('/')||path.endsWith('.html')&&!path.startsWith('/resources/'))output.headers.set('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://api.groq.com https://generativelanguage.googleapis.com https://openrouter.ai https://api.mistral.ai https://api.cerebras.ai; font-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'");
 return output;
 }
 const api=createAPI({loadCourses:async req=>(await env.ASSETS.fetch(new Request(new URL('/courses.json',req.url)))).json(),limit:env.TUTOR_LIMITER?async req=>(await env.TUTOR_LIMITER.limit({key:req.headers.get('CF-Connecting-IP')||'unknown'})).success:null});
 return api(request,env);
}};
