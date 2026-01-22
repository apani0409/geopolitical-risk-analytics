#!/usr/bin/env python3
"""Strategic minerals analysis - dependency vs geopolitical risk.

Analyzes mineral production data and correlates with geopolitical instability
in producer countries.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
PROC = ROOT / 'data' / 'processed'
OUT = ROOT / 'results'

# Critical minerals for tech/energy transition
CRITICAL_MINERALS = [
    'Lithium', 'Cobalt', 'Rare Earths', 'Copper', 'Nickel',
    'Graphite', 'Aluminum', 'Zinc', 'Silver', 'Platinum'
]


def load_mineral_data():
    """Load and parse mineral production data."""
    world_data = DATA / 'energy' / 'MCS2025_World_Data.csv'
    
    if not world_data.exists():
        logging.warning(f'{world_data} not found')
        return pd.DataFrame()
    
    # Read with error handling for encoding issues
    try:
        df = pd.read_csv(world_data, encoding='utf-8', on_bad_lines='skip')
    except:
        df = pd.read_csv(world_data, encoding='latin-1', on_bad_lines='skip')
    
    logging.info(f'Loaded mineral data: {df.shape}')
    return df


def analyze_mineral_dependency():
    """Analyze which countries control critical mineral production."""
    geo_path = PROC / 'geopolitical_normalized.csv'
    
    if not geo_path.exists():
        logging.warning('No geopolitical data found')
        return
    
    geo = pd.read_csv(geo_path)
    geo['date'] = pd.to_datetime(geo['date'], errors='coerce')
    
    # Average geopolitical risk by country
    geo_by_country = geo.groupby('country').agg({
        'geopolitical_risk': 'mean',
        'conflicts': 'mean',
        'is_strategic_minerals': 'max',
    }).reset_index()
    
    # Filter to strategic mineral producers
    mineral_producers = geo_by_country[geo_by_country['is_strategic_minerals'] == 1]
    
    if mineral_producers.empty:
        logging.warning('No mineral producer countries found in dataset')
        return
    
    # Sort by geopolitical risk
    mineral_producers = mineral_producers.sort_values('geopolitical_risk', ascending=False)
    
    logging.info('\n' + '='*60)
    logging.info('STRATEGIC MINERAL PRODUCERS - GEOPOLITICAL RISK ANALYSIS')
    logging.info('='*60)
    
    for _, row in mineral_producers.iterrows():
        risk_level = 'HIGH' if row['geopolitical_risk'] > 0.5 else 'MEDIUM' if row['geopolitical_risk'] > 0 else 'LOW'
        logging.info(f"{row['country']:20} | Risk: {row['geopolitical_risk']:6.2f} | Conflict: {row['conflicts']:6.2f} | [{risk_level}]")
    
    # Save analysis
    out_path = OUT / 'mineral_producer_risk.csv'
    mineral_producers.to_csv(out_path, index=False)
    logging.info(f'\nSaved mineral producer risk analysis to {out_path}')
    
    return mineral_producers


def main():
    logging.info('Analyzing strategic minerals dependency...')
    
    mineral_data = load_mineral_data()
    if not mineral_data.empty:
        logging.info(f'Mineral data columns: {list(mineral_data.columns[:10])}...')
    
    analyze_mineral_dependency()
    
    logging.info('Mineral analysis complete')


if __name__ == '__main__':
    main()
