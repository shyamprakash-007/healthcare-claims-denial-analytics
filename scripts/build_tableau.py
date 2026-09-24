"""Create an editable Tableau workbook and a portable Hyper-backed package."""
from pathlib import Path
import xml.etree.ElementTree as E
from copy import deepcopy
import json, zipfile
import pandas as pd
from tableauhyperapi import HyperProcess,Telemetry,Connection,CreateMode,TableDefinition,TableName,SqlType,Inserter
R=Path(__file__).resolve().parents[1];T=R/'tableau';T.mkdir(exist_ok=True)
E.register_namespace('user','http://www.tableausoftware.com/xml/user')
U='{http://www.tableausoftware.com/xml/user}'
def el(p,tag,text=None,**attrs):
    x=E.SubElement(p,tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
    if text is not None:x.text=text
    return x

def build():
    ids=['claim_id','provider_id','patient_id','procedure_code','diagnosis_code']
    d=pd.read_csv(R/'data/exports/tableau_claims_dataset.csv',dtype={c:'string' for c in ids})
    dates=['date_of_service','service_month_start']
    for c in dates:d[c]=pd.to_datetime(d[c])
    types={c:('date' if c in dates else 'string' if pd.api.types.is_string_dtype(d[c]) else 'integer' if pd.api.types.is_integer_dtype(d[c]) else 'real') for c in d}
    ht={'date':SqlType.date(),'string':SqlType.text(),'integer':SqlType.big_int(),'real':SqlType.double()}
    hyper=T/'Data/claims.hyper';hyper.parent.mkdir(exist_ok=True)
    td=TableDefinition(TableName('Extract','Extract'),[TableDefinition.Column(c,ht[types[c]]) for c in d])
    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hp:
        with Connection(hp.endpoint,str(hyper),CreateMode.CREATE_AND_REPLACE) as con:
            con.catalog.create_schema('Extract');con.catalog.create_table(td)
            rows=[[v.date() if types[c]=='date' else None if pd.isna(v) else int(v) if types[c]=='integer' else float(v) if types[c]=='real' else str(v) for c,v in zip(d.columns,row)] for row in d.itertuples(index=False,name=None)]
            with Inserter(con,td) as ins:ins.add_rows(rows);ins.execute()
            checks=con.execute_list_query('SELECT COUNT(DISTINCT "claim_id"),SUM("billed_amount"),SUM("paid_amount"),SUM("claim_status_denied_flag"),SUM("follow_up_flag") FROM "Extract"."Extract"')[0]
            expected=[len(d),d.billed_amount.sum(),d.paid_amount.sum(),d.claim_status_denied_flag.sum(),d.follow_up_flag.sum()]
            assert all(abs(float(x)-float(y))<1e-8 for x,y in zip(checks,expected))
            pd.DataFrame({'metric':['Total Claims','Total Billed','Total Paid','Denied Claims','Follow-up Claims'],'sql_export':expected,'hyper':checks,'status':'PASS'}).to_csv(R/'data/exports/hyper_reconciliation.csv',index=False)
    wb=E.Element('workbook',{'source-platform':'win','source-build':'2024.2.0 (20242.24.0426.0923)','version':'18.1'})
    prefs=el(wb,'preferences');el(prefs,'preference',name='ui.encoding.shelf.height',value=24);el(prefs,'preference',name='ui.shelf.height',value=26)
    el(wb,'style-theme',name='clean')
    sources=el(wb,'datasources');params=el(sources,'datasource',hasconnection='false',inline='true',name='Parameters',version='18.1');el(params,'aliases',enabled='yes')
    paramcols=[]
    specs=[('From','date','2024-05-01',None),('Through','date','2024-09-20',None),('Insurance','string','All',sorted(d.insurance_type.unique())),('Claim status','string','All',sorted(d.claim_status.unique())),('AR status','string','All',sorted(d.ar_status.unique())),('Month','string','All',sorted(d.service_month_start.dt.strftime('%Y-%m').unique()))]
    for name,typ,value,vals in specs:
        val=f'#{value}#' if typ=='date' else '"'+value+'"'
        c=el(params,'column',caption='Status' if name=='Claim status' else name,datatype=typ,name='['+name+']',param_domain_type='any' if vals is None else 'list',role='measure',type='ordinal' if typ=='date' else 'nominal',value=val)
        el(c,'calculation',**{'class':'tableau','formula':val})
        if vals is not None:
            mem=el(c,'members')
            for v in ['All']+vals:el(mem,'member',value='"'+v+'"')
        paramcols.append(c)
    dsname='textscan.claims';ds=el(sources,'datasource',caption='Synthetic claims | SQL analytics view',inline='true',name=dsname,version='18.1')
    conn=el(ds,'connection',**{'class':'federated'})
    named=el(el(conn,'named-connections'),'named-connection',name='hyper.claims',caption='Claims extract')
    el(named,'connection',**{'class':'hyper','dbname':'Data/claims.hyper','schema':'Extract','tablename':'Extract'})
    el(conn,'relation',connection='hyper.claims',name='Extract',table='[Extract].[Extract]',type='table')
    meta=el(conn,'metadata-records')
    for i,(c,typ) in enumerate(types.items()):
        m=el(meta,'metadata-record',**{'class':'column'})
        for tag,val in [('remote-name',c),('remote-type',{'string':129,'date':133,'integer':20,'real':5}[typ]),('local-name','['+c+']'),('parent-name','[Extract]'),('remote-alias',c),('ordinal',i),('local-type',typ),('aggregation','Count' if typ in ['string','date'] else 'Sum'),('contains-null','true')]:el(m,tag,str(val))
    cols={}
    def col(name,typ,role,formula=None,fmt=None,caption=None):
        c=el(ds,'column',name='['+name+']',caption=caption or name.replace('_',' ').title(),datatype=typ,role=role,type='nominal' if typ in ['string','boolean'] else 'quantitative' if role=='measure' or typ=='date' else 'ordinal')
        if fmt:c.set('default-format',fmt)
        if formula:el(c,'calculation',**{'class':'tableau','formula':formula})
        cols[name]=c
    for c,typ in types.items():col(c,typ,'dimension' if typ in ['string','date'] or c=='claim_key' else 'measure',fmt='p0.0%' if c.endswith('_ratio') else 'n#,##0' if c.endswith('_amount') or c=='allowed_amount_gap' else None)
    for field,caption in {'service_month_start':'Service month','status_consistency_flag':'Review flags','follow_up_flag':'Follow-up claims','open_ar_flag':'Open AR records','reason_code':'Source reason','procedure_code':'Procedure code','gross_unpaid_amount':'Gross unpaid','billed_amount':'Billed','allowed_amount':'Allowed','paid_amount':'Paid'}.items():cols[field].set('caption',caption)
    for field,caption in {'insurance_type':'Insurance','claim_status':'Status','procedure_code':'Code'}.items():cols[field].set('caption',caption)
    calcs={
      'Total claims':('COUNTD([claim_id])','n#,##0'),
      'Denied claims':('COUNTD(IF [claim_status]="Denied" THEN [claim_id] END)','n#,##0'),
      'Under review':('COUNTD(IF [claim_status]="Under Review" THEN [claim_id] END)','n#,##0'),
      'Denial rate':('IF COUNTD([claim_id])>0 THEN COUNTD(IF [claim_status]="Denied" THEN [claim_id] END)/COUNTD([claim_id]) END','p0.0%'),
      'Outcome denial rate':('IF COUNTD([claim_id])>0 THEN COUNTD(IF [outcome]="Denied" THEN [claim_id] END)/COUNTD([claim_id]) END','p0.0%'),
      'Follow-up rate':('IF COUNTD([claim_id])>0 THEN SUM([follow_up_flag])/COUNTD([claim_id]) END','p0.0%'),
      'Payment rate':('IF SUM([billed_amount])<>0 THEN SUM([paid_amount])/SUM([billed_amount]) END','p0.0%'),
      'Denied billed':('SUM(IF [claim_status]="Denied" THEN [billed_amount] ELSE 0 END)','n#,##0'),
      'Any denial billed':('SUM(IF [any_denial_flag]=1 THEN [billed_amount] ELSE 0 END)','n#,##0')}
    for name,(formula,fmt) in calcs.items():col(name,'real','measure',formula,fmt)
    col('Service period','string','dimension',"STR(DATEPART('year',[date_of_service]))+'-'+RIGHT('0'+STR(DATEPART('month',[date_of_service])),2)")
    col('Paid ratio band','string','dimension',"IF ISNULL([paid_to_billed_ratio]) THEN 'Undefined' ELSEIF [paid_to_billed_ratio]<0.5 THEN '0-<50%' ELSEIF [paid_to_billed_ratio]<0.6 THEN '50-<60%' ELSEIF [paid_to_billed_ratio]<0.7 THEN '60-<70%' ELSEIF [paid_to_billed_ratio]<0.8 THEN '70-<80%' ELSEIF [paid_to_billed_ratio]<0.9 THEN '80-<90%' ELSE '90%+' END",caption='Band')
    col('In scope','boolean','dimension',"[date_of_service]>=[Parameters].[From] AND [date_of_service]<=[Parameters].[Through] AND ([Parameters].[Insurance]='All' OR [insurance_type]=[Parameters].[Insurance]) AND ([Parameters].[Claim status]='All' OR [claim_status]=[Parameters].[Claim status]) AND ([Parameters].[AR status]='All' OR [ar_status]=[Parameters].[AR status]) AND ([Parameters].[Month]='All' OR [Service period]=[Parameters].[Month])")
    # An explicit extract declaration allows Tableau Public to use the packaged Hyper file.
    extract=el(ds,'extract',enabled='true',count=len(d),units='records')
    ec=el(extract,'connection',**{'class':'hyper','dbname':'Data/claims.hyper','schema':'Extract','tablename':'Extract'})
    el(ec,'relation',name='Extract',table='[Extract].[Extract]',type='table')
    sheets=el(wb,'worksheets');sheet_names=[]
    def sheet(name,measure,dim=None,kind='Bar',dim2=None,subtitle='',color='#197c90',tooltip='',denied_only=False):
        sheet_names.append(name);ws=el(sheets,'worksheet',name=name)
        title=el(el(ws,'layout-options'),'title');ft=el(title,'formatted-text');el(ft,'run',name,bold='true',fontname='Arial',fontsize=11)
        if subtitle:el(ft,'run','\n'+subtitle,fontname='Arial',fontsize=9,fontcolor='#617285')
        table=el(ws,'table');v=el(table,'view');dss=el(v,'datasources');el(dss,'datasource',name=dsname,caption='Synthetic claims | SQL analytics view');el(dss,'datasource',name='Parameters')
        pdp=el(v,'datasource-dependencies',datasource='Parameters')
        for pc in paramcols:pdp.append(deepcopy(pc))
        dep=el(v,'datasource-dependencies',datasource=dsname)
        for c in cols.values():dep.append(deepcopy(c))
        instances={}
        def ref(c):
            if c in instances:return f'[{dsname}].'+instances[c]
            typ=cols[c].get('datatype');aggregate=c in calcs
            der='User' if aggregate else 'None' if cols[c].get('role')=='dimension' else 'Sum'
            key='nk' if typ in ['string','boolean'] else 'qk';inst='['+{'User':'usr','None':'none','Sum':'sum'}[der]+':'+c+':'+key+']'
            el(dep,'column-instance',column='['+c+']',derivation=der,name=inst,pivot='key',type='nominal' if key=='nk' else 'quantitative');instances[c]=inst
            return f'[{dsname}].'+inst
        mr=ref(measure);dr=ref(dim) if dim else None;d2=ref(dim2) if dim2 else None
        sc=ref('In scope');f=el(v,'filter',**{'class':'categorical','column':sc});gf=el(f,'groupfilter',function='member',level=instances['In scope'],member='true');gf.set(U+'ui-enumeration','inclusive');gf.set(U+'ui-marker','enumerate')
        if denied_only:
            cr=ref('claim_status');f=el(v,'filter',**{'class':'categorical','column':cr});el(f,'groupfilter',function='member',level=instances['claim_status'],member='"Denied"')
        if dim and kind=='Bar' and dim not in ['Paid ratio band']:
            el(v,'sort',**{'class':'computed','column':dr,'direction':'DESC','using':mr})
        el(v,'aggregation',value='true')
        style=el(table,'style');sr=el(style,'style-rule',element='worksheet');el(sr,'format',attr='font-family',value='Arial');el(sr,'format',attr='font-size',value=10)
        sr=el(style,'style-rule',element='gridline');el(sr,'format',attr='line-visibility',value='off')
        if dim=='reason_code':
            sr=el(style,'style-rule',element='header');el(sr,'format',attr='width',field=dr,value=280)
        pane=el(el(table,'panes'),'pane',selection_relaxation_option='selection-relaxation-disallow');el(el(pane,'view'),'breakdown',value='auto');el(pane,'mark',**{'class':kind})
        enc=el(pane,'encodings')
        if kind=='Text':el(enc,'text',column=mr)
        if kind=='Square':el(enc,'color',column=mr);el(enc,'text',column=mr)
        definitions={'Total claims':'Distinct Claim IDs in the selected population.','Denied claims':'Distinct claims where Claim Status = Denied.','Denial rate':'Claim Status Denied / distinct claims in the selected population.','Follow-up rate':'Claims requiring follow-up / distinct claims in the selected population.','Payment rate':'Sum paid / sum billed; not an average of individual ratios.','Denied billed':'Billed amount on claims with Claim Status Denied; not lost revenue.','Any denial billed':'Billed amount where status OR outcome is Denied; overlaps counted once.','gross_unpaid_amount':'Billed minus paid. Collectibility is unknown.','status_consistency_flag':'Rule-based status/outcome conflicts; not confirmed source errors.','open_ar_flag':'Open, Pending, On Hold or Partially Paid. Denied shown separately.'}
        tt=el(el(pane,'customized-tooltip',show_buttons='true'),'formatted-text');el(tt,'run',(definitions.get(measure,tooltip)+'\n' if definitions.get(measure,tooltip) else '')+(cols[dim].get('caption')+': <'+dr+'>\n' if dim else '')+(cols[dim2].get('caption')+': <'+d2+'>\n' if dim2 else '')+measure+': <'+mr+'>\nSynthetic claims. Amounts in source currency units.')
        sr=el(el(pane,'style'),'style-rule',element='mark');el(sr,'format',attr='mark-color',value=color);el(sr,'format',attr='mark-labels-show',value='true' if kind in ['Text','Square'] else 'false');el(sr,'format',attr='font-size',value=24 if kind=='Text' and not dim else 10)
        rows=el(table,'rows');columns=el(table,'cols')
        if kind=='Line':rows.text=mr;columns.text=dr
        elif kind=='Square':rows.text=dr;columns.text=d2
        elif dim:rows.text=dr;columns.text=mr
        return name
    # KPI worksheets use independent Tableau aggregations, not saved summary numbers.
    kpi_specs=[('Total claims','Total claims'),('Total billed','billed_amount'),('Total paid','paid_amount'),('Denial rate','Denial rate'),('Follow-up rate','Follow-up rate'),('Gross unpaid','gross_unpaid_amount'),('Denied claims','Denied claims'),('Denied billed','Denied billed'),('Any denial billed','Any denial billed'),('Total allowed','allowed_amount'),('Payment rate','Payment rate'),('Open AR records','open_ar_flag'),('Status review flags','status_consistency_flag'),('Under review','Under review')]
    for name,m in kpi_specs:sheet(name,m,kind='Text',tooltip='Gross unpaid is billed minus paid; collectibility unknown.' if name=='Gross unpaid' else 'Current filter population. See metric definitions.')
    sheet('Monthly claim volume','Total claims','service_month_start','Line',subtitle='September covers days 1-20 only')
    sheet('Claim status mix','Total claims','claim_status')
    sheet('Insurance claim volume','Total claims','insurance_type')
    sheet('Outcome distribution','Total claims','outcome')
    sheet('Denials by reason','Denied claims','reason_code',subtitle='Click a bar to filter this page',color='#c66732')
    sheet('Denial rate by insurance','Denial rate','insurance_type',color='#c66732')
    sheet('Monthly denial rate','Denial rate','service_month_start','Line',subtitle='Claim status definition; September partial',color='#c66732')
    sheet('Denied billed by insurance','Denied billed','insurance_type',color='#c66732')
    sheet('Procedures by denied billed','Denied billed','procedure_code',color='#c66732',subtitle='All 10 observed codes')
    # Three aligned monthly financial series are separate small multiples to avoid dual axes.
    sheet('Monthly billed','billed_amount','service_month_start','Line')
    sheet('Monthly allowed','allowed_amount','service_month_start','Line',color='#71859c')
    sheet('Monthly paid','paid_amount','service_month_start','Line',color='#23654f')
    sheet('Payment rate by insurance','Payment rate','insurance_type')
    sheet('Procedures by gross unpaid','gross_unpaid_amount','procedure_code',subtitle='Billed minus paid; collectibility unknown')
    sheet('Paid-to-billed distribution','Total claims','Paid ratio band',subtitle='Claim-level ratios; not portfolio payment rate')
    sheet('AR status distribution','Total claims','ar_status')
    sheet('Follow-up by insurance','Follow-up rate','insurance_type')
    sheet('Follow-up by reason','follow_up_flag','reason_code')
    sheet('Status and outcome matrix','Total claims','claim_status','Square','outcome',subtitle='All combinations retained')
    sheet('Monthly status review flags','status_consistency_flag','service_month_start','Line',subtitle='Rule-based flags; not confirmed errors',color='#c66732')
    actions=el(wb,'actions')
    targets=['Denied claims','Denial rate','Denied billed','Any denial billed','Denial rate by insurance','Monthly denial rate','Denied billed by insurance','Procedures by denied billed']
    for i,target in enumerate(targets,1):
        a=el(actions,'action',caption='Reason selection: '+target,name=f'[Action{i}]');el(a,'activation',auto_clear='true',type='on-select');el(a,'source',dashboard='02 Denial Analytics',worksheet='Denials by reason',type='sheet');cmd=el(a,'command',command='tsc:tsl-filter');el(cmd,'param',name='target',value=target);el(cmd,'param',name='special-fields',value='all')
    dashboards=el(wb,'dashboards');boards=[]
    def board(name,kpis,charts,note,layout='standard'):
        boards.append((name,kpis+charts));db=el(dashboards,'dashboard',name=name)
        sr=el(el(db,'style'),'style-rule',element='table');el(sr,'format',attr='background-color',value='#edf2f6')
        el(db,'size',sizing_mode='fixed',minheight=950,maxheight=950,minwidth=1300,maxwidth=1300)
        el(el(db,'datasources'),'datasource',name='Parameters');dep=el(db,'datasource-dependencies',datasource='Parameters')
        for pc in paramcols:dep.append(deepcopy(pc))
        zones=el(db,'zones');counter=0
        def zone(x,y,w,h,typ=None,**kw):
            nonlocal counter;counter+=1
            z=el(zones,'zone',id=counter,x=x,y=y,w=w,h=h,**kw)
            if typ:z.set('type-v2',typ)
            st=el(z,'zone-style');el(st,'format',attr='background-color',value='#ffffff');el(st,'format',attr='margin',value=8)
            return z
        z=zone(0,0,100000,8500,'text');z.find('./zone-style/format').set('value','#162d43');ft=el(z,'formatted-text');el(ft,'run','HEALTHCARE CLAIMS  /  SYNTHETIC PORTFOLIO\n',fontname='Arial',fontsize=10,fontcolor='#b0deea');el(ft,'run',name[3:],fontname='Arial',fontsize=23,bold='true',fontcolor='#ffffff')
        z=zone(1600,8700,96800,3700,'text');el(el(z,'formatted-text'),'run',note,fontname='Arial',fontsize=9,fontcolor='#526579')
        for i,(p,*_) in enumerate(specs):zone(1600+i*16100,12700,15600,5800,'paramctrl',mode='compact',param='[Parameters].['+p+']')
        width=int(96800/len(kpis))
        for i,s in enumerate(kpis):zone(1600+i*width,19700,width-600,10300,name=s,show_title='true')
        if layout=='finance':positions=[(1600,32000,31000,27000),(34500,32000,31000,27000),(67400,32000,31000,27000),(1600,61500,31000,32000),(34500,61500,31000,32000),(67400,61500,31000,32000)]
        elif len(charts)==4:positions=[(1600,32000,47400,29000),(51000,32000,47400,29000),(1600,63000,47400,30000),(51000,63000,47400,30000)]
        else:positions=[(1600,32000,47400,30000),(51000,32000,47400,30000),(1600,64000,31000,29500),(34500,64000,31000,29500),(67400,64000,31000,29500)]
        for s,pos in zip(charts,positions):zone(*pos,name=s,show_title='true')
        z=zone(1600,95700,96800,2900,'text');el(el(z,'formatted-text'),'run','May 1 - September 20, 2024 | Source currency unspecified | Parameters apply to all pages | Gross unpaid is not proven recoverable AR',fontname='Arial',fontsize=9,fontcolor='#526579')
    board('01 Executive Overview',['Total claims','Total billed','Total paid','Denial rate','Follow-up rate','Gross unpaid'],['Monthly claim volume','Claim status mix','Insurance claim volume','Outcome distribution'],'Operational status and reported outcome are separate measures. Use the filters to inspect each segment.')
    board('02 Denial Analytics',['Denied claims','Denial rate','Denied billed','Any denial billed'],['Denials by reason','Denial rate by insurance','Monthly denial rate','Denied billed by insurance','Procedures by denied billed'],'Denial rate uses Claim Status. Any denial billed uses Claim Status OR Outcome. Click a reason; click empty space to clear.')
    board('03 Financial Performance',['Total billed','Total allowed','Total paid','Gross unpaid','Payment rate'],['Monthly billed','Monthly allowed','Monthly paid','Payment rate by insurance','Procedures by gross unpaid','Paid-to-billed distribution'],'Amounts are source currency units. Portfolio payment rate is total paid / total billed. September is partial.','finance')
    board('04 AR and Data Quality',['Follow-up rate','Open AR records','Status review flags','Under review'],['Follow-up by reason','AR status distribution','Follow-up by insurance','Status and outcome matrix','Monthly status review flags'],'Open AR = Open, Pending, On Hold, Partially Paid. Review flags follow the documented project rulebook.')
    windows=el(wb,'windows',saved_dpi_scale_factor='1.0')
    for name,ss in boards:
        w=el(windows,'window',**{'class':'dashboard','name':name,'maximized':'true'});vp=el(w,'viewpoints')
        for s in ss:el(el(vp,'viewpoint',name=s),'zoom',type='entire-view')
        el(w,'active',id=1)
    for s in sheet_names:
        w=el(windows,'window',**{'class':'worksheet','name':s,'hidden':'true'});el(w,'cards');el(el(w,'viewpoint',name=s),'zoom',type='entire-view')
    wb.remove(actions);wb.insert(list(wb).index(sheets),actions)
    for zone_node in wb.findall('.//zone'):
        zone_style=zone_node.find('zone-style')
        if zone_style is not None:
            zone_node.remove(zone_style);zone_node.append(zone_style)
    E.indent(wb);path=T/'Healthcare_Claims_Denial_Analytics.twb';E.ElementTree(wb).write(path,encoding='utf-8',xml_declaration=True)
    with zipfile.ZipFile(T/'Healthcare_Claims_Denial_Analytics.twbx','w',zipfile.ZIP_DEFLATED) as z:z.write(path,path.name);z.write(hyper,'Data/claims.hyper')
    print('Built',len(sheet_names),'worksheets and',len(boards),'dashboards. Hyper KPIs match SQL export.')
if __name__=='__main__':build()
