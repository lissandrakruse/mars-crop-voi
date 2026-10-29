# Mars Crop VOI — Cultivation Success
Project author: Lissandra Kruse Fuganti.

## Research question
Which plants could be cultivated successfully on Mars?

The main interface compares tomato, carrot, garden cress and rye using measured outcomes from Wamelink et al. (2014), Table S2. It estimates a defined pot-level endpoint under the study's Earth greenhouse and Mars-simulant protocol. Actual Mars success remains unidentified. Other plants are not classified as failures merely because this study did not test them.

## Success definition
Choose germination, alive plants at day 50, or flower/bud formation, and a minimum count out of five plants per pot. The default is at least three plants alive after 50 days. No harvest, edible yield, nutritional sufficiency or food-safety claim is made.

Each of 20 pots per species/substrate is one binary trial. With s successes in n pots, the chosen Beta(1,1) prior gives Beta(1+s,1+n-s). The output includes posterior mean, 95% equal-tailed credible interval, raw pot counts and a Jeffreys-prior sensitivity check. Exchangeable independent pots are assumed; residual block/greenhouse dependence and between-study heterogeneity are unmodeled. Mean-based ordering does not prove a statistically superior crop.

## Actual Mars versus simulant
An optional sensitivity projection uses p_target=q*p_simulant. q is a user assumption about avoiding additional mission failure conditional on simulant success, not an estimate from the study. It assumes extra stressors can only reduce success. Projection is disabled by default. Its interval conditions on fixed q and omits transfer uncertainty.

## Information gain
The panel calculates expected information I(theta; next pot outcome) under the beta posterior for one more comparable experimental pot. It is not the value of testing an unobserved Mars stressor and is not decision-theoretic VOI without utility and costs.

## Evidence and reproducibility
- Wamelink GWW et al. (2014), Can Plants Grow on Mars and the Moon: A Growth Experiment on Mars and Moon Soil Simulants, PLOS ONE 9(8):e103138. https://doi.org/10.1371/journal.pone.0103138. Table S2, CC BY. The CSV preserves source values; whitespace is stripped from column names only when loaded. 840 pots, 14 species, three substrates, 20 blocks; five seeds per pot.
- Curiosity/APXS: Berger (2020), https://doi.org/10.17189/1519050. Context only: bulk composition is not plant-available nutrients or an outcome dataset.
- Kaggle Crop Recommendation: https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset. Ancillary terrestrial context only, not used as cultivation-success labels.

The executed English notebook embeds the experimental CSV, original XLSX, Crop CSV and APXS CSV with SHA-256 integrity checks. No input attachment or internet is needed after opening it in a standard scientific Python environment.

## Run and API
Python 3.12: `pip install -r requirements.txt`, then `python app.py`.
- GET /health, /api/options, /api/mars
- POST /api/success: species, endpoint, minimum; optional transfer in [0,1]
- Source: success_model.py, index.html, data/wamelink2014_pots.csv

The previous interval_model.py is a retained legacy terrestrial crop-label demonstration, not the current success model. It is not served by the main application. It cannot answer which crops succeed on Mars.

## Validation and limitations
Software checks cover all four crops, three endpoints and thresholds 1–5, posterior bounds and transfer calculations, invalid thresholds, source design and HTTP endpoints. They do not constitute biological or mission validation. Only one source experiment is included; independent studies and harvest data are needed before stronger recommendations.

No external researcher is listed as a participant. Retain source attribution and applicable data terms. No blanket license over third-party data is granted; no open-source license for original project code has been selected.

## pH candidate screen
Phoenix reference: Hecht et al. (2009), https://pubmed.ncbi.nlm.nih.gov/19574385/, pH 7.7 +/-0.5 at one landing site. The Crop screen counts observed rows in 7.2–8.2. This is not a confidence interval or global soil distribution; analytical methods are unharmonized. Dataset counts are descriptive overlap, not success probabilities or verified physiological tolerances.

