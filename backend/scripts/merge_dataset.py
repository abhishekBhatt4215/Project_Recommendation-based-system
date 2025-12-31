# backend/scripts/merge_dataset.py
"""
Updated merge script for your project layout.
This version expects cleaned CSVs in: project_root/data/processed/
Files used (exact names):
 - City_clean.csv
 - Expanded_Destinations_clean.csv
 - Places_clean.csv

It will produce: project_root/data/processed/merged_dataset.csv

Run from project root:
    python backend/scripts/merge_dataset.py

This script:
 - auto-finds the three files in data/processed (using the exact names you provided)
 - normalizes column headers and values
 - creates a merge_key and performs outer merges: city <-> expanded <-> places
 - prints diagnostics and saves merged_dataset.csv
"""
from pathlib import Path
import pandas as pd
import re
import sys
from difflib import get_close_matches


DATA_SUBDIR = Path('data') / 'processed'

CITY_FILENAME = 'City_clean.csv'                      
EXPANDED_FILENAME = 'Expanded_Destinations_clean.csv'
PLACE_FILENAME = 'Places_clean.csv'
OUTPUT_FILENAME = 'merged_dataset.csv'
# ----------------------------------------


def sane_col_name(c: str) -> str:
    c = str(c).strip()
    c = re.sub(r'\s+', ' ', c)
    c = re.sub(r'[^0-9a-zA-Z]+', '_', c)
    return c.strip('_').lower()


def clean_df_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {c: sane_col_name(c) for c in df.columns}
    return df.rename(columns=rename_map)


def read_csv_flexible(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
   
    df = pd.read_csv(path)
   
    if len(df.columns) == 1:
        for sep in [';', '\t', '|']:
            try:
                df2 = pd.read_csv(path, sep=sep)
                if len(df2.columns) > 1:
                    print(f"Autodetected separator '{sep}' for {path.name}")
                    return df2
            except Exception:
                pass
    return df


def find_key(columns, candidates):
    cols = list(columns)
    for kw in candidates:
        if kw in cols:
            return kw
    for kw in candidates:
        for c in cols:
            if kw in c:
                return c
    for kw in candidates:
        matches = get_close_matches(kw, cols, n=1, cutoff=0.7)
        if matches:
            return matches[0]
    return None


def canonicalize_series(s: pd.Series) -> pd.Series:
    s = s.fillna('').astype(str)
    s = s.str.replace(r'\s+', ' ', regex=True).str.strip().str.lower()
    return s


def main():
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[2] if len(script_path.parents) >= 3 else script_path.parent
    data_dir = project_root / DATA_SUBDIR

    print("Project root:", project_root)
    print("Reading CSVs from:", data_dir)

    if not data_dir.exists():
        print("ERROR: data directory not found:", data_dir, file=sys.stderr)
        sys.exit(1)

    city_fp = data_dir / CITY_FILENAME
    expanded_fp = data_dir / EXPANDED_FILENAME
    place_fp = data_dir / PLACE_FILENAME

   
    missing = [str(p) for p in (city_fp, expanded_fp, place_fp) if not p.exists()]
    if missing:
        print("ERROR: The following expected files were not found in", data_dir)
        for m in missing:
            print(' -', m)
        print("Please verify file names or move the files into:", data_dir)
        sys.exit(1)

  
    city = read_csv_flexible(city_fp)
    expanded = read_csv_flexible(expanded_fp)
    place = read_csv_flexible(place_fp)

   
    city = clean_df_columns(city)
    expanded = clean_df_columns(expanded)
    place = clean_df_columns(place)

    print('\nColumns (normalized):')
    print(' city   :', list(city.columns))
    print(' expanded:', list(expanded.columns))
    print(' place  :', list(place.columns))

  
    candidates = ['city', 'destination', 'name', 'place', 'location', 'town']

    city_key = find_key(city.columns, candidates) or list(city.columns)[0]
    expanded_key = find_key(expanded.columns, candidates) or list(expanded.columns)[0]
    place_key = find_key(place.columns, candidates) or list(place.columns)[0]

    print('\nUsing detected merge keys:')
    print(' city_key    ->', city_key)
    print(' expanded_key->', expanded_key)
    print(' place_key   ->', place_key)

   
    city['merge_key'] = canonicalize_series(city[city_key])
    expanded['merge_key'] = canonicalize_series(expanded[expanded_key])
    place['merge_key'] = canonicalize_series(place[place_key])

    print('\nUnique non-empty merge_key counts:')
    print(' city    :', city['merge_key'].replace('', pd.NA).dropna().nunique())
    print(' expanded:', expanded['merge_key'].replace('', pd.NA).dropna().nunique())
    print(' place   :', place['merge_key'].replace('', pd.NA).dropna().nunique())

  
    city_expanded = pd.merge(
        city, expanded,
        on='merge_key',
        how='outer',
        suffixes=('_city', '_expanded'),
        indicator='merge_city_expanded'
    )

    
    full = pd.merge(
        city_expanded, place,
        on='merge_key',
        how='outer',
        suffixes=('', '_place'),
        indicator='merge_with_place'
    )

    print('\nMerge diagnostics:')
    print(' city <-> expanded:', city_expanded['merge_city_expanded'].value_counts().to_dict())
    print(' (city+expanded) <-> place:', full['merge_with_place'].value_counts().to_dict())

    out_fp = data_dir / OUTPUT_FILENAME
    out = full.copy()
    # drop indicator columns before saving
    for col in ['merge_city_expanded', 'merge_with_place']:
        if col in out.columns:
            out.drop(columns=[col], inplace=True)

    out.to_csv(out_fp, index=False)
    print('\nMerged dataset saved to:', out_fp)

    # also write inner-match subset (rows with non-empty merge_key)
    inner_fp = data_dir / ('merged_dataset_inner_matches.csv')
    inner = full[(full['merge_key'].notna()) & (full['merge_key'] != '')]
    inner.to_csv(inner_fp, index=False)
    print('Inner-match rows saved to:', inner_fp)

    print('\nDone.')

if __name__ == '__main__':
    main()
