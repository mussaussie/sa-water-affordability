"""Builder script for 08_simulation_engine.ipynb — Phase 8 of SA Water project."""
from pathlib import Path
import nbformat

nb = nbformat.v4.new_notebook()
nb.metadata["kernelspec"] = {
    "display_name": "Python 3 (ipykernel)",
    "language": "python",
    "name": "python3",
}

cells = []

# ── Cell 1: Markdown intro ──────────────────────────────────────────────────
cells.append(nbformat.v4.new_markdown_cell("""# Phase 8 — Simulation Engine

**Purpose:** Answer "if ESCoSA approves a price rise, how many SA2s cross into the Critical stress tier?"

**Inputs:**
- `data/clean/clean_master_sa2_v2.csv` — 176 SA2s with WPI-adjusted income and current burden ratios
- `data/clean/clean_master_sa2_v2.gpkg` — same data with geometry for choropleths

**Outputs:**
- `outputs/simulation/scenario_results.csv` — per-SA2 results for each scenario
- `outputs/simulation/tier_shift_map_7pct.html` — choropleth of tier changes under +7% rise
- `outputs/simulation/scenario_tier_counts.html` — grouped bar: tier counts per scenario
- `outputs/simulation/interactive_scenario_map.html` — choropleth with scenario dropdown

**Key parameters:**
- `price_increase_pct` — % change applied to the usage rate ($2.7098/kL)
- `usage_kl` — annual usage per household (default: 200 kL, SA residential average)
- `income_growth_pct` — % growth in household income (default: 0%; income already WPI-adjusted)

**Watch-outs:**
- Only the usage charge changes in simulations — access ($806.08) and sewerage (~$900) are fixed
- 7 Unknown-tier SA2s (non-residential, income = NaN) excluded from tier-shift counts
- Tier thresholds are absolute: Critical >4%, High 3–4%, Moderate 2–3%, Low <2%"""))

# ── Cell 2: Imports ─────────────────────────────────────────────────────────
cells.append(nbformat.v4.new_code_cell("""\
from pathlib import Path
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import plotly.express as px
import json

ROOT = Path().resolve().parent if Path().resolve().name == "notebooks" else Path().resolve()
DATA_CLEAN = ROOT / "data" / "clean"
SIM_OUT    = ROOT / "outputs" / "simulation"
FIG_OUT    = ROOT / "outputs" / "figures"

SIM_OUT.mkdir(parents=True, exist_ok=True)
print("Root:", ROOT)
print("Simulation output:", SIM_OUT)"""))

# ── Cell 3: Constants ────────────────────────────────────────────────────────
cells.append(nbformat.v4.new_code_cell("""\
# SA Water FY2024-25 tariff components (ESCoSA determination)
USAGE_RATE_BASE  = 2.7098   # $/kL
ACCESS_CHARGE    = 806.08   # $/year (fixed, 20mm connection)
SEWERAGE_CHARGE  = 900.00   # $/year (state-median $600K property × $1.50/1K)
USAGE_KL_DEFAULT = 200      # kL/year (SA residential average)
BASE_BILL        = USAGE_KL_DEFAULT * USAGE_RATE_BASE + ACCESS_CHARGE + SEWERAGE_CHARGE

# Tier thresholds (absolute burden ratio)
TIER_THRESHOLDS = {
    "Critical": 0.04,
    "High":     0.03,
    "Moderate": 0.02,
}
TIER_ORDER = ["Critical", "High", "Moderate", "Low", "Unknown"]
TIER_COLOURS = {
    "Critical": "#d62728",
    "High":     "#ff7f0e",
    "Moderate": "#ffdf00",
    "Low":      "#2ca02c",
    "Unknown":  "#aec7e8",
}

print(f"Base annual bill: ${BASE_BILL:.2f}")
print(f"  Usage ({USAGE_KL_DEFAULT} kL × ${USAGE_RATE_BASE}/kL): ${USAGE_KL_DEFAULT * USAGE_RATE_BASE:.2f}")
print(f"  Access charge: ${ACCESS_CHARGE:.2f}")
print(f"  Sewerage baseline: ${SEWERAGE_CHARGE:.2f}")"""))

