#!/usr/bin/env python3
"""Execute original references and all notebook code cells; no external AI calls."""
from pathlib import Path
import os,sys,json,copy,tempfile,contextlib,io,hashlib
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('MPLBACKEND','Agg')
R=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(R/'curriculum/expansion'))
from lab_engine import run
from profiles import PROFILES
scope=json.loads((R/'curriculum/expansion/scope.json').read_text());courses=json.loads((R/'apps/web/public/courses.json').read_text())
# 2026-10-27 the library merged 36 overlapping paths into 20 with modules (mergedFrom). Every one of
# the thirty original projects must still have a home: its own course or a module of a merged one.
home={}
for c in courses:
 home[c['id']]=c
 for m in c.get('mergedFrom') or []:home[m]=c
assert len(PROFILES)==30 and all(p['id'] in home for p in PROFILES),[p['id'] for p in PROFILES if p['id'] not in home]
sources={p['source'] for p in PROFILES}
listed={c['sourceListingNumber'] for c in courses if c.get('sourceListingNumber')}
assert listed<=sources
assert len(scope['incorporated'])==11
assert len(scope['conditional_not_published'])==27 and len(scope['held_not_published'])==6
assert not (sources&set(scope['conditional_not_published']+scope['held_not_published']))
for s in scope['incorporated']:
 c=home[s['course']]
 assert any(s['listing'] in (l.get('supportingInputs') or []) and s['title'] in l['text'] for l in c['lessons']),s
# every lesson in the library, merged or not, keeps the original depth bar
for c in courses:
 assert all(len(l['text'])>500 and len(l['example'])>100 for l in c['lessons']),c['id']
 assert all(len(l['steps'])>=5 and len(l['expected'])>=2 for l in c['lessons']),c['id']
new=[{'id':p['id']} for p in PROFILES]
checks=0;cells=0;extensions=0
with tempfile.TemporaryDirectory(prefix='open-practice-reference-') as tmp:
 old=os.getcwd();os.chdir(tmp)
 try:
  for c in new:
   folder=R/'curriculum/fixtures'/c['id'];d=json.loads((folder/'input.json').read_text());before=copy.deepcopy(d);expected=json.loads((folder/'expected.json').read_text());actual=run(c['id'],d)
   assert actual==expected,(c['id'],actual,expected);assert d==before
   try:run(c['id'],None)
   except ValueError:pass
   else:raise AssertionError('Malformed input accepted: '+c['id'])
   notebook=json.loads((folder/'hosted-lab.ipynb').read_text());assert notebook['nbformat']==4
   ns={'__name__':'__main__'}
   for cell in notebook['cells']:
    if cell['cell_type']=='code':
     assert cell['execution_count'] is None and cell['outputs']==[]
     with contextlib.redirect_stdout(io.StringIO()):exec(''.join(cell['source']),ns)
     cells+=1
   if len(notebook['cells'])>4:extensions+=1
   checks+=1
  assert (Path(tmp)/'checked-chart.svg').is_file()
 finally:os.chdir(old)
# Additional independently specified failure expectations, not generated from observed output.
assert run('maths-workbench',{'start':0,'learning_rate':1.5})['loss_after']==36
assert run('uncertainty-lab',{'values':[2,4,4,6,90]})['mean']==21.2
assert run('text-classification',{'texts':['not broken']})['labels']==['issue'] # documented baseline limitation
assert run('campaign-evidence',{'impressions':0,'clicks':0,'spend':10})['cpc'] is None
assert run('preprocessing-lab',{'train':[2,None,4],'test':[999,None]})['training_mean']==3
assert run('constraint-planner',{'tasks':['A','B','C'],'slots':[1,2]})['valid_schedules']==0
assert run('inventory-planning',{'demand':[10,12,14],'stock':20,'safety':2})['reorder']==0
assert run('earn-by-doing',{'price':30,'tool_cost':3,'fees':2,'delivery_hours':2,'selling_hours':1,'support_hours':1,'refund':10})['net_before_tax']==15
print(json.dumps({'references_passed':checks,'notebook_code_cells_executed':cells,'optional_experiment_notebooks':extensions,'supporting_inputs_verified':11,'excluded_inputs_unpublished':33,'network_calls':0,'scope':'Synthetic/reference checks, not external provider or learner validation.'},indent=2))
