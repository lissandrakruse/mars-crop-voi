"""Published and derived study evidence, not a joint chemical growth model."""
import json,re
from pathlib import Path
ROOT=Path(__file__).parent
SAMPLES={'RR':'Rosy Red','S1':'Sorceress 1','S2':'Sorceress 2'}
def L(pt,en):
    def clean(s):return re.sub(r'([,;:])(?=[A-Za-zÀ-ÿ])', r'\1 ', s)
    return {'pt':clean(pt),'en':clean(en)}
def get_lettuce_evidence(sample='RR'):
    if not isinstance(sample,str) or sample not in SAMPLES:raise ValueError('Select RR, S1 or S2')
    data=json.loads((ROOT/'data/lettuce_evidence.json').read_text())
    ledger=json.loads((ROOT/'data/phoenix_reference.json').read_text())
    rows=[r for r in ledger['rows'] if r['sample']==SAMPLES[sample]]
    ph=next(r for r in rows if r['quantity']=='pH');lo,hi=data['ph_observation']['min'],data['ph_observation']['max'];v=ph['value']
    data['ph_comparison']={'sample':sample,'value':v,'error_minus':ph['uncertainty_minus'],'error_plus':ph['uncertainty_plus'],'observed_solution_range':[lo,hi],'observed_readings':220,'point_inside':None if v is None else lo<=v<=hi,'numerical_overlap':None if v is None else max(lo,v-ph['uncertainty_minus'])<=min(hi,v+ph['uncertainty_plus']),'method_warning':L('220 observações de solução Bruni, não faixa ótima. Phoenix é extrato WCL; métodos não harmonizados. Sobreposição numérica do erro publicado não é intervalo de confiança, igualdade de soluções nem validação de crescimento.','220 Bruni solution observations,not an optimal range. Phoenix is a WCL extract;methods unmatched. Numerical overlap with published error is not a confidence interval,equal solutions or growth validation.')}
    data['phoenix_chemistry_rows']=rows
    mismatch=L('Elemento/íon compartilhado, mas matriz, método e exposição distintos; sem equivalência quantitativa ou efeito causal.','Shared element/ion but different matrix,method and exposure;no quantitative equivalence or causal effect.')
    def item(a,pt,en,ppt,pen,comp=mismatch):return {'analyte':a,'terrestrial':L(pt,en),'phoenix':L(ppt,pen),'comparability':comp}
    data['parameter_coverage']=[
      item('Ca / Mg / K','Pellegri,Bannon,Bruni: medições de solução mg/L; K finalBruni falta 19/20.','Pellegri,Bannon,Bruni:solution measurements mg/L;Bruni final K missing 19/20.','WCL Ca2+,Mg2+,K+ mmol/L; valores/erros por amostra abaixo.','WCL Ca2+,Mg2+,K+ mmol/L;sample values/errors below.'),
      item('P / phosphate','Pellegri P mg/L; Bannon P; Bruni fosfato com base de massa não resolvida.','Pellegri P mg/L;Bannon P;Bruni phosphate with unresolved mass basis.','Sem P disponível equivalente nesta referência WCL. APXS P2O5 é composição global de Curiosity, não P disponível Phoenix.','No equivalent available P in this WCL reference. APXS P2O5 is Curiosity bulk composition,not Phoenix available P.',L('Sem par quantitativo válido; não preencher com APXS.','No valid quantitative pair;do not fill from APXS.')),
      item('Na / Cl','Pellegri e Bruni medidos; Bannon não disponíveis. Ha varia Cl na água.','Pellegri and Bruni measured;Bannon unavailable.Ha varies water Cl.','WCL Na+,Cl− mmol/L.','WCL Na+,Cl− mmol/L.'),
      item('S / SO4','Pellegri sulfato como S mg/L; Bannon/Bruni SO4 mg/L.','Pellegri sulfate as S mg/L;Bannon/Bruni SO4 mg/L.','Sulfato lixiviável mmol/L, titulação separada, não simultânea aos outros íons.','Leachable sulfate mmol/L,separate titration,not simultaneous with other ions.'),
      item('NH4','Pellegri NH4 massa do íon mg/L; ausente Bannon/Bruni.','Pellegri NH4 ion mass mg/L;absent Bannon/Bruni.','WCL NH4 mmol/L com interferênciaK; S1 não detectado sem limite numérico.','WCL NH4 mmol/L with K interference;S1 nondetected without numeric limit.'),
      item('NO3','Pellegri massa NO3; Bannon NO3 comoN; Bruni base não resolvida; Ha mmolc/L.','Pellegri NO3 ion mass;Bannon NO3 asN;Bruni unresolved basis;Ha mmolc/L.','Sem endpoint quantitativo equivalente na referência WCL incorporada.','No equivalent quantitative endpoint in the incorporated WCL reference.',L('Não equiparar N a NO3 nem imputar Phoenix.','Do not equate N with NO3 or impute Phoenix.')),
      item('ClO4','Ausente nos três estudos de crescimento; Ha mede água/tecido em outros cultivares.','Absent in three growth studies;Ha measures water/tissue in other cultivars.','WCL ClO4− mmol/L.','WCL ClO4− mmol/L.',L('Exposição e endpoint diferentes; não extrapolar absorção ou segurança alimentar.','Different exposure and endpoint;do not extrapolate uptake or food safety.')),
      item('pH / EC','Pellegri alvos; Bannon EC sem pH bruto; Bruni pH/EC observados.','Pellegri targets;Bannon EC without raw pH;Bruni observed pH/EC.','WCL pH e EC 25°C µS/cm; S2 pH / RR EC ausentes.','WCL pH andEC 25°C µS/cm;S2 pH / RR EC missing.',L('Somente sobreposição numérica de pH. EC solução ≠ WCL ≠ ECe; nenhuma conversão.','Only numerical pH overlap.Solution EC ≠ WCL ≠ ECe;no conversion.'))]
    data['growth_model_fitted']=False;data['baseline_models_changed']=False;data['similarity_score']=None
    data['candidate_status']=L('Grand Rapids, Red Batavia e Salanova são candidatas para validação experimental por terem dados prévios úteis; não são ranqueadas entre estudos nem aprovadas para Marte. Pesquisa com perclorato deve permanecer não alimentar, sob revisão independente.','Grand Rapids,Red Batavia and Salanova are candidates for experimental validation because useful prior data exist;not ranked across studies or approved for Mars. Perchlorate research should remain non-food under independent review.')
    return data