## Joint greenhouse temperature + soil-pH interval module
The main page now includes an editable temperature, pH and air-humidity scenario with analysis-window widths and a pairwise-constraint budget (0–3). `scenario_model.py` independently implements finite-world LP bounds using eight worlds, empirical per-crop marginals, greedy pairwise-constraint selection and endpoint-witness pruning. Full reoptimization and pruned versions use the same budgets and tie-breaking and must agree within 1e-7. Exact empirical joint overlap is held out of selected constraints and checked against every interval.

The event is a randomly selected terrestrial row for a given crop lying inside all three analysis windows. It is not physiological suitability, cultivation success or a Mars probability. Actual Mars success remains unidentified [0,1] in this module, because the Crop labels do not contain success responses. NPK availability, salinity, perchlorates and water retention are unlinked; APXS oxides are not substituted. Soil pH is included with an explicit analytical-method caveat. Temperature is a greenhouse scenario, not outdoor Mars temperature.

POST /api/scenario accepts temperature, ph, humidity, temperature_tolerance, ph_tolerance, humidity_tolerance and integer budget. Tests cover budgets 0,2,3, an alternate scenario, full/pruned agreement, monotonically narrowing intervals, empirical joint containment and invalid inputs. Default software check: 264 full versus 94 pruned solver calls. This count is specific to the chosen scenario and solver witnesses, not a general speedup claim. The executed notebook includes this module and exports its bounds.

## Mathematical foundation
The site and executed notebook now document the actual implemented event definitions, eight-world distributions, empirical equality constraints, min/max LP objectives, analytic marginal bounds, greedy width-reduction selection and the endpoint-pruning proof. They distinguish identification intervals, pot-level Bayesian credible intervals, entropy-based expected information, and unidentifiable actual-Mars success. Exact equivalence to the earlier unavailable code is not claimed. See the Mathematical Foundation section on the site.

## Direct answer: conditional plant candidates
The landing page now opens with a source-linked candidate table grouped by cultivation outcome, based on four included analog studies (2014, 2022, 2024, 2025). It lists seven food-production candidates and two additional early-stage candidates, required substrate/protocol conditions and limitations. This is a focused evidence screen, not an exhaustive review or a cross-study quantitative success ranking. It does not label unassessed plants as failures. GET /api/candidates serves the auditable curation in data/candidate_evidence.json. The prior LP and outcome models remain below as supporting analyses, not substitutes for crop-yield evidence.

## Temperature/humidity scenario sweep
POST /api/sweep holds pH and its tolerance fixed and explores 432 declared greenhouse center combinations. It reports the best observed joint-overlap count per Crop label and performs the two-constraint LP/pruning agreement check at each nonzero best scenario. It uses in-sample descriptive search, not validation or optimization of actual biological outcomes. Different crops may require different settings. Default pH 7.7 +/-0.5 gives 6 initially matched labels and 10 somewhere in the grid. The four newly matched labels are chickpea, orange, rice and pigeonpeas. These labels are not claimed to have demonstrated cultivation success in Mars conditions.

## Similarity-to-outcome transfer mechanism
POST /api/transfer implements a declared power-prior hypothesis: standardized environmental distance produces w=exp(-d2/2); same-crop source outcomes k/n give Beta(1+w*k,1+w*(n-k)). Scales are assumptions (5 C, 0.5 pH, 15 humidity points), not learned calibration. Sensitivity uses half/double scales. No numerical transfer is returned for weight below 0.1 or when same-crop outcomes are absent. The four source-trial food crops are supported; Crop-only labels abstain unless the user supplies actual same-crop pilot counts and reference conditions. They are never substituted with another species. Conditional intervals exclude transfer-assumption uncertainty, so actual Mars probability remains unset. The UI explicitly states that empirical calibration still needs independent target-spanning experiments. Source simulant pH 7.3 is reproduced in NASA BVAD: https://ntrs.nasa.gov/api/citations/20210024855/downloads/BVAD_2.15.22-final.pdf.


