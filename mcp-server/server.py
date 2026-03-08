"""
Neighborhood Issue Tracker — MCP Server
Exposes tools for querying local San Diego civic data and formatting for ArcGIS.
"""

import os
import json
import logging
from typing import Optional

import pandas as pd
import geopandas as gpd
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DATA = os.path.join(os.path.dirname(__file__), '..', 'data')

mcp = FastMCP("neighborhood-issue-tracker")

# --- Cached data ---
_qol_data: Optional[pd.DataFrame] = None
_beats_gdf: Optional[gpd.GeoDataFrame] = None
_arcgis_token: Optional[dict] = None


def _load_qol_data() -> pd.DataFrame:
    global _qol_data
    if _qol_data is None:
        path = os.path.join(BASE_DATA, 'neighborhood_qol.json')
        with open(path) as f:
            records = json.load(f)
        _qol_data = pd.DataFrame(records)
        logger.info(f"Loaded {len(_qol_data)} QoL records")
    return _qol_data


def _load_beats() -> gpd.GeoDataFrame:
    global _beats_gdf
    if _beats_gdf is None:
        shp_path = os.path.join(BASE_DATA, 'pd_beats_datasd', 'pd_beats_datasd.shp')
        _beats_gdf = gpd.read_file(shp_path)
        if _beats_gdf.crs and _beats_gdf.crs.to_epsg() != 4326:
            _beats_gdf = _beats_gdf.to_crs(epsg=4326)
        _beats_gdf['beat'] = _beats_gdf['beat'].astype(str).str.strip()
        logger.info(f"Loaded {len(_beats_gdf)} PD beats")
    return _beats_gdf


# --- Inbound tools (local data) ---

@mcp.tool()
def query_311(
    category: Optional[str] = None,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    beat: Optional[str] = None,
) -> str:
    """Query 311/Get It Done QoL data by category, year, quarter, or beat."""
    df = _load_qol_data()
    df = df[df['source'] == '311']
    if category:
        df = df[df['q_o_l_category'] == category]
    if year:
        df = df[df['year'] == year]
    if quarter:
        df = df[df['quarter'] == quarter]
    if beat:
        df = df[df['beat'] == str(beat)]
    return df.to_json(orient='records')


@mcp.tool()
def query_code_enforcement(
    category: Optional[str] = None,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    beat: Optional[str] = None,
) -> str:
    """Query code enforcement QoL data by category, year, quarter, or beat."""
    df = _load_qol_data()
    df = df[df['source'] == 'code_enforcement']
    if category:
        df = df[df['q_o_l_category'] == category]
    if year:
        df = df[df['year'] == year]
    if quarter:
        df = df[df['quarter'] == quarter]
    if beat:
        df = df[df['beat'] == str(beat)]
    return df.to_json(orient='records')


@mcp.tool()
def query_police_calls(
    category: Optional[str] = None,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    beat: Optional[str] = None,
) -> str:
    """Query police calls for service QoL data by category, year, quarter, or beat."""
    df = _load_qol_data()
    df = df[df['source'] == 'police_calls']
    if category:
        df = df[df['q_o_l_category'] == category]
    if year:
        df = df[df['year'] == year]
    if quarter:
        df = df[df['quarter'] == quarter]
    if beat:
        df = df[df['beat'] == str(beat)]
    return df.to_json(orient='records')


@mcp.tool()
def load_pd_beats() -> str:
    """Load PD beats shapefile and return beat boundaries as GeoJSON."""
    gdf = _load_beats()
    return gdf[['beat', 'name', 'geometry']].to_json()


