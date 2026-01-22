#!/usr/bin/env python3
"""Correlation and volatility analyzer for geopolitical risk signals.

Analyzes:
1. Geopolitical risk vs energy prices
2. Conflict escalation vs oil volatility
3. Tech supply chain risk vs GPU/RAM prices
4. Financial uncertainty vs BTC/FX
5. Lagged correlations (t-1, t-4 weeks)
"""
from pathlib import Path
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'data' / 'processed'
OUT = ROOT / 'results'
OUT.mkdir(parents=True, exist_ok=True)


def calculate_volatility(series, window=7):
    """Calculate rolling volatility (standard deviation)."""
    return series.rolling(window=window).std()


def calculate_returns(series):
    """Calculate percentage returns."""
    return series.pct_change() * 100


def lagged_correlation(s1, s2, max_lag=28, window=None):
    """Calculate correlation at different lags (in days)."""
    results = []
    for lag in range(0, max_lag + 1, 7):  # weekly intervals
        if lag == 0:
            s1_shifted = s1
        else:
            s1_shifted = s1.shift(lag)
        
        if window:
            corr = s1_shifted.rolling(window).corr(s2).mean()
        else:
            corr = s1_shifted.corr(s2)
        
        results.append({'lag_days': lag, 'correlation': corr})
    
    return pd.DataFrame(results)


def analyze_timeseries():
    """Analyze unified time series data."""
    ts_path = PROC / 'unified_timeseries.csv'
    if not ts_path.exists():
        logging.error(f'{ts_path} not found. Run data_unifier.py first.')
        return
    
    df = pd.read_csv(ts_path)
    df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce')
    df = df.sort_values('date')
    logging.info(f'Loaded {len(df)} rows from unified timeseries')
    
    # Interpolate price data to fill gaps for smoother volatility calculation
    price_cols = [c for c in df.columns if 'price' in c or 'median' in c]
    df[price_cols] = df[price_cols].interpolate(method='linear', limit_direction='forward')
    
    # Add volatility metrics
    if 'brent_price_usd' in df.columns:
        df['brent_volatility_7d'] = calculate_volatility(df['brent_price_usd'], 7)
        df['brent_returns'] = calculate_returns(df['brent_price_usd'])
    
    if 'wti_price_usd' in df.columns:
        df['wti_volatility_7d'] = calculate_volatility(df['wti_price_usd'], 7)
        df['wti_returns'] = calculate_returns(df['wti_price_usd'])
    
    if 'btc_price_usd' in df.columns:
        df['btc_volatility_7d'] = calculate_volatility(df['btc_price_usd'], 7)
        df['btc_returns'] = calculate_returns(df['btc_price_usd'])
    
    # GPU/RAM volatility
    gpu_cols = [c for c in df.columns if 'gpu_' in c and 'median' in c]
    for col in gpu_cols:
        df[f'{col}_volatility_7d'] = calculate_volatility(df[col], 7)
    
    ram_cols = [c for c in df.columns if 'ram_' in c and 'median' in c]
    for col in ram_cols:
        df[f'{col}_volatility_7d'] = calculate_volatility(df[col], 7)
    
    # Save enriched timeseries
    enriched_path = PROC / 'unified_timeseries_enriched.csv'
    df.to_csv(enriched_path, index=False)
    logging.info(f'Saved enriched timeseries to {enriched_path}')
    
    return df


def analyze_geopolitical_correlations():
    """Analyze geopolitical indices correlation with markets."""
    geo_path = PROC / 'geopolitical_normalized.csv'
    ts_path = PROC / 'unified_timeseries_enriched.csv'
    
    if not geo_path.exists() or not ts_path.exists():
        logging.warning('Missing geopolitical or timeseries data')
        return
    
    geo = pd.read_csv(geo_path)
    geo['date'] = pd.to_datetime(geo['date'], errors='coerce')
    ts = pd.read_csv(ts_path)
    ts['date'] = pd.to_datetime(ts['date'], format='mixed', errors='coerce')
    
    # Filter to relevant period (where GPU/RAM data exists)
    ts = ts.dropna(subset=['gpu_high_median', 'gpu_mid_median'], how='all')
    if ts.empty:
        logging.warning('No GPU data in timeseries')
        return
    
    # Aggregate geopolitical risk by date (weighted avg by country tags)
    geo_agg = geo.groupby('date').agg({
        'geopolitical_risk': 'mean',
        'conflicts': 'mean',
        'bilateral_tensions': 'mean',
        'trade_policy_uncertainty': 'mean',
        'economic_policy_uncertainty': 'mean',
    }).reset_index()
    
    # Merge with timeseries
    merged = ts.merge(geo_agg, on='date', how='inner')
    
    # Calculate correlations
    correlations = []
    
    market_vars = ['brent_price_usd', 'wti_price_usd', 'btc_price_usd', 
                   'gpu_high_median', 'gpu_mid_median', 'ram_ddr5_median']
    risk_vars = ['geopolitical_risk', 'conflicts', 'bilateral_tensions']
    
    for risk_var in risk_vars:
        if risk_var not in merged.columns:
            continue
        for market_var in market_vars:
            if market_var not in merged.columns:
                continue
            
            corr = merged[risk_var].corr(merged[market_var])
            correlations.append({
                'risk_indicator': risk_var,
                'market_variable': market_var,
                'correlation': corr,
                'lag_days': 0
            })
            
            # Lagged correlations
            for lag in [7, 14, 28]:
                corr_lag = merged[risk_var].shift(lag).corr(merged[market_var])
                correlations.append({
                    'risk_indicator': risk_var,
                    'market_variable': market_var,
                    'correlation': corr_lag,
                    'lag_days': lag
                })
    
    corr_df = pd.DataFrame(correlations)
    corr_out = OUT / 'correlation_matrix.csv'
    corr_df.to_csv(corr_out, index=False)
    logging.info(f'Saved correlation matrix to {corr_out}')
    
    return corr_df


def main():
    logging.info('Analyzing time series...')
    df = analyze_timeseries()
    
    if df is not None:
        logging.info('Analyzing geopolitical correlations...')
        analyze_geopolitical_correlations()
    
    logging.info('Analysis complete')


if __name__ == '__main__':
    main()
