#!/usr/bin/env python3
"""Fill missing values in GPU and RAM price index series.

Creates files:
 - data/processed/gpu_price_index_filled.csv
 - data/processed/ram_price_index_filled.csv

Default method: forward-fill then backward-fill for leading NaNs.
"""
from pathlib import Path
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'data' / 'processed'


def fill_file(name):
    src = PROC / name
    if not src.exists():
        logging.warning(f'Missing {src}, skipping')
        return
    df = pd.read_csv(src, parse_dates=['date'])
    cols = [c for c in df.columns if c != 'date']
    # forward-fill then backward-fill remaining
    df[cols] = df[cols].ffill().bfill()
    out = PROC / src.with_suffix('').name
    # build output filename with _filled
    out = PROC / (src.stem + '_filled.csv')
    df.to_csv(out, index=False)
    logging.info(f'Wrote filled series to {out}')


def main():
    fill_file('gpu_price_index.csv')
    fill_file('ram_price_index.csv')


if __name__ == '__main__':
    main()