@mcp.tool()
def aggregate_by_neighborhood(
    source: Optional[str] = None,
    category: Optional[str] = None,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
) -> str:
    """Aggregate QoL scores by neighborhood with optional filters.
    source: '311', 'code_enforcement', 'police_calls', or 'all_sources_combined'
    category: 'critical', 'non_critical', or 'all'
    """
    df = _load_qol_data()
    if source:
        df = df[df['source'] == source]
    if category:
        df = df[df['q_o_l_category'] == category]
    if year:
        df = df[df['year'] == year]
    if quarter:
        df = df[df['quarter'] == quarter]

    agg = df.groupby('beat').agg(
        avg_score=('score', 'mean'),
        total_records=('score', 'count'),
    ).reset_index()

    return agg.to_json(orient='records')


# --- Outbound tools (ESRI) ---

@mcp.tool()
def get_arcgis_token() -> str:
    """Get or refresh an ArcGIS OAuth2 token using client credentials."""
    global _arcgis_token

    client_id = os.getenv('ARCGIS_CLIENT_ID')
    client_secret = os.getenv('ARCGIS_CLIENT_SECRET')

    if not client_id or not client_secret:
        return json.dumps({"error": "ARCGIS_CLIENT_ID and ARCGIS_CLIENT_SECRET must be set in .env"})

    resp = requests.post(
        'https://www.arcgis.com/sharing/rest/oauth2/token',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
        },
    )
    resp.raise_for_status()
    token_data = resp.json()
    _arcgis_token = token_data
    logger.info("ArcGIS token acquired")
    return json.dumps({"access_token": token_data.get("access_token"), "expires_in": token_data.get("expires_in")})


@mcp.tool()
def format_for_esri(
    source: str = 'all_sources_combined',
    category: str = 'all',
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    month: Optional[int] = None,
) -> str:
    """Convert QoL data joined with beat polygons to GeoJSON for ArcGIS Maps SDK.
    Returns a GeoJSON FeatureCollection with beat polygons and QoL properties.
    """
    df = _load_qol_data()
    beats = _load_beats()

    # Filter
    if source:
        df = df[df['source'] == source]
    if category:
        df = df[df['q_o_l_category'] == category]
    if year:
        df = df[df['year'] == year]
    if quarter:
        df = df[df['quarter'] == quarter]
    if month:
        df = df[df['month'] == month]

    # Aggregate per beat for the filtered view
    agg = df.groupby('beat').agg(
        avg_score=('score', 'mean'),
        total_records=('score', 'count'),
    ).reset_index()

    # Join with beat geometries
    merged = beats[['beat', 'name', 'geometry']].merge(agg, on='beat', how='left')
    merged['avg_score'] = merged['avg_score'].fillna(0.0).round(4)
    merged['total_records'] = merged['total_records'].fillna(0).astype(int)

    return merged.to_json()


@mcp.tool()
def geocode_address(address: str) -> str:
    """Geocode an address using ArcGIS geocoding service. Returns lat/lng."""
    global _arcgis_token

    if not _arcgis_token:
        get_arcgis_token()

    token = _arcgis_token.get('access_token', '') if _arcgis_token else ''

    resp = requests.get(
        'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates',
        params={
            'f': 'json',
            'singleLine': address,
            'outFields': 'Match_addr,Addr_type',
            'token': token,
        },
    )
    resp.raise_for_status()
    data = resp.json()

    candidates = data.get('candidates', [])
    if not candidates:
        return json.dumps({"error": "No results found"})

    top = candidates[0]
    return json.dumps({
        "address": top.get('address'),
        "lat": top['location']['y'],
        "lng": top['location']['x'],
        "score": top.get('score'),
    })


# --- HTTP endpoint for frontend ---

@mcp.tool()
def get_geojson_for_map(
    source: str = 'all_sources_combined',
    category: str = 'all',
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    month: Optional[int] = None,
) -> str:
    """Convenience tool: returns GeoJSON ready for direct use in ArcGIS Maps SDK.
    Same as format_for_esri but returns as a proper GeoJSON FeatureCollection.
    """
    return format_for_esri(source, category, year, quarter, month)


if __name__ == '__main__':
    mcp.run()