# ── Cell 4: Load data ────────────────────────────────────────────────────────
cells.append(nbformat.v4.new_code_cell("""\
df = pd.read_csv(DATA_CLEAN / "clean_master_sa2_v2.csv", dtype={"SA2_CODE21": str})
gdf = gpd.read_file(DATA_CLEAN / "clean_master_sa2_v2.gpkg")
gdf["SA2_CODE21"] = gdf["SA2_CODE21"].astype(str)

# Reproject to WGS84 for Plotly
gdf = gdf.to_crs("EPSG:4326")

print("CSV shape:", df.shape)
print("GDF shape:", gdf.shape)
print("CRS:", gdf.crs)
print()
print("Current tier counts (Phase 5 baseline):")
print(df["burden_tier"].value_counts()[TIER_ORDER].dropna())"""))

# ── Cell 5: Define simulation function ──────────────────────────────────────
cells.append(nbformat.v4.new_code_cell("""\
def assign_tier(ratio):
    \"\"\"Assign absolute burden tier from water_cost_burden_ratio.\"\"\"
    if pd.isna(ratio):
        return "Unknown"
    if ratio > TIER_THRESHOLDS["Critical"]:
        return "Critical"
    if ratio > TIER_THRESHOLDS["High"]:
        return "High"
    if ratio > TIER_THRESHOLDS["Moderate"]:
        return "Moderate"
    return "Low"


def run_scenario(df_in, price_increase_pct, usage_kl=USAGE_KL_DEFAULT, income_growth_pct=0.0):
    \"\"\"
    Recalculate bill and burden ratio for every SA2 under given parameters.
    Returns a copy of the dataframe with new scenario columns added.
    Only the usage charge is adjusted — access and sewerage remain fixed.
    \"\"\"
    out = df_in.copy()

    new_usage_cost = usage_kl * USAGE_RATE_BASE * (1 + price_increase_pct / 100)
    out["sim_annual_bill"] = new_usage_cost + ACCESS_CHARGE + SEWERAGE_CHARGE

    adjusted_income = out["median_hhd_inc_annual_adj"] * (1 + income_growth_pct / 100)
    out["sim_burden_ratio"] = out["sim_annual_bill"] / adjusted_income

    out["sim_tier"] = out["sim_burden_ratio"].apply(assign_tier)

    # Tier shift relative to Phase 5 baseline (positive = more stressed)
    tier_rank = {"Low": 0, "Moderate": 1, "High": 2, "Critical": 3, "Unknown": None}
    out["baseline_rank"] = out["burden_tier"].map(tier_rank)
    out["sim_rank"]      = out["sim_tier"].map(tier_rank)
    out["tier_shift"]    = out["sim_rank"] - out["baseline_rank"]

    return out


# Validate: 0% rise should reproduce Phase 5 tiers exactly
ref = run_scenario(df, 0)
print("Reference scenario (0% rise) tier counts:")
print(ref["sim_tier"].value_counts()[TIER_ORDER].dropna())
print()
print("Phase 5 baseline tier counts:")
print(df["burden_tier"].value_counts()[TIER_ORDER].dropna())
print()
match = (ref["sim_tier"] == ref["burden_tier"]).all()
print(f"Reference matches Phase 5 exactly: {match}")"""))

# ── Cell 6: Run all scenarios ────────────────────────────────────────────────
cells.append(nbformat.v4.new_code_cell("""\
SCENARIOS = [0, 5, 7, 10, 15, 20]

results = {}
for pct in SCENARIOS:
    results[pct] = run_scenario(df, pct)

print("Scenario results computed for:", SCENARIOS, "% price increases")"""))

# ── Cell 7: Summary table ────────────────────────────────────────────────────
cells.append(nbformat.v4.new_code_cell("""\
rows = []
for pct, r in results.items():
    known = r[r["sim_tier"] != "Unknown"]
    baseline_known = r[r["burden_tier"] != "Unknown"]

    new_critical   = int(((known["sim_tier"] == "Critical") & (known["burden_tier"] != "Critical")).sum())
    total_shifts   = int((known["tier_shift"].abs() > 0).sum())

    row = {"Scenario": f"+{pct}%" if pct > 0 else "Baseline (0%)",
           "Bill ($)": f"{(USAGE_KL_DEFAULT * USAGE_RATE_BASE * (1 + pct/100) + ACCESS_CHARGE + SEWERAGE_CHARGE):.2f}"}
    for t in ["Critical","High","Moderate","Low"]:
        row[t] = int((r["sim_tier"] == t).sum())
    row["New Critical"] = new_critical
    row["Total Shifts"]  = total_shifts
    rows.append(row)

summary = pd.DataFrame(rows)
print(summary.to_string(index=False))"""))

