# config.py — GeoVeritas Project Foundation
# This file is imported by every other script
# Change values here and everything updates automatically

# ── Flood Event ──────────────────────────────────────────
EVENT_NAME    = "Kerala Flood 2018"
EVENT_DATE    = "2018-08-01"
EVENT_ENDDATE = "2018-08-31"

# ── Bounding Box (Kerala, India) ─────────────────────────
# format: (min_lon, min_lat, max_lon, max_lat)
BBOX = (74.8, 8.4, 77.6, 12.8)

MIN_LON = 74.8
MIN_LAT = 8.4
MAX_LON = 77.6
MAX_LAT = 12.8

# ── Center Point ─────────────────────────────────────────
CENTER_LAT = 10.8505
CENTER_LON = 76.2711

# ── File Paths ───────────────────────────────────────────
OSM_RAW_PATH        = "data/raw/southern-zone.gpkg"
PROCESSED_DATA_PATH = "data/processed/canonical.csv"

# ── Source Names ─────────────────────────────────────────
SOURCES = [
    "Sentinel-1 SAR",
    "GPM Rainfall",
    "USGS Gauge",
    "GloFAS Model",
    "OpenStreetMap"
]

# ── Trust Score Weights ───────────────────────────────────
# Must add up to 1.0
WEIGHTS = {
    "source_reliability"  : 0.30,
    "cross_agreement"     : 0.30,
    "physical_plausibility": 0.20,
    "recency"             : 0.20,
}

# ── Source Base Reliability ───────────────────────────────
# Starting reliability score per source (0 to 1)
# Based on known accuracy of each data source
SOURCE_RELIABILITY = {
    "Sentinel-1 SAR" : 0.94,
    "GPM Rainfall"   : 0.91,
    "USGS Gauge"     : 0.87,
    "GloFAS Model"   : 0.73,
    "OpenStreetMap"  : 0.90,
}

# ── Risk Thresholds ───────────────────────────────────────
TRUST_HIGH   = 0.75   # above this = high confidence
TRUST_MEDIUM = 0.55   # between this and HIGH = medium
                      # below MEDIUM = low confidence