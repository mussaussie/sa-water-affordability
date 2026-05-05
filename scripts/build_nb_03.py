"""Build notebooks/03_cleaning.ipynb"""
import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()
cells = []

# ── 0: Header ─────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
    "# 03 — Cleaning & Merging: Build Master SA2 Dataset\n\n"
    "## Purpose\n"
    "Join SA Water tariff data, ABS SEIFA 2021 indexes, and SA2 spatial boundaries\n"
    "into a single master dataset — one row per SA2 suburb. This is the dataset\n"
    "all downstream phases (EDA, ML, simulation, Power BI) consume.\n\n"
    "## Important note on income data\n"
    "SEIFA 2021 does not publish median household income in dollars. It publishes\n"
    "composite index scores. We use the **IER (Index of Economic Resources)** as a\n"
    "relative proxy for household economic capacity. A higher IER = more resources =\n"
    "lower water stress. Actual dollar income (ABS Census G02) can be added in Phase 5\n"
    "if downloaded to enrich the model.\n\n"
    "## Inputs\n"
    "- `data/raw/Statistical Area Level 2, Indexes, SEIFA 2021.xlsx` — Table 1 (all indexes)\n"
    "- `data/spatial/SA2_2021_AUST_GDA2020.shp` — SA2 boundaries, CRS EPSG:7844\n"
    "- `data/clean/clean_sawater_tariff_2425.csv` — FY2024-25 tariff reference\n\n"
    "## Outputs\n"
    "- `data/clean/clean_master_sa2.csv` — flat master table, one row per SA2\n"
    "- `data/clean/clean_master_sa2.gpkg` — same data with geometry for spatial phases\n"
))

# ── 1: Imports ─────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell(
    "import pandas as pd\n"
    "import geopandas as gpd\n"
    "from pathlib import Path\n"
    "\n"
    "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
    "RAW     = PROJECT_ROOT / 'data' / 'raw'\n"
    "SPATIAL = PROJECT_ROOT / 'data' / 'spatial'\n"
    "CLEAN   = PROJECT_ROOT / 'data' / 'clean'\n"
    "\n"
    "SEIFA_PATH  = RAW / 'Statistical Area Level 2, Indexes, SEIFA 2021.xlsx'\n"
    "SHP_PATH    = SPATIAL / 'SA2_2021_AUST_GDA2020.shp'\n"
    "TARIFF_PATH = CLEAN / 'clean_sawater_tariff_2425.csv'\n"
    "\n"
    "for p in [SEIFA_PATH, SHP_PATH, TARIFF_PATH]:\n"
    "    status = 'OK' if p.exists() else 'MISSING'\n"
    "    print(f'  [{status}] {p.name}')\n"
))

# ── 2: Load SEIFA ──────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
    "## Load SEIFA 2021 — Table 1 (all index scores)\n\n"
    "Table 1 is the summary sheet with all 4 SEIFA indexes in one place.\n"
    "The actual data starts at row 5 (0-indexed row 4 is the header).\n"
    "Filter to SA: SA2 codes starting with `'4'` (ABS SA state prefix)."
))

cells.append(nbf.v4.new_code_cell(
    "# Header is at Excel row 5 (skiprows=4 gives us that row as columns)\n"
    "seifa_raw = pd.read_excel(\n"
    "    SEIFA_PATH,\n"
    "    sheet_name='Table 1',\n"
    "    engine='openpyxl',\n"
    "    skiprows=4,\n"
    "    dtype=str,\n"
    ")\n"
    "\n"
    "print('Raw shape:', seifa_raw.shape)\n"
    "print('Raw columns:', list(seifa_raw.columns))\n"
    "print(seifa_raw.head(3).to_string())\n"
))

