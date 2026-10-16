"""Retrospective two-fold blocked calibration experiment; not external validation.
Established conjugate mixture method; not a new statistical invention.
"""
from pathlib import Path
import numpy as np,pandas as pd,json
from scipy.special import betaln,expit
p=Path(__file__).resolve().parent
d=pd.read_csv(p.parent/'data/wamelink2014_pots.csv');d['y']=(d.nAlive>=3).astype(int)
rows=[];weights=[]
for parity in [0,1]:
 train=d[d.Block%2==parity];test=d[d.Block%2!=parity]
 assert len(train)==len(test)==420
 for target in ['Earth','Mars','Moon']:
  for species in sorted(d.Species.unique()):
   source=train[train.Species.eq(species)&train.Soil.ne(target)]
   cal=train[train.Species.eq(species)&train.Soil.eq(target)]
   val=test[test.Species.eq(species)&test.Soil.eq(target)]
   ns=len(source);ks=int(source.y.sum());nc=len(cal);kc=int(cal.y.sum())
   assert (ns,nc,len(val))==(20,10,10)
   predictions={'target_only':(1+kc)/(2+nc)}
   for w in [.1,.5,1.]:predictions['fixed_'+str(w)]=(1+w*ks+kc)/(2+w*ns+nc)
   for pi in [.1,.5,.9]:
    # Calibrating counts update mixture membership using only training blocks.
    a=1+ks;b=1+ns-ks
    lm1=betaln(a+kc,b+nc-kc)-betaln(a,b)
    lm0=betaln(1+kc,1+nc-kc)-betaln(1,1)
    rho=float(expit(np.log(pi/(1-pi))+lm1-lm0))
    pred=rho*(a+kc)/(a+b+nc)+(1-rho)*(1+kc)/(2+nc)
    predictions['mixture_'+str(pi)]=pred
    weights.append(dict(fold=parity,target=target,species=species,prior_mass=pi,posterior_source_mass=rho,source_successes=ks,calibration_successes=kc))
   for method,prob in predictions.items():
    for _,v in val.iterrows():rows.append(dict(fold=parity,pot=int(v.Number),block=int(v.Block),target=target,species=species,method=method,y=int(v.y),p=prob,brier=float((prob-v.y)**2),logloss=float(-v.y*np.log(prob)-(1-v.y)*np.log1p(-prob))))
r=pd.DataFrame(rows);assert r.groupby('method').size().eq(840).all();assert r.groupby(['method','pot']).size().eq(1).all()
r.to_csv(p/'calibrated_predictions.csv',index=False)
m=r.groupby(['target','method'])[['brier','logloss']].mean().reset_index();m.to_csv(p/'calibrated_metrics.csv',index=False)
o=r.groupby('method')[['brier','logloss']].mean().reset_index();o.to_csv(p/'calibrated_overall.csv',index=False)
pd.DataFrame(weights).to_csv(p/'calibrated_mixture_weights.csv',index=False)
(p/'calibrated_verification.json').write_text(json.dumps({'folds':2,'split':'odd versus even source-study blocks; roles swapped','source_pots_per_prediction':20,'target_calibration_pots':10,'test_pots_per_species_target_fold':10,'scored_pots_per_method':840,'target_test_outcomes_used_in_fitting':False,'fixed_discounts':[.1,.5,1.],'mixture_prior_masses':[.1,.5,.9],'main_mixture_prior_mass':.5,'main_mixture_chosen_before_this_script_was_run':True,'retrospective_analysis':True,'external_validation':False,'environmental_kernel_tested':False,'note':'All methods have identical target calibration data. Blocks held out simultaneously across every substrate. No hyperparameter optimized on heldout outcomes; no CI treating two folds or pots as independent environments.'},indent=2))
print(m.to_string(index=False));print(o.to_string(index=False))