## Version 2 — Phoenix mission chemistry reference (2026-10-29)
The visible Phoenix panel adds the published MECA Wet Chemistry Laboratory reference for Rosy Red, Sorceress 1 and Sorceress 2. `data/phoenix_reference.json` contains 33 endpoint records with original units, asymmetric errors, missing values, provenance and qualifiers. GET `/api/phoenix-reference` serves that ledger; `phoenix.js` presents a separate, local-only hypothetical scenario and JSON export. Empty scenario inputs remain null, never zero. Scenario edits do not change any cultivation calculation.

WCL extracted approximately 1 cm³ regolith into 25 mL calibrant. These are experiment solution concentrations, not bulk soil composition or plant-available nutrient concentrations. Conductivity at 25 °C is not saturated-paste ECe or TECP in-situ conductivity. Sulfate comes from separate titration intervals and is not coeval with Table 7 ions. Published errors are not assigned a 95% confidence level. S2 pH, RR conductivity and S1 sulfate are unavailable; S1 NH4 is nondetected without a numerical threshold. NH4 estimates require caution, and the malformed S2 Mg upper uncertainty remains unresolved/null.

Sources: NASA PDS Phoenix WCL archive https://doi.org/10.17189/1518770; Kounaves et al., JGR https://doi.org/10.1029/2009JE003424 (Table 7, final pH section 4.5, sensor pH Table 8, conductivity Table 9); sulfate https://doi.org/10.1029/2010GL042613; initial Science report https://doi.org/10.1126/science.1172466. This is a compilation of published reductions, not a new reduction of raw PDS data. It represents one landing site, not all Mars. Final JGR pH values are kept distinct from the existing Science-era 7.7 ± 0.5 screening window.

The Wamelink outcome models, source data and original screening modules are unchanged. No ion-based causal growth model, treatment recommendation, mission success or food-safety claim is added. Baseline upstream commit: `057cd1052111d6bfb8efc93bfebd9bc8debe9b7d`.

Checks: `node --check phoenix.js`; `python -m compileall -q app.py`; `python test_phoenix_v2.py` (browser test additionally needs Playwright and Chromium; not production dependencies). The optional baseline byte check needs a sibling `mars_crop_baseline_057cd105` directory. Tests validate software/data handling, not biological predictions.


## Version 2.1 — what changes for the four existing crops?

The main navigation now opens a PT/EN comparison of the unchanged Wamelink Mars-simulant result (18/20 tomato, 19/20 carrot, 20/20 garden cress, 20/20 rye pots with at least three living plants on day 50) against the limits of Phoenix chemical inference. RR/S1/S2 selection displays source-linked WCL pH, extract conductivity and perchlorate, retaining missing values and published errors. **Direct joint Phoenix viability remains unidentified; this is not evidence that the true crop ranking is unchanged.**

A separate, blank-by-default prepared-substrate **ECe scenario** checks whether crop-specific literature yield thresholds are exceeded. ECe means root-zone saturated-paste extract conductivity in dS/m, not Phoenix WCL extract EC. The FAO Annex 1 Table A1.1 gives generic tomato fruit yield 2.5, carrot storage-root yield 1.0 and rye grain yield 11.4 dS/m. At an assumed ECe of 3, carrot and generic tomato exceed those thresholds while rye grain does not; garden cress has no compatible ECe harvest curve here and is not assigned a rank. This changes conditional stress flags and can guide experiments, **not Mars success probabilities or an overall planting recommendation**. At/below a threshold is not proof of suitability or food safety.

The thresholds concern late seedlings through maturity under relatively uniform, predominantly chloride salinity and different harvest endpoints in different experiments. They are not standardized head-to-head crop outcomes. Rye shoot dry-weight has a different threshold (7.6); cherry tomato has a separate threshold (1.7). The source-trial cultivar is not harmonized with the generic reference. Published slopes are retained as evidence metadata but no relative-yield percentages are computed. The input guard 0–40 dS/m is not a validated model range.