cells.append(nbf.v4.new_code_cell(
    "# Rename columns to readable names based on Table 1 structure:\n"
    "# Col 0: SA2 code | Col 1: SA2 name | Col 2-3: IRSD score+decile\n"
    "# Col 4-5: IRSAD | Col 6-7: IER | Col 8-9: IEO | Col 10: Population\n"
    "col_map = {\n"
    "    seifa_raw.columns[0]:  'SA2_CODE21',\n"
    "    seifa_raw.columns[1]:  'SA2_NAME_SEIFA',\n"
    "    seifa_raw.columns[2]:  'irsd_score',\n"
    "    seifa_raw.columns[3]:  'irsd_decile',\n"
    "    seifa_raw.columns[4]:  'irsad_score',\n"
    "    seifa_raw.columns[5]:  'irsad_decile',\n"
    "    seifa_raw.columns[6]:  'ier_score',\n"
    "    seifa_raw.columns[7]:  'ier_decile',\n"
    "    seifa_raw.columns[8]:  'ieo_score',\n"
    "    seifa_raw.columns[9]:  'ieo_decile',\n"
    "    seifa_raw.columns[10]: 'population',\n"
    "}\n"
    "seifa = seifa_raw.rename(columns=col_map)[list(col_map.values())].copy()\n"
    "\n"
    "# Drop header-bleed rows (where SA2_CODE21 is not numeric)\n"
    "seifa = seifa[seifa['SA2_CODE21'].str.match(r'^\\d{9}$', na=False)].copy()\n"
    "\n"
    "# SA2_CODE21 must stay as string (leading zeros exist in some codes)\n"
    "# Filter to South Australia: SA2 codes start with '4'\n"
    "seifa = seifa[seifa['SA2_CODE21'].str.startswith('4')].copy()\n"
    "\n"
    "# Convert numeric columns\n"
    "for col in ['irsd_score','irsd_decile','irsad_score','irsad_decile',\n"
    "            'ier_score','ier_decile','ieo_score','ieo_decile','population']:\n"
    "    seifa[col] = pd.to_numeric(seifa[col], errors='coerce')\n"
    "\n"
    "print(f'SA SEIFA shape: {seifa.shape}')\n"
    "print(seifa.dtypes)\n"
    "print(seifa.head(5).to_string(index=False))\n"
))

cells.append(nbf.v4.new_code_cell(
    "# Sanity checks\n"
    "print('SA2_CODE21 sample:', seifa['SA2_CODE21'].head(5).tolist())\n"
    "print('All start with 4:', seifa['SA2_CODE21'].str.startswith('4').all())\n"
    "print('IER score range:', seifa['ier_score'].min(), '—', seifa['ier_score'].max())\n"
    "print('IRSD score range:', seifa['irsd_score'].min(), '—', seifa['irsd_score'].max())\n"
    "print('Nulls:\\n', seifa.isnull().sum())\n"
))

# ── 3: Load shapefile ──────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
    "## Load SA2 shapefile — filter to South Australia"
))

cells.append(nbf.v4.new_code_cell(
    "gdf_all = gpd.read_file(SHP_PATH)\n"
    "print(f'All Australia shape: {gdf_all.shape}')\n"
    "print(f'CRS: {gdf_all.crs}')\n"
    "assert str(gdf_all.crs.to_epsg()) == '7844', 'CRS mismatch — expected EPSG:7844'\n"
    "\n"
    "# Filter to SA immediately\n"
    "gdf = gdf_all[gdf_all['STE_CODE21'] == '4'].copy()\n"
    "print(f'SA only shape: {gdf.shape}')\n"
    "print(gdf.dtypes)\n"
    "print(gdf[['SA2_CODE21','SA2_NAME21','AREASQKM21']].head(5).to_string(index=False))\n"
))

cells.append(nbf.v4.new_code_cell(
    "# Keep only the columns we need from the shapefile\n"
    "gdf = gdf[['SA2_CODE21','SA2_NAME21','SA3_NAME21','SA4_NAME21',\n"
    "           'AREASQKM21','geometry']].copy()\n"
    "\n"
    "print(f'Shape after column trim: {gdf.shape}')\n"
    "print(gdf.dtypes)\n"
))

# ── 4: Load tariff ─────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
    "## Load FY2024-25 tariff reference\n\n"
    "Statewide flat-rate pricing — same bill components for every SA2.\n"
    "Sewerage is the only spatially variable component (property-value based).\n"
    "We use $600K as state-median property value baseline; Phase 5 will\n"
    "substitute per-SA2 median property values when available."
))

