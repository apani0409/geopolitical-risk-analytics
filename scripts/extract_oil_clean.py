#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'

def process_file(src: Path, dst: Path, col_names):
    logging.info(f'Reading {src} (sheet: Data 1)')
    try:
        df = pd.read_excel(src, sheet_name='Data 1')
    except Exception:
        df = pd.read_excel(src)

    # keep first two columns (date, price) and rename
    df = df.iloc[:, :2]
    df.columns = col_names

    # drop empty rows
    df = df.dropna()

    dst.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dst, index=False)
    logging.info(f'Wrote cleaned CSV to {dst}')


def main():
    oil_dir = DATA_DIR / 'energy' / 'oil'

    rbrt = oil_dir / 'RBRTEd.xls'
    rwtt = oil_dir / 'RWTCd.xls'

    if rbrt.exists():
        out = DATA_DIR / 'energy' / 'brent_daily.csv'
        process_file(rbrt, out, ['date', 'brent_price_usd'])
    else:
        logging.warning(f'Missing file: {rbrt}')

    if rwtt.exists():
        out2 = DATA_DIR / 'energy' / 'wti_daily.csv'
        process_file(rwtt, out2, ['date', 'wti_price_usd'])
    else:
        logging.warning(f'Missing file: {rwtt}')


if __name__ == '__main__':
    main()
