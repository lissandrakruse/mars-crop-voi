"""Reproduce using the three original XLSX files and IPK.csv in an input directory.
Usage: python analyze_vegetables.py INPUT_DIRECTORY OUTPUT_JSON
Source DOIs and experiment-level split are recorded in the output.
"""
import sys,json,hashlib
from pathlib import Path
import pandas as pd
import numpy as np

def run(root):
    rows=[]; summaries=[];hashes={}
    for exp in ['c','v1','v2']:
        p=next(root.rglob(f'*data_Exp_{exp}.xlsx'));hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
        climate=pd.read_excel(p,sheet_name='Greenhouse climate',usecols=range(5));climate.columns=['time','co2','temperature','humidity','radiation'];climate.time=pd.to_datetime(climate.time)
        for c in climate.columns[1:]:climate[c]=pd.to_numeric(climate[c],errors='coerce')
        g=pd.read_excel(p,sheet_name='Lettuce growth',header=1);g.iloc[:,0]=g.iloc[:,0].ffill();plants=pd.to_numeric(g.iloc[:,2],errors='coerce');g=g[plants.notna()].copy();g['date']=pd.to_datetime(g.iloc[:,0]);g['dry']=pd.to_numeric(g['Total dry weight [g]'],errors='coerce');g['fresh']=pd.to_numeric(g['Total fresh weight [g]'],errors='coerce');g['area']=pd.to_numeric(g['Leaf area [cm2]'],errors='coerce');g=g.dropna(subset=['dry'])
        # Destructive samples: plant numbers are NOT longitudinal identities.
        sam=g.groupby('date').agg(dry=('dry','mean'),fresh=('fresh','mean'),area=('area','mean'),n=('dry','count')).reset_index();start=climate.time.min();sam['age']=(sam.date-start.normalize()).dt.total_seconds()/86400
        summaries.append(dict(experiment=exp,climate_rows=len(climate),plant_observations=len(g),sampling_dates=len(sam),climate_missing=climate.iloc[:,1:].isna().sum().to_dict(),temperature_range=[float(climate.temperature.min()),float(climate.temperature.max())],humidity_range=[float(climate.humidity.min()),float(climate.humidity.max())],samples=json.loads(sam.to_json(orient='records',date_format='iso'))))
        for a,b in zip(sam.to_dict('records'),sam.to_dict('records')[1:]):
            sub=climate[(climate.time>=a['date'])&(climate.time<b['date'])];days=(b['date']-a['date']).days
            if len(sub)<days*288*.9 or days<=0:continue
            features=sub[['temperature','humidity','co2','radiation']].mean().to_numpy(float)
            if not np.isfinite(features).all():continue
            rows.append(dict(experiment=exp,age=float(a['age']),days=days,initial=a['dry'],observed=b['dry'],rate=float(np.log(b['dry']/a['dry'])/days),features=features.tolist()))
    train=[r for r in rows if r['experiment']=='c'];X=np.array([[r['age']]+r['features'] for r in train]);Y=np.array([r['rate'] for r in train]);scale=X.std(axis=0);scale[scale==0]=1
    # Fixed Gaussian kernel, no tuning using validation outcomes. Age baseline uses same kernel on age only.
    metrics=[];predictions=[]
    for exp in ['v1','v2']:
        test=[r for r in rows if r['experiment']==exp]
        for model in ['age_only','age_and_environment']:
            pred=[];obs=[]
            for r in test:
                x=np.array([r['age']]+r['features']);dims=1 if model=='age_only' else 5;d2=np.mean(((X[:,:dims]-x[:dims])/scale[:dims])**2,axis=1);w=np.exp(-.5*(d2-d2.min()));rate=float(w@Y/w.sum());p=float(r['initial']*np.exp(rate*r['days']));pred.append(p);obs.append(r['observed']);predictions.append(dict(experiment=exp,model=model,age=r['age'],days=r['days'],initial_g=r['initial'],observed_g=r['observed'],predicted_g=p,nearest_standardized_distance=float(np.sqrt(d2.min()))))
            err=np.array(pred)-obs;metrics.append(dict(experiment=exp,model=model,intervals=len(test),mae_g=float(np.mean(abs(err))),rmse_g=float(np.sqrt(np.mean(err**2)))))
    p=next(root.rglob('IPK.csv'));hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest();a=pd.read_csv(p)
    return dict(sources={'lettuce':'https://doi.org/10.17632/r7z9ttvkyh.2','arugula':'https://doi.org/10.17632/jbknff2kpv.1'},hashes=hashes,lettuce=summaries,metrics=metrics,predictions=predictions,training_intervals=len(train),arugula=dict(rows=len(a),columns=len(a.columns),accessions=a['Accession number'].nunique(),traits=len(a.columns)-4,total_fresh_weight_g=dict(min=float(a.TFW.min()),median=float(a.TFW.median()),max=float(a.TFW.max())),records=a[['Label','Accession number','TFW']].to_dict('records')),method='Exploratory retrospective interval prediction. Exp_c only for training and scaling. Fixed Gaussian bandwidth=1. Target: next sampling mean total dry weight g/plant, initialized with measured current mean. Features use climate observed during the interval; this is conditional reconstruction, not an advance weather forecast. All individual raw samples, excluding Average/SD rows and TOP12. No binary survival or Mars probability. Destructive samples and shared greenhouse conditions prevent interpreting plants/readings as independent experiments. Only two held-out experiments; no tuning on their outcomes; no causal claim.')
if __name__=='__main__':
    r=run(Path(sys.argv[1]));Path(sys.argv[2]).write_text(json.dumps(r,indent=2,allow_nan=False));print(json.dumps({'training_intervals':r['training_intervals'],'metrics':r['metrics'],'arugula':{k:v for k,v in r['arugula'].items() if k!='records'}},indent=2))
