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
