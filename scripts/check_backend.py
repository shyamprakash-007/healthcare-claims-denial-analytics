"""Independent engine reconciliation and preparation boundary tests; no desktop access."""
import json,re
from pathlib import Path
import pandas as pd
import numpy as np
import duckdb
from pipeline import ROOT,load_raw,clean,engineer,safe_div

def main():
    checks=[]
    def record(name,passed,detail):
        checks.append({'check':name,'status':'PASS' if passed else 'FAIL','detail':detail})
    raw=load_raw();d=engineer(clean(raw))
    # Structural boundaries that would otherwise silently misstate totals.
    for field,value,label in [('claim_id','','missing ID'),('date_of_service','02/30/2024','invalid calendar date'),('billed_amount','bad','invalid amount'),('insurance_type','Unrecognized','unapproved category')]:
        bad=raw.copy();bad.loc[0,field]=value
        try:clean(bad);passed=False
        except AssertionError:passed=True
        record(label+' rejected',passed,'Required input / category gate')
    duplicate=pd.concat([raw,raw.iloc[[0]]],ignore_index=True)
    record('Exact duplicate not double counted',len(clean(duplicate))==len(raw),'Original raw file remains unchanged')
    conflict=raw.copy();conflict.loc[1,'claim_id']=conflict.loc[0,'claim_id']
    try:clean(conflict);passed=False
    except AssertionError:passed=True
    record('Conflicting duplicate ID rejected',passed,'No arbitrary first/last claim selection')
    sample=clean(raw.iloc[:3]).copy()
    sample.loc[0,['billed_amount','allowed_amount','paid_amount']]=[0,0,0]
    sample.loc[1,['billed_amount','allowed_amount','paid_amount']]=[100,90,110]
    sample.loc[2,['billed_amount','allowed_amount','paid_amount']]=[100,-5,-10]
    e=engineer(sample)
    record('Zero denominator ratios are null',e.loc[0,['billed_to_allowed_ratio','paid_to_billed_ratio','paid_to_allowed_ratio']].isna().all(),'Undefined is not zero')
    record('Overpayment retained and flagged',e.loc[1,'gross_unpaid_amount']==-10 and e.loc[1,'monetary_anomaly_flag']==1,'No clipping balances to zero')
    record('Negative amounts retained and flagged',e.loc[2,'allowed_amount']==-5 and e.loc[2,'monetary_anomaly_flag']==1,'No silent deletion or absolute value')
    # Equality of every source and derived field in the PostgreSQL analytical view.
    pg=pd.read_json(ROOT/'data/exports/postgres_claims_verification.json',dtype=False)
    db=duckdb.connect(str(ROOT/'data/processed/claims.duckdb'),read_only=True)
    local=db.execute('SELECT * FROM vw_claims_analytics ORDER BY claim_id').df()
    for c in local:
        if pd.api.types.is_numeric_dtype(local[c]):passed=np.allclose(local[c].astype(float),pd.to_numeric(pg[c]),equal_nan=True,rtol=0,atol=1e-8)
        elif pd.api.types.is_datetime64_any_dtype(local[c]):passed=local[c].dt.strftime('%Y-%m-%d').tolist()==pd.to_datetime(pg[c],utc=True).dt.strftime('%Y-%m-%d').tolist()
        else:passed=local[c].astype(str).tolist()==pg[c].astype(str).tolist()
        record('PostgreSQL field '+c,bool(passed),'1,000 values checked against DuckDB')
    for n,title,query in re.findall(r'-- Q(\d+) \| ([^\n]+)\n(.*?);',(ROOT/'sql/05_business_analysis.sql').read_text(),re.S):
        actual=db.execute(query).df();expected=pd.DataFrame(json.loads((ROOT/f'sql/results_postgres/Q{n}_{title}.json').read_text()))
        passed=actual.shape==expected.shape and list(actual)==list(expected)
        if passed:
            for c in actual:
                if pd.api.types.is_numeric_dtype(actual[c]):ok=np.allclose(actual[c].astype(float),pd.to_numeric(expected[c]).astype(float),equal_nan=True,rtol=0,atol=1e-8)
                elif pd.api.types.is_datetime64_any_dtype(actual[c]):ok=actual[c].dt.strftime('%Y-%m-%d').tolist()==pd.to_datetime(expected[c],utc=True).dt.strftime('%Y-%m-%d').tolist()
                else:ok=actual[c].astype(str).tolist()==expected[c].astype(str).tolist()
                passed=passed and bool(ok)
        record('Q'+n+' cross-engine results',passed,f'{len(actual)} result rows; {title}')
    db.close()
    result=pd.DataFrame(checks);result.to_csv(ROOT/'data/exports/backend_test_results.csv',index=False)
    assert result.status.eq('PASS').all(),result.loc[result.status.ne('PASS')].to_string()
    print(f'{len(result)} backend boundary / cross-engine checks passed.')
if __name__=='__main__':main()
