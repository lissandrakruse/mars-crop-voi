# Mars Crop VOI — Interval Lab
Author: Lissandra Kruse Fuganti.

Interactive independent implementation of finite-world probabilistic interval queries, greedy constraint selection and endpoint-witness pruning. This is a methodological adaptation, not a verified reproduction of an earlier unavailable implementation. No collaborator is listed as a participant.

## Scientific interpretation
The event is a terrestrial Crop Recommendation label, conditional on the joint environmental window (temperature ±5 C, relative humidity ±15 percentage points, pH ±1). It is not a germination, productivity or Mars survival event. Windows are assumptions, not measured biological tolerances.

Sixteen binary worlds encode crop membership and three environmental-window events. Nonnegative world probabilities sum to one; the joint evidence probability is fixed to its empirical terrestrial frequency. Conditional bounds are linear objectives because this denominator is fixed. Zero-support queries are withheld.

Candidate constraints reveal exact plug-in empirical conjunction frequencies up to degree three. Greedy selection minimizes the resulting interval width. For each candidate endpoint, an existing optimal witness is reused only if it satisfies the added equality. Otherwise the LP is solved again. The full and pruned versions use identical budgets and tie-breaking, and their bounds are checked for agreement. This is retrospective constraint revelation, not prospective experimental design. Degenerate optimizers can limit pruning efficiency.

These identification bounds are not sampling confidence intervals. No rigorous VOI is claimed: decisions, utilities, observation likelihoods and costs are absent. Mars APXS chemistry is presented separately and does not provide plant-available NPK or calibrated crop success probabilities.

## Run
Python 3.12 recommended. `pip install -r requirements.txt`, then `python app.py`.
Open port 10000 (or PORT). Endpoints: GET /health, /api/crops, /api/mars; POST /api/analyze with crop, temperature, humidity, ph, budget (1–10).

## Notebook and measured data
The executed English notebook embeds terrestrial Crop and real NASA PDS APXS data for offline use. Source files and XML labels are preserved under data/. Soil records are selected by the original Soil classification; low-quality flags are visible.

- Crop: https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset
- Berger (2020), Overview of MSL APXS Targets from Sol 0 to 2301: https://doi.org/10.17189/1519050

Retain attribution and comply with source-specific terms. No blanket license over third-party data is granted. An open-source license for original code has not been selected.

## Validation
Paired full/pruned bounds agree within 1e-7 on rice, maize and apple example queries; interval widths do not increase as constraints are added. Zero-support queries are blocked. These software checks are not biological validation.
