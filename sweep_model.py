"""Exploratory greenhouse scenario sweep. Optimization is descriptive, in-sample."""
import math
import numpy as np
from scenario_model import CROP,solve_bounds

def sweep(ph=7.7,ph_tolerance=.5):
    ph=float(ph);ph_tolerance=float(ph_tolerance)
    if not math.isfinite(ph) or not math.isfinite(ph_tolerance) or not 0<=ph<=14 or not 0<ph_tolerance<=14:raise ValueError('Invalid pH or window')
    # Declared exploration grid, not a recommended greenhouse operating envelope.
    temps=sorted(set(list(np.arange(10.,36.,1.))+[21.1]))
    humidities=list(np.arange(20.,96.,5.))
    rows=[]
    for label,g in CROP.groupby('label'):
        p=g.ph.between(ph-ph_tolerance,ph+ph_tolerance).to_numpy()
        t=g.temperature.to_numpy();h=g.humidity.to_numpy()
        base=int((p&(np.abs(t-21.1)<=5)&(np.abs(h-65)<=15)).sum())
        options=[]
        for tc in temps:
            for hc in humidities:
                matches=int((p&(np.abs(t-tc)<=5)&(np.abs(h-hc)<=15)).sum())
                options.append((matches,tc,hc))
        maximum=max(v[0] for v in options)
        # Ties favor proximity to the original scenario, then stable coordinates.
        best=min((v for v in options if v[0]==maximum),key=lambda v:(((v[1]-21.1)/5)**2+((v[2]-65)/15)**2,v[1],v[2]))
        bounds=None
        if maximum==0:tc=hc=None
        else:
            _,tc,hc=best
            obs=np.column_stack([(np.abs(t-tc)<=5).astype(float),p.astype(float),(np.abs(h-hc)<=15).astype(float)])
            full,pruned,agree,joint=solve_bounds(obs,2)
            assert agree
            bounds={'lower':pruned['history'][-1]['lower'],'upper':pruned['history'][-1]['upper'],'equivalent_bounds':agree}
        rows.append(dict(crop=label,baseline_matching_rows=base,best_matching_rows=maximum,
            added_matching_rows=maximum-base,dataset_rows=len(g),ph_matching_rows=int(p.sum()),
            best_temperature_c=tc,best_humidity_percent=hc,
            temperature_window_c=[tc-5,tc+5] if tc is not None else None,
            humidity_window_percent=[max(0,hc-15),min(100,hc+15)] if hc is not None else None,
            best_scenario_lp=bounds,newly_matched=bool(base==0 and maximum>0)))
    rows.sort(key=lambda v:(-v['best_matching_rows'],v['crop']))
    return dict(rows=rows,ph_window=[ph-ph_tolerance,ph+ph_tolerance],
        temperature_centers=temps,humidity_centers=humidities,scenario_count=len(temps)*len(humidities),
        matching_crops_baseline=sum(v['baseline_matching_rows']>0 for v in rows),
        matching_crops_sweep=sum(v['best_matching_rows']>0 for v in rows),
        interpretation='Best observed joint-overlap count over the declared grid for each crop. In-sample exploratory search, not plant tolerance, out-of-sample validation, or success on Mars.',
        tie_rule='Closest standardized distance to 21.1 C / 65% RH, then lower coordinates',
        caution='Different crops can have different best scenarios. Counts cannot be pooled as if one greenhouse setting matches every crop. NPK/salinity/mission conditions remain unlinked.')
