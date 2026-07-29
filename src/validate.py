# validate.py — Phase 5: Validation Engine
# Checks canonical data for quality issues before trust scoring

import pandas as pd
from config import PROCESSED_DATA_PATH, SOURCES

def run_validation():
    print("\n── Phase 5: Validation Engine ──")
    
    df = pd.read_csv(PROCESSED_DATA_PATH)
    issues = []

    # Check 1 — Missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        issues.append(f"❌ Missing values found: {missing}")
    else:
        print("  ✅ No missing values")

    # Check 2 — Invalid coordinates
    invalid_coords = df[
        (df['lat'] < -90)  | (df['lat'] > 90) |
        (df['lon'] < -180) | (df['lon'] > 180)
    ]
    if len(invalid_coords) > 0:
        issues.append(f"❌ Invalid coordinates: {len(invalid_coords)} rows")
    else:
        print("  ✅ All coordinates valid")

    # Check 3 — Quality score range
    invalid_quality = df[
        (df['quality'] < 0) | (df['quality'] > 1)
    ]
    if len(invalid_quality) > 0:
        issues.append(f"❌ Invalid quality scores: {len(invalid_quality)} rows")
    else:
        print("  ✅ All quality scores valid (0-1)")

    # Check 4 — Unknown sources
    unknown_sources = df[~df['source'].isin(SOURCES)]
    if len(unknown_sources) > 0:
        issues.append(f"❌ Unknown sources found: {unknown_sources['source'].unique()}")
    else:
        print("  ✅ All sources recognised")

    # Check 5 — Duplicate rows
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        issues.append(f"❌ Duplicate rows: {duplicates}")
    else:
        print("  ✅ No duplicate rows")

    # Summary
    print(f"\n── Validation Summary ──")
    print(f"  Total rows checked : {len(df)}")
    print(f"  Issues found       : {len(issues)}")

    if issues:
        for issue in issues:
            print(f"  {issue}")
    else:
        print("  ✅ All checks passed — data is clean")

    return df, issues

if __name__ == "__main__":
    run_validation()