"""Descriptive Crop/EcoCrop screen, deliberately independent of pot outcomes."""
import csv
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).parent
SAMPLES = {'RR': 'Rosy Red', 'S1': 'Sorceress 1', 'S2': 'Sorceress 2'}


def ph_position(value, taxon):
    if taxon is None:
        return 'taxon_unresolved'
    if value is None:
        return 'unknown'
    lo, hi = taxon['ph_absolute_min'], taxon['ph_absolute_max']
    olo, ohi = taxon['ph_optimal_min'], taxon['ph_optimal_max']
    if lo is None or hi is None:
        return 'unknown'
    if not lo <= value <= hi:
        return 'outside_absolute'
    if olo is not None and ohi is not None and olo <= value <= ohi:
        return 'within_optimal'
    return 'within_absolute'


def compare_crop22(sample='RR', ece=None, selections=None):
    if not isinstance(sample, str) or sample not in SAMPLES:
        raise ValueError('Select RR, S1 or S2')
    if ece is not None and (isinstance(ece, bool) or not isinstance(ece, (float, int))
                            or not 0 <= ece <= 40 or not math.isfinite(ece)):
        raise ValueError('Independent ECe scenario must be finite, 0–40 dS/m, or null')
    eco = json.loads((ROOT / 'data/crop22_ecocrop_candidates.json').read_text())
    salt = json.loads((ROOT / 'data/crop22_salinity_evidence.json').read_text())
    if selections is None:
        selections = {}
    labels = {c['crop22_label'] for c in eco['crops']}
    if not isinstance(selections, dict) or set(selections) - labels:
        raise ValueError('Unknown crop selection')
    with (ROOT / 'data/Crop_recommendation.csv').open() as f:
        observed = {label: [] for label in labels}
        for row in csv.DictReader(f):
            observed[row['label']].append(float(row['ph']))
    ledger = json.loads((ROOT / 'data/phoenix_reference.json').read_text())
    ph = next(r for r in ledger['rows'] if r['sample'] == SAMPLES[sample] and r['quantity'] == 'pH')
    rows = []
    for crop in sorted(eco['crops'], key=lambda c: c['crop22_label']):
        label = crop['crop22_label']
        selected = selections.get(label, crop['default_candidate_id'])
        if selected is not None and (type(selected) is not int or selected not in [t['ecoport_id'] for t in crop['candidates']]):
            raise ValueError('Taxon does not belong to selected crop')
        taxon = next((t for t in crop['candidates'] if t['ecoport_id'] == selected), None)
        evidence = next((s for s in salt['entries'] if taxon and s['scientific_name'] == taxon['scientific_name']), None)
        threshold = evidence.get('threshold_ds_m') if evidence and evidence.get('comparison_eligible') else None
        status = ('scenario_not_entered' if ece is None else 'taxon_unresolved' if taxon is None else
                  'no_comparable_threshold' if threshold is None else
                  'above_reported_threshold' if ece > threshold else 'not_above_reported_threshold')
        values = observed[label]
        rows.append({'crop': label, 'mapping_status': crop['mapping_status'], 'mapping_note': crop['mapping_note'],
                     'candidates': crop['candidates'], 'selected_taxon': taxon,
                     'crop_observed_ph': {'min': min(values), 'median': statistics.median(values), 'max': max(values), 'n': len(values)},
                     'ph_position': ph_position(ph['value'], taxon),
                     'ph_uncertainty_endpoint_positions': [ph_position(ph['value'] - ph['uncertainty_minus'], taxon), ph_position(ph['value'] + ph['uncertainty_plus'], taxon)] if ph['value'] is not None else None,
                     'salinity_evidence': evidence, 'scenario_status': status})
    return {'version': '2.2-crop22-enriched-reference', 'sample': sample,
            'phoenix_ph': {'value': ph['value'], 'error_minus': ph['uncertainty_minus'], 'error_plus': ph['uncertainty_plus'], 'ledger': ph},
            'ece_scenario_ds_m': ece, 'selections': selections, 'rows': rows,
            'sources': {'ecocrop': {k: v for k, v in eco.items() if k != 'crops'}, 'salinity': {k: v for k, v in salt.items() if k != 'entries'},
                        'crop': 'https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset'},
            'limitations': ['Numerical pH position only: extraction methods unmatched; not measured growth.',
                           'EcoCrop ecological ranges are not physiological lethal limits; taxon proxies are not cultivar identification.',
                           'No Phoenix WCL EC to ECe conversion; APXS bulk oxides are a separate Curiosity dataset.',
                           'Missing evidence stays unknown. No combined rank, Mars probability, yield prediction or edible safety inference.',
                           'ECe input range is a software guard, not a validated exposure range.'],
            'wamelink_results_changed': False, 'phoenix_ec_converted': False, 'combined_rank': None}
