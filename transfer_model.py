"""Explicit hypothesis: similarity-discounted outcome evidence.
No species substitution, no learned calibration, no validated Mars probability.
"""
import math
import numpy as np
from scipy.stats import beta
from success_model import estimate,SPECIES
from scenario_model import CROP

def transfer(crop='lentil',temperature=21.1,ph=7.7,humidity=65.,temperature_scale=5.,ph_scale=.5,humidity_scale=15.,endpoint='alive50',minimum=3,successes=None,trials=None,reference_temperature=None,reference_ph=None,reference_humidity=None):
    known=set(CROP.label)|set(SPECIES)
    if crop not in known:raise ValueError('Unknown crop or studied species')
    target=np.array([temperature,ph,humidity],dtype=float);scale=np.array([temperature_scale,ph_scale,humidity_scale],dtype=float)
    if not np.isfinite(target).all() or not np.isfinite(scale).all() or not (scale>0).all() or not 0<=target[1]<=14 or not 0<=target[2]<=100:raise ValueError('Invalid target or distance scales')
    # Similarity to Crop is returned for selection only; labels are not outcomes.
    label_rows=CROP[CROP.label.eq(crop)]
    compatibility=None
    if len(label_rows):
        x=label_rows[['temperature','ph','humidity']].to_numpy()
        sim=np.exp(-.5*np.mean(((x-target)/scale)**2,axis=1))
        compatibility=dict(mean_kernel_similarity=float(sim.mean()),rows=len(x),interpretation='Mean feature similarity, NOT a success probability')
    if successes is not None or trials is not None:
        if successes is None or trials is None:raise ValueError('Provide both successes and trials')
        k=float(successes);n=float(trials)
        if not math.isfinite(k+n) or not k.is_integer() or not n.is_integer() or not 0<=k<=n or n<1 or n>100000:raise ValueError('Invalid experimental counts')
        if None in [reference_temperature,reference_ph,reference_humidity]:raise ValueError('Experimental reference conditions are required')
        ref=np.array([reference_temperature,reference_ph,reference_humidity],float)
        source='User-supplied experimental counts; not verified by this application'
    elif crop in SPECIES:
        e=estimate(crop,endpoint,int(minimum));r=e['results']['Mars'];k=r['successes'];n=r['pots']
        ref=np.array([21.1,7.3,65.])
        source='Wamelink et al. 2014, Mars-simulant pot outcomes; source pH 7.3 as reproduced in NASA BVAD table'
    else:
        return dict(status='outcome_data_required',crop=crop,compatibility=compatibility,
            reason='No same-crop success/failure observations are included. Crop labels cannot serve as outcome labels; experiments from another species are not substituted.',
            required=['Successful and unsuccessful independent experimental units for this crop','Same success criterion/horizon','Reference temperature, substrate pH and air humidity','Substrate/treatment and measurement-method comparability'],
            actual_mars_probability=None)
    if not np.isfinite(ref).all() or not 0<=ref[1]<=14 or not 0<=ref[2]<=100:raise ValueError('Invalid reference conditions')
    distance_squared=float(np.mean(((ref-target)/scale)**2));weight=math.exp(-.5*distance_squared)
    if weight<.1:return dict(status='outside_transfer_support',crop=crop,similarity_weight=weight,compatibility=compatibility,actual_mars_probability=None,reason='Similarity weight below the declared 0.1 abstention threshold; numerical target estimate withheld.')
    a=1.+weight*k;b=1.+weight*(n-k);ci=beta.ppf([.025,.975],a,b)
    sensitivity=[]
    for mult in [.5,1.,2.]:
        w=math.exp(-.5*distance_squared/mult**2);aa=1+w*k;bb=1+w*(n-k)
        sensitivity.append(dict(scale_multiplier=mult,weight=w,effective_trials=w*n,conditional_mean=aa/(aa+bb)))
    return dict(status='hypothesis_estimate',crop=crop,source=source,reference=dict(zip(['temperature','ph','humidity'],ref.tolist())),target=dict(zip(['temperature','ph','humidity'],target.tolist())),
        compatibility=compatibility,successes=int(k),trials=int(n),similarity_weight=weight,effective_trials=weight*n,
        conditional_mean=a/(a+b),conditional_credible95=list(map(float,ci)),alpha=a,beta=b,sensitivity=sensitivity,
        actual_mars_probability=None,calibration_status='NOT EMPIRICALLY CALIBRATED OR VALIDATED FOR MARS',
        assumptions=['Same crop and outcome definition','Environmentally similar source and target share an outcome parameter after discounting','Distance scales and kernel are assumptions, not fitted response curves','Other soil properties and mission effects are unresolved'],
        formula='w=exp(-0.5*mean(((x_target-x_reference)/scale)^2)); theta_target|D,assumptions ~ Beta(1+w*k,1+w*(n-k))',
        interpretation='A hypothesis-based power-prior posterior; the interval excludes uncertainty in the transfer assumptions. It is not a calibrated chance of success on actual Mars.')
