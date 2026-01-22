# Resumen Ejecutivo - Análisis Geopolítico

## Estado del Proyecto: ✅ COMPLETADO

Pipeline de análisis geopolítico completamente funcional, con datos procesados, correlaciones calculadas y visualizaciones generadas.

## Resultados Clave

### 1. Hallazgos de Correlación

**Riesgo Geopolítico → Mercados**

| Variable de Mercado | Lag 0 | Lag 7d | Lag 14d | Lag 28d |
|---------------------|-------|--------|---------|---------|
| Bitcoin | 0.29 | 0.53 | 0.65 | **0.81** |
| Brent | 0.57 | 0.53 | 0.18 | 0.32 |
| WTI | 0.44 | 0.43 | 0.29 | 0.59 |
| GPU High-End | 0.07 | 0.13 | 0.25 | 0.34 |
| GPU Mid-Range | -0.60 | -0.38 | -0.11 | 0.10 |

**Insights:**
- **Bitcoin muestra correlación fuerte con lag de 4 semanas (0.81)** → El riesgo geopolítico anticipa movimientos de BTC
- **Petróleo tiene correlación inmediata moderada (0.44-0.57)** → Reacción más directa a eventos
- **GPUs muestran comportamiento mixto** → Tier alto correlaciona positivamente, tier medio negativamente (posible sustitución)

### 2. Datasets Procesados

```
data/processed/
├── geopolitical_normalized.csv     (37,575 filas - 34 países, 5 indicadores)
├── unified_timeseries.csv          (11,647 filas - 1986-2026)
├── unified_timeseries_enriched.csv (con volatilidad, retornos)
├── gpu_price_index_filled.csv      (109 días, 3 tiers)
└── ram_price_index_filled.csv      (110 días, 4 categorías)
```

### 3. Visualizaciones Generadas

```
results/figures/
├── geopolitical_timeseries.png     (Top 10 países por riesgo)
├── market_timeseries.png           (Oil, GPU, BTC)
├── correlation_heatmap.png         (Matriz completa)
├── lagged_correlations.png         (4 relaciones clave)
└── volatility_comparison.png       (Volatilidad normalizada)
```

### 4. Arquitectura del Sistema

**Pipeline Modular:**
1. `data_unifier.py` → Unifica 5 fuentes de datos con categorización de países
2. `correlation_analyzer.py` → Calcula correlaciones con lags de 0-28 días
3. `visualizer.py` → Genera 5 gráficos de análisis
4. `main.py` → Orquesta ejecución completa

**Ejecución:**
```bash
python src/main.py  # Pipeline completo
```

### 5. Categorización de Países

7 categorías estratégicas aplicadas a 34 países:
- `geopolitical_core` (4): USA, China, Russia, India
- `active_conflict` (5): Ukraine, Israel, Palestine, Syria, Yemen
- `energy_markets` (10): OPEC+ productores
- `tech_supply_chain` (3): Taiwan, South Korea, Japan
- `strategic_minerals` (6): Chile, DRC, Australia, Peru, Zambia, Zimbabwe
- `financial_systemic` (6): UK, Switzerland, Singapore, Hong Kong, Brazil, India
- `maritime_choke_points` (4): Egypt, Turkey, Yemen, Iran

### 6. Métricas Implementadas

**Volatilidad:**
- Rolling window 7 días
- Calculada para: Brent, WTI, BTC, GPU (3 tiers), RAM (4 categorías)

**Correlaciones:**
- Pearson entre indicadores geopolíticos y precios
- Lags: 0, 7, 14, 28 días
- Agregación por media diaria cross-country

**Retornos:**
- Cambios porcentuales diarios
- Base para análisis de volatilidad

## Dependencias Instaladas

```
pandas        # Procesamiento de datos
matplotlib    # Gráficos base
seaborn       # Visualizaciones estadísticas
numpy         # Cálculos numéricos
openpyxl      # Lectura XLSX
xlrd          # Lectura XLS
```

## Período Analizado

**Rango completo:** 1986-01-02 → 2026-01-22 (40 años)
**Rango principal:** 2025-09-19 → 2026-01-22 (109-110 días)
- GPU/RAM: 109-110 observaciones diarias
- Petróleo: 9,806 días
- Bitcoin: 4,651 días
- Geopolítico: 384 días (filtrado a período relevante)

## Próximos Pasos (Opcionales)

1. **Análisis Regional:** Agrupar países por región geográfica
2. **Series Temporales Avanzadas:** ARIMA, GARCH para modelado predictivo
3. **Eventos Discretos:** Marcar fechas específicas de crisis
4. **Dashboard Interactivo:** Dash/Streamlit para exploración
5. **API REST:** Exponer datos y correlaciones vía HTTP

## Conclusión

El sistema está **plenamente operativo** y genera insights cuantitativos sobre relaciones entre riesgo geopolítico y mercados. Los resultados muestran que:

1. **Bitcoin es el activo más sensible a riesgo geopolítico con lag**
2. **Petróleo reacciona más inmediatamente**
3. **GPU/RAM muestran patrones de mercado específicos no directamente correlacionados**

Todos los datos, código y visualizaciones están listos para análisis adicional o presentación.
