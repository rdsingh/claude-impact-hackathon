"""
Script 2: Build neighborhood_qol.json
Reads local CSVs + shapefile + category_mappings.json.
Performs spatial joins, date normalization, aggregation, and QoL scoring.
Outputs data/neighborhood_qol.json. Run once after generate_category_mappings.py.
"""

import os
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

BASE_DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
MAPPINGS_FILE = os.path.join(BASE_DATA, 'category_mappings.json')
OUTPUT_FILE = os.path.join(BASE_DATA, 'neighborhood_qol.json')

# Configurable weights
WEIGHT_CRITICAL = 0.7
WEIGHT_NON_CRITICAL = 0.3

# Last 7 years
MIN_YEAR = 2018
MAX_YEAR = 2025


def load_category_mappings():
    with open(MAPPINGS_FILE) as f:
        return json.load(f)


def load_pd_beats():
    """Load PD beats shapefile and return GeoDataFrame with beat polygons."""
    shp_path = os.path.join(BASE_DATA, 'pd_beats_datasd', 'pd_beats_datasd.shp')
    gdf = gpd.read_file(shp_path)
    # Ensure WGS84
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    # Standardize beat column to string
    gdf['beat'] = gdf['beat'].astype(str).str.strip()
    return gdf[['beat', 'name', 'geometry']]


def load_311_data(mappings):
    """Load all 311 CSVs, filter to date range, assign beat via spatial join."""
    print("  Loading 311 data...")
    dir_311 = os.path.join(BASE_DATA, '311')
    frames = []
    cols = ['service_name', 'date_requested', 'date_closed', 'status', 'lat', 'lng']
    for f in sorted(os.listdir(dir_311)):
        if f.endswith('.csv') and 'dictionary' not in f:
            df = pd.read_csv(os.path.join(dir_311, f), usecols=cols, dtype={'lat': str, 'lng': str})
            frames.append(df)

    df = pd.concat(frames, ignore_index=True)

    # Use date_closed for closed requests, date_requested for open
    df['date'] = pd.to_datetime(df['date_closed'], errors='coerce')
    mask_open = df['date'].isna()
    df.loc[mask_open, 'date'] = pd.to_datetime(df.loc[mask_open, 'date_requested'], errors='coerce')

    # Filter date range
    df['year'] = df['date'].dt.year
    df = df[(df['year'] >= MIN_YEAR) & (df['year'] <= MAX_YEAR)].copy()

    # Parse coordinates
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lng'] = pd.to_numeric(df['lng'], errors='coerce')
    df = df.dropna(subset=['lat', 'lng'])

    # Assign category
    df['category'] = df['service_name'].map(mappings.get('311_service_name', {})).fillna('non_critical')

    # Add time columns
    df['quarter'] = df['date'].dt.quarter
    df['month'] = df['date'].dt.month

    print(f"    {len(df)} rows after filtering")
    return df[['lat', 'lng', 'category', 'year', 'quarter', 'month']]


def load_code_enforcement_data(mappings):
    """Load code enforcement CSV, filter to date range, return with coordinates."""
    print("  Loading code enforcement data...")
    path = os.path.join(BASE_DATA, 'code_enforcement', 'code_enf_past_2015_to_2018_datasd.csv')
    df = pd.read_csv(path, dtype=str, encoding='latin-1')

    df['date'] = pd.to_datetime(df['date_open'], errors='coerce')
    df['year'] = df['date'].dt.year
    df = df[(df['year'] >= MIN_YEAR) & (df['year'] <= MAX_YEAR)].copy()

    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lng'] = pd.to_numeric(df['lng'], errors='coerce')
    df = df.dropna(subset=['lat', 'lng'])

    # Map complaint_type description to category
    ce_mappings = mappings.get('code_enforcement_complaint_type', {})
    df['category'] = df['description'].apply(
        lambda x: _match_ce_category(str(x).strip(), ce_mappings) if pd.notna(x) else 'non_critical'
    )

    df['quarter'] = df['date'].dt.quarter
    df['month'] = df['date'].dt.month

    print(f"    {len(df)} rows after filtering")
    return df[['lat', 'lng', 'category', 'year', 'quarter', 'month']]


def _match_ce_category(description, mappings):
    """Match code enforcement description to category mapping."""
    # Try exact match first
    if description in mappings:
        return mappings[description]
    # Try prefix match (description often starts with complaint type)
    for key, val in mappings.items():
        if description.upper().startswith(key.upper().split('-')[0].strip()):
            return val
    return 'non_critical'


def load_police_calls_data(mappings):
    """Load police call CSVs, filter to date range. Uses BEAT field directly."""
    print("  Loading police calls data...")
    dir_police = os.path.join(BASE_DATA, 'police_calls')
    frames = []
    for f in sorted(os.listdir(dir_police)):
        if f.startswith('pd_calls_for_service_') and f.endswith('.csv') and 'dictionary' not in f:
            # Extract year from filename
            year_str = f.replace('pd_calls_for_service_', '').replace('_datasd.csv', '')
            try:
                year = int(year_str)
                if year < MIN_YEAR or year > MAX_YEAR:
                    continue
            except ValueError:
                continue

            df = pd.read_csv(os.path.join(dir_police, f), dtype=str)
            df.columns = df.columns.str.strip().str.strip('"').str.upper()
            df = df[['DATE_TIME', 'CALL_TYPE', 'BEAT']]
            frames.append(df)

    df = pd.concat(frames, ignore_index=True)
    df['date'] = pd.to_datetime(df['DATE_TIME'], errors='coerce')
    df['year'] = df['date'].dt.year
    df = df[(df['year'] >= MIN_YEAR) & (df['year'] <= MAX_YEAR)].copy()

    # Assign category from call type
    police_mappings = mappings.get('police_call_type', {})
    df['category'] = df['CALL_TYPE'].map(police_mappings).fillna('non_critical')

    df['beat'] = df['BEAT'].astype(str).str.strip()
    df['quarter'] = df['date'].dt.quarter
    df['month'] = df['date'].dt.month

    print(f"    {len(df)} rows after filtering")
    return df[['beat', 'category', 'year', 'quarter', 'month']]


