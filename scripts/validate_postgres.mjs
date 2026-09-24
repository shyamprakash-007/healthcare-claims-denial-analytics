import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
// Optional module override is used only by the build environment. Normal usage: npm install.
const modulePath=process.env.PGLITE_MODULE;
const { PGlite }=modulePath ? await import(pathToFileURL(modulePath)) : await import('@electric-sql/pglite');
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const read=async p=>fs.readFile(path.join(root,p),'utf8');
const db=new PGlite();
await db.exec(await read('sql/01_schema.sql'));
await db.query("COPY stg_claims FROM '/dev/blob' WITH (FORMAT csv, HEADER true)",[],{blob:new Blob([await read('data/processed/claims_staging.csv')])});
for(const name of ['03_cleaning.sql','04_derived_metrics.sql','06_views_for_tableau.sql']) await db.exec(await read('sql/'+name));
const version=(await db.query('SELECT version() AS version')).rows[0].version;
const sql=await read('sql/05_business_analysis.sql');
const queries=[...sql.matchAll(/-- Q(\d+) \| ([^\n]+)\n([\s\S]*?);/g)];
const resultDir=path.join(root,'sql/results_postgres');await fs.mkdir(resultDir,{recursive:true});
for(const [,number,title,query] of queries){const r=await db.query(query);await fs.writeFile(path.join(resultDir,`Q${number}_${title.trim()}.json`),JSON.stringify(r.rows,null,2));}
const metrics=(await db.query('SELECT * FROM vw_kpi_summary')).rows[0];
const expected=JSON.parse(await read('data/exports/kpi_summary.json'));
const checks=Object.entries(expected).map(([metric,value])=>({metric,python:Number(value),postgres:Number(metrics[metric]),status:Math.abs(Number(value)-Number(metrics[metric]))<1e-8?'PASS':'FAIL'}));
const actual=(await db.query('SELECT * FROM vw_claims_analytics ORDER BY claim_id')).rows;
await fs.writeFile(path.join(root,'data/exports/postgres_claims_verification.json'),JSON.stringify(actual,null,2));
await fs.writeFile(path.join(root,'data/exports/postgres_validation.json'),JSON.stringify({engine:version,runner:'PGlite embedded PostgreSQL; not a network PostgreSQL server',queries_executed:queries.length,checks},null,2));
await db.close();
if(checks.some(c=>c.status!=='PASS'))throw new Error('PostgreSQL KPI reconciliation failed');
console.log(JSON.stringify({engine:version,queries_executed:queries.length,kpis_passed:checks.length},null,2));
