#!/usr/bin/env python3
"""Main analysis pipeline for geopolitical risk analytics.

Orchestrates:
1. Data unification
2. Correlation analysis
3. Visualization generation
4. Report generation
"""
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

SCRIPTS = {
    'unifier': ROOT / 'src' / 'data_unifier.py',
    'analyzer': ROOT / 'src' / 'correlation_analyzer.py',
    'visualizer': ROOT / 'src' / 'visualizer.py',
    'mineral': ROOT / 'src' / 'mineral_analyzer.py',
    'regional': ROOT / 'src' / 'regional_analyzer.py',
    'predictive': ROOT / 'src' / 'predictive_analyzer.py',
    'insights': ROOT / 'src' / 'insights_generator.py',
    'dashboard': ROOT / 'src' / 'dashboard_generator.py',
}


def run_script(name, script_path):
    """Execute a Python script and log results."""
    logging.info(f'\n{"="*60}')
    logging.info(f'Running: {name}')
    logging.info(f'{"="*60}')
    
    try:
        result = subprocess.run(
            [PYTHON, str(script_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        logging.info(f'✓ {name} completed successfully')
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f'✗ {name} failed with exit code {e.returncode}')
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        return False


def main():
    logging.info('Starting geopolitical risk analytics pipeline...')
    
    # Step 1: Unify data sources
    if not run_script('Data Unifier', SCRIPTS['unifier']):
        logging.error('Pipeline halted: data unification failed')
        return 1
    
    # Step 2: Correlation analysis
    if not run_script('Correlation Analyzer', SCRIPTS['analyzer']):
        logging.error('Pipeline halted: correlation analysis failed')
        return 1
    
    # Step 3: Generate visualizations
    if not run_script('Visualizer', SCRIPTS['visualizer']):
        logging.error('Pipeline halted: visualization generation failed')
        return 1
    
    # Step 4: Mineral dependency analysis
    if not run_script('Mineral Analyzer', SCRIPTS['mineral']):
        logging.warning('Mineral analysis failed (non-critical)')
    
    # Step 5: Regional/categorical analysis
    if not run_script('Regional Analyzer', SCRIPTS['regional']):
        logging.warning('Regional analysis failed (non-critical)')
    
    # Step 6: Predictive modeling & scenarios
    if not run_script('Predictive Analyzer', SCRIPTS['predictive']):
        logging.warning('Predictive analysis failed (non-critical)')
    
    # Step 7: Generate insights report
    if not run_script('Insights Generator', SCRIPTS['insights']):
        logging.warning('Insights generation failed (non-critical)')
    
    # Step 8: Create executive dashboard
    if not run_script('Dashboard Generator', SCRIPTS['dashboard']):
        logging.warning('Dashboard generation failed (non-critical)')
    
    logging.info('\n' + '='*60)
    logging.info('PIPELINE COMPLETE')
    logging.info('='*60)
    logging.info(f'Results saved to: {ROOT / "results"}')
    logging.info(f'Visualizations: {ROOT / "results" / "figures"}')
    logging.info(f'Dashboard: {ROOT / "results" / "dashboard.html"}')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
