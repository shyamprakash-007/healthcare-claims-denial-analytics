"""Reproducible source -> audit -> clean -> metrics -> SQL -> Tableau export."""
from pathlib import Path
import hashlib, json, re
import numpy as np
import pandas as pd
import duckdb

ROOT = Path(__file__).resolve().parents[1]
IDS = ['claim_id','provider_id','patient_id','procedure_code','diagnosis_code']
MONEY = ['billed_amount','allowed_amount','paid_amount']
CATS = ['insurance_type','claim_status','reason_code','follow_up_required','ar_status','outcome']
SOURCE = ['claim_id','provider_id','patient_id','date_of_service','billed_amount','procedure_code','diagnosis_code','allowed_amount','paid_amount','insurance_type','claim_status','reason_code','follow_up_required','ar_status','outcome']
OPEN_AR = ['Open','Pending','On Hold','Partially Paid']

def load_raw():
    raw = pd.read_csv(ROOT/'data/raw/claim_data.csv', dtype='string', keep_default_na=False)
    raw.columns = raw.columns.str.lower().str.replace(' ','_').str.replace('-','_')
    assert list(raw.columns)==SOURCE, 'Source contract changed; investigate before processing'
    return raw

def audit(raw):
    out=ROOT/'data/audit';out.mkdir(exist_ok=True)
    profile=pd.DataFrame({'field':raw.columns,'loaded_dtype':raw.dtypes.astype(str).values,'unique_count':raw.nunique().values,'missing_count':raw.apply(lambda s:s.str.strip().eq('').sum()).values})
    profile.to_csv(out/'column_profile.csv',index=False)
    checks=[('Rows',len(raw),'retain'),('Columns',len(raw.columns),'retain'),('Exact duplicate rows',int(raw.duplicated().sum()),'remove exact repeats only; preserve raw'),('Duplicate Claim IDs',int(raw.claim_id.duplicated().sum()),'stop on conflicting duplicates'),('Missing cells',int(raw.apply(lambda s:s.str.strip().eq('').sum()).sum()),'required fields fail validation')]
    dates=pd.to_datetime(raw.date_of_service,format='%m/%d/%Y',errors='coerce')
    checks.append(('Invalid dates',int(dates.isna().sum()),'flag; stop required-date validation'))
    m=raw[MONEY].apply(pd.to_numeric,errors='coerce')
    for c in MONEY:
        for label,mask in [('negative',m[c]<0),('zero',m[c]==0),('invalid',m[c].isna())]:checks.append((c+' '+label,int(mask.sum()),'retain + flag; invalid numbers stop validation'))
    for name,mask in [('Allowed > Billed',m.allowed_amount>m.billed_amount),('Paid > Allowed',m.paid_amount>m.allowed_amount),('Paid > Billed',m.paid_amount>m.billed_amount)]:checks.append((name,int(mask.sum()),'retain + flag'))
    for c in IDS:checks.append((c+' leading zeros',int(raw[c].str.startswith('0').sum()),'preserve as text'))
    for c in CATS:raw[c].value_counts(dropna=False).rename_axis(c).reset_index(name='claims').to_csv(out/f'{c}_values.csv',index=False)
    m.describe().to_csv(out/'financial_ranges.csv')
    pd.crosstab(raw.claim_status,raw.outcome).to_csv(out/'status_outcome_crosstab.csv')
    pd.crosstab(raw.claim_status,raw.ar_status).to_csv(out/'status_ar_crosstab.csv')
    summary=pd.DataFrame(checks,columns=['check','result','action']);summary.to_csv(out/'data_quality_summary.csv',index=False)
    return summary

def clean(raw):
    d=raw.copy()
    rules=json.loads((ROOT/'docs/rules.json').read_text())
    for c in d:d[c]=d[c].str.strip().replace('',pd.NA)
    # Use the frozen, observed vocabulary to correct case only, including Self-Pay.
    for c in CATS:
        lookup={v.casefold():v for v in rules[c]}
        d[c]=d[c].map(lambda v: lookup.get(v.casefold(),v) if pd.notna(v) else pd.NA).astype('string')
    d=d.drop_duplicates().reset_index(drop=True)
    assert not d.claim_id.duplicated().any(), 'Conflicting claim IDs require an explicit resolution'
    d['date_of_service']=pd.to_datetime(d.date_of_service,format='%m/%d/%Y',errors='coerce')
    for c in MONEY:d[c]=pd.to_numeric(d[c],errors='coerce')
    assert not d[SOURCE].isna().any().any(), 'Required source value missing or invalid'
    for c in CATS:assert set(d[c])<=set(rules[c]), f'Unexpected {c}'
    for c in IDS:assert list(d[c])==list(raw.drop_duplicates()[c].str.strip()),f'ID preservation failed: {c}'
    return d

def safe_div(a,b):return a/b.replace(0,np.nan)

