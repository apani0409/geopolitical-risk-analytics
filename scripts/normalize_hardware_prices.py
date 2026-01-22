#!/usr/bin/env python3
"""Normalize GPU and RAM listings into daily median price indices.

Outputs:
 - data/processed/gpu_price_index.csv
 - data/processed/ram_price_index.csv

Uses only pandas and standard library.
"""
from pathlib import Path
import re
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUT = DATA / 'processed'
OUT.mkdir(parents=True, exist_ok=True)


def find_column(df, candidates):
    cols = list(df.columns)
    for c in candidates:
        for col in cols:
            if c.lower() in str(col).lower():
                return col
    return None


def parse_price(x):
    if pd.isna(x):
        return None
    s = str(x)
    # remove currency symbols and words
    s = re.sub(r'[\$€£¥]|USD|EUR|GBP|\s+USD|\s+EUR', '', s, flags=re.I)
    # remove non-numeric except . and ,
    s = re.sub(r"[^0-9.,-]", "", s)
    if s == '':
        return None
    # normalize thousands separators: remove commas
    s = s.replace(',', '')
    try:
        return float(s)
    except Exception:
        return None


def normalize_gpu(path_candidates):
    # try candidate paths in order
    df = None
    source_path = None
    for p in path_candidates:
        if p.exists():
            df = pd.read_csv(p)
            source_path = p
            logging.info(f'Loaded GPU data from {p}')
            break
    if df is None:
        logging.error('GPU source CSV not found in candidates.')
        return

    title_col = find_column(df, ['title', 'name', 'model']) or df.columns[0]
    date_col = find_column(df, ['date', 'posted', 'created'])
    price_col = find_column(df, ['price', 'amount', 'precio'])

    if price_col is None:
        logging.error('No price column found in GPU CSV')
        return

    cols = [title_col, price_col]
    if date_col is not None:
        cols.insert(0, date_col)
    df = df[cols].rename(columns={title_col: 'title', price_col: 'price', **({date_col: 'date'} if date_col is not None else {})})
    if date_col is not None:
        df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
    else:
        # use file modification date as snapshot date
        mtime = pd.to_datetime(source_path.stat().st_mtime, unit='s').date()
        df['date'] = mtime
    df['price_num'] = df['price'].apply(parse_price)

    # drop invalid prices and dates
    df = df.dropna(subset=['date', 'price_num'])

    # extract model numbers from title
    def tier_from_title(t):
        if pd.isna(t):
            return None
        # find first 3-4 digit token
        m = re.search(r"(\d{3,4})", str(t))
        if not m:
            return None
        model = m.group(1)
        if re.search(r'8?0$|90$|80$|90', model):
            return 'high'
        if re.search(r'6?0$|70$|60$|70', model):
            return 'mid'
        if re.search(r'50$|50', model):
            return 'low'
        # fallback: classify by presence of digits ending with 0-9
        return None

    df['tier'] = df['title'].apply(tier_from_title)
    df = df.dropna(subset=['tier'])

    # group by date and tier and compute median
    med = df.groupby(['date', 'tier'])['price_num'].median().unstack()

    # ensure columns exist
    for col in ['high', 'mid', 'low']:
        if col not in med.columns:
            med[col] = pd.NA

    med = med.reset_index().rename(columns={'high': 'gpu_high_median', 'mid': 'gpu_mid_median', 'low': 'gpu_low_median'})
    med = med[['date', 'gpu_high_median', 'gpu_mid_median', 'gpu_low_median']]
    med['date'] = pd.to_datetime(med['date'])
    med = med.sort_values('date')

    out_path = OUT / 'gpu_price_index.csv'
    med.to_csv(out_path, index=False)
    logging.info(f'Wrote GPU price index to {out_path}')


def normalize_ram(path_candidates):
    df = None
    source_path = None
    for p in path_candidates:
        if p.exists():
            df = pd.read_csv(p)
            source_path = p
            logging.info(f'Loaded RAM data from {p}')
            break
    if df is None:
        logging.error('RAM source CSV not found in candidates.')
        return

    title_col = find_column(df, ['title', 'name', 'product']) or df.columns[0]
    date_col = find_column(df, ['date', 'posted', 'created'])
    price_col = find_column(df, ['price', 'amount', 'precio'])

    if price_col is None:
        logging.error('No price column found in RAM CSV')
        return

    cols = [title_col, price_col]
    if date_col is not None:
        cols.insert(0, date_col)
    df = df[cols].rename(columns={title_col: 'title', price_col: 'price', **({date_col: 'date'} if date_col is not None else {})})
    if date_col is not None:
        df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
    else:
        mtime = pd.to_datetime(source_path.stat().st_mtime, unit='s').date()
        df['date'] = mtime
    df['price_num'] = df['price'].apply(parse_price)

    df = df.dropna(subset=['date', 'price_num'])

    s = df['title'].astype(str).str.lower()
    mask_16 = s.str.contains(r'16\s?gb')
    mask_32 = s.str.contains(r'32\s?gb')
    mask_ddr4 = s.str.contains('ddr4')
    mask_ddr5 = s.str.contains('ddr5')

    # helper to compute median series for a mask
    def median_for(mask, label):
        sub = df[mask]
        if sub.empty:
            return pd.Series([], dtype='float64')
        med = sub.groupby('date')['price_num'].median()
        med.name = label
        return med

    m16 = median_for(mask_16, 'ram_16gb_median')
    m32 = median_for(mask_32, 'ram_32gb_median')
    m4 = median_for(mask_ddr4, 'ram_ddr4_median')
    m5 = median_for(mask_ddr5, 'ram_ddr5_median')

    # combine into single DataFrame by outer join on date
    df_out = pd.concat([m16, m32, m4, m5], axis=1).reset_index()
    df_out['date'] = pd.to_datetime(df_out['date'])
    df_out = df_out.sort_values('date')

    out_path = OUT / 'ram_price_index.csv'
    df_out.to_csv(out_path, index=False)
    logging.info(f'Wrote RAM price index to {out_path}')


def main():
    # GPU candidate paths (user-provided and converted fallback)
    gpu_candidates = [
        DATA / 'computer' / 'current-gpu-deals.csv',
        DATA / 'converted_csv' / 'computer' / 'gpu-deals-main' / 'current-gpu-deals.csv',
    ]

    ram_candidates = [
        DATA / 'computer' / 'current-ram-deals.csv',
        DATA / 'converted_csv' / 'computer' / 'ram-deals-main' / 'current-ram-deals.csv',
    ]

    normalize_gpu(gpu_candidates)
    normalize_ram(ram_candidates)


if __name__ == '__main__':
    main()
