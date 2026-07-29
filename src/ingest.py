# ingest.py — Phase 4: Data Ingestion Layer
# Reads all raw data sources and converts to canonical schema
# Canonical row: location | time | source | feature | value | quality

import geopandas as gpd
import pandas as pd
import fiona
from shapely.geometry import box, Point
from config import *

# ── Helper ────────────────────────────────────────────────
def make_row(lat, lon, source, feature, value, quality):
    return {
        "timestamp" : EVENT_DATE,
        "lat"       : lat,
        "lon"       : lon,
        "source"    : source,
        "feature"   : feature,
        "value"     : value,
        "quality"   : quality
    }

# ── Step 1: Inspect OSM file ──────────────────────────────
def inspect_osm():
    print("\n── Layers inside your GPK file ──")
    layers = fiona.listlayers(OSM_RAW_PATH)
    for i, layer in enumerate(layers):
        print(f"  {i}: {layer}")
    return layers

# ── Step 2: Load OSM waterways ────────────────────────────
def load_osm_waterways():
    print("\n── Loading OSM waterways ──")
    bbox_shape = box(MIN_LON, MIN_LAT, MAX_LON, MAX_LAT)
    
    gdf = gpd.read_file(
        OSM_RAW_PATH,
        layer="waterways",
        bbox=(MIN_LON, MIN_LAT, MAX_LON, MAX_LAT)
    )
    print(f"  Found {len(gdf)} waterway features")
    return gdf

# ── Step 3: Convert OSM to canonical rows ────────────────
def ingest_osm(waterways_gdf):
    print("\n── Converting OSM to canonical schema ──")
    rows = []

    # Sample 10 points across Kerala bounding box
    import numpy as np
    lats = np.linspace(MIN_LAT, MAX_LAT, 5)
    lons = np.linspace(MIN_LON, MAX_LON, 5)

    for lat in lats:
        for lon in lons:
            point = Point(lon, lat)
            
            # Check if this point is within 1km of any waterway
            try:
                distances = waterways_gdf.geometry.distance(point)
                min_dist  = distances.min()
                near_river = min_dist < 0.01  # ~1km in degrees
                value      = "Yes" if near_river else "No"
            except:
                value = "Unknown"

            row = make_row(
                lat     = lat,
                lon     = lon,
                source  = "OpenStreetMap",
                feature = "NearRiver",
                value   = value,
                quality = SOURCE_RELIABILITY["OpenStreetMap"]
            )
            rows.append(row)

    print(f"  Generated {len(rows)} canonical rows from OSM")
    return rows

# ── Step 4: Add dummy rows for other 4 sources ───────────
# (real API calls come later — this proves the pipeline works)
def ingest_dummy_sources():
    print("\n── Adding dummy data for remaining sources ──")
    rows = []

    locations = [
        (10.0889, 76.3710, "Ernakulam"),
        (9.9312,  76.2673, "Alappuzha"),
        (8.5241,  76.9366, "Thiruvananthapuram"),
        (11.2588, 75.7804, "Kozhikode"),
        (10.5276, 76.2144, "Thrissur"),
    ]

    for lat, lon, name in locations:
        # Sentinel-1 SAR
        rows.append(make_row(lat, lon,
            source  = "Sentinel-1 SAR",
            feature = "WaterDetected",
            value   = True,
            quality = SOURCE_RELIABILITY["Sentinel-1 SAR"]
        ))

        # GPM Rainfall
        rows.append(make_row(lat, lon,
            source  = "GPM Rainfall",
            feature = "RainfallMM",
            value   = 124.5,
            quality = SOURCE_RELIABILITY["GPM Rainfall"]
        ))

        # USGS Gauge
        rows.append(make_row(lat, lon,
            source  = "USGS Gauge",
            feature = "RiverLevel",
            value   = 8.3,
            quality = SOURCE_RELIABILITY["USGS Gauge"]
        ))

        # GloFAS Model — intentionally conflicts at Alappuzha
        glofas_value = "Low" if name == "Alappuzha" else "High"
        rows.append(make_row(lat, lon,
            source  = "GloFAS Model",
            feature = "FloodRisk",
            value   = glofas_value,
            quality = SOURCE_RELIABILITY["GloFAS Model"]
        ))

    print(f"  Generated {len(rows)} dummy rows")
    return rows
# ── Main: Run all ingestion and save ─────────────────────
def run_ingestion():
    all_rows = []

    # OSM real data
    layers    = inspect_osm()
    
    if "waterways" in layers:
        waterways = load_osm_waterways()
        osm_rows  = ingest_osm(waterways)
        all_rows.extend(osm_rows)
    else:
        print("  WARNING: no waterways layer found")

    # Dummy data for other sources
    dummy_rows = ingest_dummy_sources()
    all_rows.extend(dummy_rows)

    # Save to canonical CSV
    df = pd.DataFrame(all_rows)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    
    print(f"\n✅ Ingestion complete")
    print(f"   Total rows : {len(df)}")
    print(f"   Saved to   : {PROCESSED_DATA_PATH}")
    print(f"\n── Preview ──")
    print(df.head(10).to_string())
    return df

if __name__ == "__main__":
    run_ingestion()