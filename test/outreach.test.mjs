import test from 'node:test';import assert from 'node:assert/strict';import {mkdtemp,rm,readFile} from 'node:fs/promises';import {tmpdir} from 'node:os';import {join} from 'node:path';import {openDatabase} from '../adapters/node/database.mjs';import {runOutreach,outreachAPI,outreachSchema,contactAddress,robotsAllow} from '../packages/outreach/api.mjs';import {smtpMail,mailMessage} from '../packages/outreach/smtp.mjs';import {sendOne,readReplies,compose,ramp,brake,outreachV2Schema} from '../packages/outreach/v2.mjs';
const site='https://open-practice.open-practice.workers.dev';
test('outreach has additive portable schema and role-only, exact-domain contacts',async()=>{assert.equal(outreachSchema,await readFile(new URL('../migrations/0003_outreach.sql',import.meta.url),'utf8'));assert.equal(contactAddress('person@uncommon.org and hello@uncommon.org','uncommon.org'),'hello@uncommon.org');assert.equal(contactAddress('hello@uncommon.org.evil.com','uncommon.org'),null);assert.equal(contactAddress('hello@other.org','uncommon.org'),null);assert.equal(robotsAllow('User-agent: *\nDisallow: /','/contact'),false);assert.equal(robotsAllow('User-agent: *\nUser-agent: Other\nDisallow: /','/contact'),false);assert.equal(robotsAllow('User-agent: *\nDisallow: /con*','/contact'),false);assert.equal(robotsAllow('User-agent: Other\nDisallow: /','/contact'),true)});
test('TLS SMTP uses authenticated implicit TLS, no send during test and safe MIME',async()=>{
 const recorded=[];let options;
 function connector(address,opts){assert.equal(address.hostname,'smtp.gmail.com');assert.equal(address.port,465);options=opts;const lines=['220 ready','250-host','250 AUTH PLAIN','235 authenticated'];return {opened:Promise.resolve(),readable:new ReadableStream({pull(c){if(lines.length)c.enqueue(new TextEncoder().encode(lines.shift()+'\r\n'));else c.close()}}),writable:new WritableStream({write(x){recorded.push(new TextDecoder().decode(x))}}),close:async()=>{}}}
 const result=await smtpMail({OUTREACH_SMTP_USER:'owner@gmail.com',OUTREACH_SMTP_PASSWORD:'test-not-a-real-password'},null,connector);assert.equal(result.sent,false);assert.equal(result.authenticated,true);assert.equal(options.secureTransport,'on');assert.ok(!recorded.some(x=>x.includes('MAIL FROM')||x.includes('DATA')));
 const message=mailMessage({from:'owner@gmail.com',to:'hello@uncommon.org',subject:'Pilot?',text:'A useful café example',id:'test-message'});assert.match(message,/Content-Transfer-Encoding: base64/);assert.ok(message.includes(Buffer.from('A useful café example').toString('base64')));assert.throws(()=>mailMessage({from:'owner@gmail.com',to:'a@example.org\r\nBcc: b@example.org',subject:'x',text:'x',id:'x'}));
});
async function fixture(fn){const dir=await mkdtemp(join(tmpdir(),'op-outreach-')),db=openDatabase(join(dir,'test.sqlite'));try{await fn(db)}finally{db.close();await rm(dir,{recursive:true,force:true})}}
const fetcher=async input=>{const url=new URL(input);if(url.hostname==='www.bing.com')return new Response('<rss><item><title>Adult community research candidate</title><link>https://example.org/contact</link></item></rss>');if(url.pathname==='/robots.txt')return new Response(url.hostname==='impacthubharare.net'?'User-agent: *\nAllow: /':'User-agent: *\nDisallow: /');return new Response('<a href="mailto:info@impacthubharare.net">Organisational contact</a>')};
test('outreach v2: disabled by default, private, bounded; verified organisations join the sequence; T1 has no links and a header opt-out',async()=>fixture(async db=>{
 const env={DB:db,GROWTH_ADMIN_KEY:'private-test-key',OUTREACH_ENABLED:'true',OUTREACH_SEND_ENABLED:'true',OUTREACH_SMTP_USER:'one@gmail.com',OUTREACH_SMTP_PASSWORD:'p',OUTREACH_START:'2020-01-01',POSTAL_ADDRESS:'Jacaranda Labs, P.O. Box 900, Bulawayo, Zimbabwe'};let messages=[];const mail=async(_env,message)=>{messages.push(message);return {sent:true,messageId:'<'+message.id+'@gmail.com>'}};const now=Date.UTC(2026,9,21,9);
 assert.equal((await runOutreach({...env,OUTREACH_ENABLED:'false'},{fetcher,mail,now})).result,'disabled');assert.equal((await outreachAPI(new Request(site+'/api/outreach/summary'),env)).status,401);
 const results=await Promise.all([runOutreach(env,{fetcher,mail,now}),runOutreach(env,{fetcher,mail,now})]);assert.ok(results.some(x=>x.result==='daily_limit'));assert.equal(messages.length,0,'the daily run verifies and queues; it never sends');
 const seq=await db.prepare('SELECT * FROM outreach_seq').all();assert.equal(seq.results.length,1,'research behind a robots refusal never becomes a recipient');assert.equal(seq.results[0].email,'info@impacthubharare.net');
 const r=await sendOne(env,{now,mail,box:0});assert.equal(r.kind,'first');assert.equal(messages.length,1);
 const t1=messages[0];assert.equal(t1.to,'info@impacthubharare.net');assert.doesNotMatch(t1.text,/https?:\/\/|www\./,'T1 carries no links');assert.match(t1.text,/reply "stop"/);assert.match(t1.text,/P\.O\. Box 900, Bulawayo/);assert.ok(!t1.text.includes('Tafadzwa'));
 assert.match(t1.unsubscribe,/\/api\/outreach\/unsubscribe\?t=[a-f0-9]{64}$/);assert.equal(t1.inReplyTo,'');
 const summary=await outreachAPI(new Request(site+'/api/outreach/summary',{headers:{Authorization:'Bearer private-test-key'}}),env),data=await summary.json();assert.equal(data.sequence[0].status,'contacted');assert.equal(data.research.length,1);assert.ok(!JSON.stringify(data).includes('info@impacthubharare.net'));
 const token=t1.unsubscribe.match(/t=([a-f0-9]{64})/)[1];assert.equal((await outreachAPI(new Request(site+'/api/outreach/unsubscribe?t='+token,{method:'POST'}),env)).status,200);const row=await db.prepare('SELECT * FROM outreach_seq').first();assert.equal(row.status,'suppressed');assert.equal(row.email,null);
 assert.equal((await sendOne(env,{now:now+8*86400000,mail,box:0})).sent,false);assert.equal(messages.length,1);
}));