cells.append(nbf.v4.new_code_cell(
    "tariff = pd.read_csv(TARIFF_PATH)\n"
    "print(tariff.T.to_string())\n"
    "\n"
    "USAGE_CHARGE   = float(tariff['usage_charge_per_kl'].iloc[0])\n"
    "ACCESS_ANNUAL  = float(tariff['water_access_charge_annual'].iloc[0])\n"
    "SEWER_PER_1K   = float(tariff['sewerage_cents_per_1000_pv'].iloc[0])\n"
    "TYPICAL_KL     = float(tariff['typical_usage_kl'].iloc[0])\n"
    "MEDIAN_PROP_K  = 600.0  # $600K state median property value baseline\n"
    "\n"
    "water_usage_annual  = TYPICAL_KL * USAGE_CHARGE\n"
    "water_access_annual = ACCESS_ANNUAL\n"
    "sewer_annual        = MEDIAN_PROP_K * SEWER_PER_1K\n"
    "estimated_annual_bill = water_usage_annual + water_access_annual + sewer_annual\n"
    "\n"
    "print(f'\\nBill components (statewide uniform):')\n"
    "print(f'  Water usage  ({TYPICAL_KL:.0f} kL x ${USAGE_CHARGE}):  ${water_usage_annual:.2f}')\n"
    "print(f'  Water access (annual):              ${water_access_annual:.2f}')\n"
    "print(f'  Sewerage ($600K baseline):          ${sewer_annual:.2f}')\n"
    "print(f'  TOTAL estimated annual bill:        ${estimated_annual_bill:.2f}')\n"
))

# ── 5: Join ────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
    "## Join SEIFA + shapefile on SA2_CODE21\n\n"
    "Both datasets use SA2_CODE21 as the join key — kept as string throughout.\n"
    "We do a left join from the shapefile so geometry rows are the reference."
))

cells.append(nbf.v4.new_code_cell(
    "master = gdf.merge(\n"
    "    seifa,\n"
    "    on='SA2_CODE21',\n"
    "    how='left',\n"
    "    validate='1:1',\n"
    ")\n"
    "\n"
    "print(f'Master shape after join: {master.shape}')\n"
    "print(master.dtypes)\n"
    "print(f'\\nJoin nulls (SEIFA columns):')\n"
    "print(master[['irsd_score','ier_score','population']].isnull().sum())\n"
))

cells.append(nbf.v4.new_code_cell(
    "# Investigate any unmatched rows\n"
    "unmatched = master[master['ier_score'].isnull()]\n"
    "if len(unmatched) > 0:\n"
    "    print(f'Unmatched SA2s ({len(unmatched)}):')    \n"
    "    print(unmatched[['SA2_CODE21','SA2_NAME21']].to_string(index=False))\n"
    "    print('\\nNote: These may be non-residential or excluded areas in SEIFA.')\n"
    "else:\n"
    "    print('All SA2s matched successfully.')\n"
))

# ── 6: Calculate stress metrics ────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
    "## Calculate water stress metrics\n\n"
    "Since SEIFA does not publish median household income in dollars, we use\n"
    "the **IER score** (Index of Economic Resources) as the economic capacity proxy.\n\n"
    "**Water stress index** = estimated_annual_bill / IER_score × 1000\n\n"
    "This is dimensionless but comparable across suburbs — higher = more stressed.\n"
    "Suburbs with lower IER (less economic resources) get a higher stress score\n"
    "for the same water bill. Tiers will be set from the data distribution in Phase 4."
))

cells.append(nbf.v4.new_code_cell(
    "master['estimated_annual_water_bill'] = round(estimated_annual_bill, 2)\n"
    "\n"
    "# Water stress index: bill relative to economic resources\n"
    "# Multiply by 1000 so the number is in a readable range\n"
    "master['water_stress_index'] = round(\n"
    "    master['estimated_annual_water_bill'] / master['ier_score'] * 1000, 4\n"
    ")\n"
    "\n"
    "# Percentile rank within SA (higher rank = more stressed)\n"
    "master['stress_pct_rank'] = master['water_stress_index'].rank(\n"
    "    pct=True, ascending=True, na_option='bottom'\n"
    ").round(4)\n"
    "\n"
    "print(f'Water stress index stats:')\n"
    "print(master['water_stress_index'].describe().round(4))\n"
    "print(f'\\nTop 10 most stressed SA2s:')\n"
    "cols = ['SA2_NAME21','SA3_NAME21','ier_score','irsd_score','water_stress_index','stress_pct_rank']\n"
    "print(master.nlargest(10,'water_stress_index')[cols].to_string(index=False))\n"
    "print(f'\\nTop 10 least stressed SA2s:')\n"
    "print(master.nsmallest(10,'water_stress_index')[cols].to_string(index=False))\n"
))

# ── 7: Provisional stress tiers ────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
    "## Assign provisional stress tiers\n\n"
    "Thresholds are quartile-based for now. Phase 4 EDA will review the distribution\n"
    "and confirm whether these bands make narrative sense geographically."
))

