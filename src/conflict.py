# conflict.py — Phase 6: Conflict Detection
# Finds disagreements between sources for the same location

import pandas as pd
from config import PROCESSED_DATA_PATH

def run_conflict_detection():
    print("\n── Phase 6: Conflict Detection ──")

    df = pd.read_csv(PROCESSED_DATA_PATH)
    conflicts = []

    # Group by location
    locations = df.groupby(['lat', 'lon'])

    for (lat, lon), group in locations:

        # Conflict 1 — SAR says water but GloFAS says low risk
        sar  = group[group['source'] == 'Sentinel-1 SAR']
        glofas = group[group['source'] == 'GloFAS Model']

        if not sar.empty and not glofas.empty:
            sar_water    = str(sar['value'].values[0]).lower()
            glofas_risk  = str(glofas['value'].values[0]).lower()

            if sar_water == 'true' and glofas_risk == 'low':
                conflicts.append({
                    'lat'         : lat,
                    'lon'         : lon,
                    'conflict'    : 'SAR detects water but GloFAS says Low risk',
                    'source_a'    : 'Sentinel-1 SAR',
                    'source_b'    : 'GloFAS Model',
                    'severity'    : 'HIGH'
                })
                print(f"  ⚠️  HIGH conflict at ({lat},{lon}): SAR vs GloFAS")

        # Conflict 2 — High rainfall but no water detected
        rain = group[group['source'] == 'GPM Rainfall']
        if not rain.empty and not sar.empty:
            try:
                rainfall  = float(str(rain['value'].values[0]).strip())
            except (ValueError, TypeError):
                rainfall  = 0.0
            sar_water = str(sar['value'].values[0]).lower().strip()
            if rainfall > 100 and sar_water == 'false':
                conflicts.append({
                    'lat'         : lat,
                    'lon'         : lon,
                    'conflict'    : 'High rainfall but SAR shows no water',
                    'source_a'    : 'GPM Rainfall',
                    'source_b'    : 'Sentinel-1 SAR',
                    'severity'    : 'MEDIUM'
                })
                print(f"  ⚠️  MEDIUM conflict at ({lat},{lon}): Rainfall vs SAR")

        # Conflict 3 — High river level but no flood risk
        gauge = group[group['source'] == 'USGS Gauge']
        if not gauge.empty and not glofas.empty:
            try:
                river_level = float(str(gauge['value'].values[0]).strip())
            except (ValueError, TypeError):
                river_level = 0.0
            glofas_risk = str(glofas['value'].values[0]).lower().strip()

            if river_level > 7 and glofas_risk == 'low':
                conflicts.append({
                    'lat'         : lat,
                    'lon'         : lon,
                    'conflict'    : 'High river level but GloFAS says Low risk',
                    'source_a'    : 'USGS Gauge',
                    'source_b'    : 'GloFAS Model',
                    'severity'    : 'MEDIUM'
                })
                print(f"  ⚠️  MEDIUM conflict at ({lat},{lon}): Gauge vs GloFAS")

    # Summary
    print(f"\n── Conflict Summary ──")
    print(f"  Total locations checked : {df.groupby(['lat','lon']).ngroups}")
    print(f"  Conflicts found         : {len(conflicts)}")

    if conflicts:
        conflict_df = pd.DataFrame(conflicts)
        print(f"\n── Conflict Table ──")
        print(conflict_df.to_string())
        # Save conflicts
        conflict_df.to_csv("data/processed/conflicts.csv", index=False)
        print(f"\n  Saved to: data/processed/conflicts.csv")
    else:
        print("  ✅ No conflicts detected")

    return conflicts

if __name__ == "__main__":
    run_conflict_detection()