pH evidence is qualitative and qualified: tomato pH 7.5 chlorosis depends on Fe supply in a hydroponic experiment; absence of chlorosis does not imply unchanged biomass. Cress grew in a study reporting soil pH 7.6, but this is not a pH dose-response or Phoenix-method match. No crop-specific Phoenix-mixture/perchlorate growth or edible-tissue safety cutoff is inferred. Presence of Ca/Mg/K does not establish nutrient sufficiency; sulfate/perchlorate chemistry is not represented by chloride-salinity curves. Preparation, comparable substrate chemistry, independent crop experiments and edible-tissue testing remain required.

- Sources and machine-readable endpoints: `data/crop_chemistry_evidence.json`; expanded research audit: `research/phoenix_tolerance/crop_tolerance_evidence.json`.
- Backend: `chemistry_comparison.py`; independent UI: `chemistry-comparison.js`.
- GET `/api/chemistry-comparison` returns the blank default; POST accepts only `ece` (number or null) and `sample` (`RR`, `S1`, `S2`). Existing crop APIs are unchanged.
- Export includes the selected Phoenix reference, scenario assumptions, endpoint definitions, original counts, sources and explicit no-conversion/no-probability-change flags. It does not save user entries on the server.
- `python -m unittest -v test_chemistry_comparison` checks nine cases including HTTP validation, sample missingness, threshold boundaries and all 60 original crop/endpoint/threshold outputs.
- `node test_chemistry_ui.js` checks default/sample/example flows, export, invalid inputs, repeated clearing, stale-response protection and request failures with a mock DOM. `node test_phoenix_ui.js` covers the separate reference panel. These are not visual browser QA.

The comparison has its own language selector. Switching language preserves selected sample, scenario values, computed flags and exported evidence; it does not change model inputs or send a new request. Exports retain both-language evidence metadata.

No license change or redistribution of full source publications is made. Links and short factual evidence summaries preserve attribution; original project licensing and third-party source conditions remain applicable.

## Version 2.2 — 22 Crop labels enriched with EcoCrop and USDA references
A separate bilingual top-level panel now compares all 22 Crop labels; the four Wamelink crops and their measured pot outcomes remain a different panel/model. Crop observed pH distributions are descriptive. EcoCrop adds ecological optimal/absolute pH and temperature ranges, annual rainfall, crop-cycle duration, and categorical salinity. It does not add observed survival or prove Mars suitability.

