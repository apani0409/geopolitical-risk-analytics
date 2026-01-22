## Instalación

```bash
# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

### Ejecución Completa

```bash
python src/main.py
```

Ejecuta en secuencia:
1. Unificación de datos (`data_unifier.py`)
2. Análisis de correlaciones (`correlation_analyzer.py`)
3. Generación de visualizaciones (`visualizer.py`)

### Módulos Individuales

```bash
# Solo unificar datos
python src/data_unifier.py

# Solo análisis de correlaciones
python src/correlation_analyzer.py

# Solo visualizaciones
python src/visualizer.py
```

## Resultados

### Archivos Generados

- `data/processed/geopolitical_normalized.csv`: Índices BBVA con tags de países
- `data/processed/unified_timeseries.csv`: Serie temporal unificada de todos los mercados
- `data/processed/unified_timeseries_enriched.csv`: Con métricas de volatilidad
- `results/correlation_matrix.csv`: Matriz de correlaciones con diferentes lags
- `results/figures/*.png`: Visualizaciones

### Visualizaciones

1. **geopolitical_timeseries.png**: Top 10 países por riesgo geopolítico
2. **market_timeseries.png**: Series temporales petróleo, GPU, BTC
3. **correlation_heatmap.png**: Matriz correlación riesgo vs mercados
4. **lagged_correlations.png**: Correlaciones con lag temporal
5. **volatility_comparison.png**: Volatilidad normalizada por mercado

## Fuentes de Datos

- **BBVA Research**: Índices geopolíticos por país (2026)
- **EIA**: Precios históricos Brent/WTI
- **GPU Deals**: Scraping histórico mercado GPUs
- **RAM Deals**: Scraping histórico mercado RAM
- **Bitcoin**: Precios históricos

## Período Analizado

Septiembre 2025 - Enero 2026 (~110 días)

## Dependencias

- `pandas`: Manipulación de datos
- `numpy`: Cálculos numéricos
- `matplotlib`: Gráficos
- `seaborn`: Visualizaciones estadísticas

## Licencia

MIT

## Autor

Análisis desarrollado para estudio de relaciones entre eventos geopolíticos y mercados globales.