# ── Cell 8: Figure — tier counts per scenario ────────────────────────────────
cells.append(nbformat.v4.new_code_cell("""\
scenario_labels = summary["Scenario"].tolist()
tiers_to_plot = ["Critical","High","Moderate","Low"]

fig_counts = go.Figure()
for tier in tiers_to_plot:
    fig_counts.add_trace(go.Bar(
        name=tier,
        x=scenario_labels,
        y=summary[tier],
        marker_color=TIER_COLOURS[tier],
        text=summary[tier],
        textposition="auto",
    ))

fig_counts.update_layout(
    title="SA2 Stress Tier Distribution Under Different Price Rise Scenarios",
    xaxis_title="Price Increase Scenario",
    yaxis_title="Number of SA2 Areas",
    barmode="group",
    legend_title="Stress Tier",
    template="plotly_white",
    height=500,
)
fig_counts.show()
fig_counts.write_html(SIM_OUT / "scenario_tier_counts.html")
print("Saved: scenario_tier_counts.html")"""))

# ── Cell 9: New Critical entrants per scenario ───────────────────────────────
cells.append(nbformat.v4.new_code_cell("""\
# For each scenario, list the SA2s that shift into Critical from a lower tier
for pct in SCENARIOS[1:]:  # skip baseline
    r = results[pct]
    new_crits = r[(r["sim_tier"] == "Critical") & (r["burden_tier"] != "Critical") & (r["burden_tier"] != "Unknown")]
    print(f"+{pct}% scenario — {len(new_crits)} SA2s newly enter Critical tier:")
    if len(new_crits) > 0:
        display_cols = ["SA2_NAME21","burden_tier","sim_tier","sim_burden_ratio","sim_annual_bill","median_hhd_inc_annual_adj"]
        print(new_crits[display_cols].sort_values("sim_burden_ratio", ascending=False).to_string(index=False))
    print()"""))

# ── Cell 10: Choropleth of tier changes — +7% headline scenario ──────────────
cells.append(nbformat.v4.new_code_cell("""\
# Join +7% scenario results back to geodataframe
r7 = results[7][["SA2_CODE21","sim_tier","tier_shift","sim_burden_ratio","sim_annual_bill"]].copy()
gdf7 = gdf.merge(r7, on="SA2_CODE21", how="left")

# Label shift direction for tooltip
def shift_label(shift):
    if pd.isna(shift) or shift == 0:
        return "No change"
    if shift > 0:
        return f"+{int(shift)} tier (more stressed)"
    return f"{int(shift)} tier (less stressed)"

gdf7["shift_label"]   = gdf7["tier_shift"].apply(shift_label)
gdf7["sim_tier"]      = gdf7["sim_tier"].fillna("Unknown")
gdf7["tooltip_name"]  = gdf7["SA2_NAME21"]

# Build choropleth coloured by the NEW tier under +7%
geojson7 = json.loads(gdf7.to_json())

fig_7pct = px.choropleth_mapbox(
    gdf7,
    geojson=geojson7,
    locations=gdf7.index,
    color="sim_tier",
    color_discrete_map=TIER_COLOURS,
    category_orders={"sim_tier": TIER_ORDER},
    hover_name="SA2_NAME21",
    hover_data={
        "sim_tier": True,
        "shift_label": True,
        "sim_burden_ratio": ":.2%",
        "sim_annual_bill": ":$.2f",
    },
    labels={
        "sim_tier": "Stress Tier (+7%)",
        "shift_label": "Tier shift vs baseline",
        "sim_burden_ratio": "Burden ratio (+7%)",
        "sim_annual_bill": "Annual bill (+7%)",
    },
    mapbox_style="carto-positron",
    center={"lat": -30.0, "lon": 135.5},
    zoom=4.5,
    opacity=0.75,
    title="SA Water Stress Tiers After +7% Price Rise (ESCoSA Scenario)",
)
fig_7pct.update_layout(height=700, template="plotly_white", margin={"r":0,"t":50,"l":0,"b":0})
fig_7pct.show()
fig_7pct.write_html(SIM_OUT / "tier_shift_map_7pct.html")
print("Saved: tier_shift_map_7pct.html")"""))

