"""Source-qualified chemical screening; separate from Wamelink survival inference."""
import json
import math
from pathlib import Path
from success_model import estimate

ROOT = Path(__file__).parent
SAMPLES = {'RR': 'Rosy Red', 'S1': 'Sorceress 1', 'S2': 'Sorceress 2'}


def compare(ece=None, sample='RR'):
    """Threshold comparison only; do not infer ECe from Phoenix extract EC."""
    if sample not in SAMPLES:
        raise ValueError('Select RR, S1 or S2')
    if ece is not None:
        if isinstance(ece, bool) or not isinstance(ece, (int, float)):
            raise ValueError('ECe must be a finite nonnegative number or null')
        if not math.isfinite(ece) or not 0 <= ece <= 40:
            raise ValueError('Scenario ECe must be between 0 and 40 dS/m')
    evidence = json.loads((ROOT / 'data/crop_chemistry_evidence.json').read_text())
    phoenix = json.loads((ROOT / 'data/phoenix_reference.json').read_text())
    reference = [r for r in phoenix['rows'] if r['sample'] == SAMPLES[sample]
                 and r['quantity'] in ('pH', 'extract_conductivity_25C', 'total_solution_concentration')]
    rows = []
    for crop in evidence['crops']:
        mars = estimate(crop['species'], 'alive50', 3)['results']['Mars']
        threshold = crop['ece_threshold_ds_m']
        status = ('scenario_not_entered' if ece is None else
                  'no_comparable_curve' if threshold is None else
                  'above_reported_threshold' if ece > threshold else
                  'not_above_reported_threshold')
        rows.append({**crop, 'baseline': {'successes': mars['successes'], 'pots': mars['pots'],
                                         'posterior_mean': mars['posterior_mean']},
                     'phoenix_direct_status': 'not_identifiable_method_or_outcome_gap',
                     'scenario_status': status,
                     'exceeds_threshold': None if ece is None or threshold is None else ece > threshold})
    return {'version': '2.1-conditional-chemistry-comparison',
            'sample': sample, 'sample_name': SAMPLES[sample], 'phoenix_reference': reference,
            'ece_scenario_ds_m': ece, 'ece_is_user_assumption': ece is not None,
            'phoenix_ec_converted': False, 'crop_success_probabilities_changed': False,
            'relative_yield_calculated': False, 'rows': rows,
            'method': evidence['method'], 'method_en': evidence['method_en'], 'sources': evidence['sources']}
