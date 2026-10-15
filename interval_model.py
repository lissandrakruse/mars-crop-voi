"""Independent finite-world interval queries; not Mars cultivation probabilities."""
from itertools import product, combinations
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from pathlib import Path

DATA = pd.read_csv(Path(__file__).parent/'data/Crop_recommendation.csv')
WORLDS = np.array(list(product([0.,1.],repeat=4)))

def analyze(crop, temperature, humidity, ph, budget=6):
    if crop not in set(DATA.label): raise ValueError('Unknown crop')
    values=np.array([temperature,humidity,ph],float)
    if not np.isfinite(values).all() or not 0<=humidity<=100 or not 0<=ph<=14:
        raise ValueError('Invalid environmental values')
    budget=int(budget)
    if not 1<=budget<=10: raise ValueError('Budget must be between 1 and 10')
    # Explicit windows, not physiological tolerances or calibrated uncertainties.
    tolerances=np.array([5.,15.,1.])
    e=(np.abs(DATA[['temperature','humidity','ph']].to_numpy()-values)<=tolerances).astype(float)
    observations=np.column_stack([DATA.label.eq(crop).astype(float),e])
    evidence=np.prod(e,axis=1)
    support=int(evidence.sum()); denominator=float(evidence.mean())
    if support==0:
        return {'status':'unsupported','message':'No terrestrial observations in this joint window. Query withheld.','support':0}
    evidence_world=np.prod(WORLDS[:,1:],axis=1)
    objective=WORLDS[:,0]*evidence_world/denominator
    base_A=[np.ones(16),evidence_world];base_b=[1.,denominator]
    candidates=[]
    for degree in [1,2,3]:
        for subset in combinations(range(4),degree):
            if subset==(1,2,3): continue
            row=np.prod(WORLDS[:,subset],axis=1)
            value=float(np.prod(observations[:,subset],axis=1).mean())
            name=' & '.join(['crop','temperature window','humidity window','pH window'][j] for j in subset)
            candidates.append((name,row,value))
    def run(prune):
        A=list(base_A); b=list(base_b); pool=list(candidates);calls=0;skips=0
        def solve(a,bb,sign):
            nonlocal calls
            calls+=1
            r=linprog(sign*objective,A_eq=np.array(a),b_eq=np.array(bb),bounds=(0,None),method='highs')
            if not r.success: raise ValueError('Infeasible constraint set: '+r.message)
            return float(objective@r.x),r.x
        lower,xl=solve(A,b,1);upper,xu=solve(A,b,-1)
        history=[dict(step=0,lower=lower,upper=upper,width=upper-lower,selected='initial constraints')]
        for step in range(1,min(budget,len(pool))+1):
            options=[]
            for name,row,value in pool:
                if prune and abs(row@xl-value)<=1e-8: l,xxl=lower,xl;skips+=1
                else:l,xxl=solve(A+[row],b+[value],1)
                if prune and abs(row@xu-value)<=1e-8:u,xxu=upper,xu;skips+=1
                else:u,xxu=solve(A+[row],b+[value],-1)
                options.append((u-l,name,row,value,l,u,xxl,xxu))
            # Both versions use identical stable tie-breaking; numerical rounding only for ordering.
            best=min(options,key=lambda z:(round(z[0],10),z[1]))
            _,name,row,value,lower,upper,xl,xu=best
            A.append(row);b.append(value);pool=[c for c in pool if c[0]!=name]
            history.append(dict(step=step,lower=lower,upper=upper,width=upper-lower,selected=name))
        return dict(history=history,solver_calls=calls,pruned_endpoint_solves=skips)
    full=run(False);pruned=run(True)
    equivalent=all(abs(a[k]-b[k])<1e-7 for a,b in zip(full['history'],pruned['history']) for k in ['lower','upper'])
    return dict(status='ok',crop=crop,support=support,n=len(DATA),empirical_conditional=float(observations[evidence==1,0].mean()),
        window_half_widths=dict(temperature=5,humidity=15,ph=1),full=full,pruned=pruned,equivalent_bounds=equivalent,
        solver_calls_saved=full['solver_calls']-pruned['solver_calls'],
        interpretation='Empirical terrestrial crop-label probability conditional on the joint window. Not germination, yield, or Mars survival.',
        method='Greedy constraint selection by immediate interval-width reduction; finite-world linear programming with endpoint-witness pruning.',
        limitations=['Plug-in frequencies, not confidence intervals','Retrospective constraint revelation, not prospective experiment outcomes',
        'No decision utility or costs: not rigorous VOI','APXS is not used as plant-available NPK','No exact reproduction of the previous unavailable implementation is claimed'])
