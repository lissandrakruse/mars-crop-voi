"""Retrospective within-study substrate holdout; NOT external validation.
No target outcomes used in fitting; no environmental distances fitted or claimed.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import betabinom
p=Path(__file__).resolve().parent
d=pd.read_csv(p.parent/'data/wamelink2014_pots.csv');d['y']=(d.nAlive>=3).astype(int)
rows=[]
for target in ['Earth','Mars','Moon']:
 for species in sorted(d.Species.unique()):
  train=d[d.Species.eq(species)&d.Soil.ne(target)];test=d[d.Species.eq(species)&d.Soil.eq(target)]
  assert len(train)==40 and len(test)==20
  k=int(train.y.sum());kt=int(test.y.sum())
  for w in [0.,.1,.5,1.]:
   a=1+w*k;b=1+w*(40-k);prob=a/(a+b)
   lo,hi=betabinom.ppf([.025,.975],20,a,b)
   rows.append(dict(target_substrate=target,species=species,weight=w,source_pots=40,source_successes=k,target_pots=20,target_successes=kt,probability=prob,brier=float(np.mean((prob-test.y.to_numpy())**2)),logloss=float(-np.mean(test.y*np.log(prob)+(1-test.y)*np.log1p(-prob))),predictive_low=int(lo),predictive_high=int(hi),covered=bool(lo<=kt<=hi)))
r=pd.DataFrame(rows);r.to_csv(p/'substrate_holdout_cells.csv',index=False)
m=r.groupby(['target_substrate','weight']).agg(brier=('brier','mean'),logloss=('logloss','mean'),predictive_coverage=('covered','mean'),cells=('covered','size')).reset_index();m.to_csv(p/'substrate_holdout_metrics.csv',index=False)
a=r.groupby('weight').agg(brier=('brier','mean'),logloss=('logloss','mean'),predictive_coverage=('covered','mean')).reset_index();a.to_csv(p/'substrate_holdout_overall.csv',index=False)
# Identity: mean_w - 1/2 = w*(k-n/2)/(2+w*n). Same n and same w preserve ordering.
for n in [1,20,40]:
 for w in [.1,.5,1.]:
  means=(1+w*np.arange(n+1))/(2+w*n)
  assert np.all(np.diff(means)>0)
  assert np.allclose(means-.5,w*(np.arange(n+1)-n/2)/(2+w*n))
(p/'substrate_holdout_verification.json').write_text(json.dumps({'endpoint':'at least 3 living plants at day 50','design':'retrospective leave-one-entire-substrate-out within the same greenhouse study','source_pots_per_species':40,'target_pots_per_species':20,'species':14,'target_substrates':3,'weights':[0,.1,.5,1],'target_outcomes_used_in_fitting':False,'weight_selection_performed':False,'environmental_distance_evaluated':False,'external_validation':False,'warning':'Only three substrate domains; source and target share blocks and greenhouse. Coverage is descriptive across 42 cells. Weights are sensitivity settings, not estimated environmental responses.'},indent=2))
print(m.to_string(index=False));print(a.to_string(index=False))