- Source: FAO ECOCROP, CC BY 4.0, [official licence metadata](https://data.fao.org/catalog/api/3/action/package_show?id=ecocrop). Source attribution, pinned OpenCLIM CSV commit and SHA256, modifications, and no-endorsement notice are included in `data/crop22_ecocrop_candidates.json`; licence evidence is retained in `research/ecocrop_fao_catalog_license_evidence.json`. The underlying database is historical/discontinued; a catalogue metadata update does not mean new experiments.
- 31 candidate records across 22 labels. Banana, cotton, coffee and jute have no default taxon. Explicit selection records an identification assumption; other default species matches remain proxies, not cultivar verification. Jute has only one available candidate, which does not resolve the generic label.
- pH placement uses the selected Phoenix sample's central value; reported propagated-error endpoint positions are also exported. Phoenix WCL and EcoCrop soil pH methods are not harmonized. An ecological absolute range is not a lethal physiological limit. S2 has no usable measured pH.
- Minimal factual USDA references: common bean / Phaseolus vulgaris seed yield ECe 1.0; maize / Zea mays ear fresh weight 1.7; cotton / Gossypium hirsutum seed-cotton yield 7.7 dS/m. No slopes/full publication table reproduced or blanket source licence claimed. Source/method/endpoint/cultivar cautions included in `data/crop22_salinity_evidence.json`. Generic cotton requires explicit G. hirsutum selection.
- Rice's reported 3.0 dS/m is flooded soil-water conductivity, not standard saturated-paste ECe; excluded from ECe calculations. Uncovered labels remain unknown, not zero or resistant. EcoCrop salinity classes lack confirmed extraction-method compatibility and are never converted into continuous ECe curves.
- Optional ECe is an independent prepared-substrate assumption, blank by default; the software guard 0–40 is not a validated response interval. It only flags whether an eligible source threshold is exceeded. No Phoenix EC-to-ECe conversion, yield prediction, combined score or Mars success probability is calculated. Curiosity APXS oxides remain separate from Phoenix soluble chemistry; neither supplies crop-specific multi-ion tolerance or food-safety validation.

API: GET/POST `/api/crop22-comparison`; POST fields `sample`, `ece`, `selections` (crop label to listed EcoPort integer ID or null; omitted means documented default). Export retains source attribution, selected taxa, methods, sample uncertainty and all unknowns.

Tests: `python -m unittest -v test_crop22_comparison test_chemistry_comparison`; `node test_crop22_ui.js`; existing reference/UI tests remain applicable. Mock-DOM tests are not visual browser QA; browser rendering remains blocked by this execution environment's Chromium sandbox/socket restriction.

## Version 2.3 — lettuce evidence, not a new growth model
The standalone PT/EN lettuce section keeps Grand Rapids (Pellegri 2026), Red Batavia (Bannon 2026) and Salanova (Bruni 2023) separate. These cultivars are candidates for experimental validation because source data exist, not because this interface ranks them or establishes cultivation on Mars. Ha 2013 is a separate perchlorate-tissue uptake evidence stream, not a harvest prediction or food-safety clearance. AI-assisted secondary analysis; human scientific review for interpretation and publication remains pending.

The interface exposes actual derived solution chemistry summaries, including Ca/Mg/K/P where reported, original harvest bases, experimental units, source quality flags, and parameter-by-parameter Phoenix availability. Same ions do not imply matched concentrations, ion activities or effects. Phoenix WCL, nutrient solution and Curiosity bulk APXS are never equated. No equivalent Phoenix plant-available P is imputed from APXS P2O5. pH overlap compares a selected WCL central value/published error with the observed Bruni solution-reading range (220 readings, 7.47–8.36); it is numerical and method-unmatched, not an optimal range, confidence interval or growth-validation test.

GET/POST `/api/lettuce-evidence` accepts only `sample` RR/S1/S2. JSON export preserves sample-specific missingness, uncertainty, concentrations, methods and all study limitations. No existing Wamelink, Crop22 or salinity computation is changed.

Rebuild the small attributed derived evidence file with `python research/lettuce/build_evidence.py`; three source-analysis CSVs are included under `research/lettuce/inputs`, with their SHA256 hashes in the generated JSON. These are secondary summaries, not reconstructed raw outcomes. They originate from the separately delivered reproducible lettuce evidence package. Pellegri and Bruni article/data and Bannon source dataset are CC BY 4.0; their authors, DOIs and derived modifications are identified below. No source paper PDF, figures or Ha regression coefficients are redistributed. No new blanket licence over third-party publications or project code is asserted.

- Pellegri et al. 2026: https://doi.org/10.3389/fspas.2026.1687731 — nine measured solution analytes summarized by trapezoidal time weighting over 28 days; four sequential runs; published shoot mean±plant SD. S is sulfur-equivalent mass; NO3/NH4 are ion mass. pH/EC are targets, not measured series.
- Bannon et al. 2026: https://doi.org/10.1002/fes3.70220; raw dataset https://doi.org/10.5281/zenodo.18804397 — equal-system initial/final concentration summaries and harvest contrasts; temporal confounding and unresolved weight-provenance flags retained.
- Bruni et al. 2023: https://doi.org/10.3390/w15112109 — means over five different microbial conditions, not replicate identical treatments; pooled harvest mass remains reported g, not g/plant. K missingness retained, nitrate/phosphate basis unresolved.
- Ha et al. 2013: https://doi.org/10.2134/jeq2012.0142 — minimal factual uptake/design summary only; no dietary-risk prediction.

Run `python -m unittest -v test_lettuce_evidence test_crop22_comparison test_chemistry_comparison` and all four `test_*_ui.js` Node scripts. These cover source-summary regeneration, counts, missing values, units, HTTP validation, old 60-result baseline regression, bilingual state/export and interrupted requests. Live visual verification is performed separately at deployment.
