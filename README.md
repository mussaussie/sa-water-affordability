# SA Water Affordability & Infrastructure Stress
### Suburb-level analysis of water cost burden across 176 SA2 areas — South Australia · V2

---

## Why I built this

SA Water uses a single statewide tariff. Every household in South Australia pays the same rate per kilolitre — there is no alternative provider, no way to negotiate, no way to opt out.

When the regulator approves a price rise, it applies that percentage uniformly across the state. But household incomes are not uniform. A $1,160 annual bill is under 1% of income in Burnside. In Elizabeth, it's over 2%. The same regulatory decision lands very differently depending on where you live.

I wanted to model that — suburb by suburb — and find out which communities were already closest to the edge, and which would cross it first if prices rose.

The result surprised me. The suburbs I expected to find in crisis (remote outback communities) were there — but so were coastal retirement towns like Victor Harbor, Goolwa, and Moonta. Fixed superannuation. No ability to earn more. Already ranking in the top 10% of water affordability stress in the state.

**V2 adds a rainfall dimension:** the suburbs nearest the affordability threshold are also in the fastest-declining rainfall zones. Drought years push usage (and bills) up — but retirement-income households can't adapt with greywater systems or efficient appliances. The regulatory risk compounds.

---

## What I found

- **42 SA2s** are already in High or Critical tier by relative vulnerability ranking at current FY2024-25 prices
- **Victor Harbor, Goolwa, Moonta** rank Critical — not because they're impoverished, but because retirees on fixed incomes have no buffer when a fixed cost rises
- At the **FY2025-26 approved increase (+4.7%)**, 5 SA2s shift to a worse absolute stress tier. At +10%, it's 13. At +20%, it's 28.
- SA Water's hardship assistance program (2,732 customers statewide) appears underweighted toward the suburbs the data predicts need it most
- **SHAP analysis** confirmed that SEIFA socioeconomic indexes are a genuine leading indicator of water affordability stress — meaning we can identify at-risk suburbs *before* income data is collected
- **V2 — 13 double-stress SA2s** are Critical on water affordability *and* in long-term rainfall decline (2000–2025). SA mean rainfall trend: −2.8 mm/yr. Worst affected: Elizabeth, Victor Harbor, Wallaroo, Moonta, Yorke Peninsula, Berri, Renmark.

---

## The dashboard

Open `outputs/dashboard.html` in any browser — no server required. Five tabs, all interactive Plotly figures.

| Tab | What it shows |
|-----|---------------|
| **Vulnerability Map** | Burden tier choropleth (relative percentile + absolute policy threshold). Hover any SA2 for suburb name, burden ratio, and tier. |
| **Price Rise Simulator** | Interactive scenario selector (8 price scenarios). Shows exactly which SA2s shift tier at each increment. |
| **Hardship Priority** | Estimated hardship need map — volume of households likely experiencing payment stress by suburb. |
| **ML Explainability** | SHAP global importance, beeswarm (Critical tier), and waterfall for the top 3 Critical SA2s. |
| **V2: Rainfall Overlay** | Double-stress map (Critical burden + declining rainfall), rainfall trend choropleth, top 20 steepest-decline bar chart. |

---

## What I built — the full pipeline

| Phase | Notebook | What I did |
|-------|----------|------------|
| 2 | `02_pdf_extraction.ipynb` | Extracted and corrected the FY2024-25 residential tariff schedule from SA Water PDFs |
| 3 | `03_cleaning.ipynb` | Joined SA Water pricing, ABS SEIFA 2021, and SA2 spatial boundaries into a single suburb-level table |
| 4 | `04_eda.ipynb` | Explored the stress distribution across SA — first time I saw the geographic pattern clearly |
| 5 | `05_feature_engineering.ipynb` | Replaced the SEIFA proxy with true ABS Census 2021 household income, WPI-adjusted to FY2024-25. Built the corrected tiered billing engine and dual tier system |
| 6 | `06_ml_modelling.ipynb` | Trained baseline classifiers (Logistic Regression, Random Forest, Gradient Boosting) using SEIFA proxies only. Macro F1 ~0.60 — honest signal, not tautology |
| 7 | `07_automl_pycaret.ipynb` | Ran 14 models via PyCaret AutoML. Best: ExtraTrees at F1 = 0.685 |
| 8 | `08_simulation_engine.ipynb` | Built the price-rise simulation engine — 8 scenarios × 176 SA2s, tipping point analysis per suburb |
| 9 | `09_shap_explainability.ipynb` | Used SHAP TreeExplainer to decompose each suburb's predicted tier into per-feature contributions |
| 10 | `10_powerbi_export.ipynb` | Packaged the three output tables into a Power BI data model |
| 11 *(V2)* | `11_rainfall_overlay.ipynb` | Layered 55 BOM stations onto SA2 centroids (nearest-point join), computed 2000–2025 linear rainfall trends, identified 13 double-stress SA2s |