# ── Cell 11: Interactive multi-scenario choropleth with dropdown ─────────────
cells.append(nbformat.v4.new_code_cell("""\
# Build one choropleth trace per scenario, toggle visibility with dropdown buttons

# Merge all scenario results into gdf
all_gdf = gdf[["SA2_CODE21","SA2_NAME21","geometry"]].copy()
for pct in SCENARIOS:
    r = results[pct][["SA2_CODE21","sim_tier","sim_burden_ratio","sim_annual_bill"]]
    r = r.rename(columns={
        "sim_tier":         f"tier_{pct}",
        "sim_burden_ratio": f"ratio_{pct}",
        "sim_annual_bill":  f"bill_{pct}",
    })
    all_gdf = all_gdf.merge(r, on="SA2_CODE21", how="left")

geojson_all = json.loads(all_gdf.to_json())
idx = list(range(len(all_gdf)))

fig_interactive = go.Figure()
traces_per_scenario = []

for pct in SCENARIOS:
    tier_col  = f"tier_{pct}"
    ratio_col = f"ratio_{pct}"
    bill_col  = f"bill_{pct}"
    label     = f"+{pct}%" if pct > 0 else "Baseline (0%)"

    # One trace per tier value for legend colours — but simpler: use a single trace with discrete colour
    # Encode tier as numeric then map colours manually via marker.colors
    tier_vals  = all_gdf[tier_col].fillna("Unknown")
    tier_nums  = tier_vals.map({"Low":0,"Moderate":1,"High":2,"Critical":3,"Unknown":4})
    fill_colors = tier_vals.map(TIER_COLOURS)

    trace = go.Choroplethmapbox(
        geojson=geojson_all,
        locations=idx,
        z=tier_nums,
        colorscale=[
            [0.00, TIER_COLOURS["Low"]],
            [0.25, TIER_COLOURS["Low"]],
            [0.25, TIER_COLOURS["Moderate"]],
            [0.50, TIER_COLOURS["Moderate"]],
            [0.50, TIER_COLOURS["High"]],
            [0.75, TIER_COLOURS["High"]],
            [0.75, TIER_COLOURS["Critical"]],
            [1.00, TIER_COLOURS["Critical"]],
        ],
        zmin=0, zmax=3,
        showscale=False,
        marker_opacity=0.75,
        marker_line_width=0.3,
        name=label,
        text=all_gdf["SA2_NAME21"] + "<br>" + tier_vals + "<br>" +
             (all_gdf[ratio_col] * 100).round(2).astype(str) + "% burden ratio<br>" +
             "$" + all_gdf[bill_col].round(2).astype(str) + " annual bill",
        hovertemplate="%{text}<extra></extra>",
        visible=(pct == 0),
    )
    traces_per_scenario.append(trace)
    fig_interactive.add_trace(trace)

# Dropdown buttons
buttons = []
for i, pct in enumerate(SCENARIOS):
    label = f"+{pct}% rise" if pct > 0 else "Baseline (no rise)"
    visibility = [j == i for j in range(len(SCENARIOS))]
    buttons.append(dict(
        label=label,
        method="update",
        args=[{"visible": visibility},
              {"title": f"SA Water Stress Tiers — {label} Scenario"}]
    ))

fig_interactive.update_layout(
    title="SA Water Stress Tiers — Baseline (no rise) Scenario",
    mapbox_style="carto-positron",
    mapbox_center={"lat": -30.0, "lon": 135.5},
    mapbox_zoom=4.5,
    margin={"r":0,"t":60,"l":0,"b":0},
    height=750,
    updatemenus=[dict(
        active=0,
        buttons=buttons,
        direction="down",
        pad={"r":10,"t":10},
        showactive=True,
        x=0.01, xanchor="left",
        y=0.99, yanchor="top",
    )],
    annotations=[dict(
        text="Select scenario:",
        x=0.01, y=1.04,
        xref="paper", yref="paper",
        showarrow=False, align="left",
    )],
)
fig_interactive.show()
fig_interactive.write_html(SIM_OUT / "interactive_scenario_map.html")
print("Saved: interactive_scenario_map.html")"""))

