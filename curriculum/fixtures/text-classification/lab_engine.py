"""Deterministic educational references; no live AI calls, credentials or network.
Run model exercises only in a permitted hosted runtime. Synthetic wiring tests are
not production benchmarks, independent assessment or real-world validation.
"""
import math,re,statistics,itertools,copy

def numeric(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def run(kind,d):
 if not isinstance(d,dict):raise ValueError('Input must be an object.')
 if kind in ['reproducible-cloud-lab','python-records','data-cleaning']:
  accepted=[];rejected=[];reasons=[];seen=set()
  for r in d['rows']:
   reason='duplicate_id' if r['id'] in seen else 'non_numeric' if not numeric(r.get('amount')) else 'negative_amount' if r['amount']<0 else None
   if reason:rejected.append(r['id']);reasons.append(reason)
   else:seen.add(r['id']);accepted.append(r)
  result={'accepted':len(accepted),'total':sum(r['amount'] for r in accepted)}
  result.update({'reasons':reasons} if kind=='data-cleaning' else {'rejected':rejected});return result
 if kind=='visual-brief':
  failed=[k for k,v in d['brief'].items() if d['candidate'].get(k)!=v];return {'passed':len(d['brief'])-len(failed),'failed':failed,'decision':'revise' if failed else 'approve_spec_only'}
 if kind=='measured-ml':
  truth,pred=d['truth'],d['predicted']
  if not truth or len(truth)!=len(pred) or any(x not in [0,1] for x in truth+pred):raise ValueError('Equal nonempty binary lists required.')
  correct=sum(a==b for a,b in zip(truth,pred));return {'correct':correct,'total':len(truth),'accuracy':round(correct/len(truth),6),'baseline_accuracy':max(truth.count(0),truth.count(1))/len(truth),'false_positive':sum(a==0 and b==1 for a,b in zip(truth,pred)),'false_negative':sum(a==1 and b==0 for a,b in zip(truth,pred))}
 if kind=='generative-workbench':
  scores={r['id']:int(r['facts'])+int(r['format'])+int(not r['invented_discount']) for r in d['candidates']};return {'scores':scores,'selected':max(scores,key=scores.get)}
 if kind=='evidence-assistant':
  answers=[]
  for q in d['questions']:
   source=q['evidence'] if q.get('evidence') in d['source'] else None;answers.append({'id':q['id'],'status':'supported' if source else 'unknown','citation':source})
  return {'answers':answers}
 if kind=='ai-fieldwork':
  manual=sum(d['manual_minutes']);assisted=sum(d['assisted_minutes'])+sum(d['checking_minutes']);saving=manual-assisted;return {'manual_total':manual,'assisted_total':assisted,'saved_minutes':saving,'claim':'no measured time saving' if saving==0 else 'observed sample only'}
 if kind=='faq-assistant':return {'routes':{m['id']:'draft_with_source' if m['type']=='known_faq' else 'human_review' for m in d['messages']},'automatic_actions':0}
 if kind=='data-report':
  cats={}
  for r in d['rows']:cats[r['category']]=cats.get(r['category'],0)+r['amount']
  return {'rows':len(d['rows']),'categories':cats,'total':sum(cats.values())}
 if kind=='algorithms-lab':
  values=d['values'];target=d['target']
  if values!=sorted(values):raise ValueError('Sorted values required for binary search.')
  count=0;idx=-1
  for i,v in enumerate(values):
   count+=1
   if v==target:idx=i;break
  lo,hi=0,len(values)-1;binary=0
  while lo<=hi:
   mid=(lo+hi)//2;binary+=1
   if values[mid]==target:break
   if values[mid]<target:lo=mid+1
   else:hi=mid-1
  return {'index':idx,'linear_comparisons':count,'binary_comparisons':binary}
 if kind=='constraint-planner':
  valid=[]
  for slots in itertools.permutations(d['slots'],len(d['tasks'])):
   plan=dict(zip(d['tasks'],slots))
   if plan['B']>plan['A'] and plan['C']!=1:valid.append(plan)
  return {'valid_schedules':len(valid),'selected':valid[0] if valid else None}
 if kind=='maths-workbench':
  x,rate=d['start'],d['learning_rate']
  if not numeric(x) or not numeric(rate) or rate<0:raise ValueError('Finite x and non-negative rate required.')
  g=2*(x-3);n=x-rate*g;return {'gradient':g,'next_x':n,'loss_before':(x-3)**2,'loss_after':(n-3)**2}
 if kind=='api-integration':
  result=[]
  for r in d['responses']:
   status,body=r['status'],r.get('body');result.append('accept_draft' if status==200 and isinstance(body,dict) and isinstance(body.get('text'),str) else 'schema_error' if status==200 else 'bounded_retry_later' if status==429 else 'stop_auth_error' if status in [401,403] else 'unavailable')
  return {'decisions':result}
 if kind=='augmentation-lab':
  before=copy.deepcopy(d['test']);aug=copy.deepcopy(d['train'])
  for row in d['train']:aug.append({**row,'id':row['id']+'-aug','parent':row['id'],'x':row['x']+0.01})
  return {'original_train':len(d['train']),'augmented_train':len(aug),'unchanged_test':before==d['test'],'unique_originals':len({x['id'] for x in d['train']})}
 if kind=='text-classification':
  labels=[]
  for text in d['texts']:
   tokens=set(re.findall(r'\b\w+\b',text.lower()));a,b='refund' in tokens,'broken' in tokens;labels.append('request' if a and not b else 'issue' if b and not a else 'review')
  return {'labels':labels,'review_count':labels.count('review')}
 if kind=='uncertainty-lab':
  v=d['values']
  if not v or not all(numeric(x) for x in v):raise ValueError('Finite nonempty observations required.')
  return {'count':len(v),'mean':statistics.mean(v),'minimum':min(v),'maximum':max(v),'range':max(v)-min(v)}
 if kind=='inventory-planning':
  if not d['demand'] or not all(numeric(x) and x>=0 for x in d['demand']):raise ValueError('Valid demand observations required.')
  f=statistics.mean(d['demand']);return {'forecast':f,'reorder':max(0,math.ceil(f+d['safety']-d['stock']))}
 if kind=='project-planning':
  finish={};visiting=set()
  def end(t):
   if t in finish:return finish[t]
   if t in visiting:raise ValueError('Dependency cycle.')
   visiting.add(t);v=d['duration'][t]+max([end(p) for p in d['depends'][t]] or [0]);visiting.remove(t);finish[t]=v;return v
  for t in d['duration']:end(t)
  return {'finish':finish,'project_days':max(finish.values(),default=0)}
 if kind=='supervised-lab':
  x,y=d['x'],d['y'];mx,my=statistics.mean(x),statistics.mean(y);den=sum((v-mx)**2 for v in x)
  if not den:raise ValueError('Slope undefined for equal x values.')
  slope=sum((a-mx)*(b-my) for a,b in zip(x,y))/den;intercept=my-slope*mx;pred=slope*d['test_x']+intercept
  return {'slope':slope,'intercept':intercept,'prediction':pred,'absolute_error':abs(d['test_y']-pred),'mean_baseline_error':abs(d['test_y']-my)}
 if kind=='preprocessing-lab':
  observed=[x for x in d['train'] if x is not None]
  if not observed or not all(numeric(x) for x in observed):raise ValueError('Training mean unavailable.')
  m=statistics.mean(observed);return {'training_mean':m,'train_filled':[m if x is None else x for x in d['train']],'test_filled':[m if x is None else x for x in d['test']]}
 if kind=='responsible-ai':
  groups={}
  for r in d['cases']:groups.setdefault(r['group'],[]).append(r['correct'])
  return {'group_accuracy':{k:sum(v)/len(v) for k,v in groups.items()},'release':'hold' if d['privacy_failure'] else 'review_residual_risks'}
 if kind=='time-experiment':
  m=sum(d['manual']);a=sum(d['draft'])+sum(d['check'])+sum(d['rework']);return {'manual_total':m,'assisted_total':a,'saved_minutes':m-a}
 if kind=='data-wrangling':
  total=0;missing=[]
  for r in d['orders']:
   if r['product'] not in d['prices']:missing.append(r['id'])
   else:total+=r['qty']*d['prices'][r['product']]
  return {'orders':len(d['orders']),'matched':len(d['orders'])-len(missing),'unmatched':missing,'known_total':total}
 if kind=='sklearn-lab':
  from sklearn.pipeline import make_pipeline
  from sklearn.preprocessing import StandardScaler
  from sklearn.linear_model import LogisticRegression
  model=make_pipeline(StandardScaler(),LogisticRegression(random_state=7));model.fit(d['train_x'],d['train_y']);pred=model.predict(d['test_x']).tolist();return {'predictions':pred,'correct':sum(a==b for a,b in zip(d['test_y'],pred)),'test_count':len(pred)}
 if kind=='pandas-cleaning':
  import pandas as pd
  frame=pd.DataFrame(d['rows']).drop_duplicates(subset=['id'],keep='first').copy();frame['units']=frame['units'].fillna(0);return {'rows':len(frame),'units':frame['units'].tolist(),'total':float(frame['units'].sum()),'outlier_retained':100 in frame['units'].values}
 if kind=='campaign-evidence':return {'ctr':d['clicks']/d['impressions'] if d['impressions'] else None,'cpc':d['spend']/d['clicks'] if d['clicks'] else None,'sales_lift':'not established'}
 if kind=='data-visualisation':
  failed=[]
  if d['chart']['axis_min']!=0:failed.append('axis_baseline')
  if not d['chart'].get('units'):failed.append('units')
  if not d['chart'].get('alt'):failed.append('text_alternative')
  return {'total':sum(d['values'].values()),'failed_checks':failed,'release':'revise' if failed else 'inspect_rendered_chart'}
 if kind=='clustering-lab':
  from sklearn.cluster import KMeans
  labels=KMeans(n_clusters=2,random_state=7,n_init=10).fit_predict(d['points']);groups={}
  for id,label in zip(d['ids'],labels):groups.setdefault(int(label),[]).append(id)
  members=sorted(sorted(v) for v in groups.values());return {'groups':members,'sizes':[len(v) for v in members]}
 if kind=='earn-by-doing':
  hours=d['delivery_hours']+d['selling_hours']+d['support_hours']
  if hours<=0:raise ValueError('Positive total hours required.')
  net=d['price']-d['tool_cost']-d['fees']-d.get('refund',0);return {'net_before_tax':net,'total_hours':hours,'effective_hourly_before_tax':net/hours}
 raise ValueError('Unknown reference project.')
