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
