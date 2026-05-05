"""
Generates outputs/sa_water_linkedin_deck.pptx
10-slide LinkedIn carousel — SA Water affordability story
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "outputs" / "sa_water_linkedin_deck.pptx"

# ── Palette ──────────────────────────────────────────────────────────────────
NAVY    = RGBColor(0x0A, 0x16, 0x28)
BLUE    = RGBColor(0x00, 0x95, 0xD9)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
GOLD    = RGBColor(0xF5, 0xA6, 0x23)
MUTED   = RGBColor(0x8A, 0xA0, 0xB8)
RED     = RGBColor(0xC0, 0x39, 0x2B)
PANEL   = RGBColor(0x14, 0x26, 0x40)
BORDER  = RGBColor(0x1E, 0x3A, 0x5F)

W = Inches(13.33)   # slide width
H = Inches(7.5)     # slide height


# ── Helpers ───────────────────────────────────────────────────────────────────

def new_slide(prs):
    layout = prs.slide_layouts[6]          # blank
    return prs.slides.add_slide(layout)


def fill_bg(slide, color=NAVY):
    bg = slide.shapes.add_shape(1, 0, 0, W, H)  # MSO_SHAPE_TYPE.RECTANGLE = 1
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()


def accent_bar(slide, color=BLUE):
    bar = slide.shapes.add_shape(1, 0, 0, W, Inches(0.12))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()


def slide_number(slide, n):
    txb = slide.shapes.add_textbox(W - Inches(1), H - Inches(0.4), Inches(0.8), Inches(0.3))
    tf = txb.text_frame
    tf.text = f"{n} / 10"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    r = p.runs[0]
    r.font.size = Pt(10)
    r.font.color.rgb = MUTED
    r.font.bold = False


def add_label(slide, text, color=BLUE):
    """Small uppercase category label."""
    txb = slide.shapes.add_textbox(Inches(0.6), Inches(0.25), Inches(6), Inches(0.35))
    tf = txb.text_frame
    tf.text = text.upper()
    r = tf.paragraphs[0].runs[0]
    r.font.size = Pt(10)
    r.font.color.rgb = color
    r.font.bold = True


def add_title(slide, text, top=Inches(0.7), size=Pt(40), color=WHITE, width=W - Inches(1.2)):
    txb = slide.shapes.add_textbox(Inches(0.6), top, width, Inches(1.5))
    tf = txb.text_frame
    tf.word_wrap = True
    tf.text = text
    p = tf.paragraphs[0]
    r = p.runs[0]
    r.font.size = size
    r.font.color.rgb = color
    r.font.bold = True


def add_body(slide, lines, top=Inches(2.0), left=Inches(0.6), width=Inches(6),
             size=Pt(18), color=WHITE, line_spacing=1.4):
    txb = slide.shapes.add_textbox(left, top, width, H - top - Inches(0.5))
    tf = txb.text_frame
    tf.word_wrap = True
    for i, (text, bold, col) in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.space_after = Pt(6)
        r = p.add_run()
        r.text = text
        r.font.size = size
        r.font.color.rgb = col or color
        r.font.bold = bold


def stat_box(slide, label, value, unit, left, top, w=Inches(2.8), h=Inches(1.6),
             val_color=GOLD):
    box = slide.shapes.add_shape(1, left, top, w, h)
    box.fill.solid()
    box.fill.fore_color.rgb = PANEL
    box.line.color.rgb = BORDER

    txb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.1),
                                   w - Inches(0.3), h - Inches(0.2))
    tf = txb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = value
    r.font.size = Pt(34)
    r.font.bold = True
    r.font.color.rgb = val_color

    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    r2.text = unit
    r2.font.size = Pt(12)
    r2.font.color.rgb = MUTED
    r2.font.bold = False

    p3 = tf.add_paragraph()
    r3 = p3.add_run()
    r3.text = label
    r3.font.size = Pt(11)
    r3.font.color.rgb = WHITE
    r3.font.bold = True


def img_placeholder(slide, left, top, w, h, label="[ Paste screenshot here ]"):
    box = slide.shapes.add_shape(1, left, top, w, h)
    box.fill.solid()
    box.fill.fore_color.rgb = PANEL
    box.line.color.rgb = BORDER

    txb = slide.shapes.add_textbox(left + Inches(0.2), top + h / 2 - Inches(0.3),
                                   w - Inches(0.4), Inches(0.6))
    tf = txb.text_frame
    tf.text = label
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.runs[0]
    r.font.size = Pt(13)
    r.font.color.rgb = MUTED
    r.font.bold = False


def divider(slide, top, color=BORDER):
    line = slide.shapes.add_shape(1, Inches(0.6), top, W - Inches(1.2), Inches(0.01))
    line.fill.solid()
    line.fill.fore_color.rgb = color
    line.line.fill.background()


# ── Slides ────────────────────────────────────────────────────────────────────

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H


# ── Slide 1: HOOK ─────────────────────────────────────────────────────────────
s = new_slide(prs)
fill_bg(s)
accent_bar(s)

add_label(s, "Data Science × Public Policy")
add_title(s, "SA Water is a monopoly.\nYou can't switch providers.", top=Inches(1.0), size=Pt(44))
add_body(s, [
    ("When the regulator approves a price rise, Victor Harbor feels it", False, MUTED),
    ("very differently than Burnside — but nobody models that before", False, MUTED),
    ("the decision is made.", False, MUTED),
    ("", False, None),
    ("I built the model they don't have.", True, BLUE),
], top=Inches(3.2), size=Pt(19))

# Tag line at bottom
txb = s.shapes.add_textbox(Inches(0.6), H - Inches(0.9), Inches(10), Inches(0.5))
tf = txb.text_frame
tf.text = "176 SA2 areas  ·  ABS Census 2021  ·  SA Water tariff schedule  ·  ML + simulation engine"
r = tf.paragraphs[0].runs[0]
r.font.size = Pt(12)
r.font.color.rgb = MUTED

slide_number(s, 1)


# ── Slide 2: THE PROBLEM ──────────────────────────────────────────────────────
s = new_slide(prs)
fill_bg(s)
accent_bar(s)

add_label(s, "The core asymmetry")
add_title(s, "Same bill. Very different pain.", top=Inches(0.7), size=Pt(40))

stat_box(s, "Burnside (affluent)",  "1.7%",  "of household income", Inches(0.6),  Inches(2.0))
stat_box(s, "Elizabeth (working class)", "4.6%",  "of household income", Inches(3.7),  Inches(2.0), val_color=RED)
stat_box(s, "Hardship threshold",  ">4%",   "water cost burden", Inches(6.8),  Inches(2.0), val_color=GOLD)

add_body(s, [
    ("One price. One tariff. One regulator.", True, WHITE),
    ("", False, None),
    ("ESCoSA approves SA Water price determinations without a suburb-level", False, MUTED),
    ("impact model. The same dollar amount is an inconvenience in one suburb", False, MUTED),
    ("and a crisis in another.", False, MUTED),
], top=Inches(4.0), size=Pt(17))

slide_number(s, 2)


# ── Slide 3: WHAT I BUILT ─────────────────────────────────────────────────────
s = new_slide(prs)
fill_bg(s)
accent_bar(s)

add_label(s, "The pipeline")
add_title(s, "A full decision-support system.\nBuilt from scratch.", top=Inches(0.7), size=Pt(38))

steps = [
    ("1  ", "PDF extraction",          "SA Water Annual Reports (2022–25) → corrected tariff schedule"),
    ("2  ", "ABS Census 2021",         "Median household income for all 176 SA2s, WPI-adjusted to 2024"),
    ("3  ", "Water cost burden ratio", "Annual bill ÷ income — per suburb, per scenario"),
    ("4  ", "ML model",                "ExtraTrees classifier, F1 = 0.685 (SEIFA proxies, no leakage)"),
    ("5  ", "Simulation engine",       "8 price scenarios — named suburbs, not aggregate counts"),
    ("6  ", "SHAP explainability",     "What drives risk: IER score dominates"),
    ("7  ", "Hardship gap analysis",   "SA Water program uptake vs estimated suburb-level need"),
]

top = Inches(2.1)
for num, bold_part, rest in steps:
    txb = s.shapes.add_textbox(Inches(0.6), top, W - Inches(1.2), Inches(0.45))
    tf = txb.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    r1 = p.add_run(); r1.text = num;        r1.font.size = Pt(15); r1.font.color.rgb = BLUE;  r1.font.bold = True
    r2 = p.add_run(); r2.text = bold_part;  r2.font.size = Pt(15); r2.font.color.rgb = WHITE; r2.font.bold = True
    r3 = p.add_run(); r3.text = "   " + rest; r3.font.size = Pt(14); r3.font.color.rgb = MUTED; r3.font.bold = False
    top += Inches(0.58)

slide_number(s, 3)


# ── Slide 4: VULNERABILITY MAP ────────────────────────────────────────────────
s = new_slide(prs)
fill_bg(s)
accent_bar(s)

add_label(s, "Finding 1 — who's already in crisis")
add_title(s, "42 SA2s are already High or Critical\nat current prices.", top=Inches(0.7), size=Pt(36))

img_placeholder(s, Inches(0.5), Inches(2.0), Inches(7.8), Inches(5.0),
                "[ Screenshot: fig_burden_tier_rel_map.html ]")

# Legend panel
legend_items = [
    ("Critical",  "Top 10% of burden ratio",        RED),
    ("High",      "75th–90th percentile",            HIGH_ORANGE := RGBColor(0xE6, 0x7E, 0x22)),
    ("Moderate",  "25th–75th percentile",            GOLD),
    ("Low",       "Bottom 25%",                      BLUE),
]
lx = Inches(8.6); ly = Inches(2.2)
for tier, desc, col in legend_items:
    dot = s.shapes.add_shape(1, lx, ly + Inches(0.1), Inches(0.15), Inches(0.15))
    dot.fill.solid(); dot.fill.fore_color.rgb = col; dot.line.fill.background()
    txb = s.shapes.add_textbox(lx + Inches(0.25), ly, Inches(4.0), Inches(0.4))
    tf = txb.text_frame
    p = tf.paragraphs[0]
    r1 = p.add_run(); r1.text = tier + "  "; r1.font.size = Pt(13); r1.font.color.rgb = col; r1.font.bold = True
    r2 = p.add_run(); r2.text = desc;         r2.font.size = Pt(12); r2.font.color.rgb = MUTED
    ly += Inches(0.6)

txb = s.shapes.add_textbox(Inches(8.6), Inches(5.0), Inches(4.4), Inches(0.9))
tf = txb.text_frame
tf.word_wrap = True
tf.text = "Tier = relative percentile rank within all SA Water SA2s. Critical does not require >4% absolute burden."
r = tf.paragraphs[0].runs[0]
r.font.size = Pt(11); r.font.color.rgb = MUTED

slide_number(s, 4)


# ── Slide 5: THE SURPRISE ─────────────────────────────────────────────────────
s = new_slide(prs)
fill_bg(s)
accent_bar(s)

add_label(s, "Finding 2 — the suburbs nobody warned about")
add_title(s, "The coastal retirees are already Critical.", top=Inches(0.7), size=Pt(38))

suburbs = [
    ("Victor Harbor",      "2.32%", "Critical (relative)"),
    ("Goolwa–Port Elliot", "2.33%", "Critical (relative)"),
    ("Moonta",             "2.34%", "Critical (relative)"),
]
top = Inches(2.2); lx = Inches(0.6)
for name, ratio, tier in suburbs:
    box = s.shapes.add_shape(1, lx, top, Inches(12.0), Inches(0.85))
    box.fill.solid(); box.fill.fore_color.rgb = PANEL; box.line.color.rgb = RED

    txb = s.shapes.add_textbox(lx + Inches(0.2), top + Inches(0.1), Inches(5), Inches(0.65))
    tf = txb.text_frame; p = tf.paragraphs[0]
    r = p.add_run(); r.text = name; r.font.size = Pt(20); r.font.bold = True; r.font.color.rgb = WHITE

    txb2 = s.shapes.add_textbox(lx + Inches(5.5), top + Inches(0.15), Inches(2), Inches(0.55))
    tf2 = txb2.text_frame; p2 = tf2.paragraphs[0]
    r2 = p2.add_run(); r2.text = ratio; r2.font.size = Pt(22); r2.font.bold = True; r2.font.color.rgb = GOLD

    txb3 = s.shapes.add_textbox(lx + Inches(8.0), top + Inches(0.2), Inches(3.5), Inches(0.5))
    tf3 = txb3.text_frame; p3 = tf3.paragraphs[0]; p3.alignment = PP_ALIGN.RIGHT
    r3 = p3.add_run(); r3.text = tier; r3.font.size = Pt(14); r3.font.bold = True; r3.font.color.rgb = RED

    top += Inches(1.0)

add_body(s, [
    ("These are retirement towns. Fixed superannuation.", True, WHITE),
    ("Not in the statistical 'low income' bucket — but their income won't grow.", False, MUTED),
    ("Every percentage point on the tariff is money they genuinely don't have.", False, MUTED),
], top=Inches(5.3), size=Pt(16))

slide_number(s, 5)


# ── Slide 6: SIMULATION ───────────────────────────────────────────────────────
s = new_slide(prs)
fill_bg(s)
accent_bar(s)

add_label(s, "Finding 3 — the simulation engine")
add_title(s, "FY2025-26: approved.\nImpact: now modelled.", top=Inches(0.7), size=Pt(38))

scenarios = [
    ("+4.7%  (FY2025-26 approved)", "5",  "SA2s shift to a worse absolute tier"),
    ("+10%",                         "13", "SA2s shift"),
    ("+15%",                         "20", "SA2s shift"),
    ("+20%",                         "28", "SA2s shift"),
]
top = Inches(2.1)
for label, count, desc in scenarios:
    txb = s.shapes.add_textbox(Inches(0.6), top, W - Inches(1.2), Inches(0.55))
    tf = txb.text_frame; p = tf.paragraphs[0]
    r1 = p.add_run(); r1.text = label + "  →  "; r1.font.size = Pt(17); r1.font.color.rgb = MUTED
    r2 = p.add_run(); r2.text = count;            r2.font.size = Pt(22); r2.font.bold = True; r2.font.color.rgb = GOLD
    r3 = p.add_run(); r3.text = "  " + desc;      r3.font.size = Pt(17); r3.font.color.rgb = WHITE
    top += Inches(0.7)

img_placeholder(s, Inches(0.5), Inches(4.8), Inches(7.5), Inches(2.3),
                "[ Screenshot: outputs/simulation/scenario_tier_counts.html ]")

add_body(s, [
    ("Christie Downs, Jamestown, Kadina tip first at +4.7%.", True, WHITE),
    ("Named suburbs. Not aggregate counts.", False, MUTED),
], top=Inches(4.85), left=Inches(8.2), width=Inches(4.8), size=Pt(15))

slide_number(s, 6)


# ── Slide 7: HARDSHIP GAP ─────────────────────────────────────────────────────
s = new_slide(prs)
fill_bg(s)
accent_bar(s)

add_label(s, "Finding 4 — the hardship program gap")
add_title(s, "SA Water's assistance program\nisn't reaching the right suburbs.", top=Inches(0.7), size=Pt(36))

stat_box(s, "customers enrolled statewide", "2,732", "SA Water hardship program", Inches(0.6), Inches(2.2), w=Inches(3.2))
stat_box(s, "average outstanding debt",     "$2,590", "per enrolled customer",    Inches(4.1), Inches(2.2), w=Inches(3.2), val_color=RED)

img_placeholder(s, Inches(0.5), Inches(4.0), Inches(7.5), Inches(3.0),
                "[ Screenshot: fig_estimated_hardship_need_map.html ]")

add_body(s, [
    ("The map shows estimated hardship need by suburb.", True, WHITE),
    ("", False, None),
    ("High-stress SA2s — especially outer metro and", False, MUTED),
    ("regional SA — are underrepresented in the program", False, MUTED),
    ("relative to their predicted need.", False, MUTED),
    ("", False, None),
    ("No suburb-level uptake data is publicly available.", False, MUTED),
    ("This is the gap the data can identify.", False, MUTED),
], top=Inches(4.0), left=Inches(8.2), width=Inches(4.8), size=Pt(14))

slide_number(s, 7)


# ── Slide 8: SHAP ─────────────────────────────────────────────────────────────
s = new_slide(prs)
fill_bg(s)
accent_bar(s)

add_label(s, "Finding 5 — what drives vulnerability")
add_title(s, "SHAP says: economic resources\nare the dominant signal.", top=Inches(0.7), size=Pt(38))

img_placeholder(s, Inches(0.5), Inches(2.1), Inches(7.5), Inches(4.9),
                "[ Screenshot: outputs/figures/09_shap_global_importance.html ]")

add_body(s, [
    ("Model: ExtraTrees (PyCaret AutoML)", True, WHITE),
    ("Macro F1 = 0.685  ·  168 SA2s  ·  6 SEIFA features", False, MUTED),
    ("", False, None),
    ("Features used — SEIFA proxies only.", True, BLUE),
    ("No income. No bill. No leakage.", False, MUTED),
    ("", False, None),
    ("IER (economic resources) is the top predictor.", True, WHITE),
    ("IEO (education/occupation) ranks second.", False, MUTED),
    ("", False, None),
    ("Why it matters: SEIFA is a leading indicator.", True, WHITE),
    ("You can flag a suburb as at-risk without", False, MUTED),
    ("needing income data — which lags by 5 years.", False, MUTED),
], top=Inches(2.1), left=Inches(8.3), width=Inches(4.7), size=Pt(14))

slide_number(s, 8)


# ── Slide 9: THE 5 OUTPUTS ────────────────────────────────────────────────────
s = new_slide(prs)
fill_bg(s)
accent_bar(s)

add_label(s, "What this project delivers")
add_title(s, "5 outputs no public tool offers.", top=Inches(0.7), size=Pt(40))

outputs = [
    ("Suburb vulnerability map",      "Critical / High / Moderate / Low for every SA2 — at current prices."),
    ("Price-rise simulator",          "If ESCoSA approves X%, which named suburbs cross the threshold?"),
    ("Tipping point analysis",        "The exact % price increase that tips each borderline suburb over the edge."),
    ("Hardship program gap map",      "Which high-stress suburbs are underrepresented in SA Water's own assistance scheme?"),
    ("Rainfall overlay (V2)",         "The stressed suburbs are also in declining-rainfall zones. Drought compounding fixed-income risk."),
]

top = Inches(2.1)
for i, (title, desc) in enumerate(outputs, 1):
    box = s.shapes.add_shape(1, Inches(0.5), top, W - Inches(1.0), Inches(0.9))
    box.fill.solid(); box.fill.fore_color.rgb = PANEL; box.line.color.rgb = BORDER

    txb = s.shapes.add_textbox(Inches(0.8), top + Inches(0.05), W - Inches(1.6), Inches(0.85))
    tf = txb.text_frame; p = tf.paragraphs[0]; tf.word_wrap = True
    r1 = p.add_run(); r1.text = f"{i}  {title}  "; r1.font.size = Pt(16); r1.font.bold = True; r1.font.color.rgb = BLUE
    r2 = p.add_run(); r2.text = desc;             r2.font.size = Pt(14); r2.font.color.rgb = MUTED

    top += Inches(1.0)

slide_number(s, 9)


# ── Slide 10: CTA ─────────────────────────────────────────────────────────────
s = new_slide(prs)
fill_bg(s)

# Full-width blue bar at top
bar = s.shapes.add_shape(1, 0, 0, W, Inches(0.5))
bar.fill.solid(); bar.fill.fore_color.rgb = BLUE; bar.line.fill.background()

add_title(s, "The regulatory gap exists.", top=Inches(1.0), size=Pt(46))
add_title(s, "I built the tool to close it.", top=Inches(2.1), size=Pt(38), color=GOLD)

add_body(s, [
    ("Before ESCoSA approves the next price rise, this is what", False, MUTED),
    ("the data says — suburb by suburb, for every SA2 in SA.", False, MUTED),
    ("", False, None),
    ("The methodology, data, and code are open.", True, WHITE),
], top=Inches(3.5), size=Pt(19))

# Stack line
txb = s.shapes.add_textbox(Inches(0.6), H - Inches(1.3), W - Inches(1.2), Inches(0.5))
tf = txb.text_frame
tf.text = "Python  ·  pandas / geopandas  ·  scikit-learn  ·  PyCaret  ·  SHAP  ·  Plotly  ·  Power BI"
r = tf.paragraphs[0].runs[0]
r.font.size = Pt(13); r.font.color.rgb = MUTED

# Bottom bar
bbar = s.shapes.add_shape(1, 0, H - Inches(0.5), W, Inches(0.5))
bbar.fill.solid(); bbar.fill.fore_color.rgb = PANEL; bbar.line.fill.background()

txb2 = s.shapes.add_textbox(Inches(0.5), H - Inches(0.45), W - Inches(1), Inches(0.4))
tf2 = txb2.text_frame; p2 = tf2.paragraphs[0]; p2.alignment = PP_ALIGN.CENTER
r2 = p2.add_run()
r2.text = "github.com/mussaussie  ·  linkedin.com/in/mussaussie  ·  Data Science for Public Policy"
r2.font.size = Pt(11); r2.font.color.rgb = MUTED

slide_number(s, 10)


# ── Save ──────────────────────────────────────────────────────────────────────
prs.save(OUT)
print(f"Saved: {OUT}")
