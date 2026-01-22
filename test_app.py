#!/usr/bin/env python3
"""Testing suite for Geopolitical Risk Analytics Streamlit App"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).parent
DATA = ROOT / 'data' / 'processed'
RES = ROOT / 'results'

def test_dependencies():
    """Test all required dependencies."""
    print("🧪 Testing dependencies...")
    dependencies = [
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'matplotlib',
        'seaborn'
    ]
    
    all_ok = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep}")
            all_ok = False
    
    return all_ok

def test_data_files():
    """Test that all required data files exist and are readable."""
    print("\n📁 Testing data files...")
    
    required_files = {
        'unified_timeseries_enriched.csv': DATA / 'unified_timeseries_enriched.csv',
        'geopolitical_normalized.csv': DATA / 'geopolitical_normalized.csv',
        'correlation_matrix.csv': RES / 'correlation_matrix.csv',
        'btc_forecast.csv': RES / 'btc_forecast.csv',
        'stress_scenarios.csv': RES / 'stress_scenarios.csv',
        'early_warning_signals.csv': RES / 'early_warning_signals.csv',
    }
    
    all_ok = True
    for name, path in required_files.items():
        if not path.exists():
            print(f"  ❌ {name} - NOT FOUND")
            all_ok = False
            continue
        
        try:
            size_mb = path.stat().st_size / (1024*1024)
            print(f"  ✅ {name} ({size_mb:.1f} MB)")
        except Exception as e:
            print(f"  ❌ {name} - {e}")
            all_ok = False
    
    return all_ok

def test_data_integrity():
    """Test that data files are valid and contain expected columns."""
    print("\n🔍 Testing data integrity...")
    
    tests = [
        ('unified_timeseries_enriched.csv', DATA / 'unified_timeseries_enriched.csv', 
         ['date', 'btc_price_usd', 'brent_price_usd']),
        ('geopolitical_normalized.csv', DATA / 'geopolitical_normalized.csv',
         ['date', 'country', 'geopolitical_risk']),
        ('correlation_matrix.csv', RES / 'correlation_matrix.csv',
         ['risk_indicator', 'market_variable', 'correlation']),
        ('btc_forecast.csv', RES / 'btc_forecast.csv',
         ['forecast_date', 'base_case', 'bull_case']),
    ]
    
    all_ok = True
    for name, path, expected_cols in tests:
        try:
            df = pd.read_csv(path)
            
            # Check columns
            missing_cols = [col for col in expected_cols if col not in df.columns]
            if missing_cols:
                print(f"  ⚠️  {name} - Missing columns: {missing_cols}")
                all_ok = False
            else:
                print(f"  ✅ {name} - {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            print(f"  ❌ {name} - {e}")
            all_ok = False
    
    return all_ok

def test_data_loading():
    """Test that data can be loaded and processed as in the app."""
    print("\n⚡ Testing data loading and processing...")
    
    try:
        # Load unified timeseries
        df = pd.read_csv(DATA / 'unified_timeseries_enriched.csv')
        df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce')
        
        # Check date range
        date_min = df['date'].min()
        date_max = df['date'].max()
        print(f"  ✅ Unified timeseries: {len(df)} rows, {date_min.date()} to {date_max.date()}")
        
        # Load geopolitical
        geo = pd.read_csv(DATA / 'geopolitical_normalized.csv')
        geo['date'] = pd.to_datetime(geo['date'], errors='coerce')
        
        countries = geo['country'].nunique()
        print(f"  ✅ Geopolitical data: {len(geo)} rows, {countries} countries")
        
        # Load correlations
        corr = pd.read_csv(RES / 'correlation_matrix.csv')
        print(f"  ✅ Correlation matrix: {len(corr)} correlations")
        
        # Load forecasts
        forecast = pd.read_csv(RES / 'btc_forecast.csv')
        print(f"  ✅ BTC Forecast: {len(forecast)} forecasts")
        
        return True
    except Exception as e:
        print(f"  ❌ Data loading failed: {e}")
        return False

def test_calculations():
    """Test that key calculations work."""
    print("\n📊 Testing calculations...")
    
    try:
        df = pd.read_csv(DATA / 'unified_timeseries_enriched.csv')
        
        # Test correlation calculation
        corr = df[['btc_price_usd', 'brent_price_usd']].dropna().corr().iloc[0, 1]
        print(f"  ✅ Correlation calculation: {corr:.3f}")
        
        # Test volatility
        returns = np.log(df['btc_price_usd'].dropna() / df['btc_price_usd'].dropna().shift(1))
        vol = returns.rolling(7).std().mean()
        print(f"  ✅ Volatility calculation: {vol:.6f}")
        
        # Test normalization
        first_price = df['btc_price_usd'].dropna().iloc[0]
        normalized = (df['btc_price_usd'] / first_price) * 100
        print(f"  ✅ Normalization: {normalized.mean():.1f} (base 100)")
        
        return True
    except Exception as e:
        print(f"  ❌ Calculations failed: {e}")
        return False

def test_app_syntax():
    """Test that the Streamlit app has valid Python syntax."""
    print("\n✏️  Testing app syntax...")
    
    try:
        import py_compile
        py_compile.compile(str(ROOT / 'streamlit_app.py'), doraise=True)
        print(f"  ✅ streamlit_app.py - Valid Python syntax")
        return True
    except py_compile.PyCompileError as e:
        print(f"  ❌ streamlit_app.py - Syntax error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🌍 Geopolitical Risk Analytics - Testing Suite")
    print("=" * 60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Data Files", test_data_files),
        ("Data Integrity", test_data_integrity),
        ("Data Loading", test_data_loading),
        ("Calculations", test_calculations),
        ("App Syntax", test_app_syntax),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} - Unexpected error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n" + "=" * 60)
        print("✅ All tests passed! App is ready for deployment.")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Commit changes: git add . && git commit -m 'Ready for deployment'")
        print("2. Push to GitHub: git push origin main")
        print("3. Deploy to Streamlit Cloud: https://streamlit.io/cloud")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed. Fix errors before deployment.")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