# ── Cell 12: Tier-shift heatmap — which SA2s shift which tiers ──────────────
cells.append(nbformat.v4.new_code_cell("""\
# For the LinkedIn story: SA2s most at risk of entering a higher tier
# Show the 20 SA2s closest to the next tier boundary under baseline

known_df = df[df["burden_tier"] != "Unknown"].copy()

# Distance to next tier boundary
def dist_to_next_tier(row):
    ratio = row["water_cost_burden_ratio"]
    tier  = row["burden_tier"]
    if tier == "Critical":
        return None  # already worst
    if tier == "High":
        return TIER_THRESHOLDS["Critical"] - ratio
    if tier == "Moderate":
        return TIER_THRESHOLDS["High"] - ratio
    if tier == "Low":
        return TIER_THRESHOLDS["Moderate"] - ratio
    return None

known_df["dist_to_next_tier"] = known_df.apply(dist_to_next_tier, axis=1)
at_risk = known_df[known_df["burden_tier"] != "Critical"].nsmallest(20, "dist_to_next_tier")[
    ["SA2_NAME21","burden_tier","water_cost_burden_ratio","dist_to_next_tier","median_hhd_inc_annual_adj"]
].copy()
at_risk["ratio_pct"]    = (at_risk["water_cost_burden_ratio"] * 100).round(2).astype(str) + "%"
at_risk["gap_pct"]      = (at_risk["dist_to_next_tier"] * 100).round(2).astype(str) + "%"
at_risk["income_adj"]   = at_risk["median_hhd_inc_annual_adj"].round(0).astype(int)

print("Top 20 SA2s closest to crossing into next stress tier:")
print(at_risk[["SA2_NAME21","burden_tier","ratio_pct","gap_pct"]].to_string(index=False))"""))

# ── Cell 13: Save scenario_results.csv ──────────────────────────────────────
cells.append(nbformat.v4.new_code_cell("""\
# Build long-format combined CSV: one row per SA2 × scenario
all_rows = []
for pct, r in results.items():
    subset = r[["SA2_CODE21","SA2_NAME21","SA3_NAME21","SA4_NAME21",
                "burden_tier","median_hhd_inc_annual_adj",
                "sim_annual_bill","sim_burden_ratio","sim_tier","tier_shift"]].copy()
    subset.insert(0, "price_increase_pct", pct)
    all_rows.append(subset)

scenario_results = pd.concat(all_rows, ignore_index=True)
print("scenario_results shape:", scenario_results.shape)
print(scenario_results.head(3).to_string())

scenario_results.to_csv(SIM_OUT / "scenario_results.csv", index=False)
print("\\nSaved: scenario_results.csv")"""))

# ── Cell 14: Summary markdown ────────────────────────────────────────────────
cells.append(nbformat.v4.new_markdown_cell("""\
## Phase 8 Complete

### Outputs saved to `outputs/simulation/`
- `scenario_results.csv` — per-SA2 tier and burden ratio under 0%, +5%, +7%, +10%, +15%, +20% scenarios
- `scenario_tier_counts.html` — grouped bar chart of tier distribution per scenario
- `tier_shift_map_7pct.html` — choropleth of stress tiers under +7% price rise
- `interactive_scenario_map.html` — choropleth with dropdown to select any scenario

### Key numbers for LinkedIn
- See summary table above for tier counts per scenario
- "New Critical" column shows SA2s pushed over the 4% burden threshold

### Next: Phase 9 — SHAP Explainability (`09_shap_explainability.ipynb`)
- Which features drive the ML model's stress risk predictions?
- `median_hhd_inc_annual_adj` expected to dominate given flat tariff structure"""))

nb.cells = cells

out_path = Path(
    "C:/Users/mussa/OneDrive/Desktop/Projects/sa_water_project/notebooks/08_simulation_engine.ipynb"
)
with open(out_path, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print("Notebook written to:", out_path)