def engineer(d):
    d=d.copy()
    d['gross_unpaid_amount']=d.billed_amount-d.paid_amount
    d['allowed_amount_gap']=d.allowed_amount-d.paid_amount
    d['billed_to_allowed_ratio']=safe_div(d.allowed_amount,d.billed_amount)
    d['paid_to_billed_ratio']=safe_div(d.paid_amount,d.billed_amount)
    d['paid_to_allowed_ratio']=safe_div(d.paid_amount,d.allowed_amount)
    d['claim_status_denied_flag']=d.claim_status.eq('Denied').astype(int)
    d['outcome_denied_flag']=d.outcome.eq('Denied').astype(int)
    d['any_denial_flag']=(d.claim_status.eq('Denied')|d.outcome.eq('Denied')).astype(int)
    d['follow_up_flag']=d.follow_up_required.map({'Yes':1,'No':0}).astype(int)
    d['open_ar_flag']=d.ar_status.isin(OPEN_AR).astype(int)
    d['status_consistency_flag']=((d.claim_status.eq('Denied')&d.outcome.isin(['Paid','Partially Paid']))|(d.claim_status.eq('Paid')&d.outcome.eq('Denied'))).astype(int)
    d['status_ambiguity_flag']=(d.claim_status.eq('Under Review')&d.outcome.isin(['Paid','Partially Paid'])).astype(int)
    d['ar_status_review_flag']=((d.claim_status.eq('Paid')&d.ar_status.eq('Denied'))|(d.claim_status.eq('Under Review')&d.ar_status.eq('Closed'))|(d.claim_status.eq('Denied')&d.ar_status.eq('Partially Paid'))).astype(int)
    d['monetary_anomaly_flag']=((d[MONEY]<0).any(axis=1)|(d.allowed_amount>d.billed_amount)|(d.paid_amount>d.allowed_amount)|(d.paid_amount>d.billed_amount)).astype(int)
    d['zero_amount_flag']=(d[MONEY]==0).any(axis=1).astype(int)
    d['denied_with_payment_flag']=(d.claim_status.eq('Denied')&(d.paid_amount>0)).astype(int)
    d['paid_with_allowed_gap_flag']=(d.claim_status.eq('Paid')&(d.allowed_amount>d.paid_amount)).astype(int)
    formats={'claim_id':r'[A-Z0-9]{10}','provider_id':r'\d{10}','patient_id':r'\d{10}','procedure_code':r'\d{5}','diagnosis_code':r'[A-Z]\d{2}\.\d'}
    d['code_format_flag']=pd.concat([~d[c].str.fullmatch(v) for c,v in formats.items()],axis=1).any(axis=1).astype(int)
    dt=d.date_of_service.dt
    for c,v in {'service_year':dt.year,'service_month':dt.month,'service_month_name':dt.month_name(),'service_quarter':dt.quarter,'service_week':dt.isocalendar().week.astype(int),'service_day_of_week':dt.dayofweek+1,'service_month_start':dt.to_period('M').dt.to_timestamp()}.items():d[c]=v
    return d

def quality_summary(d):
    t=pd.read_csv(ROOT/'data/audit/data_quality_summary.csv')
    extra=[(c,int(d[c].sum()),'retain + review under frozen rulebook') for c in d if c.endswith('_flag') and c not in ['claim_status_denied_flag','outcome_denied_flag','any_denial_flag','follow_up_flag','open_ar_flag']]
    extra += [('Unexpected categories',0,'Validated against observed source vocabulary, not an external coding standard'),('Unusable required values',0,'Hard stop before analytics if encountered')]
    t=pd.concat([t,pd.DataFrame(extra,columns=t.columns)],ignore_index=True)
    t.to_csv(ROOT/'data/audit/data_quality_summary.csv',index=False)
    return t

def kpis(d):
    n=d.claim_id.nunique();b=d.billed_amount.sum();p=d.paid_amount.sum();a=d.allowed_amount.sum()
    return {'total_claims':n,'total_billed_amount':b,'total_allowed_amount':a,'total_paid_amount':p,'denied_claims':d.loc[d.claim_status.eq('Denied'),'claim_id'].nunique(),'outcome_denied_claims':d.loc[d.outcome.eq('Denied'),'claim_id'].nunique(),'paid_claims':d.claim_status.eq('Paid').sum(),'under_review_claims':d.claim_status.eq('Under Review').sum(),'follow_up_claims':d.follow_up_flag.sum(),'gross_unpaid_amount':(d.billed_amount-d.paid_amount).sum(),'denied_billed_amount':d.loc[d.claim_status.eq('Denied'),'billed_amount'].sum(),'any_denial_amount':d.loc[d.any_denial_flag.eq(1),'billed_amount'].sum(),'open_ar_records':d.open_ar_flag.sum(),'status_inconsistency_count':d.status_consistency_flag.sum(),'payment_rate':p/b if b else np.nan,'allowed_rate':a/b if b else np.nan,'average_claim_value':b/n if n else np.nan,'claim_status_denial_rate':d.claim_status_denied_flag.sum()/n if n else np.nan,'outcome_denial_rate':d.outcome_denied_flag.sum()/n if n else np.nan,'follow_up_rate':d.follow_up_flag.sum()/n if n else np.nan}

