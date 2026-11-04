import {DatabaseSync} from 'node:sqlite';
import {mkdirSync,readFileSync,chmodSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
export function openDatabase(filename=process.env.DATABASE_PATH||'data/learners.sqlite'){
 const path=resolve(filename);mkdirSync(dirname(path),{recursive:true});const db=new DatabaseSync(path);chmodSync(path,0o600);db.exec('PRAGMA foreign_keys = ON');db.exec(readFileSync(new URL('../../migrations/0001_learners.sql',import.meta.url),'utf8'));db.exec(readFileSync(new URL('../../migrations/0002_growth.sql',import.meta.url),'utf8'));db.exec(readFileSync(new URL('../../migrations/0003_outreach.sql',import.meta.url),'utf8'));db.exec(readFileSync(new URL('../../migrations/0004_outreach_v2.sql',import.meta.url),'utf8'));
 function prepare(sql){return {sql,params:[],bind(...params){return {...this,params}},async first(){return db.prepare(this.sql).get(...this.params)||null},async all(){return {results:db.prepare(this.sql).all(...this.params)}},async run(){const r=db.prepare(this.sql).run(...this.params);return {success:true,meta:{changes:Number(r.changes)}}}}}
 return {prepare,async batch(statements){db.exec('BEGIN IMMEDIATE');try{const result=[];for(const s of statements){const r=db.prepare(s.sql).run(...s.params);result.push({success:true,meta:{changes:Number(r.changes)}})}db.exec('COMMIT');return result}catch(e){db.exec('ROLLBACK');throw e}},close(){db.close()}};
}
