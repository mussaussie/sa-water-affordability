# SA Water Affordability & Infrastructure Stress

Suburb-level analysis of water affordability across South Australia's 176 SA2 areas.
Full pipeline: PDF extraction → data cleaning → ML classification → simulation engine → SHAP → Power BI dashboard.

---

## The question

SA Water uses a single statewide tariff — the same rate for every suburb. But household incomes vary significantly across SA. So the same annual bill represents a very different proportion of income depending on where you live.

ESCoSA (Essential Services Commission of SA) approves price determinations that apply uniformly across the state. This project builds the suburb-level impact model that quantifies what each pricing decision means for each community.

---

## Key findings

- **42 SA2s** are already in High or Critical tier by relative vulnerability ranking at current FY2024-25 prices
- **Coastal retirement towns** — Victor Harbor, Goolwa, Moonta — rank Critical despite not fitting the typical low-income profile. Fixed superannuation incomes cannot absorb price rises.
- At the **FY2025-26 approved increase (+4.7%)**, 5 SA2s shift to a worse absolute stress tier. At +10%, it's 13.
- SA Water's hardship assistance program (**2,732 customers statewide**) appears underweighted toward the highest-need suburbs by estimated need.
- **SHAP analysis**: IER score (economic resources index) is the dominant predictor of water affordability stress — confirming SEIFA as a genuine leading indicator even without direct income data.

---

## Pipeline

| Phase | Notebook | Output |
|-------|----------|--------|
| 2 | `02_pdf_extraction.ipynb` | Corrected FY2024-25 residential tariff schedule |
| 3 | `03_cleaning.ipynb` | `clean_master_sa2.csv` — 176 SA2s, SEIFA joined |
| 4 | `04_eda.ipynb` | 8 exploratory figures |
| 5 | `05_feature_engineering.ipynb` | `clean_master_sa2_v2.csv` — true burden ratio, dual tier system |
| 6 | `06_ml_modelling.ipynb` | Baseline RF classifier, macro F1 ~0.60 (SEIFA proxies only) |
| 7 | `07_automl_pycaret.ipynb` | ExtraTrees, F1 = 0.685 (PyCaret AutoML, 14 models) |
| 8 | `08_simulation_engine.ipynb` | 8 price scenarios × 176 SA2s, tipping point analysis |
| 9 | `09_shap_explainability.ipynb` | Per-SA2 SHAP values, IER identified as top driver |
| 10 | `10_powerbi_export.ipynb` | 3 CSVs for Power BI data model |

---

## Tier system

Two parallel classifications are used throughout:

**`burden_tier_abs`** — absolute policy threshold (water cost as % of income):
- Critical: > 4% | High: 3–4% | Moderate: 2–3% | Low: < 2%
- At current FY2024-25 tariffs: 0 Critical, 0 High, 24 Moderate, 144 Low

**`burden_tier_rel`** — relative percentile rank within SA Water SA2s:
- Critical: top 10% | High: 75th–90th | Moderate: 25th–75th | Low: bottom 25%
- Distribution: 17 Critical, 25 High, 84 Moderate, 42 Low

Use `burden_tier_rel` for vulnerability mapping and ML. Use `burden_tier_abs` for simulation and policy reporting.

---

## Data sources

All data is publicly available. Download and place in the paths below before running notebooks.

| File | Source | Path |
|------|--------|------|
| SA Water Annual Reports 2022-23, 2023-24, 2024-25 | [sawater.com.au](https://www.sawater.com.au/about-us/our-publications/our-reports/annual-report) | `data/raw/` |
| ABS SEIFA 2021 — SA2 level | [ABS SEIFA 2021](https://www.abs.gov.au/statistics/people/people-and-communities/socio-economic-indexes-areas-seifa-australia/2021) | `data/raw/` |
| ABS Census 2021 G02 — SA | [ABS Census DataPacks](https://www.abs.gov.au/census/find-census-data/datapacks) | `data/raw/` |
| ABS WPI SA quarterly | [ABS 6345.0 Table 2b](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia) | `data/raw/` |
| ABS SA2 Shapefile GDA2020 | [ABS ASGS Edition 3](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3) | `data/spatial/` |
| BOM HQ rainfall SA (districts 016-026) | [BOM FTP](ftp://ftp.bom.gov.au/anon/home/ncc/www/change/HQmonthlyR/) | `data/raw/bom_rainfall_sa.csv` |

---

## Billing constants (FY2024-25)

| Charge | Rate |
|--------|------|
| Tier 1 usage | $2.251/kL (first 140 kL/year) |
| Tier 2 usage | $3.214/kL (140–520 kL/year) |
| Tier 3 usage | $3.482/kL (above 520 kL/year) |
| Supply charge | $314.40/year (fixed) |
| Sewerage — metro | $0.622 per $1,000 property value |
| Sewerage — country | $0.928 per $1,000 property value |
| Typical usage | 189 kL/year (SA Water residential average) |

Coober Pedy is supplied by the District Council of Coober Pedy, not SA Water. Bill and burden columns are set to NaN for this SA2.

---

## Reproduce

```bash
# Spatial phases (geopandas, PyCaret)
conda activate sa-water-py311
jupyter nbconvert --to notebook --execute --inplace notebooks/05_feature_engineering.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/07_automl_pycaret.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/08_simulation_engine.ipynb

# All other phases
conda activate data-sci-scratch
jupyter nbconvert --to notebook --execute --inplace notebooks/02_pdf_extraction.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/03_cleaning.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/04_eda.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/06_ml_modelling.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/09_shap_explainability.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/10_powerbi_export.ipynb
```

---

## Stack

Python 3.11 · pandas · geopandas · scikit-learn · PyCaret · SHAP · Plotly · Power BI

---

## Disclaimer

Personal learning project. All data is publicly available. Methodology is my own and has not been peer-reviewed. The 4% hardship threshold reflects the benchmark most commonly cited in Australian water affordability research — ESCoSA has not published an equivalent figure for South Australia.
