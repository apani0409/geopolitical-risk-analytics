#!/usr/bin/env python3
"""Unified dataset builder combining all data sources.

Combines:
- Geopolitical risk indices (BBVA)
- Oil prices (Brent, WTI)
- GPU/RAM price indices
- Bitcoin prices
- Country metadata

Output: data/processed/unified_dataset.csv
"""
from pathlib import Path
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
PROC = DATA / 'processed'
PROC.mkdir(parents=True, exist_ok=True)

# Country categorization per prompt.md
COUNTRY_TAGS = {
    'USA': ['geopolitical_core', 'tech_supply_chain', 'financial_systemic'],
    'Russia': ['geopolitical_core', 'energy_markets', 'active_conflict'],
    'China': ['geopolitical_core', 'tech_supply_chain', 'strategic_minerals'],
    'Ukraine': ['geopolitical_core', 'active_conflict'],
    'Taiwan': ['geopolitical_core', 'tech_supply_chain'],
    'Israel': ['geopolitical_core', 'active_conflict'],
    'Iran': ['geopolitical_core', 'energy_markets'],
    'Venezuela': ['geopolitical_core', 'energy_markets'],
    'Palestine': ['active_conflict'],
    'Syria': ['active_conflict'],
    'Yemen': ['active_conflict'],
    'Afghanistan': ['active_conflict'],
    'Myanmar': ['active_conflict'],
    'Ethiopia': ['active_conflict'],
    'Saudi Arabia': ['energy_markets', 'maritime_choke_points'],
    'United Arab Emirates': ['energy_markets', 'maritime_choke_points'],
    'Iraq': ['energy_markets', 'maritime_choke_points'],
    'Qatar': ['energy_markets', 'maritime_choke_points'],
    'Nigeria': ['energy_markets', 'maritime_choke_points'],
    'South Korea': ['tech_supply_chain'],
    'Japan': ['tech_supply_chain'],
    'Netherlands': ['tech_supply_chain'],
    'Germany': ['tech_supply_chain'],
    'Vietnam': ['tech_supply_chain'],
    'Mexico': ['tech_supply_chain'],
    'Chile': ['strategic_minerals'],
    'Argentina': ['strategic_minerals'],
    'Bolivia': ['strategic_minerals'],
    'DR Congo': ['strategic_minerals'],
    'Australia': ['strategic_minerals'],
    'South Africa': ['strategic_minerals'],
    'United Kingdom': ['financial_systemic'],
    'Turkey': ['financial_systemic'],
    'Brazil': ['financial_systemic'],
    'India': ['financial_systemic'],
}


def load_geopolitical_data():
    """Load and process BBVA geopolitical indices."""
    bbva_dir = DATA / 'bbva'
    files = {
        'geopolitical_risk': 'geopolitics_geopolitics_&_economics_geopolitical_risk_countries_2026-01-21_17-30-58.csv',
        'conflicts': 'geopolitics_geopolitics_&_economics_conflicts_countries_2026-01-21_17-31-52.csv',
        'bilateral_tensions': 'geopolitics_geopolitics_&_economics_bilateral_tensions_countries_2026-01-21_17-32-25.csv',
        'trade_policy_uncertainty': 'geopolitics_geopolitics_&_economics_trade_policy_uncertainty_countries_2026-01-21_17-33-02.csv',
        'economic_policy_uncertainty': 'geopolitics_geopolitics_&_economics_economic_policy_uncertainty_countries_2026-01-21_17-33-24.csv',
    }
    
    dfs = {}
    for key, fname in files.items():
        fpath = bbva_dir / fname
        if fpath.exists():
            df = pd.read_csv(fpath, sep=';')
            # Melt from wide to long format
            id_cols = [c for c in df.columns if 'date' in c.lower() or c == df.columns[0]]
            if not id_cols:
                id_cols = [df.columns[0]]
            value_cols = [c for c in df.columns if c not in id_cols]
            
            df_long = df.melt(id_vars=id_cols, value_vars=value_cols, 
                             var_name='country', value_name=key)
            df_long.rename(columns={id_cols[0]: 'date'}, inplace=True)
            dfs[key] = df_long
    
    if not dfs:
        logging.warning('No geopolitical data found')
        return pd.DataFrame()
    
    # Merge all geopolitical indicators
    base = dfs['geopolitical_risk']
    for key in ['conflicts', 'bilateral_tensions', 'trade_policy_uncertainty', 'economic_policy_uncertainty']:
        if key in dfs:
            base = base.merge(dfs[key], on=['date', 'country'], how='outer')
    
    # Remove extra Date columns and convert date
    base = base.loc[:, ~base.columns.str.startswith('Date')]
    base['date'] = pd.to_datetime(base['date'], errors='coerce')
    
    # Drop rows with all NaN values in indicator columns
    indicator_cols = ['geopolitical_risk', 'conflicts', 'bilateral_tensions', 
                     'trade_policy_uncertainty', 'economic_policy_uncertainty']
    existing_indicators = [c for c in indicator_cols if c in base.columns]
    base = base.dropna(subset=existing_indicators, how='all')
    
    return base


