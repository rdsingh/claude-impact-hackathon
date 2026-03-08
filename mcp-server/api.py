"""
REST API wrapper for the MCP server tools.
Serves GeoJSON and token endpoints for the ArcGIS Maps SDK frontend.
"""

import os
import json
import logging
from typing import Optional

import pandas as pd
import geopandas as gpd
import requests as http_requests
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DATA = os.path.join(os.path.dirname(__file__), '..', 'data')

# Cached data
_qol_data: Optional[pd.DataFrame] = None
_beats_gdf: Optional[gpd.GeoDataFrame] = None
_beats_geojson: Optional[dict] = None


def load_qol_data() -> pd.DataFrame:
    global _qol_data
    if _qol_data is None:
        with open(os.path.join(BASE_DATA, 'neighborhood_qol.json')) as f:
            _qol_data = pd.DataFrame(json.load(f))
        logger.info(f"Loaded {len(_qol_data)} QoL records")
    return _qol_data


def load_beats() -> gpd.GeoDataFrame:
    global _beats_gdf
    if _beats_gdf is None:
        shp_path = os.path.join(BASE_DATA, 'pd_beats_datasd', 'pd_beats_datasd.shp')
        _beats_gdf = gpd.read_file(shp_path)
        if _beats_gdf.crs and _beats_gdf.crs.to_epsg() != 4326:
            _beats_gdf = _beats_gdf.to_crs(epsg=4326)
        _beats_gdf['beat'] = _beats_gdf['beat'].astype(str).str.strip()
        logger.info(f"Loaded {len(_beats_gdf)} PD beats")
    return _beats_gdf


def load_beats_geojson() -> dict:
    global _beats_geojson
    if _beats_geojson is None:
        gdf = load_beats()
        _beats_geojson = json.loads(gdf[['beat', 'name', 'geometry']].to_json())
    return _beats_geojson


async def geojson_endpoint(request):
    """GET /api/geojson?source=...&category=...&year=...&quarter=...&month=..."""
    params = request.query_params
    source = params.get('source', 'all_sources_combined')
    category = params.get('category', 'all')
    year = params.get('year')
    quarter = params.get('quarter')
    month = params.get('month')

    df = load_qol_data()
    beats = load_beats()

    df = df[df['source'] == source]
    df = df[df['q_o_l_category'] == category]
    if year:
        df = df[df['year'] == int(year)]
    if quarter:
        df = df[df['quarter'] == int(quarter)]
    if month:
        df = df[df['month'] == int(month)]

    # Aggregate per beat
    if len(df) > 0:
        agg = df.groupby('beat').agg(
            avg_score=('score', 'mean'),
            total_records=('score', 'count'),
        ).reset_index()
    else:
        agg = pd.DataFrame(columns=['beat', 'avg_score', 'total_records'])

    merged = beats[['beat', 'name', 'geometry']].merge(agg, on='beat', how='left')
    merged['avg_score'] = merged['avg_score'].fillna(0.0).round(4)
    merged['total_records'] = merged['total_records'].fillna(0).astype(int)

    geojson = json.loads(merged.to_json())
    return JSONResponse(geojson)


async def beats_endpoint(request):
    """GET /api/beats — raw beat polygons as GeoJSON."""
    return JSONResponse(load_beats_geojson())


async def token_endpoint(request):
    """GET /api/token — get ArcGIS OAuth token."""
    client_id = os.getenv('ARCGIS_CLIENT_ID')
    client_secret = os.getenv('ARCGIS_CLIENT_SECRET')

    if not client_id or not client_secret:
        return JSONResponse({"error": "Missing ARCGIS credentials"}, status_code=500)

    resp = http_requests.post(
        'https://www.arcgis.com/sharing/rest/oauth2/token',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
        },
    )
    resp.raise_for_status()
    data = resp.json()
    return JSONResponse({
        "access_token": data.get("access_token"),
        "expires_in": data.get("expires_in"),
    })


async def filters_endpoint(request):
    """GET /api/filters — available filter values."""
    df = load_qol_data()
    return JSONResponse({
        "sources": sorted(df['source'].unique().tolist()),
        "categories": sorted(df['q_o_l_category'].unique().tolist()),
        "years": sorted(df['year'].unique().tolist()),
        "quarters": sorted(df['quarter'].unique().tolist()),
    })


async def health_endpoint(request):
    return JSONResponse({"status": "ok"})


app = Starlette(
    routes=[
        Route('/api/geojson', geojson_endpoint),
        Route('/api/beats', beats_endpoint),
        Route('/api/token', token_endpoint),
        Route('/api/filters', filters_endpoint),
        Route('/api/health', health_endpoint),
    ],
    middleware=[
        Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]),
    ],
)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