test('uncertain delivery parks the organisation (never a second copy), and source redirects cannot escape approved domains',async()=>fixture(async db=>{
 const env={DB:db,OUTREACH_ENABLED:'true',OUTREACH_SEND_ENABLED:'true',OUTREACH_SMTP_USER:'one@gmail.com',OUTREACH_SMTP_PASSWORD:'p',OUTREACH_START:'2020-01-01'};let attempts=0;const mail=async()=>{attempts++;throw Object.assign(Error('lost acknowledgement'),{uncertain:true})},now=Date.UTC(2026,9,21,9);
 await runOutreach(env,{fetcher,mail,now});assert.equal((await sendOne(env,{now,mail,box:0})).why,'delivery_unknown');assert.equal((await sendOne(env,{now:now+3600000,mail,box:0})).sent,false);assert.equal(attempts,1);
}));

test('an external redirect and a denied robots policy cannot be used to harvest a contact',async()=>fixture(async db=>{
 let mailCount=0,externalFetch=false;const restricted=async input=>{const url=new URL(input);if(url.hostname==='www.bing.com')return new Response('<rss/>');if(!['impacthubharare.net','uncommon.org','bongohive.co.zm'].includes(url.hostname))externalFetch=true;if(url.pathname==='/robots.txt')return new Response('User-agent: *\nAllow: /');return new Response('',{status:302,headers:{Location:'https://private.example.org/'}})};
 await runOutreach({DB:db,OUTREACH_ENABLED:'true',OUTREACH_SEND_ENABLED:'true'},{fetcher:restricted,mail:async()=>mailCount++,now:Date.UTC(2026,9,21)});assert.equal(mailCount,0);assert.equal(externalFetch,false);
}));