def eda(d):
    for category in ['claim_status','outcome']:
        pd.crosstab(d.service_month_start,d[category]).to_csv(ROOT/f'data/exports/monthly_{category}_mix.csv')
    for group in ['insurance_type','claim_status','reason_code','ar_status','procedure_code','diagnosis_code','service_month_start']:
        t=d.groupby(group,dropna=False).agg(claims=('claim_id','nunique'),billed=('billed_amount','sum'),paid=('paid_amount','sum'),gross_unpaid=('gross_unpaid_amount','sum'),denied=('claim_status_denied_flag','sum'),follow_up=('follow_up_flag','sum'),open_ar=('open_ar_flag','sum'))
        t['denial_rate']=t.denied/t.claims;t['follow_up_rate']=t.follow_up/t.claims;t['payment_rate']=t.paid/t.billed
        t.to_csv(ROOT/f'data/exports/summary_{group}.csv')
    return pd.read_csv(ROOT/'data/exports/summary_insurance_type.csv')

def build_sql(d):
    # Recreate only the generated database; the immutable raw file is never overwritten.
    database=ROOT/'data/processed/claims.duckdb'
    if database.exists():database.unlink()
    con=duckdb.connect(str(database))
    con.execute((ROOT/'sql/01_schema.sql').read_text())
    stage=d[SOURCE].copy();stage.date_of_service=stage.date_of_service.dt.strftime('%Y-%m-%d')
    stage=stage.astype(str)
    con.register('source_frame',stage)
    con.execute('INSERT INTO stg_claims SELECT * FROM source_frame')
    for name in ['03_cleaning.sql','04_derived_metrics.sql','06_views_for_tableau.sql']:con.execute((ROOT/'sql'/name).read_text())
    queries=(ROOT/'sql/05_business_analysis.sql').read_text()
    for number,title,query in re.findall(r'-- Q(\d+) \| ([^\n]+)\n(.*?);',queries,re.S):
        result=con.execute(query).df();result.to_csv(ROOT/f'sql/results/Q{number}_{title}.csv',index=False)
    export=con.execute('SELECT * FROM vw_claims_analytics ORDER BY claim_id').df()
    export.to_csv(ROOT/'data/exports/tableau_claims_dataset.csv',index=False,date_format='%Y-%m-%d')
    con.execute('CHECKPOINT')
    return con,export

def validate(d,con,export):
    py=kpis(d); sql=con.execute('SELECT * FROM vw_kpi_summary').df().iloc[0].to_dict(); checks=[]
    for key,expected in py.items():
        actual=sql[key];ok=bool(np.isclose(float(expected),float(actual),rtol=0,atol=1e-8))
        checks.append((key,expected,actual,'PASS' if ok else 'FAIL','Python vs executed SQL'))
    left=d.sort_values('claim_id').reset_index(drop=True);right=export.sort_values('claim_id').reset_index(drop=True)
    for c in d.columns:
        if pd.api.types.is_numeric_dtype(d[c]):ok=np.allclose(left[c].astype(float),right[c].astype(float),equal_nan=True,atol=1e-10)
        elif pd.api.types.is_datetime64_any_dtype(d[c]):ok=(left[c].values==pd.to_datetime(right[c]).values).all()
        else:ok=left[c].astype(str).equals(right[c].astype(str))
        checks.append(('row_match_'+c,len(d),len(d) if ok else 'mismatch','PASS' if ok else 'FAIL','Independent Python / SQL field comparison'))
    sqlcounts=con.execute('SELECT count(*),count(DISTINCT claim_id) FROM fact_claims').fetchone()
    checks.append(('unique_fact_claim_id',len(d),sqlcounts[1],'PASS' if sqlcounts==(len(d),len(d)) else 'FAIL','Fact grain'))
    rawhash=hashlib.sha256((ROOT/'data/raw/claim_data.csv').read_bytes()).hexdigest()
    sourcehash=json.loads((ROOT/'docs/rules.json').read_text())['source_sha256']
    checks.append(('raw_sha256',sourcehash,rawhash,'PASS' if rawhash==sourcehash else 'FAIL','Unchanged input'))
    t=pd.DataFrame(checks,columns=['validation','expected','actual','status','scope'])
    t.to_csv(ROOT/'data/exports/validation_summary.csv',index=False)
    (ROOT/'data/exports/kpi_summary.json').write_text(json.dumps({k:float(v) for k,v in py.items()},indent=2))
    assert t.status.eq('PASS').all(),t.loc[t.status.ne('PASS')].to_string()
    # Native Tableau totals must be checked separately in Tableau; never mark them PASS here.
    return t

def main():
    raw=load_raw();audit(raw);d=engineer(clean(raw));quality_summary(d);eda(d)
    d.to_csv(ROOT/'data/processed/claims_cleaned.csv',index=False,date_format='%Y-%m-%d')
    d[SOURCE].to_csv(ROOT/'data/processed/claims_staging.csv',index=False,date_format='%Y-%m-%d')
    con,export=build_sql(d);validation=validate(d,con,export)
    print(json.dumps({k:float(v) for k,v in kpis(d).items()},indent=2))
    print(f'{len(validation)} reconciliation checks passed; native Tableau verification is separate.')
    con.close()

if __name__=='__main__':main()
