# trust_engine.py — Phase 8: GeoTrust Engine
# Calculates final trust score per location

import pandas as pd
from config import (PROCESSED_DATA_PATH, WEIGHTS,
                    TRUST_HIGH, TRUST_MEDIUM)

def run_trust_engine():
    print("\n── Phase 8: GeoTrust Engine ──")

    df           = pd.read_csv(PROCESSED_DATA_PATH)
    reliability  = pd.read_csv("data/processed/reliability.csv")
    conflicts    = pd.read_csv("data/processed/conflicts.csv") \
                   if __import__('os').path.exists(
                       "data/processed/conflicts.csv") else pd.DataFrame()

    # Build reliability lookup
    rel_lookup = dict(zip(
        reliability['source'],
        reliability['reliability']
    ))

    results = []
    locations = df.groupby(['lat', 'lon'])

    for (lat, lon), group in locations:

        # ── Component 1: Source Reliability ──────────────
        avg_reliability = group['source'].map(rel_lookup).mean()

        # ── Component 2: Cross Source Agreement ──────────
        total_sources  = len(group)
        # Count conflicts at this location
        if not conflicts.empty:
            loc_conflicts = conflicts[
                (conflicts['lat'] == lat) &
                (conflicts['lon'] == lon)
            ]
            conflict_count = len(loc_conflicts)
        else:
            conflict_count = 0

        agreement = 1 - (conflict_count / max(total_sources, 1))

        # ── Component 3: Physical Plausibility ───────────
        # If SAR detects water AND rainfall > 50mm = plausible
        sar   = group[group['source'] == 'Sentinel-1 SAR']
        rain  = group[group['source'] == 'GPM Rainfall']

        plausibility = 0.5  # default
        if not sar.empty and not rain.empty:
            sar_water = str(sar['value'].values[0]).lower().strip()
            try:
                rainfall = float(str(rain['value'].values[0]).strip())
            except (ValueError, TypeError):
                rainfall = 0.0
                
            if sar_water == 'true' and rainfall > 50:
                plausibility = 1.0
            elif sar_water == 'false' and rainfall < 50:
                plausibility = 0.9
            else:
                plausibility = 0.4

        # ── Component 4: Recency ─────────────────────────
        # All data is from same date so recency = 1.0
        recency = 1.0

        # ── Final Trust Score ─────────────────────────────
        trust = (
            WEIGHTS['source_reliability']   * avg_reliability +
            WEIGHTS['cross_agreement']       * agreement       +
            WEIGHTS['physical_plausibility'] * plausibility    +
            WEIGHTS['recency']               * recency
        )

        # Uncertainty band (±)
        uncertainty = round(0.05 + (conflict_count * 0.03), 2)

        # Risk level
        if trust >= TRUST_HIGH:
            risk = "HIGH"
        elif trust >= TRUST_MEDIUM:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        results.append({
            'lat'           : lat,
            'lon'           : lon,
            'trust_score'   : round(trust, 2),
            'uncertainty'   : f"±{uncertainty}",
            'risk_level'    : risk,
            'agreement'     : round(agreement, 2),
            'plausibility'  : round(plausibility, 2),
            'conflicts'     : conflict_count
        })

    # Results
    trust_df = pd.DataFrame(results)
    trust_df.to_csv("data/processed/trust_scores.csv", index=False)

    print(f"\n── Trust Scores by Location ──")
    for _, row in trust_df.iterrows():
        bar = "█" * int(row['trust_score'] * 20)
        print(f"  ({row['lat']},{row['lon']}) "
              f"Trust: {row['trust_score']:.0%} "
              f"{bar} "
              f"Risk: {row['risk_level']} "
              f"Uncertainty: {row['uncertainty']}")

    print(f"\n── Overall Event Trust Score ──")
    overall = trust_df['trust_score'].mean()
    print(f"  GeoTrust Score : {overall:.0%}")
    print(f"\n  Saved to: data/processed/trust_scores.csv")

    return trust_df

if __name__ == "__main__":
    run_trust_engine()