def spatial_join_to_beats(df, beats_gdf):
    """Assign beat to rows with lat/lng via point-in-polygon spatial join."""
    print("  Performing spatial join...")
    geometry = [Point(lng, lat) for lng, lat in zip(df['lng'], df['lat'])]
    points_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
    joined = gpd.sjoin(points_gdf, beats_gdf, how='left', predicate='within')
    joined = joined.dropna(subset=['beat'])
    joined['beat'] = joined['beat'].astype(str).str.strip()
    print(f"    {len(joined)} rows matched to beats")
    return joined[['beat', 'category', 'year', 'quarter', 'month']]


def aggregate_and_score(records_list, source_names):
    """Aggregate counts by beat/category/time and compute QoL scores."""
    all_results = []

    for records, source in zip(records_list, source_names):
        print(f"  Aggregating {source}...")
        df = pd.DataFrame(records)

        # Count by beat, category, year, quarter, month
        grouped = df.groupby(['beat', 'category', 'year', 'quarter', 'month']).size().reset_index(name='count')

        # Compute weighted counts per beat/time
        for _, row in grouped.iterrows():
            weight = WEIGHT_CRITICAL if row['category'] == 'critical' else WEIGHT_NON_CRITICAL
            all_results.append({
                'beat': str(row['beat']),
                'q_o_l_category': row['category'],
                'count': int(row['count']),
                'weighted_count': float(row['count'] * weight),
                'source': source,
                'year': int(row['year']),
                'quarter': int(row['quarter']),
                'month': int(row['month']),
            })

    results_df = pd.DataFrame(all_results)

    # Also create combined "all_sources" entries
    combined = results_df.groupby(['beat', 'q_o_l_category', 'year', 'quarter', 'month']).agg(
        count=('count', 'sum'),
        weighted_count=('weighted_count', 'sum')
    ).reset_index()
    combined['source'] = 'all_sources_combined'
    results_df = pd.concat([results_df, combined], ignore_index=True)

    # Also create "all" category entries per source
    all_cat = results_df.groupby(['beat', 'source', 'year', 'quarter', 'month']).agg(
        count=('count', 'sum'),
        weighted_count=('weighted_count', 'sum')
    ).reset_index()
    all_cat['q_o_l_category'] = 'all'
    results_df = pd.concat([results_df, all_cat], ignore_index=True)

    # Compute QoL score: neighborhood weighted count / city average weighted count
    # Group by source, category, year, quarter, month to get city averages
    city_avg = results_df.groupby(['source', 'q_o_l_category', 'year', 'quarter', 'month']).agg(
        avg_weighted=('weighted_count', 'mean')
    ).reset_index()

    results_df = results_df.merge(
        city_avg,
        on=['source', 'q_o_l_category', 'year', 'quarter', 'month'],
        how='left'
    )

    results_df['score'] = (results_df['weighted_count'] / results_df['avg_weighted']).round(4)
    results_df.loc[results_df['avg_weighted'] == 0, 'score'] = 0.0

    # Drop intermediate columns
    results_df = results_df[['beat', 'q_o_l_category', 'score', 'source', 'year', 'quarter', 'month']]

    return results_df


def main():
    print("Loading category mappings...")
    mappings = load_category_mappings()

    print("Loading PD beats shapefile...")
    beats = load_pd_beats()
    print(f"  {len(beats)} beats loaded")

    print("\nLoading data sources...")
    data_311 = load_311_data(mappings)
    data_ce = load_code_enforcement_data(mappings)
    data_police = load_police_calls_data(mappings)

    # Spatial join for 311 and code enforcement (they have lat/lng)
    print("\nSpatial joins...")
    joined_311 = spatial_join_to_beats(data_311, beats)
    joined_ce = spatial_join_to_beats(data_ce, beats)
    # Police calls already have beat field
    joined_police = data_police

    # Aggregate and score
    print("\nComputing QoL scores...")
    results = aggregate_and_score(
        [joined_311, joined_ce, joined_police],
        ['311', 'code_enforcement', 'police_calls']
    )

    # Save output
    output = results.to_dict(orient='records')
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f)

    print(f"\nOutput: {len(output)} records saved to {OUTPUT_FILE}")
    print(f"File size: {os.path.getsize(OUTPUT_FILE) / 1024 / 1024:.1f} MB")

    # Summary stats
    print(f"\nBeats: {results['beat'].nunique()}")
    print(f"Year range: {results['year'].min()}-{results['year'].max()}")
    print(f"Sources: {results['source'].unique().tolist()}")


if __name__ == '__main__':
    main()
