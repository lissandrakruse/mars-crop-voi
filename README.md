# Mars Crop VOI

Project author: Lissandra Kruse Fuganti.

Exploratory terrestrial crop similarity, real Mars geochemistry, and a planned Bayesian experimental-design extension.

## Current implementation
- Executed English-language notebook with embedded Crop Recommendation and NASA PDS APXS data; no Kaggle Input or internet required.
- Audit, terrestrial holdout evaluation, hypothetical greenhouse similarity, extrapolation flags, and sensitivity analysis.
- Real APXS bulk chemistry separated from plant-available nutrients; incompatible Crop comparisons are blocked.
- Minimal project landing page and `/health` endpoint. This is not yet an interactive scientific dashboard.

## Planned research
Define measurable cultivation outcomes, acquire simulant experiment results, specify priors and likelihoods, and estimate expected information gain. No validated Mars cultivation probability or VOI implementation is claimed at this stage. This repository does not reuse a collaborator's code or list that person as a participant.

## Run
`python app.py` starts the landing page on port 10000, or PORT when set.
The notebook requires numpy, pandas, scikit-learn.

## Render
Connect this GitHub repository to Render and create a Blueprint using render.yaml. A free web service is requested; availability is subject to the connected account and current Render offerings. Review any billing requirement before selecting a paid plan.

## Sources and rights
- NASA PDS: Berger (2020), Overview of MSL APXS Targets from Sol 0 to 2301, DOI https://doi.org/10.17189/1519050. Original files and XML labels retained in data/.
- Kaggle: https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset (embedded in notebook).
- Retain source attribution and comply with source-specific terms. No blanket license is granted over third-party data. No open-source license for original project code has been selected yet.
