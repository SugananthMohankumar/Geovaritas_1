# reliability.py — Phase 7: Source Reliability Engine
# Calculates a reliability score for each source

import pandas as pd
from config import PROCESSED_DATA_PATH, SOURCE_RELIABILITY

def run_reliability():
    print("\n── Phase 7: Source Reliability Engine ──")

    df       = pd.read_csv(PROCESSED_DATA_PATH)
    results  = []

    for source, base_score in SOURCE_RELIABILITY.items():
        source_df = df[df['source'] == source]

        if source_df.empty:
            continue

        # Freshness score — based on quality column average
        freshness = source_df['quality'].mean()

        # Coverage score — how many locations this source covers
        total_locations = df.groupby(['lat','lon']).ngroups
        source_locations = source_df.groupby(['lat','lon']).ngroups
        coverage = source_locations / total_locations

        # Final reliability score
        reliability = (
            0.5 * base_score +
            0.3 * freshness  +
            0.2 * coverage
        )

        results.append({
            'source'      : source,
            'base_score'  : round(base_score,   2),
            'freshness'   : round(freshness,     2),
            'coverage'    : round(coverage,      2),
            'reliability' : round(reliability,   2)
        })

        print(f"  {source:<20} reliability: {reliability:.0%}")

    # Save
    reliability_df = pd.DataFrame(results)
    reliability_df.to_csv("data/processed/reliability.csv", index=False)

    print(f"\n── Reliability Table ──")
    print(reliability_df.to_string())
    print(f"\n  Saved to: data/processed/reliability.csv")

    return reliability_df

if __name__ == "__main__":
    run_reliability()