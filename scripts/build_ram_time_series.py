#!/usr/bin/env python3
"""Build RAM daily median price series from historical snapshot CSVs.

Saves to: data/processed/ram_price_index.csv
"""
from pathlib import Path
import re
import pandas as pd
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

ROOT = Path(__file__).resolve().parents[1]
HIST_DIR = ROOT / 'data' / 'converted_csv' / 'computer' / 'ram-deals-main' / 'historical-ram-deals-data'
OUT = ROOT / 'data' / 'processed' / 'ram_price_index.csv'
OUT.parent.mkdir(parents=True, exist_ok=True)

def parse_price(x):
    if pd.isna(x):
        return np.nan
    s = str(x)
    s = re.sub(r'[\$€£¥]|USD|EUR|GBP|\s+USD|\s+EUR', '', s, flags=re.I)
    s = re.sub(r"[^0-9.,-]", "", s)
    if s == '':
        return np.nan
    s = s.replace(',', '')
    try:
        return float(s)
    except Exception:
        return np.nan


def find_price_column(df):
    for c in df.columns:
        if 'price' in c.lower() or '$/gb' in c.lower() or 'amount' in c.lower():
            return c
    return None


def compute_medians_for_file(fpath):
    # try to extract date from filename
    m = re.search(r'(\d{4}-\d{2}-\d{2})', fpath.name)
    if m:
        date = pd.to_datetime(m.group(1)).date()
    else:
        date = pd.to_datetime(fpath.stat().st_mtime, unit='s').date()

    try:
        df = pd.read_csv(fpath)
    except Exception:
        logging.warning(f'Failed to read {fpath}, skipping')
        return None

    price_col = find_price_column(df)
    if price_col is None:
        logging.warning(f'No price column in {fpath}, skipping')
        return None

    title_col = None
    for c in df.columns:
        if 'title' in c.lower() or 'name' in c.lower() or 'model' in c.lower():
            title_col = c
            break
    if title_col is None:
        title_col = df.columns[0]

    df = df[[title_col, price_col]].dropna(subset=[price_col])
    df['price_num'] = df[price_col].apply(parse_price)
    df = df.dropna(subset=['price_num'])

    s = df[title_col].astype(str).str.lower()
    mask_16 = s.str.contains(r'16\s?gb')
    mask_32 = s.str.contains(r'32\s?gb')
    mask_ddr4 = s.str.contains('ddr4')
    mask_ddr5 = s.str.contains('ddr5')

    def median(mask):
        sub = df[mask]
        if sub.empty:
            return np.nan
        return sub['price_num'].median()

    return {
        'date': date,
        'ram_16gb_median': median(mask_16),
        'ram_32gb_median': median(mask_32),
        'ram_ddr4_median': median(mask_ddr4),
        'ram_ddr5_median': median(mask_ddr5),
    }


def main():
    files = sorted([p for p in HIST_DIR.iterdir() if p.is_file()])
    logging.info(f'Found {len(files)} snapshot files in {HIST_DIR}')
    rows = []
    for f in files:
        r = compute_medians_for_file(f)
        if r:
            rows.append(r)

    if not rows:
        logging.error('No data collected from snapshots')
        return

    df_out = pd.DataFrame(rows).drop_duplicates(subset=['date']).sort_values('date')
    df_out.to_csv(OUT, index=False)
    logging.info(f'Wrote time series with {len(df_out)} dates to {OUT}')


if __name__ == '__main__':
    main()
