"""
Script 1: Generate category mappings (critical / non-critical)
Classifies event types from all three data sources using rule-based logic.
Saves mappings to data/category_mappings.json. Run once.
"""

import os
import json
import pandas as pd

BASE_DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
OUTPUT_FILE = os.path.join(BASE_DATA, 'category_mappings.json')


def classify_311():
    """Classify 311 service names as critical or non-critical."""
    critical = {
        'Biohazard',
        'Street Flooded',
        'Stormwater',
        'Stormwater Code Enforcement',
        'Encampment',
        'Illegal Dumping',
        'Dead Animal',
    }
    dir_311 = os.path.join(BASE_DATA, '311')
    names = set()
    for f in os.listdir(dir_311):
        if f.endswith('.csv') and 'dictionary' not in f:
            df = pd.read_csv(os.path.join(dir_311, f), usecols=['service_name'], dtype=str)
            names.update(df['service_name'].dropna().unique())

    return {name: 'critical' if name in critical else 'non_critical' for name in sorted(names)}


def classify_code_enforcement():
    """Classify code enforcement complaint types."""
    df = pd.read_csv(
        os.path.join(BASE_DATA, 'code_enforcement', 'complaint_types_datasd.csv'),
        dtype=str, encoding='latin-1'
    )
    types = df['Complaint Type'].dropna().str.strip().unique()

    critical_prefixes = (
        'Building-Hazard',
        'Building-Boarded',
        'Building-LandDev-Landslide',
        'Building-LandDev-Stormwater',
        'Building-LandDev-Dumping',
        'Housing-Structural',
        'Housing-Electrical',
        'Housing-Plumbing',
        'Housing-Mechanical',
        'Housing-Fire Prevention',
        'Housing-No Fence w/ Pool',
        'Housing-Structure Not Intended',
        'Zoning-Danger to the Public',
    )

    mapping = {}
    for t in sorted(types):
        if any(t.startswith(p) for p in critical_prefixes):
            mapping[t] = 'critical'
        else:
            mapping[t] = 'non_critical'
    return mapping


def classify_police_calls():
    """Classify police call types."""
    df = pd.read_csv(
        os.path.join(BASE_DATA, 'police_calls', 'pd_cfs_calltypes_datasd.csv'),
        dtype=str, encoding='latin-1'
    )
    df = df.drop_duplicates(subset=[df.columns[0]])

    # Critical call type codes — violent crime, weapons, life-threatening emergencies
    critical_codes = {
        # Homicide / assault / weapons
        '187', '187-SUSP', '245', '245-CR', '245-SUSP', '245DV', '245R',
        '246', '246R', '247', '247R',
        '11-6', '11-6SPT',  # Discharging firearms
        '417', '417R',  # Threatening with weapon
        '422', '422R',  # Criminal threats
        # Robbery / carjacking
        '211', '211-SUSP', '211A', '211C', '211R', '211SPEC',
        '215', '215R',
        # Kidnapping
        '207', '207R',
        # Burglary in progress / hot prowl
        '459', '459-SUSP', '459HP',
        # Arson
        '451', '451R',
        # Person down / injury / death
        '11-8',  # Person down
        '1140OD',  # Overdose
        '1141',  # Ambulance needed
        '1144',  # Coroner's case
        '1146',  # Report of death
        '1147',  # Injured person
        '1180', '1180-CR',  # Serious injury accident
        # DUI
        '23152', '23152-CR',
        # Fire / explosion / hazmat
        '1171',  # Fire
        '1155',  # Hazardous/chemical spill
        'EXPLO',  # Explosion
        'BIOALARM',
        'BOMB', 'BOMB-S',
        'ALERT2', 'ALERT3', 'ALERT4',
        # Officer/public safety
        '1199',  # Officer needs help
        'COVER', 'COVER-CR',
        'FP',  # Foot pursuit
        'TP',  # Traffic pursuit
        'RESCUE',
        'EVAC',
        # Domestic violence
        '415DV', '415V', '415W',
        # Stalking
        '646', '646R',
        # Child-related
        '271',  # Child desertion
        '278', '278R',  # Child stealing
        'MJ',  # Missing juvenile tender years
        'AMBER',
        # Elder abuse
        '368',
        # Firing at occupied vehicle/house
        '20001', '20001-CR',  # Felony hit and run
        # Prowler
        '11-7',
        # Escape
        'ESCAPE',
        # Cruelty to animals in progress
        '597',
        # Mental case violent
        '5150V',
        # Impersonating officer
        '146',
        # Witness intimidation
        '136',
        # SWAT
        'C10', 'C11', 'C11-CR', 'C12', 'C100',
        # Mutual aid
        'MUTAID',
        # All units for critical events
        'AU187', 'AU211', 'AU215', 'AU245', 'AU1', 'AU1171',
    }

    mapping = {}
    for _, row in df.iterrows():
        code = str(row.iloc[0]).strip()
        mapping[code] = 'critical' if code in critical_codes else 'non_critical'

    return mapping


def main():
    print("Generating category mappings...")

    mappings_311 = classify_311()
    print(f"  311: {sum(1 for v in mappings_311.values() if v == 'critical')} critical, "
          f"{sum(1 for v in mappings_311.values() if v == 'non_critical')} non-critical")

    mappings_ce = classify_code_enforcement()
    print(f"  Code enforcement: {sum(1 for v in mappings_ce.values() if v == 'critical')} critical, "
          f"{sum(1 for v in mappings_ce.values() if v == 'non_critical')} non-critical")

    mappings_police = classify_police_calls()
    print(f"  Police calls: {sum(1 for v in mappings_police.values() if v == 'critical')} critical, "
          f"{sum(1 for v in mappings_police.values() if v == 'non_critical')} non-critical")

    result = {
        "311_service_name": mappings_311,
        "code_enforcement_complaint_type": mappings_ce,
        "police_call_type": mappings_police,
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\nSaved to {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
