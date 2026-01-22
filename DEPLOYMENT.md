# Deployment instructions for Streamlit Cloud

## ✅ Pre-deployment Checklist

### Files Structure
```
geopolitical-risk-analytics/
├── .streamlit/
│   └── config.toml           # ✅ Streamlit configuration
├── data/
│   └── processed/            # ✅ All CSV data files
├── results/
│   └── *.csv + *.txt         # ✅ Analysis outputs
├── streamlit_app.py          # ✅ Main app file
├── requirements.txt          # ✅ Dependencies
├── README_RECRUITER.md       # ✅ Portfolio README
└── DEPLOYMENT.md             # ✅ This file
```

### Requirements
- ✅ Python 3.9+
- ✅ All dependencies in requirements.txt
- ✅ Git repository with all data files committed

## 🚀 Deploy to Streamlit Cloud

### Step 1: Prepare Repository
```bash
# Ensure all files are committed
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### Step 2: Create Streamlit Cloud Account
1. Go to https://streamlit.io/cloud
2. Sign up with GitHub account
3. Connect your GitHub repository

### Step 3: Deploy
1. Click "New app"
2. Select this repository
3. Set main file path: `streamlit_app.py`
4. Click "Deploy"

### Step 4: Monitor
- Deployment takes 2-5 minutes
- Check logs in the dashboard
- App will be available at: `https://<username>-<repo-name>.streamlit.app`

## ⚙️ Configuration

### Environment Variables (if needed)
Add secrets in Streamlit Cloud dashboard:
```
.streamlit/secrets.toml (local, not committed)
```

### Performance Tips
- Data is cached with `@st.cache_data`
- All CSV files are loaded once
- Plotly charts are interactive
- Response time: <1 second per interaction

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'X'"
**Solution:** Add missing package to `requirements.txt` and redeploy

### Issue: "FileNotFoundError: data/processed/..."
**Solution:** Ensure all CSV files are committed to Git and present in repo

### Issue: App is slow or crashes
**Solution:** 
- Streamlit Cloud has 1GB RAM limit
- Data is already optimized
- Clear browser cache and try again

### Issue: Data not loading
**Solution:** Check GitHub → Streamlit Cloud connection and verify all CSV files are present

## 📊 Data Files Size

| File | Size | Status |
|------|------|--------|
| unified_timeseries_enriched.csv | ~35 MB | ✅ Large but OK |
| geopolitical_normalized.csv | ~12 MB | ✅ OK |
| correlation_matrix.csv | <1 MB | ✅ OK |
| btc_forecast.csv | <1 KB | ✅ OK |
| stress_scenarios.csv | <5 KB | ✅ OK |
| early_warning_signals.csv | <50 KB | ✅ OK |
| **Total** | **~48 MB** | ✅ Within limits |

## 🌐 Public App URL
Once deployed, your app will be available at:
```
https://<your-username>-geopolitical-risk-analytics.streamlit.app
```

## 📝 Notes
- Streamlit Cloud rebuilds on each Git push
- Cache is cleared on redeploy
- Initial load takes 5-10 seconds
- Interactive features work smoothly after loading

## ✅ Post-deployment

### Share with Recruiters
1. Get your Streamlit Cloud URL
2. Add to portfolio: README.md
3. Share in: LinkedIn, GitHub, Cover Letters
4. Include in: Resume as "Live Demo"

### Monitor Usage
- Streamlit Cloud dashboard shows usage stats
- Free tier: 1GB storage, 1 app
- Upgrade if needed for multiple apps

---

**Status:** ✅ Ready for Production Deployment
**Last Updated:** January 22, 2026