def load_oil_data():
    """Load Brent and WTI oil prices."""
    brent_path = DATA / 'energy' / 'oil' / 'brent_daily.csv'
    wti_path = DATA / 'energy' / 'oil' / 'wti_daily.csv'
    
    dfs = []
    if brent_path.exists():
        df = pd.read_csv(brent_path, skiprows=2)
        df.columns = ['date', 'brent_price_usd']
        df['date'] = pd.to_datetime(df['date'])
        dfs.append(df)
    if wti_path.exists():
        df = pd.read_csv(wti_path, skiprows=2)
        df.columns = ['date', 'wti_price_usd']
        df['date'] = pd.to_datetime(df['date'])
        dfs.append(df)
    
    if not dfs:
        logging.warning('No oil data found')
        return pd.DataFrame()
    
    oil = dfs[0]
    for df in dfs[1:]:
        oil = oil.merge(df, on='date', how='outer')
    
    return oil.sort_values('date')


def load_hardware_data():
    """Load GPU and RAM price indices."""
    gpu_path = PROC / 'gpu_price_index_filled.csv'
    ram_path = PROC / 'ram_price_index_filled.csv'
    
    dfs = []
    if gpu_path.exists():
        df = pd.read_csv(gpu_path)
        df['date'] = pd.to_datetime(df['date'])
        dfs.append(df)
    if ram_path.exists():
        df = pd.read_csv(ram_path)
        df['date'] = pd.to_datetime(df['date'])
        dfs.append(df)
    
    if not dfs:
        logging.warning('No hardware data found')
        return pd.DataFrame()
    
    hw = dfs[0]
    for df in dfs[1:]:
        hw = hw.merge(df, on='date', how='outer')
    
    return hw.sort_values('date')


def load_bitcoin_data():
    """Load Bitcoin price data."""
    btc_path = DATA / 'finance' / 'crypto' / 'btc-usd-max.csv'
    if not btc_path.exists():
        logging.warning('No Bitcoin data found')
        return pd.DataFrame()
    
    df = pd.read_csv(btc_path)
    # Find date and price columns
    date_col = 'snapped_at'
    price_col = 'price'
    
    if date_col in df.columns and price_col in df.columns:
        df = df[[date_col, price_col]].rename(columns={date_col: 'date', price_col: 'btc_price_usd'})
        df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True)
        df['date'] = df['date'].dt.tz_localize(None)  # Remove timezone
        return df.dropna(subset=['date']).sort_values('date')
    
    logging.warning('Could not parse Bitcoin data columns')
    return pd.DataFrame()


def add_country_metadata(df):
    """Add country tags and categories."""
    if 'country' not in df.columns:
        return df
    
    # Add tags
    tag_cols = {
        'is_geopolitical_core': [],
        'is_active_conflict': [],
        'is_energy_market': [],
        'is_tech_supply_chain': [],
        'is_strategic_minerals': [],
        'is_financial_systemic': [],
        'is_maritime_choke': [],
    }
    
    for country in df['country'].unique():
        tags = COUNTRY_TAGS.get(country, [])
        for col, lst in tag_cols.items():
            tag = col.replace('is_', '')
            lst.append({'country': country, col: 1 if tag in tags else 0})
    
    for col, lst in tag_cols.items():
        tag_df = pd.DataFrame(lst)
        if not tag_df.empty:
            df = df.merge(tag_df, on='country', how='left')
            df[col] = df[col].fillna(0).astype(int)
    
    return df


def main():
    logging.info('Loading geopolitical data...')
    geo_df = load_geopolitical_data()
    
    logging.info('Loading oil price data...')
    oil_df = load_oil_data()
    
    logging.info('Loading hardware price indices...')
    hw_df = load_hardware_data()
    
    logging.info('Loading Bitcoin data...')
    btc_df = load_bitcoin_data()
    
    # Merge on date
    if not oil_df.empty:
        base = oil_df
    elif not hw_df.empty:
        base = hw_df
    else:
        logging.error('No time series data available')
        return
    
    if not hw_df.empty and not oil_df.empty:
        base = base.merge(hw_df, on='date', how='outer')
    
    if not btc_df.empty:
        base = base.merge(btc_df, on='date', how='outer')
    
    # Add geopolitical data (expand to all dates via cross join)
    if not geo_df.empty:
        geo_df = add_country_metadata(geo_df)
        
        # Filter to relevant date range (Sept 2025 - Jan 2026 to match hardware data)
        if not base.empty:
            min_date = base['date'].min()
            max_date = base['date'].max()
            geo_df = geo_df[(geo_df['date'] >= min_date) & (geo_df['date'] <= max_date)]
        
        # For now, save separately since geopolitical is country-specific
        geo_out = PROC / 'geopolitical_normalized.csv'
        geo_df.to_csv(geo_out, index=False)
        logging.info(f'Saved geopolitical data to {geo_out} ({len(geo_df)} rows)')
    
    # Save unified time series
    base = base.sort_values('date')
    out_path = PROC / 'unified_timeseries.csv'
    base.to_csv(out_path, index=False)
    logging.info(f'Saved unified time series to {out_path} ({len(base)} rows)')


if __name__ == '__main__':
    main()