test('research-only mode verifies organisational inboxes without sending, then requires explicit sending enablement',async()=>fixture(async db=>{
 const env={DB:db,OUTREACH_ENABLED:'true',OUTREACH_SEND_ENABLED:'false',OUTREACH_SMTP_USER:'one@gmail.com',OUTREACH_SMTP_PASSWORD:'p',OUTREACH_START:'2020-01-01'};let count=0;const mail=async()=>{count++;return {sent:true}},now=Date.UTC(2026,9,21,9);
 await runOutreach(env,{fetcher,mail,now});assert.equal(count,0);assert.equal((await db.prepare('SELECT status FROM outreach_leads').first()).status,'eligible');
 assert.equal((await sendOne(env,{now,mail,box:0})).why,'sender_disabled');
 await runOutreach({...env,OUTREACH_SEND_ENABLED:'true'},{fetcher,mail,now:now+86400000});assert.equal((await db.prepare('SELECT status FROM outreach_seq').first()).status,'ready');
 await sendOne({...env,OUTREACH_SEND_ENABLED:'true'},{fetcher,mail,now:now+86400000,box:0});assert.equal(count,1);
}));

test('outreach v2 sequence: T2 on day 7 with the kit (threaded), T3 on day 14, then silence; v1 invitations are never followed up',async()=>fixture(async db=>{
 const env={DB:db,OUTREACH_ENABLED:'true',OUTREACH_SEND_ENABLED:'true',OUTREACH_SMTP_USER:'one@gmail.com',OUTREACH_SMTP_PASSWORD:'p',OUTREACH_START:'2020-01-01'};const sent=[];const mail=async(_e,m)=>{sent.push(m);return {sent:true,messageId:'<'+m.id+'@gmail.com>'}};const t0=Date.UTC(2026,10,9,9);
 await db.prepare("INSERT INTO outreach_leads (domain,organisation,source,status,detail,updated_at) VALUES ('uncommon.org','Uncommon.org','s','smtp_accepted','v1',0)").run();
 await db.prepare("INSERT INTO outreach_seq (domain,organisation,relevance,source,email,box,touches,status,updated_at) VALUES ('hub.zw','Hub','your hub','s','hello@hub.zw',0,0,'ready',0)").run();
 assert.equal((await sendOne(env,{now:t0,mail,box:0})).kind,'first');
 assert.equal((await sendOne(env,{now:t0+6*86400000,mail,box:0})).sent,false,'nothing before day 7');
 assert.equal((await sendOne(env,{now:t0+7*86400000,mail,box:0})).kind,'follow');
 assert.match(sent[1].text,/facilitators\.html/);
 assert.equal(sent[1].attachments.length,1,'T2 carries the run sheet');assert.match(sent[1].attachments[0].filename,/^open-practice-ai-taster-hub\.pdf$/);
 assert.equal(String.fromCharCode(...sent[1].attachments[0].content.subarray(0,5)),'%PDF-');assert.ok(!sent[0].attachments,'T1 has no attachment');
 assert.match(sent[1].text,/attached is a one-page run sheet/);assert.equal(sent[1].inReplyTo,'<'+sent[0].id+'@gmail.com>');assert.match(sent[1].subject,/^Re: /);
 assert.equal((await sendOne(env,{now:t0+14*86400000,mail,box:0})).kind,'nudge');assert.match(sent[2].text,/I will not write again/);
 assert.equal((await sendOne(env,{now:t0+30*86400000,mail,box:0})).sent,false,'three emails at most');
 assert.equal(sent.length,3);assert.ok(!sent.some(m=>/uncommon/.test(m.to)),'the v1 invitation promised no follow-ups');
 const row=await db.prepare("SELECT * FROM outreach_seq WHERE domain='hub.zw'").first();assert.equal(row.status,'finished');assert.equal(row.email,null,'the address is dropped when the sequence ends');
}));

