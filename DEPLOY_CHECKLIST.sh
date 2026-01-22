#!/usr/bin/env bash
# Quick deployment checklist for Streamlit Cloud

echo "🚀 Geopolitical Risk Analytics - Deployment Checklist"
echo "======================================================"

echo ""
echo "✅ Step 1: Verify all files exist"
if [ -f "streamlit_app.py" ] && [ -f "requirements.txt" ] && [ -d ".streamlit" ]; then
    echo "  ✓ streamlit_app.py"
    echo "  ✓ requirements.txt"
    echo "  ✓ .streamlit/ directory"
else
    echo "  ✗ Missing critical files"
    exit 1
fi

echo ""
echo "✅ Step 2: Verify data files"
data_files=(
    "data/processed/unified_timeseries_enriched.csv"
    "data/processed/geopolitical_normalized.csv"
    "results/correlation_matrix.csv"
    "results/btc_forecast.csv"
    "results/stress_scenarios.csv"
    "results/early_warning_signals.csv"
)

all_exist=true
for file in "${data_files[@]}"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        echo "  ✓ $file ($size)"
    else
        echo "  ✗ $file - NOT FOUND"
        all_exist=false
    fi
done

if [ "$all_exist" = false ]; then
    echo "  ✗ Some data files are missing"
    exit 1
fi

echo ""
echo "✅ Step 3: Check Git status"
echo ""
echo "Run these commands:"
echo ""
echo "  # Stage all changes"
echo "  git add ."
echo ""
echo "  # Commit with message"
echo "  git commit -m 'Prepare for Streamlit Cloud deployment'"
echo ""
echo "  # Push to GitHub"
echo "  git push origin main"
echo ""

echo ""
echo "✅ Step 4: Deploy to Streamlit Cloud"
echo ""
echo "  1. Go to https://streamlit.io/cloud"
echo "  2. Sign in with GitHub"
echo "  3. Click 'New app'"
echo "  4. Select your repository"
echo "  5. Set main file: streamlit_app.py"
echo "  6. Click 'Deploy'"
echo ""

echo ""
echo "✅ Step 5: Share your app"
echo ""
echo "  Your live app URL will be:"
echo "  https://<username>-<repo-name>.streamlit.app"
echo ""
echo "  Share this URL with recruiters!"
echo ""

echo "======================================================"
echo "✅ Ready for deployment!"
echo "======================================================"