---

## The leakage lesson (worth reading)

My first ML model produced F1 = 1.000. That looked impressive — until I realised why.

The stress tier label is derived from `bill ÷ income`. If you include both `bill` and `income` as features, the model trivially learns the threshold formula. It's not predicting anything — it's recalculating the label.

I rebuilt the model with SEIFA proxies only: no income, no bill. Macro F1 dropped to ~0.60. That's the real number — and it means SEIFA indexes genuinely predict water affordability risk, not just reflect the label. The lesson is documented in `06_ml_modelling.ipynb`.

---

## Tier system

I use two parallel classifications throughout:

**`burden_tier_abs`** — absolute policy threshold (water bill as % of household income):

| Tier | Threshold | SA2 count at current prices |
|------|-----------|----------------------------|
| Critical | > 4% | 0 |
| High | 3–4% | 0 |
| Moderate | 2–3% | 24 |
| Low | < 2% | 144 |

No SA2 breaches the 4% hardship threshold at current FY2024-25 prices. The story is about which suburbs get there first as prices rise.

**`burden_tier_rel`** — relative percentile rank within SA Water SA2s:

| Tier | Threshold | SA2 count |
|------|-----------|-----------|
| Critical | Top 10% | 17 |
| High | 75th–90th percentile | 25 |
| Moderate | 25th–75th percentile | 84 |
| Low | Bottom 25% | 42 |

The relative tier is the vulnerability map — it shows which suburbs are most at risk *right now*, even before any absolute threshold is crossed.

---

## Data sources

All data is publicly available. Download and place in the paths shown before running notebooks.

| Dataset | Source | Path |
|---------|--------|------|
| SA Water Annual Reports 2022–23, 2023–24, 2024–25 | [sawater.com.au](https://www.sawater.com.au/about-us/our-publications/our-reports/annual-report) | `data/raw/` |
| ABS SEIFA 2021 — SA2 level | [ABS SEIFA 2021](https://www.abs.gov.au/statistics/people/people-and-communities/socio-economic-indexes-areas-seifa-australia/2021) | `data/raw/` |
| ABS Census 2021 G02 (SA) | [ABS Census DataPacks](https://www.abs.gov.au/census/find-census-data/datapacks) | `data/raw/` |
| ABS Wage Price Index 6345.0 Table 2b (SA) | [ABS WPI](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia) | `data/raw/` |
| ABS SA2 Shapefile GDA2020 | [ABS ASGS Edition 3](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3) | `data/spatial/` |
| BOM HQ rainfall — SA stations (districts 016–026) | BOM FTP: `ftp.bom.gov.au/anon/home/ncc/www/change/HQmonthlyR/` | `data/raw/bom_rainfall_sa.csv` |

---

## Billing constants (FY2024-25)

| Charge | Rate |
|--------|------|
| Tier 1 usage | $2.251/kL — first 140 kL/year |
| Tier 2 usage | $3.214/kL — 140–520 kL/year |
| Tier 3 usage | $3.482/kL — above 520 kL/year |
| Supply charge | $314.40/year (fixed, same everywhere) |
| Sewerage — metro | $0.622 per $1,000 Valuer-General property value |
| Sewerage — country | $0.928 per $1,000 property value |
| Typical usage | 189 kL/year (SA Water residential average) |

Note: Coober Pedy is supplied by the District Council of Coober Pedy, not SA Water. Bill and burden columns are set to NaN for this SA2.

---

## How to reproduce

All phases run on the `data-sci-scratch` conda environment (Python 3.13, geopandas installed via conda-forge).

```bash
conda activate data-sci-scratch

# V1 — core pipeline
jupyter nbconvert --to notebook --execute --inplace notebooks/02_pdf_extraction.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/03_cleaning.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/04_eda.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/05_feature_engineering.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/06_ml_modelling.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/07_automl_pycaret.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/08_simulation_engine.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/09_shap_explainability.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/10_powerbi_export.ipynb

# V2 — rainfall overlay
jupyter nbconvert --to notebook --execute --inplace notebooks/11_rainfall_overlay.ipynb
```

Then open `outputs/dashboard.html` in a browser.

---

## Stack

Python 3.13 · pandas · geopandas · scipy · scikit-learn · PyCaret · SHAP · Plotly

---

## Disclaimer

Personal learning project. All data is publicly available from SA Water, ABS, and BOM. Methodology is my own and has not been peer-reviewed. The 4% hardship threshold reflects the benchmark most commonly cited in Australian water affordability research (National Water Commission, IPART). ESCoSA has not published an equivalent figure for South Australia.