test('outreach v2 replies: a real reply to T1 gets the kit once, in-thread; stop suppresses; out-of-office carries on',async()=>fixture(async db=>{
 const env={DB:db,OUTREACH_ENABLED:'true',OUTREACH_SEND_ENABLED:'true',OUTREACH_SMTP_USER:'one@gmail.com',OUTREACH_SMTP_PASSWORD:'p',OUTREACH_START:'2020-01-01'};const sent=[];const mail=async(_e,m)=>{sent.push(m);return {sent:true,messageId:'<'+m.id+'@gmail.com>'}};const t0=Date.UTC(2026,10,9,9);
 for(const [d,e] of [['a.zw','hello@a.zw'],['b.zw','info@b.zw'],['c.zw','contact@c.zw']])await db.prepare("INSERT INTO outreach_seq (domain,organisation,relevance,source,email,box,touches,status,updated_at) VALUES (?,?,?,?,?,0,0,'ready',0)").bind(d,d,'x','s',e).run();
 for(let i=0;i<3;i++)await sendOne(env,{now:t0+i,mail,box:0});
 const texts={'hello@a.zw':'Yes please, send it.\n\nOn Mon, 9 Nov 2026 Open Practice wrote:\n> If you would rather not hear from me again, just reply "stop".','info@b.zw':'Stop','contact@c.zw':'Automatic reply: out of the office until Monday'};
 const open=async()=>{let last='';return {async examine(){},async uidSearch(q){const m=q.match(/FROM "([^"]+)"/);last=m?m[1]:'';return texts[last]?[7]:[]},async fetchText(){return [{uid:7,text:texts[last]}]},async logout(){}}};
 const r=await readReplies(env,{now:t0+3600000,open});assert.deepEqual([r.replied,r.stopped],[1,1],'our quoted footer is never read as a stop');
 const lk=await sendOne(env,{now:t0+3600000,mail,box:0});assert.equal(lk.kind,'link');assert.match(sent[3].text,/facilitators\.html/);assert.equal(sent[3].unsubscribe,'');assert.ok(sent[3].inReplyTo);
 const st=Object.fromEntries((await db.prepare('SELECT domain,status FROM outreach_seq').all()).results.map(x=>[x.domain,x.status]));assert.deepEqual(st,{'a.zw':'replied','b.zw':'suppressed','c.zw':'contacted'});
 assert.deepEqual([ramp(Date.parse('2026-11-04T12:00Z')),ramp(Date.parse('2026-11-05T12:00Z')),ramp(Date.parse('2026-11-12T12:00Z')),ramp(Date.parse('2026-11-19T12:00Z'))],[0,10,25,50]);
 assert.equal(brake({sent:19,bounced:5}),'');assert.equal(brake({sent:40,bounced:20}),'');assert.equal(brake({sent:40,stops:2}),'stops');
 assert.equal(outreachV2Schema,await readFile(new URL('../migrations/0004_outreach_v2.sql',import.meta.url),'utf8'));
}));


// Owner 2026-11-04: wrong inbox, full inbox, unavailable, unmonitored are delivery problems, never stop replies.
import {classifyInbound as _classifyInbound} from '../packages/outreach/inbound.mjs';
import {readFileSync as _readFx} from 'node:fs';
test('inbound classifier: shared delivery-problem fixtures', () => {
 for (const f of JSON.parse(_readFx(new URL('./fixtures/inbound.json', import.meta.url), 'utf8')))
  assert.equal(_classifyInbound(f).kind, f.kind, f.name);
});

test('mailMessage: a T2 with an attachment is multipart/mixed with the text first and the PDF base64',async()=>{
 const {mailMessage}=await import('../packages/outreach/smtp.mjs');
 const m=mailMessage({from:'one@gmail.com',to:'hello@hub.zw',subject:'Re: x',text:'Hello again',id:'abc',attachments:[{filename:'sheet.pdf',content:new TextEncoder().encode('%PDF-1.4 test')}]});
 assert.match(m,/Content-Type: multipart\/mixed; boundary="jl[a-z0-9]+"/);
 assert.ok(m.indexOf('text/plain')<m.indexOf('application/pdf'));
 assert.match(m,/filename="sheet\.pdf"/);
 const plain=mailMessage({from:'one@gmail.com',to:'hello@hub.zw',subject:'x',text:'Hi',id:'abd'});
 assert.match(plain,/Content-Type: text\/plain/);assert.doesNotMatch(plain,/multipart/);
});