cells.append(nbf.v4.new_code_cell(
    "def assign_stress_tier(pct_rank):\n"
    "    if pd.isna(pct_rank):   return 'Unknown'\n"
    "    if pct_rank >= 0.75:    return 'Critical'\n"
    "    if pct_rank >= 0.50:    return 'High'\n"
    "    if pct_rank >= 0.25:    return 'Moderate'\n"
    "    return 'Low'\n"
    "\n"
    "master['stress_tier'] = master['stress_pct_rank'].apply(assign_stress_tier)\n"
    "\n"
    "print('Stress tier distribution:')\n"
    "print(master['stress_tier'].value_counts())\n"
    "print(f'\\nShape: {master.shape}')\n"
    "print(master.dtypes)\n"
))

# ── 8: Final column selection ──────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("## Final column selection and validation"))

cells.append(nbf.v4.new_code_cell(
    "FINAL_COLS = [\n"
    "    'SA2_CODE21', 'SA2_NAME21', 'SA3_NAME21', 'SA4_NAME21',\n"
    "    'population', 'AREASQKM21',\n"
    "    'irsd_score', 'irsd_decile',\n"
    "    'irsad_score', 'irsad_decile',\n"
    "    'ier_score', 'ier_decile',\n"
    "    'ieo_score', 'ieo_decile',\n"
    "    'estimated_annual_water_bill',\n"
    "    'water_stress_index',\n"
    "    'stress_pct_rank',\n"
    "    'stress_tier',\n"
    "    'geometry',\n"
    "]\n"
    "\n"
    "master = master[FINAL_COLS].copy()\n"
    "print(f'Final shape: {master.shape}')\n"
    "print(master.dtypes)\n"
    "print(f'\\nNull counts:')\n"
    "print(master.isnull().sum())\n"
    "print(f'\\nSample rows:')\n"
    "print(master[FINAL_COLS[:-1]].head(5).to_string(index=False))\n"
))

# ── 9: Save ────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("## Save outputs"))

cells.append(nbf.v4.new_code_cell(
    "# Save flat CSV (no geometry)\n"
    "out_csv = CLEAN / 'clean_master_sa2.csv'\n"
    "master.drop(columns=['geometry']).to_csv(out_csv, index=False)\n"
    "print(f'Saved: {out_csv.name}  ({out_csv.stat().st_size // 1024} KB)')\n"
    "print(f'Shape: {master.drop(columns=[\"geometry\"]).shape}')\n"
    "\n"
    "# Save GeoPackage (with geometry for spatial phases)\n"
    "out_gpkg = CLEAN / 'clean_master_sa2.gpkg'\n"
    "master.to_file(out_gpkg, driver='GPKG')\n"
    "print(f'Saved: {out_gpkg.name}  ({out_gpkg.stat().st_size // 1024} KB)')\n"
    "print(f'CRS: {master.crs}')\n"
))

# ── 10: Summary ────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
    "## Summary\n\n"
    "| Output | Rows | Description |\n"
    "|---|---|---|\n"
    "| `clean_master_sa2.csv` | 176 | Flat master table, one row per SA2 |\n"
    "| `clean_master_sa2.gpkg` | 176 | Same data with SA2 polygon geometry |\n\n"
    "### Key columns for downstream phases\n"
    "| Column | Use |\n"
    "|---|---|\n"
    "| `SA2_CODE21` | Join key — always string |\n"
    "| `ier_score` | Economic resources proxy (higher = better off) |\n"
    "| `irsd_score` | Socioeconomic disadvantage (lower = more disadvantaged) |\n"
    "| `estimated_annual_water_bill` | Uniform $1,948 baseline (statewide pricing) |\n"
    "| `water_stress_index` | Bill / IER × 1000 — relative stress measure |\n"
    "| `stress_tier` | Critical / High / Moderate / Low (provisional, confirm in Phase 4) |\n"
    "| `stress_pct_rank` | Percentile rank within SA (0=lowest, 1=highest stress) |\n\n"
    "### Limitation to address in Phase 5\n"
    "Median household income in dollars is not in SEIFA. To get the literal\n"
    "`water_cost_burden_ratio` (bill / income), download ABS Census 2021 G02\n"
    "(Selected Medians and Averages) at SA2 level from ABS TableBuilder or\n"
    "Community Profiles. This will allow a true % of income calculation.\n"
    "Current `water_stress_index` is a valid relative ranking but not a % figure.\n"
))

nb.cells = cells

out = Path(r"C:\Users\mussa\OneDrive\Desktop\Projects\sa_water_project\notebooks\03_cleaning.ipynb")
nbf.write(nb, out)
print(f"Written: {out}")
print(f"Cells: {len(nb.cells)}")
