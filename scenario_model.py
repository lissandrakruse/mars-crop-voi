"""Independent LP bounds and endpoint-witness pruning for joint Crop overlap.
The event is measured environmental overlap, never biological cultivation success.
"""
from itertools import product,combinations
from pathlib import Path
import math
import numpy as np
import pandas as pd
from scipy.optimize import linprog
CROP=pd.read_csv(Path(__file__).parent/'data/Crop_recommendation.csv')
FEATURES=['temperature','ph','humidity']
WORLD=np.array(list(product([0.,1.],repeat=3)))
OBJECTIVE=np.prod(WORLD,axis=1)

def solve_bounds(observations,budget=2):
    base_A=[np.ones(8)]+[WORLD[:,i] for i in range(3)]
    base_b=[1.]+observations.mean(axis=0).tolist()
    candidates=[]
    for i,j in combinations(range(3),2):
        candidates.append((FEATURES[i]+' & '+FEATURES[j],WORLD[:,i]*WORLD[:,j],float((observations[:,i]*observations[:,j]).mean())))
    def run(prune):
        A=list(base_A);b=list(base_b);pool=list(candidates);calls=0;skips=0
        def lp(a,bb,sign):
            nonlocal calls
            calls+=1;r=linprog(sign*OBJECTIVE,A_eq=np.array(a),b_eq=np.array(bb),bounds=(0,None),method='highs')
            if not r.success:raise ValueError('Infeasible empirical constraints')
            return float(OBJECTIVE@r.x),r.x
        lower,xl=lp(A,b,1);upper,xu=lp(A,b,-1)
        history=[dict(step=0,lower=max(0.,lower),upper=min(1.,upper),width=upper-lower,selected='marginals')]
        for step in range(1,budget+1):
            trial=[]
            for name,row,value in pool:
                if prune and abs(row@xl-value)<=1e-8:l,xxl=lower,xl;skips+=1
                else:l,xxl=lp(A+[row],b+[value],1)
                if prune and abs(row@xu-value)<=1e-8:u,xxu=upper,xu;skips+=1
                else:u,xxu=lp(A+[row],b+[value],-1)
                trial.append((u-l,name,row,value,l,u,xxl,xxu))
            _,name,row,value,lower,upper,xl,xu=min(trial,key=lambda t:(round(t[0],10),t[1]))
            A.append(row);b.append(value);pool=[c for c in pool if c[0]!=name]
            history.append(dict(step=step,lower=max(0.,lower),upper=min(1.,upper),width=upper-lower,selected=name))
        return dict(history=history,solver_calls=calls,pruned_endpoint_solves=skips)
    full=run(False);pruned=run(True)
    agree=all(abs(a[k]-b[k])<1e-7 for a,b in zip(full['history'],pruned['history']) for k in ['lower','upper'])
    joint=float(np.prod(observations,axis=1).mean())
    for h in pruned['history']:
        if not h['lower']-1e-7<=joint<=h['upper']+1e-7:raise ValueError('Empirical joint outside LP bounds')
    return full,pruned,agree,joint

def scenario(temperature=21.1,ph=7.7,humidity=65.,temperature_tolerance=5.,ph_tolerance=.5,humidity_tolerance=15.,budget=2):
    inputs=[temperature,ph,humidity,temperature_tolerance,ph_tolerance,humidity_tolerance]
    try:inputs=list(map(float,inputs))
    except (ValueError,TypeError):raise ValueError('Scenario inputs must be numeric')
    if not all(math.isfinite(v) for v in inputs):raise ValueError('Scenario must contain finite values')
    t,p,h,tt,pt,ht=inputs
    if not -100<=t<=100 or not 0<=p<=14 or not 0<=h<=100:raise ValueError('Scenario value outside allowed range')
    if not 0<tt<=50 or not 0<pt<=14 or not 0<ht<=100:raise ValueError('Window widths must be positive and within limits')
    if isinstance(budget,bool) or not isinstance(budget,int) or not 0<=budget<=3:raise ValueError('Budget must be an integer from 0 to 3')
    center=np.array([t,p,h]);tol=np.array([tt,pt,ht]);rows=[]
    for label,g in CROP.groupby('label'):
        obs=(np.abs(g[FEATURES].to_numpy()-center)<=tol).astype(float)
        full,pruned,agree,joint=solve_bounds(obs,budget)
        last=pruned['history'][-1]
        outside=[f for f in FEATURES if center[FEATURES.index(f)]<g[f].min() or center[FEATURES.index(f)]>g[f].max()]
        rows.append(dict(crop=label,lower=last['lower'],upper=last['upper'],width=last['width'],
            empirical_joint=joint,matching_rows=int(np.prod(obs,axis=1).sum()),dataset_rows=len(g),
            marginal_overlap=dict(zip(FEATURES,obs.mean(axis=0).tolist())),
            full=full,pruned=pruned,equivalent_bounds=agree,
            solver_calls_saved=full['solver_calls']-pruned['solver_calls'],
            center_outside_observed_ranges=outside,
            actual_mars_success_bounds=[0.,1.],
            evidence_link_to_cultivation_success='UNAVAILABLE: no matching experimental outcome labels'))
    rows.sort(key=lambda r:(-r['lower'],-r['upper'],r['crop']))
    return dict(rows=rows,scenario=dict(zip(FEATURES,center.tolist())),windows=dict(zip(FEATURES,tol.tolist())),budget=budget,
        modeled_event='A randomly selected terrestrial Crop row for this crop lies inside all three scenario windows.',
        interpretation='Partial-identification bounds from empirical marginals and selected pairwise constraints; not success probabilities or biological tolerance limits.',
        all_bounds_agree=all(r['equivalent_bounds'] for r in rows),
        solver_calls_full=sum(r['full']['solver_calls'] for r in rows),
        solver_calls_pruned=sum(r['pruned']['solver_calls'] for r in rows),
        soil_evidence=dict(ph='Phoenix 7.7 +/-0.5 is an optional site-specific reference; scenario pH is editable',
            NPK='Not integrated: plant-available fractions and analytical units are not harmonized',
            salinity='Not integrated: no matched Crop electrical-conductivity feature',
            APXS='Real bulk chemistry shown as context; no conversion to available fertilizer'),
        mars_cultivation_success='NOT IDENTIFIED: [0,1] without additional response/transfer assumptions',
        method='Finite-world LP (8 worlds), greedy pairwise-constraint selection by immediate width reduction, endpoint-witness pruning; independently implemented, not verified as an exact reproduction of earlier work.')
