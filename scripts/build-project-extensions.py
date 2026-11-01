#!/usr/bin/env python3
"""Executable optional cloud experiments and a bounded, mock-tested HTTP client."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent.parent
experiments={
'measured-ml':'''# Optional model-building experiment; synthetic wiring test, not a field benchmark.
from sklearn.tree import DecisionTreeClassifier
train_x=[[0],[1],[2],[8],[9],[10]]
train_y=[0,0,0,1,1,1]
test_x=[[0.5],[1.5],[8.5],[9.5]]
test_y=[0,0,1,1]
model=DecisionTreeClassifier(max_depth=1,random_state=7).fit(train_x,train_y)
predicted=model.predict(test_x).tolist()
report=run('measured-ml',{'truth':test_y,'predicted':predicted})
assert report['total']==4
print(report)
# Change feature values in a COPY, predict consequences, rerun and retain failures.
''',
'augmentation-lab':'''from sklearn.linear_model import LogisticRegression
from copy import deepcopy
train=deepcopy(fixture['train'])
test_before=deepcopy(fixture['test'])
augmented=train+[dict(r,x=r['x']+0.01) for r in train]
results={}
for name,rows in [('baseline',train),('augmented',augmented)]:
    model=LogisticRegression(random_state=7).fit([[r['x']] for r in rows],[r['label'] for r in rows])
    preds=model.predict([[r['x']] for r in fixture['test']]).tolist()
    results[name]=run('measured-ml',{'truth':[r['label'] for r in fixture['test']],'predicted':preds})
assert fixture['test']==test_before
print(results)
# Improvement is NOT required. The tiny holdout does not establish real-world performance.
''',
'preprocessing-lab':'''from sklearn.impute import SimpleImputer
import numpy as np
train=np.array([[np.nan if x is None else x] for x in fixture['train']])
test=np.array([[np.nan if x is None else x] for x in fixture['test']])
imputer=SimpleImputer(strategy='mean').fit(train)
transformed=imputer.transform(test).ravel().tolist()
assert transformed==[100.0,3.0]
assert imputer.statistics_.tolist()==[3.0]
print({'fitted_on':'training only','parameters':imputer.statistics_.tolist(),'test':transformed})
''',
'python-records':'''# Refactor while keeping the original input and independently specified result.
from copy import deepcopy
original=deepcopy(fixture)
changed=deepcopy(fixture)
changed['rows'].append({'id':'new','amount':2})
assert run('python-records',changed)['total']==12
assert fixture==original
try:
    run('python-records',None)
    raise AssertionError('Malformed input was not rejected')
except ValueError:
    print('Malformed input rejected as expected; original unchanged.')
''',
'data-wrangling':'''# Optional Pandas implementation: validate cardinality before merging.
import pandas as pd
orders=pd.DataFrame(fixture['orders'])
prices=pd.DataFrame([{'product':k,'price':v} for k,v in fixture['prices'].items()])
merged=orders.merge(prices,on='product',how='left',validate='many_to_one',indicator=True)
assert len(merged)==3
assert merged.loc[merged['_merge']=='left_only','id'].tolist()==['o3']
assert float((merged['qty']*merged['price']).sum())==11
print(merged.to_string(index=False))
''',
'data-visualisation':'''# Render a corrected chart in a hosted runtime. Keep the text alternative with it.
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(5,3))
ax.bar(list(fixture['values']),list(fixture['values'].values()),color=['#7c1f16','#376c65'],edgecolor='#33241a')
ax.set_ylim(bottom=0)
ax.set_ylabel('Fictional item count')
ax.set_title('A: 8 items; B: 10 items')
fig.tight_layout()
fig.savefig('checked-chart.svg')
plt.close(fig)
text_alternative='Two bars: A has 8 fictional items and B has 10; total 18. No cause or trend is established.'
print(text_alternative)
''',
'earn-by-doing':'''from copy import deepcopy
refunded=deepcopy(fixture)
refunded['refund']=10
actual_refund_case=run('earn-by-doing',refunded)
assert actual_refund_case['net_before_tax']==15
assert actual_refund_case['effective_hourly_before_tax']==3.75
print(actual_refund_case)
print('A hypothetical price is not earned income. Verify actual payments, acceptance and refunds separately.')
''',
'project-planning':'''from copy import deepcopy
cyclic=deepcopy(fixture)
cyclic['depends']['A']=['B']
try:
    run('project-planning',cyclic)
    raise AssertionError('Cycle was not detected')
except ValueError:
    print('Cycle rejected; no schedule fabricated.')
changed=deepcopy(fixture)
changed['duration']['A']=4
assert run('project-planning',changed)['project_days']==7
''',
'maths-workbench':'''overshoot=run('maths-workbench',{'start':0,'learning_rate':1.5})
assert overshoot['next_x']==9 and overshoot['loss_after']==36
stationary=run('maths-workbench',{'start':3,'learning_rate':0.25})
assert stationary['gradient']==0 and stationary['next_x']==3
print({'overshoot':overshoot,'stationary':stationary})
''',
'uncertainty-lab':'''changed=run('uncertainty-lab',{'values':[2,4,4,6,90]})
assert changed['mean']==21.2
print(changed)
print('The mean changed; this alone does not explain why the extreme value occurred.')
''',
'clustering-lab':'''from sklearn.cluster import KMeans
import numpy as np
points=np.array(fixture['points'],dtype=float)
checks=[]
for k in [2,3]:
    model=KMeans(n_clusters=k,random_state=7,n_init=10).fit(points)
    checks.append({'k':k,'inertia':float(model.inertia_),'labels':model.labels_.tolist()})
scaled=points*np.array([100,1])
checks.append({'scale':[100,1],'labels':KMeans(n_clusters=2,random_state=7,n_init=10).fit_predict(scaled).tolist()})
print(checks)
# A changed partition or unchanged partition is a result to explain, not evidence of human categories.
'''
}
for id,code in experiments.items():
 f=R/'curriculum/fixtures'/id;notebook=json.loads((f/'hosted-lab.ipynb').read_text())
 notebook['cells'] += [{'cell_type':'markdown','metadata':{},'source':['## Optional implementation experiment\nRun only in an authorised hosted runtime. Record installed versions. This is not a live provider benchmark.\n']},{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':[code]}]
 (f/'hosted-lab.ipynb').write_text(json.dumps(notebook,indent=2,ensure_ascii=False)+'\n')
 deps=(f/'requirements.txt').read_text()
 if 'sklearn' in code and 'scikit-learn' not in deps:deps+='scikit-learn>=1.6,<2\nnumpy>=2,<3\n'
 if 'import pandas' in code and 'pandas' not in deps:deps+='pandas>=2.2,<3\n'
 if 'import matplotlib' in code:deps+='matplotlib>=3.9,<4\n'
 (f/'requirements.txt').write_text(deps)
f=R/'curriculum/fixtures/api-integration'
(f/'bounded-client.mjs').write_text('''// Educational server/hosted-runtime example. No key is embedded and no request runs on import.
// Check current account/country eligibility first. Do not accept an endpoint from untrusted input.
const approved=new Set(['api.groq.com','api.cloudflare.com']);
export async function requestDraft({endpoint,headers={},body,fetcher=fetch,timeoutMs=8000}){
 const url=new URL(endpoint);
 if(url.protocol!=='https:'||!approved.has(url.hostname)||url.username||url.password||url.search)throw Error('Use an approved configured HTTPS endpoint without URL credentials.');
 if(!Number.isInteger(timeoutMs)||timeoutMs<1||timeoutMs>15000)throw Error('Bounded timeout required.');
 if(typeof body!=='object'||body===null)throw Error('JSON request body required.');
 const payload=JSON.stringify(body);if(payload.length>12000)throw Error('Request too large.');
 let response;try{response=await fetcher(url,{method:'POST',headers:{'Content-Type':'application/json',...headers},body:payload,signal:AbortSignal.timeout(timeoutMs),redirect:'error'})}catch{return {state:'unavailable'}}
 if(response.status===429)return {state:'quota_wait'};
 if(response.status===401||response.status===403)return {state:'stop_auth'};
 if(!response.ok)return {state:'unavailable'};
 const reader=response.body?.getReader();if(!reader)return {state:'schema_error'};
 const chunks=[];let size=0;
 for(;;){const {done,value}=await reader.read();if(done)break;size+=value.length;if(size>64000){await reader.cancel();return {state:'too_large'}}chunks.push(value)}
 const bytes=new Uint8Array(size);let offset=0;for(const part of chunks){bytes.set(part,offset);offset+=part.length}
 let parsed;try{parsed=JSON.parse(new TextDecoder().decode(bytes))}catch{return {state:'schema_error'}}
 const text=parsed?.choices?.[0]?.message?.content??parsed?.result?.response;
 return typeof text==='string'&&text.length>0?{state:'draft',text}:{state:'schema_error'};
}
''')
print('Built optional executable notebook extensions and a bounded, no-default-credentials API client.')
