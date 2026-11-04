import {outreachSchema} from '../../packages/outreach/api.mjs';
import {outreachV2Schema} from '../../packages/outreach/v2.mjs';
import {growthSchema} from '../../packages/growth/schema.mjs';
// SQLite Durable Object adapter with a D1-like minimal interface.
// Core account code remains SQL-based; replace this adapter with D1 on migration.
const schema=`CREATE TABLE IF NOT EXISTS learners (id TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE, salt TEXT NOT NULL, password_hash TEXT NOT NULL, recovery_hash TEXT NOT NULL, created_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, learner_id TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE, expires_at INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS sessions_expiry ON sessions(expires_at);
CREATE TABLE IF NOT EXISTS workspaces (learner_id TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE, course_id TEXT NOT NULL, content TEXT NOT NULL, updated_at INTEGER NOT NULL, PRIMARY KEY(learner_id,course_id));
CREATE TABLE IF NOT EXISTS learning_events (id TEXT PRIMARY KEY, learner_id TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE, event TEXT NOT NULL, course_id TEXT NOT NULL, created_at INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS events_date ON learning_events(created_at);`;
export class LearnerDatabase {
 constructor(ctx){this.ctx=ctx;this.sql=ctx.storage.sql;this.sql.exec(schema);this.sql.exec(growthSchema);this.sql.exec(outreachSchema);this.sql.exec(outreachV2Schema)}
 async fetch(request){
  try{
   const {statements}=await request.json();
   if(!Array.isArray(statements)||statements.length>20)return new Response('Invalid batch',{status:400});
   const results=this.ctx.storage.transactionSync(()=>statements.map(s=>{const cursor=this.sql.exec(s.sql,...(s.params||[]));const rows=cursor.toArray();return {results:rows,meta:{changes:cursor.rowsWritten},success:true}}));
   return Response.json({results});
  }catch{return Response.json({error:'Database operation failed'},{status:400})}
 }
}
export function database(env){
 if(env.DB?.prepare)return env.DB; // D1 option, if configured later.
 if(!env.LEARNER_DB)return null;
 const stub=env.LEARNER_DB.get(env.DB_OBJECT_ID?env.LEARNER_DB.idFromString(env.DB_OBJECT_ID):env.LEARNER_DB.idFromName('open-practice'));
 async function execute(statements){const response=await stub.fetch('https://internal-database/query',{method:'POST',body:JSON.stringify({statements:statements.map(s=>({sql:s.sql,params:s.params}))})});const data=await response.json();if(!response.ok)throw Error('Database operation failed');return data.results}
 function prepare(sql){return {sql,params:[],bind(...params){return {...this,params}},async first(){return (await execute([this]))[0].results[0]||null},async all(){return (await execute([this]))[0]},async run(){return (await execute([this]))[0]}}}
 return {prepare,batch:execute};
}
