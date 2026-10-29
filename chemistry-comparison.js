/* Endpoint-aware screening. No Phoenix EC -> ECe conversion or outcome changes. */
(function () {
  'use strict';
  const q = id => document.getElementById(id);
  let result = null, reference = null, revision = 0, status = 'loading';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const copy = {
    pt: {
      eyebrow:'VERSÃO 2 · COMPARAÇÃO CONDICIONAL',title:'Os dados da Phoenix mudam as candidatas?',
      intro:'Comparamos as quatro culturas do simulador. <b>A química da Phoenix não permite recalcular uma ordem de sucesso em Marte.</b> Mas a evidência sobre sais distingue prioridades para ensaios, sob condições declaradas — sem misturar sobrevivência em vasos com produção de alimentos.',
      sample:'Amostra Phoenix',referenceWarning:'Medições de extrato WCL em um sítio da Phoenix: não representam todo Marte. <b>EC do extrato Phoenix não é ECe agrícola.</b> Nenhuma conversão foi presumida. <a href="#phoenixV2">Ver unidades, erros e fontes de todos os íons ↓</a>',
      tableTitle:'Antes × evidência química × cenário',scenarioTitle:'Experimente uma hipótese independente',scenarioIntro:'Informe a <b>ECe de um substrato preparado</b> para investigar a sinalização de estresse salino. Os exemplos são hipóteses didáticas, não medições da Phoenix nem recomendações de cultivo.',
      eceLabel:'ECe hipotética (dS/m)',run:'Comparar cenário',clear:'Limpar',examples:'Exemplos hipotéticos:',
      safety:'pH, íons e perclorato não foram transformados em um modelo conjunto de crescimento. Ausência de evidência não significa que uma cultura falhe. Crescer ou produzir frutos não comprova segurança alimentar.',
      methodTitle:'Método, condições e fontes',endpointCaveat:'O limiar marca o início da redução de produção na curva publicada, não um limite de sobrevivência. Tomate: referência genérica de 2,5 dS/m; tomate-cereja tem limiar separado de 1,7. Cultivar de Wamelink não harmonizado. Centeio: 11,4 se refere a grãos; a fonte apresenta 7,6 para massa seca aérea. Agrião-de-jardim tem evidência de resposta a NaCl, mas nenhuma curva ECe de colheita comparável foi estabelecida aqui.',
      scope:'Não calculamos porcentagens de rendimento, nova probabilidade de sucesso nem ranking combinado. Esta atualização acrescenta um filtro de evidência e condições para planejar ensaios, não valida plantio em Marte.',export:'Baixar comparação e fontes (JSON)',
      headers:['Cultura','Antes: vasos vivos ≥3/5 no dia 50','Evidência de pH e mistura Phoenix','Limiar ECe da fonte','Depois: cenário hipotético de sais'],pots:'vasos',baseline:'Mars simulant, Terra; resultado preservado',direct:'Viabilidade direta não identificável',details:'O que a evidência acrescenta?',noThreshold:'Sem limiar comparável',source:'Fonte',unknown:'Não disponível',error:'erro publicado',
      endpoints:{'fruit yield':'produção de frutos','storage-root yield':'produção de raízes','grain yield':'produção de grãos','no compatible ECe harvest-yield curve':'curva ECe de colheita não disponível'},
      labels:{scenario_not_entered:'Sem cenário ECe: não calculado',no_comparable_curve:'Não avaliável: curva ECe comparável ausente',above_reported_threshold:'Acima do limiar: sinal de redução de produção na fonte',not_above_reported_threshold:'Não excede o limiar; não comprova aptidão ou segurança'},
      loading:'Comparando hipótese…',invalid:'Informe ECe entre 0 e 40 dS/m ou deixe vazio. Este limite de entrada não é uma faixa validada.',dirty:'Entrada alterada: clique em Comparar cenário para atualizar.',failed:'Comparação indisponível. Tente novamente; os modelos originais não foram alterados.',blank:'Nenhuma ECe presumida. A EC da Phoenix não foi copiada para o cenário.',scenario:'Hipótese: ECe = ',scenarioEnd:' dS/m no substrato preparado. Não é medição da Phoenix.',
      initial:'<b>O que muda?</b> A Phoenix acrescenta exigências de ensaio do substrato preparado, da ECe e dos íons, além de verificar contaminantes no tecido comestível; não fornece reclassificação direta das culturas. A curva genérica de cenoura começa a perder produção em ECe menor que a de tomate e a de grãos de centeio. Isso distingue sensibilidade salina e pode orientar ensaios, mas não compara produtividade absoluta ou a mistura Phoenix. Agrião-de-jardim permanece sem posição nessa comparação quantitativa. Escolha um exemplo para ver quais limiares seriam ultrapassados.',
      changed:'O que muda neste cenário?',above:'Acima do limiar publicado: ',below:'Sem exceder esse limiar: ',none:'nenhuma das culturas com limiar disponível',unresolved:'Agrião-de-jardim permanece não avaliável nesta escala.',interpretation:'Muda a sinalização de estresse salino, <b>não uma probabilidade de sucesso ou ordem de plantio na Phoenix</b>. Centeio não foi declarado seguro para consumo ou superior em produção absoluta. A referência genérica também não valida o cultivar de Wamelink.'
    },
    en: {
      eyebrow:'VERSION 2 · CONDITIONAL COMPARISON',title:'Does Phoenix evidence change the crop candidates?',
      intro:'We compare the simulator’s four crops. <b>Phoenix chemistry does not identify a new Mars success ranking.</b> Salt-response evidence can distinguish priorities for experiments under stated conditions—without conflating pot survival with food production.',
      sample:'Phoenix sample',referenceWarning:'WCL extract measurements from one Phoenix landing site, not all of Mars. <b>Phoenix extract EC is not agricultural ECe.</b> No conversion was assumed. <a href="#phoenixV2">See all ion units, errors and sources ↓</a>',
      tableTitle:'Before × chemistry evidence × scenario',scenarioTitle:'Explore an independent hypothesis',scenarioIntro:'Enter the <b>ECe of a prepared substrate</b> to investigate salinity-stress flags. Examples are teaching hypotheses, not Phoenix measurements or cultivation recommendations.',
      eceLabel:'Hypothetical ECe (dS/m)',run:'Compare scenario',clear:'Clear',examples:'Hypothetical examples:',
      safety:'pH, ions and perchlorate have not been turned into a joint growth model. Missing evidence does not mean a crop fails. Growth or fruit production does not establish food safety.',
      methodTitle:'Method, conditions and sources',endpointCaveat:'A threshold marks the onset of yield decline in the published curve, not a survival limit. Tomato: generic reference 2.5 dS/m; cherry tomato has a separate 1.7 threshold. Wamelink cultivar not harmonized. Rye: 11.4 concerns grain; the source reports 7.6 for shoot dry weight. Garden cress has NaCl-response evidence, but no compatible harvest ECe curve was established here.',
      scope:'No yield percentages, new success probabilities or combined rankings are calculated. This update adds evidence screening and conditions for planning experiments; it does not validate cultivation on Mars.',export:'Download comparison and sources (JSON)',
      headers:['Crop','Before: ≥3/5 living plants per pot at day 50','pH and Phoenix-mixture evidence','Source ECe threshold','After: hypothetical salinity scenario'],pots:'pots',baseline:'Mars simulant on Earth; original result preserved',direct:'Direct viability not identifiable',details:'What does the evidence add?',noThreshold:'No comparable threshold',source:'Source',unknown:'Not available',error:'published error',
      endpoints:{'fruit yield':'fruit yield','storage-root yield':'storage-root yield','grain yield':'grain yield','no compatible ECe harvest-yield curve':'compatible harvest ECe curve unavailable'},
      labels:{scenario_not_entered:'No ECe scenario: not calculated',no_comparable_curve:'Not evaluable: compatible ECe curve absent',above_reported_threshold:'Above threshold: source yield-decline flag',not_above_reported_threshold:'Does not exceed threshold; no proof of suitability or safety'},
      loading:'Comparing hypothesis…',invalid:'Enter ECe from 0 to 40 dS/m or leave blank. This input guard is not a validated range.',dirty:'Input changed: click Compare scenario to update.',failed:'Comparison unavailable. Try again; original models were not changed.',blank:'No assumed ECe. Phoenix EC was not copied into the scenario.',scenario:'Hypothesis: ECe = ',scenarioEnd:' dS/m in the prepared substrate. Not a Phoenix measurement.',
      initial:'<b>What changes?</b> Phoenix adds requirements to test prepared substrate, ECe and ions, and contaminants in edible tissue; it does not directly reclassify crops. The generic carrot curve begins to lose yield at a lower ECe than tomato or grain rye. This distinguishes salt sensitivity and can guide experiments, but does not compare absolute productivity or the Phoenix mixture. Garden cress remains unranked in this quantitative comparison. Choose an example to see which thresholds would be exceeded.',
      changed:'What changes in this scenario?',above:'Above the published threshold: ',below:'Not exceeding that threshold: ',none:'none of the crops with an available threshold',unresolved:'Garden cress remains unevaluable on this scale.',interpretation:'The salinity-stress flag changes, <b>not a success probability or Phoenix planting order</b>. Rye has not been declared safe to eat or superior in absolute production. The generic reference also does not validate the Wamelink cultivar.'
    }
  };
  const lang = () => q('chemLanguage').value === 'en' ? 'en' : 'pt';
  const text = () => copy[lang()];
  function translate() {
    const t = text();
    q('chemistryComparison').lang = lang() === 'pt' ? 'pt-BR' : 'en';
    document.querySelectorAll('[data-ci]').forEach(node => {node.innerHTML = t[node.dataset.ci];});
    if (result) draw(result); else {if(reference) drawReference(reference);q('chemStatus').textContent = t[status];}
  }
  function drawReference(data) {
    const t = text();
    q('chemReference').innerHTML = ['pH','EC_25C','ClO4-'].map(analyte => {
      const r = data.phoenix_reference.find(row => row.analyte === analyte);
      if (!r) return '';
      const value = r.value === null ? t.unknown : esc(r.value) + ' ' + esc(r.unit);
      const error = r.value === null ? esc(r.result_status) : `−${r.uncertainty_minus ?? '?'} / +${r.uncertainty_plus ?? '?'} (${t.error})`;
      return `<div>${esc(analyte)} · ${esc(data.sample_name)}<strong>${value}</strong><small>${error}</small><br><a href="${esc(r.source_url)}" target="_blank" rel="noopener">${esc(r.source_location)}</a></div>`;
    }).join('');
  }
  function draw(data) {
    result = data;status = 'ready';
    const t = text(), english = lang() === 'en';
    const cropName = r => english ? r.name : r.name_pt;
    q('chemExport').disabled = false;
    reference = data;drawReference(data);
    q('chemTable').innerHTML = '<table><thead><tr>' + t.headers.map(h=>'<th scope="col">'+h+'</th>').join('') + '</tr></thead><tbody>' + data.rows.map(r => `<tr><th scope="row">${esc(cropName(r))}<br><small>${esc(r.species)}</small></th><td>${r.baseline.successes}/${r.baseline.pots} ${t.pots}<br><small>${t.baseline}</small></td><td>${t.direct}<details><summary>${t.details}</summary><p>${esc(english?r.ph_evidence_en:r.ph_evidence)}</p><p>${esc(english?r.perchlorate_evidence_en:r.perchlorate_evidence)}</p><p>${esc(english?r.caveat_en:r.caveat)}</p></details></td><td>${r.ece_threshold_ds_m === null ? t.noThreshold : r.ece_threshold_ds_m + ' dS/m'}<br><small>${esc(t.endpoints[r.endpoint])}</small><br><a href="${esc(r.source_url)}" target="_blank" rel="noopener">${t.source}</a></td><td>${esc(t.labels[r.scenario_status])}</td></tr>`).join('') + '</tbody></table>';
    q('chemStatus').textContent = data.ece_scenario_ds_m === null ? t.blank : t.scenario + data.ece_scenario_ds_m + t.scenarioEnd;
    const above = data.rows.filter(r => r.exceeds_threshold === true).map(cropName);
    const below = data.rows.filter(r => r.exceeds_threshold === false).map(cropName);
    q('chemInterpretation').innerHTML = data.ece_scenario_ds_m === null ? '<p>'+t.initial+'</p>' : `<p><b>${t.changed}</b> ${t.above}${esc(above.join(', ') || t.none)}. ${t.below}${esc(below.join(', ') || t.none)}. ${t.unresolved}</p><p>${t.interpretation}</p>`;
    q('chemMethod').innerHTML = '<ul>' + Object.values(english?data.method_en:data.method).map(x => '<li>' + esc(x) + '</li>').join('') + '</ul><ul>' + data.sources.map(s => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(english?s.label_en:s.label)}</a></li>`).join('') + '</ul>';
  }
  function invalidate(key) {
    result = null;status = key;
    q('chemExport').disabled = true;q('chemStatus').textContent = text()[key];
    q('chemTable').innerHTML = '';q('chemInterpretation').innerHTML = '';q('chemMethod').innerHTML = '';
  }
  async function run() {
    const current = ++revision;reference = null;q('chemReference').innerHTML = '';
    const input = q('chemEce'), raw = input.value, ece = raw === '' ? null : Number(raw);
    if (input.validity?.badInput || (ece !== null && (!Number.isFinite(ece) || ece < 0 || ece > 40))) {invalidate('invalid');return;}
    invalidate('loading');
    try {
      const response = await fetch('/api/chemistry-comparison',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ece,sample:q('chemSample').value})});
      if (!response.ok) throw Error('HTTP');
      const data = await response.json();if (current === revision) draw(data);
    } catch (error) {if (current === revision) invalidate('failed');}
  }
  q('chemLanguage').onchange = translate;
  q('chemRun').onclick = run;q('chemClear').onclick = () => {q('chemEce').value = '';run();};q('chemSample').onchange = run;
  for (const n of [1,3,8]) q('chemExample'+n).onclick = () => {q('chemEce').value = String(n);run();};
  q('chemEce').oninput = () => {revision++;invalidate('dirty');};
  q('chemExport').onclick = () => {
    if (!result) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(result,null,2)],{type:'application/json'}));
    const a = document.createElement('a');a.href=url;a.download='mars-crop-voi-conditional-chemistry-comparison.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  };
  translate();run();
})();
