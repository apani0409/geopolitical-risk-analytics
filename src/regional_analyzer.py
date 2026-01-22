#!/usr/bin/env python3
"""Regional and categorical analysis of geopolitical risks.

Groups countries by strategic categories and analyzes trends.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'data' / 'processed'
OUT = ROOT / 'results'
FIGS = OUT / 'figures'

CATEGORIES = {
    'is_geopolitical_core': 'Geopolitical Core Powers',
    'is_active_conflict': 'Active Conflict Zones',
    'is_energy_market': 'Energy Markets (OPEC+)',
    'is_tech_supply_chain': 'Tech Supply Chain',
    'is_strategic_minerals': 'Strategic Minerals',
    'is_financial_systemic': 'Financial Centers',
    'is_maritime_choke': 'Maritime Choke Points',
}


def analyze_by_category():
    """Analyze geopolitical risk trends by country category."""
    geo_path = PROC / 'geopolitical_normalized.csv'
    
    if not geo_path.exists():
        logging.warning(f'{geo_path} not found')
        return
    
    df = pd.read_csv(geo_path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    results = []
    
    for cat_col, cat_name in CATEGORIES.items():
        if cat_col not in df.columns:
            continue
        
        # Filter to countries in this category
        cat_df = df[df[cat_col] == 1]
        
        if cat_df.empty:
            continue
        
        # Aggregate by date
        daily_avg = cat_df.groupby('date').agg({
            'geopolitical_risk': 'mean',
            'conflicts': 'mean',
            'bilateral_tensions': 'mean',
        }).reset_index()
        
        daily_avg['category'] = cat_name
        results.append(daily_avg)
    
    if not results:
        logging.warning('No category data found')
        return
    
    # Combine all categories
    combined = pd.concat(results, ignore_index=True)
    
    # Create visualization
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Geopolitical risk by category
    for cat_name in combined['category'].unique():
        cat_data = combined[combined['category'] == cat_name]
        axes[0].plot(cat_data['date'], cat_data['geopolitical_risk'], 
                    label=cat_name, linewidth=2, alpha=0.8)
    
    axes[0].set_title('Geopolitical Risk Index by Strategic Category', fontsize=16)
    axes[0].set_ylabel('Risk Index')
    axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    axes[0].grid(True, alpha=0.3)
    
    # Conflicts by category
    for cat_name in combined['category'].unique():
        cat_data = combined[combined['category'] == cat_name]
        axes[1].plot(cat_data['date'], cat_data['conflicts'], 
                    label=cat_name, linewidth=2, alpha=0.8)
    
    axes[1].set_title('Conflict Index by Strategic Category', fontsize=16)
    axes[1].set_ylabel('Conflict Index')
    axes[1].set_xlabel('Date')
    axes[1].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    out_path = FIGS / 'categorical_risk_trends.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    logging.info(f'Saved {out_path}')
    plt.close()
    
    # Summary statistics
    summary = combined.groupby('category').agg({
        'geopolitical_risk': ['mean', 'std', 'max'],
        'conflicts': ['mean', 'std', 'max'],
    }).round(3)
    
    summary_path = OUT / 'category_summary_stats.csv'
    summary.to_csv(summary_path)
    logging.info(f'Saved category statistics to {summary_path}')
    
    return summary


def main():
    logging.info('Analyzing regional/categorical trends...')
    analyze_by_category()
    logging.info('Regional analysis complete')


if __name__ == '__main__':
    main()
