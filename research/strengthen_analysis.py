"""Within-study blocked analyses. No external or spaceflight validation."""
from pathlib import Path
import json, sys
import numpy as np
import pandas as pd
from scipy.stats import binomtest
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
font_path=Path('/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf')
if font_path.exists(): font_manager.fontManager.addfont(str(font_path))
plt.rcParams.update({'font.family':'Nimbus Sans','font.size':10,'axes.titlesize':11,'axes.labelsize':10,'ps.fonttype':3})
p=Path(__file__).resolve().parent
(p/'figures').mkdir(exist_ok=True)
d=pd.read_csv(p.parent/'data/wamelink2014_pots.csv')
d['y']=(d.nAlive>=3).astype(int)
assert len(d)==840 and not d.duplicated(['Block','Species','Soil']).any()
assert d.groupby('Block').size().eq(42).all()
rng=np.random.default_rng(20261016);B=20000
blocks=sorted(d.Block.unique());idx=rng.integers(0,20,size=(B,20))
names={'S. lycopersicum':'Tomato','D. carota':'Carrot','L. sativum':'Garden cress','S. cereale':'Rye'}
out=[]
for sp,name in names.items():
 a=d[d.Species.eq(sp)].pivot(index='Block',columns='Soil',values='y').loc[blocks]
 for comparator in ['Earth','Moon']:
  diff=(a.Mars-a[comparator]).to_numpy();bs=diff[idx].mean(1)
  n10=int(((a.Mars==1)&(a[comparator]==0)).sum());n01=int(((a.Mars==0)&(a[comparator]==1)).sum())
  pv=binomtest(n10,n10+n01,.5).pvalue if n10+n01 else 1.
  lo,hi=np.quantile(bs,[.025,.975])
  out.append(dict(crop=name,contrast='Mars minus '+comparator,paired_difference=float(diff.mean()),bootstrap_low=float(lo),bootstrap_high=float(hi),mars_only=n10,comparator_only=n01,exact_p=float(pv)))
r=pd.DataFrame(out)
# Holm family correction over eight retrospectively declared contrasts in this secondary analysis.
order=np.argsort(r.exact_p.to_numpy());adj=np.maximum.accumulate(np.minimum(1,(8-np.arange(8))*r.exact_p.to_numpy()[order]));r['holm_p']=0.
r.loc[order,'holm_p']=adj;r.to_csv(p/'paired_substrate_contrasts.csv',index=False)
# All species included to expose selection in four-crop illustrations.
allcells=d.groupby(['Species','Soil']).agg(successes=('y','sum'),pots=('y','size')).reset_index();allcells.to_csv(p/'all_species_counts.csv',index=False)
pred=[]
for b in blocks:
 train=d[d.Block.ne(b)];test=d[d.Block.eq(b)]
 for _,row in test.iterrows():
  bycell=train[train.Species.eq(row.Species)&train.Soil.eq(row.Soil)].y
  bycrop=train[train.Species.eq(row.Species)].y
  bysoil=train[train.Soil.eq(row.Soil)].y
  for method,x in [('crop_and_substrate',bycell),('crop_only',bycrop),('substrate_only',bysoil)]:
   prob=(x.sum()+1)/(len(x)+2)
   pred.append(dict(block=int(b),pot=int(row.Number),species=row.Species,substrate=row.Soil,y=int(row.y),method=method,p=float(prob),brier=float((prob-row.y)**2),logloss=float(-row.y*np.log(prob)-(1-row.y)*np.log1p(-prob))))
o=pd.DataFrame(pred);o.to_csv(p/'blocked_oof_predictions.csv',index=False)
assert len(o)==2520 and o.groupby(['pot','method']).size().eq(1).all()
metrics=[];diffs=[]
for scope,sp in [('all_14',None),('selected_4',list(names))]:
 x=o if sp is None else o[o.species.isin(sp)]
 q=x.groupby(['block','method'])[['brier','logloss']].mean()
 for method in x.method.unique():
  z=q.xs(method,level='method').loc[blocks]
  vals=z.brier.to_numpy();lo,hi=np.quantile(vals[idx].mean(1),[.025,.975])
  metrics.append(dict(scope=scope,method=method,brier=float(vals.mean()),brier_low=float(lo),brier_high=float(hi),logloss=float(z.logloss.mean())))
 for method in ['crop_only','substrate_only']:
  delta=(q.xs('crop_and_substrate',level='method').loc[blocks].brier-q.xs(method,level='method').loc[blocks].brier).to_numpy()
  lo,hi=np.quantile(delta[idx].mean(1),[.025,.975])
  diffs.append(dict(scope=scope,contrast='crop_and_substrate minus '+method,delta_brier=float(delta.mean()),low=float(lo),high=float(hi)))
m=pd.DataFrame(metrics);m.to_csv(p/'blocked_cv_metrics.csv',index=False);pd.DataFrame(diffs).to_csv(p/'blocked_cv_differences.csv',index=False)
fig,ax=plt.subplots(figsize=(6.3,4.6))
for j,comp in enumerate(['Earth','Moon']):
 q=r[r.contrast.eq('Mars minus '+comp)];yy=np.arange(4)+(j-.5)*.18
 ax.errorbar(q.paired_difference,yy,xerr=[q.paired_difference-q.bootstrap_low,q.bootstrap_high-q.paired_difference],fmt='o',capsize=3,label='Mars simulant minus '+comp)
ax.axvline(0,color='gray',linewidth=.8);ax.set(yticks=range(4),yticklabels=list(names.values()),xlabel='Difference in qualifying-pot proportion',title='Paired by experimental block');ax.invert_yaxis();ax.legend(fontsize=10);fig.tight_layout();fig.savefig(p/'figures/Figure4.png',dpi=300);fig.savefig(p/'figures/FugantiFig4.eps',dpi=1200);plt.close(fig)
fig,ax=plt.subplots(figsize=(6.3,3.8));q=m[m.scope.eq('all_14')]
ax.errorbar(q.brier,np.arange(3),xerr=[q.brier-q.brier_low,q.brier_high-q.brier],fmt='o',capsize=4)
ax.set(yticks=range(3),yticklabels=['Crop and substrate','Crop only','Substrate only'],xlabel='Held-out Brier score; lower is better',title='Leave one complete block out, all 14 species');ax.invert_yaxis();fig.tight_layout();fig.savefig(p/'figures/Figure5.png',dpi=300);fig.savefig(p/'figures/FugantiFig5.eps',dpi=1200);plt.close(fig)
(p/'blocked_analysis_verification.json').write_text(json.dumps({'seed':20261016,'bootstrap_replicates':B,'independent_resampling_units':'20 source-study blocks, not independent greenhouse runs','folds':20,'rows':840,'heldout_predictions':2520,'no_hyperparameter_tuning':True,'endpoint':'at least 3 alive at day 50','python':sys.version,'main_scope':'all 14 species','secondary_scope':'four crops already used in earlier prototype','external_validation':False,'similarity_hypothesis_validated':False},indent=2))
print(r.to_string(index=False));print(m.to_string(index=False));print(pd.DataFrame(diffs).to_string(index=False))
