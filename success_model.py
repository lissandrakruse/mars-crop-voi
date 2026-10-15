"""Pot-level Bayesian establishment estimates from a published simulant trial.
Not calibrated to Mars. Beta posterior assumes exchangeable independent pots.
"""
from pathlib import Path
import math
import pandas as pd
from scipy.stats import beta
from scipy.special import digamma

DOI='https://doi.org/10.1371/journal.pone.0103138'
DATA=pd.read_csv(Path(__file__).parent/'data/wamelink2014_pots.csv')
DATA.columns=DATA.columns.str.strip()
SPECIES={'S. lycopersicum':'Tomato','D. carota':'Carrot','L. sativum':'Garden cress','S. cereale':'Rye'}
ENDPOINTS={'alive50':('nAlive','Alive at day 50'), 'germinated':('nGerminated','Germinated by day 50'), 'flowered':('nFlowers','Flower/bud formation by day 50')}

def posterior(k,n,prior=1.):
    a=prior+k;b=prior+n-k
    mean=a/(a+b);ci=beta.ppf([.025,.975],a,b)
    entropy=lambda p: -p*math.log(p)-(1-p)*math.log(1-p) if 0<p<1 else 0.
    expected_binary_entropy=float(digamma(a+b+1)-(a*digamma(a+1)+b*digamma(b+1))/(a+b))
    ig=(entropy(mean)-expected_binary_entropy)/math.log(2)
    return dict(successes=int(k),pots=int(n),observed_rate=k/n,alpha=a,beta=b,
                posterior_mean=mean,credible95=[float(ci[0]),float(ci[1])],
                expected_information_next_pot_bits=max(0.,ig))

def estimate(species='S. lycopersicum',endpoint='alive50',minimum=3,transfer=None):
    if species not in SPECIES:raise ValueError('Select a studied food crop')
    if endpoint not in ENDPOINTS:raise ValueError('Unknown endpoint')
    if isinstance(minimum,bool) or int(minimum)!=minimum or not 1<=int(minimum)<=5:raise ValueError('Minimum plants must be an integer from 1 to 5')
    minimum=int(minimum)
    if transfer is not None and (not math.isfinite(float(transfer)) or not 0<=float(transfer)<=1):raise ValueError('Transfer factor must be between 0 and 1')
    column,label=ENDPOINTS[endpoint];results={}
    for soil in ['Mars','Earth','Moon']:
        subset=DATA[(DATA.Species==species)&(DATA.Soil==soil)]
        if len(subset)!=20 or subset.Block.nunique()!=20:raise ValueError('Unexpected experimental design')
        vals=subset[column]
        if vals.isna().any() or not vals.between(0,5).all():raise ValueError('Invalid outcome values')
        k=int(vals.ge(minimum).sum());p=posterior(k,len(subset))
        p['jeffreys_prior_sensitivity']=posterior(k,len(subset),.5)['posterior_mean']
        p['seed_counts_descriptive_only']=int(vals.sum());results[soil]=p
    source=results['Mars'];projection=None
    if transfer is not None:
        q=float(transfer)
        projection=dict(status='ASSUMPTION-BASED, NOT VALIDATED ON MARS',transfer_factor=q,
            assumed_mean=q*source['posterior_mean'],
            conditional_credible95=[q*v for v in source['credible95']],
            formula='p_target = q * p_simulant',
            meaning='q is an assumed probability of avoiding additional mission-related failure given simulant success; the source data do not estimate q.',
            caveat='Interval conditions on fixed q and excludes uncertainty in transport, gravity, radiation, pressure, actual regolith and mission operations. This assumes additional stressors can only reduce source success.')
    return dict(species=species,crop=SPECIES[species],endpoint=endpoint,criterion=f'At least {minimum} of 5 plants per pot: {label.lower()}',
        horizon_days=50,minimum=minimum,results=results,mars_projection=projection,
        source_pots=[dict(block=int(row.Block),pot=int(row.Number),count=int(row[column]),success=bool(row[column]>=minimum)) for _,row in DATA[(DATA.Species==species)&(DATA.Soil=='Mars')].sort_values('Block').iterrows()],
        actual_mars_probability='NOT IDENTIFIED FROM AVAILABLE DATA',
        target_scope='A pot under the source greenhouse protocol with the selected simulant, seed material and success definition; not a whole harvest or mission.',
        prior='Beta(1,1), chosen uniform prior; sensitivity to Beta(0.5,0.5) reported',
        method='Binomial likelihood on 20 pot-level binary outcomes; Beta posterior. 95% equal-tailed credible interval.',
        study=dict(doi=DOI,supplement='Table S2',year=2014,conditions='Earth greenhouse; 50 days; five seeds per pot; study watering protocol; no added nutrient treatment',
            simulant='JSC-1A Mars regolith simulant as identified by the study',
            design='One study; 20 blocks, one pot per species/substrate in each block'),
        limitations=['Not validated on Mars or across independent studies','Exchangeable independent-pot model; residual block/greenhouse dependence is not modeled',
                    'No edible-yield, nutrition, toxicity, or food-safety endpoint','Simulant composition differs from actual regolith',
                    'No calibrated response surface for changing temperature, pH, irrigation or nutrients'])

def ranking(endpoint='alive50',minimum=3):
    out=[]
    for species in SPECIES:
        d=estimate(species,endpoint,minimum)
        out.append(dict(species=species,crop=d['crop'],**d['results']['Mars']))
    return sorted(out,key=lambda r:r['posterior_mean'],reverse=True)
