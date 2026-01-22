#!/usr/bin/env python3
"""Generate visualizations for geopolitical risk analytics.

Creates:
1. Time series plots for all indicators
2. Correlation heatmaps
3. Lagged correlation charts
4. Volatility trends
5. Regional comparison dashboards
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'data' / 'processed'
RES = ROOT / 'results'
FIGS = RES / 'figures'
FIGS.mkdir(parents=True, exist_ok=True)

sns.set_style('darkgrid')
plt.rcParams['figure.figsize'] = (14, 8)


def plot_geopolitical_timeseries():
    """Plot geopolitical risk indices by country."""
    geo_path = PROC / 'geopolitical_normalized.csv'
    if not geo_path.exists():
        logging.warning(f'{geo_path} not found')
        return
    
    df = pd.read_csv(geo_path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Top countries by avg geopolitical risk
    top_risk = df.groupby('country')['geopolitical_risk'].mean().nlargest(7).index.tolist()
    
    # Add priority countries (US, Russia, Denmark/Greenland) for strategic monitoring
    priority_countries = ['United States', 'Russia', 'Denmark']
    for country in priority_countries:
        if country not in top_risk:
            top_risk.append(country)
    
    selected_countries = top_risk[:10]  # Keep only 10 for readability
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Geopolitical Risk
    for country in selected_countries:
        data = df[df['country'] == country].sort_values('date')
        axes[0].plot(data['date'], data['geopolitical_risk'], label=country, linewidth=2)
    
    axes[0].set_title('Geopolitical Risk Index - Key Countries (incl. US, Russia & Denmark/Greenland)', fontsize=16)
    axes[0].set_ylabel('Risk Index')
    axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    axes[0].grid(True, alpha=0.3)
    
    # Conflicts
    for country in selected_countries:
        data = df[df['country'] == country].sort_values('date')
        axes[1].plot(data['date'], data['conflicts'], label=country, linewidth=2)
    
    axes[1].set_title('Conflict Index - Key Countries (incl. US, Russia & Denmark/Greenland)', fontsize=16)
    axes[1].set_ylabel('Conflict Index')
    axes[1].set_xlabel('Date')
    axes[1].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    out_path = FIGS / 'geopolitical_timeseries.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    logging.info(f'Saved {out_path}')
    plt.close()


def plot_market_timeseries():
    """Plot energy, tech, and crypto prices."""
    ts_path = PROC / 'unified_timeseries_enriched.csv'
    if not ts_path.exists():
        logging.warning(f'{ts_path} not found')
        return
    
    df = pd.read_csv(ts_path)
    df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce')
    df = df.sort_values('date')
    
    # Filter to relevant period (where GPU/RAM data exists)
    df = df[df['date'] >= '2025-09-01']
    
    # Fill gaps with interpolation for smooth visualization
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].interpolate(method='linear', limit_direction='both')
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    
    # Oil prices
    if 'brent_price_usd' in df.columns:
        axes[0].plot(df['date'], df['brent_price_usd'], label='Brent', linewidth=2, color='#d62728')
    if 'wti_price_usd' in df.columns:
        axes[0].plot(df['date'], df['wti_price_usd'], label='WTI', linewidth=2, color='#ff7f0e')
    axes[0].set_title('Oil Prices', fontsize=16)
    axes[0].set_ylabel('USD per barrel')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # GPU/RAM prices
    gpu_cols = [c for c in df.columns if 'gpu_' in c and 'median' in c]
    for col in gpu_cols:
        label = col.replace('gpu_', '').replace('_median', '').upper()
        axes[1].plot(df['date'], df[col], label=label, linewidth=2)
    axes[1].set_title('GPU Median Prices by Tier', fontsize=16)
    axes[1].set_ylabel('USD')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Bitcoin
    if 'btc_price_usd' in df.columns:
        axes[2].plot(df['date'], df['btc_price_usd'], linewidth=2, color='#f7931a')
        axes[2].set_title('Bitcoin Price', fontsize=16)
        axes[2].set_ylabel('USD')
        axes[2].set_xlabel('Date')
        axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    out_path = FIGS / 'market_timeseries.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    logging.info(f'Saved {out_path}')
    plt.close()


def plot_correlation_heatmap():
    """Generate correlation matrix heatmap."""
    corr_path = RES / 'correlation_matrix.csv'
    if not corr_path.exists():
        logging.warning(f'{corr_path} not found')
        return
    
    df = pd.read_csv(corr_path)
    
    # Filter for lag=0 only
    df_lag0 = df[df['lag_days'] == 0]
    
    # Pivot for heatmap
    pivot = df_lag0.pivot(index='risk_indicator', columns='market_variable', values='correlation')
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot, annot=True, fmt='.3f', cmap='coolwarm', center=0, 
                vmin=-1, vmax=1, linewidths=0.5)
    plt.title('Correlation Matrix: Geopolitical Risk vs Market Variables (Lag=0)', fontsize=16)
    plt.tight_layout()
    
    out_path = FIGS / 'correlation_heatmap.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    logging.info(f'Saved {out_path}')
    plt.close()


def plot_lagged_correlations():
    """Plot correlations at different lags."""
    corr_path = RES / 'correlation_matrix.csv'
    if not corr_path.exists():
        logging.warning(f'{corr_path} not found')
        return
    
    df = pd.read_csv(corr_path)
    
    # Focus on key relationships
    key_pairs = [
        ('geopolitical_risk', 'brent_price_usd'),
        ('conflicts', 'wti_price_usd'),
        ('geopolitical_risk', 'btc_price_usd'),
        ('bilateral_tensions', 'gpu_high_median'),
    ]
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for idx, (risk_var, market_var) in enumerate(key_pairs):
        data = df[(df['risk_indicator'] == risk_var) & (df['market_variable'] == market_var)]
        
        if not data.empty:
            axes[idx].plot(data['lag_days'], data['correlation'], 
                          marker='o', linewidth=2, markersize=8)
            axes[idx].axhline(y=0, color='black', linestyle='--', alpha=0.3)
            axes[idx].set_title(f'{risk_var} → {market_var}', fontsize=12)
            axes[idx].set_xlabel('Lag (days)')
            axes[idx].set_ylabel('Correlation')
            axes[idx].grid(True, alpha=0.3)
    
    plt.suptitle('Lagged Correlations: Geopolitical Risk Leading Market Variables', fontsize=16)
    plt.tight_layout()
    
    out_path = FIGS / 'lagged_correlations.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    logging.info(f'Saved {out_path}')
    plt.close()


def plot_volatility_comparison():
    """Compare volatility across different markets."""
    ts_path = PROC / 'unified_timeseries_enriched.csv'
    if not ts_path.exists():
        logging.warning(f'{ts_path} not found')
        return
    
    df = pd.read_csv(ts_path)
    df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce')
    df = df.sort_values('date')
    
    # Filter to relevant period (Sept 2025 - Jan 2026)
    df = df[df['date'] >= '2025-09-01']
    
    # Fill gaps with interpolation
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].interpolate(method='linear', limit_direction='both')
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    volatility_cols = {
        'brent_volatility_7d': 'Brent Oil',
        'wti_volatility_7d': 'WTI Oil',
        'btc_volatility_7d': 'Bitcoin',
    }
    
    for col, label in volatility_cols.items():
        if col in df.columns and df[col].notna().sum() > 0:
            # Normalize to percentage of mean price
            base_col = col.replace('_volatility_7d', '_price_usd')
            if base_col in df.columns:
                mean_price = df[base_col].mean()
                if mean_price > 0:
                    normalized_vol = (df[col] / mean_price) * 100
                    ax.plot(df['date'], normalized_vol, label=label, linewidth=2, alpha=0.8)
    
    # Ensure date range is visible
    ax.set_xlim(df['date'].min(), df['date'].max())
    
    ax.set_title('Market Volatility Comparison (Sept 2025 - Jan 2026)\n7-day Rolling, Normalized', 
                 fontsize=16, pad=15)
    ax.set_ylabel('Volatility (% of mean price)', fontsize=12)
    ax.set_xlabel('Date', fontsize=12)
    ax.legend(fontsize=11, loc='best')
    ax.grid(True, alpha=0.3)
    
    # Rotate date labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    out_path = FIGS / 'volatility_comparison.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    logging.info(f'Saved {out_path}')
    plt.close()


def main():
    logging.info('Generating visualizations...')
    
    plot_geopolitical_timeseries()
    plot_market_timeseries()
    plot_correlation_heatmap()
    plot_lagged_correlations()
    plot_volatility_comparison()
    
    logging.info(f'All visualizations saved to {FIGS}')


if __name__ == '__main__':
    main()
