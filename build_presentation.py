import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Paths
BASE_DIR = r"C:\Users\tmmud\.gemini\antigravity-ide\scratch\stroke-xai-framework"
IMAGES_DIR = os.path.join(BASE_DIR, "images")
OUTPUT_PPTX = os.path.join(BASE_DIR, "NEUROPULSE_STROKE_XAI_PRESENTATION.pptx")
OUTPUT_DESKTOP = r"C:\Users\tmmud\OneDrive\Desktop\NEUROPULSE_STROKE_XAI_PRESENTATION.pptx"
OUTPUT_DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads", "NEUROPULSE_STROKE_XAI_PRESENTATION.pptx")

# Color Palette Constants
NAVY_DARK = RGBColor(11, 19, 43)       # #0B132B
NAVY_MID = RGBColor(28, 37, 65)        # #1C2541
TEAL_ACCENT = RGBColor(13, 148, 136)   # #0D9488
CYAN_ACCENT = RGBColor(6, 182, 212)    # #06B6D4
BLUE_ACCENT = RGBColor(37, 99, 235)    # #2563EB
SLATE_BG = RGBColor(248, 250, 252)     # #F8FAFC
SLATE_CARD = RGBColor(255, 255, 255)   # #FFFFFF
SLATE_BORDER = RGBColor(226, 232, 240) # #E2E8F0
TEXT_MAIN = RGBColor(15, 23, 42)       # #0F172A
TEXT_MUTED = RGBColor(100, 116, 139)   # #64748B
TEXT_LIGHT = RGBColor(241, 245, 249)   # #F1F5F9
EMERALD = RGBColor(16, 185, 129)       # #10B981
ROSE_RED = RGBColor(239, 68, 68)       # #EF4444
AMBER = RGBColor(245, 158, 11)         # #F59E0B

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def add_header(slide, title_text, category_text, dark_mode=False):
    # Category tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.5), Inches(0.35))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.size = Pt(10)
    p_c.font.bold = True
    p_c.font.color.rgb = CYAN_ACCENT if dark_mode else TEAL_ACCENT

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.5), Inches(0.6))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_LIGHT if dark_mode else TEXT_MAIN

def add_card(slide, left, top, width, height, bg_color=SLATE_CARD, border_color=SLATE_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

# ==========================================
# SLIDE 1: Title Slide (Dark Theme)
# ==========================================
s1 = prs.slides.add_slide(blank_layout)
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg1.fill.solid()
bg1.fill.fore_color.rgb = NAVY_DARK
bg1.line.fill.background()

# Title badge
badge1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.1), Inches(4.2), Inches(0.42))
badge1.fill.solid()
badge1.fill.fore_color.rgb = NAVY_MID
badge1.line.color.rgb = CYAN_ACCENT
badge1.line.width = Pt(1)
p_b1 = badge1.text_frame.paragraphs[0]
p_b1.text = "IEEE TRANSACTIONS COMPLIANT RESEARCH"
p_b1.font.size = Pt(10)
p_b1.font.bold = True
p_b1.font.color.rgb = CYAN_ACCENT
p_b1.alignment = PP_ALIGN.CENTER

# Main Title & Subtitle
tb1 = s1.shapes.add_textbox(Inches(0.9), Inches(1.75), Inches(11.5), Inches(2.6))
tf1 = tb1.text_frame
tf1.word_wrap = True
tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = 0

p1 = tf1.paragraphs[0]
p1.text = "NeuroPulse XAI"
p1.font.size = Pt(46)
p1.font.bold = True
p1.font.color.rgb = RGBColor(255, 255, 255)

p1_sub = tf1.add_paragraph()
p1_sub.text = "An Explainable Machine Learning Framework for Stroke Risk, Severity, and Functional Outcome Prediction on Imbalanced Clinical Data"
p1_sub.font.size = Pt(18)
p1_sub.font.color.rgb = RGBColor(148, 163, 184)
p1_sub.space_before = Pt(10)

# Author & Affiliation Card
card_auth = add_card(s1, Inches(0.9), Inches(4.7), Inches(11.5), Inches(1.8), NAVY_MID, CYAN_ACCENT)
tb_a = s1.shapes.add_textbox(Inches(1.2), Inches(4.85), Inches(10.9), Inches(1.5))
tf_a = tb_a.text_frame
tf_a.word_wrap = True
tf_a.margin_left = tf_a.margin_top = tf_a.margin_right = tf_a.margin_bottom = 0

p_a1 = tf_a.paragraphs[0]
p_a1.text = "Researcher & Lead Author: Tanishka Mudgal (Reg. No: RA2311003011560)"
p_a1.font.size = Pt(15)
p_a1.font.bold = True
p_a1.font.color.rgb = RGBColor(255, 255, 255)

p_a2 = tf_a.add_paragraph()
p_a2.text = "Department of Computing Technologies | SRM Institute of Science and Technology, Chennai, India"
p_a2.font.size = Pt(13)
p_a2.font.color.rgb = CYAN_ACCENT
p_a2.space_before = Pt(4)

p_a3 = tf_a.add_paragraph()
p_a3.text = "Contact: tm6968@srmist.edu.in | Core Stack: CatBoost • Platt Calibration • TreeSHAP • Decision Curve Analysis"
p_a3.font.size = Pt(11.5)
p_a3.font.color.rgb = RGBColor(148, 163, 184)
p_a3.space_before = Pt(6)

# ==========================================
# SLIDE 2: Executive Summary & Overview
# ==========================================
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "Executive Overview: Bridging Predictive AI and Clinical Practice", "Project Mission")

cols_data_s2 = [
    ("The Clinical Dilemma", "Strokes are the #2 cause of mortality globally (6.6M annual deaths). Early identification saves millions of neurons, but traditional scores fail to model complex biological synergies.", ROSE_RED),
    ("The AI Translation Barrier", "Standard machine learning models suffer from severe class imbalance (<5%), produce wildly inflated probabilities (up to 38%), and act as opaque black boxes that doctors reject.", AMBER),
    ("The NeuroPulse Solution", "A 5-Stage framework on the Kaggle cohort (N=5,110) combining 19.54:1 cost-sensitive CatBoost, Platt calibration (75.6% Brier drop), and TreeSHAP mechanistic insights.", TEAL_ACCENT)
]

for i, (title, desc, accent) in enumerate(cols_data_s2):
    left = Inches(0.8 + i * 3.95)
    add_card(s2, left, Inches(1.6), Inches(3.8), Inches(5.1))
    
    # Top accent bar
    top_bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, Inches(1.6), Inches(3.8), Inches(0.12))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = accent
    top_bar.line.fill.background()
    
    tb = s2.shapes.add_textbox(left + Inches(0.3), Inches(2.0), Inches(3.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p_t = tf.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(17)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_MAIN
    
    p_d = tf.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(13)
    p_d.font.color.rgb = TEXT_MUTED
    p_d.space_before = Pt(14)

# ==========================================
# SLIDE 3: The Problem Statement (The 3 Critical Barriers)
# ==========================================
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "Problem Statement: The Triad of Clinical AI Failure Modes", "Challenges & Gap")

problems = [
    ("1. Extreme Minority Class Imbalance", 
     "In real screening populations (and the Kaggle cohort), positive stroke prevalence is under 5% (4.87%, 19.54:1 ratio).\n\n• Unweighted algorithms collapse toward majority voting: achieving 95% accuracy while missing 100% of life-threatening events.\n• Synthetic oversampling (SMOTE) distorts real patient biological manifolds in mixed tabular data.", 
     ROSE_RED),
    ("2. Distorted Probability Calibration", 
     "When models apply loss reweighting to force sensitivity, output probabilities become severely shifted positive.\n\n• A patient with an actual 5% biological risk receives an uncalibrated raw score of 38.74%.\n• This triggers inappropriate clinical alarm, overtreatment, and expensive invasive angiography.", 
     AMBER),
    ("3. Black-Box Inscrutability & Opacity", 
     "Deep learning and standard ensembles conceal their internal decision boundaries.\n\n• Attending physicians cannot verify whether a high score is driven by legitimate vascular pathology or dataset artifacts.\n• Complete lack of bedside counterfactual guidance leaves clinicians without clear therapeutic levers.", 
     BLUE_ACCENT)
]

for i, (p_title, p_desc, p_accent) in enumerate(problems):
    left = Inches(0.8 + i * 3.95)
    add_card(s3, left, Inches(1.6), Inches(3.8), Inches(5.1))
    
    # Header tag
    tag = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.25), Inches(1.85), Inches(3.3), Inches(0.55))
    tag.fill.solid()
    tag.fill.fore_color.rgb = p_accent
    tag.line.fill.background()
    p_tag = tag.text_frame.paragraphs[0]
    p_tag.text = p_title
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = RGBColor(255, 255, 255)
    p_tag.alignment = PP_ALIGN.CENTER
    
    tb = s3.shapes.add_textbox(left + Inches(0.3), Inches(2.6), Inches(3.2), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = p_desc
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(6)

# ==========================================
# SLIDE 4: What The System Does
# ==========================================
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "System Purpose: Calibrated, Multi-Pillar Clinical Decision Support", "Core Solution")

add_card(s4, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
tb_s4_l = s4.shapes.add_textbox(Inches(1.1), Inches(1.85), Inches(5.0), Inches(4.5))
tf_s4_l = tb_s4_l.text_frame
tf_s4_l.word_wrap = True

p = tf_s4_l.paragraphs[0]
p.text = "End-to-End 5-Stage Machine Learning Pipeline"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = TEAL_ACCENT

p2 = tf_s4_l.add_paragraph()
p2.text = "Trained and validated on the public Kaggle Healthcare Stroke Dataset (N = 5,110 patients), resolving all three core barriers:\n\n" \
          "1. Preprocessing: Leakage-free train-median imputation (28.1 kg/m²).\n" \
          "2. Cost-Sensitive CatBoost: 19.54:1 inverse class weighting capturing 84% acute sensitivity (42/50 strokes).\n" \
          "3. Out-of-Fold Platt Calibration: Reduces Brier score by 75.6% (0.0416), matching true population prevalence (4.87%).\n" \
          "4. TreeSHAP Interpretability: Explains global drivers and local patient waterfalls.\n" \
          "5. Clinical Verification: Fairness audit and Decision Curve Net Benefit."
p2.font.size = Pt(12.5)
p2.font.color.rgb = TEXT_MAIN
p2.space_before = Pt(8)

add_card(s4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb_s4_r = s4.shapes.add_textbox(Inches(7.1), Inches(1.85), Inches(5.1), Inches(4.5))
tf_s4_r = tb_s4_r.text_frame
tf_s4_r.word_wrap = True

p_r = tf_s4_r.paragraphs[0]
p_r.text = "Tri-Pillar Bedside Clinical Scope"
p_r.font.size = Pt(17)
p_r.font.bold = True
p_r.font.color.rgb = BLUE_ACCENT

pillars_text = [
    ("Pillar 1: 10-Year Long-Term Stroke Risk", "Predicts Platt-calibrated biological probability & risk tier (Low, Moderate, High, Critical) based on patient vitals and vascular biomarkers."),
    ("Pillar 2: Acute Neurological Severity (NIHSS)", "Calculates bedside NIHSS score (0–42) from presenting acute neurological deficits (facial palsy, motor drift, aphasia, consciousness)."),
    ("Pillar 3: Reperfusion Prognosis (mRS <= 2)", "Estimates 90-day functional recovery conditioned on emergency interventions (IV tPA thrombolysis, Endovascular Thrombectomy).")
]

for p_title, p_body in pillars_text:
    p_t = tf_s4_r.add_paragraph()
    p_t.text = p_title
    p_t.font.size = Pt(13)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_MAIN
    p_t.space_before = Pt(10)
    
    p_b = tf_s4_r.add_paragraph()
    p_b.text = p_body
    p_b.font.size = Pt(11.5)
    p_b.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 5: Keywords & Scientific Concepts
# ==========================================
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "Domain Keywords & Theoretical Foundations", "Scientific Glossary")

keywords = [
    ("Explainable AI (XAI)", "Algorithmic methods ensuring model outputs can be audited and pathophysiologically verified by clinicians."),
    ("TreeSHAP (Shapley Values)", "Game-theoretic additive feature decomposition satisfying local accuracy, missingness, and consistency."),
    ("Platt Sigmoid Scaling", "Post-hoc out-of-fold logistic calibration mapping raw model logits into empirical posterior probabilities."),
    ("Brier Score", "Strictly proper scoring rule measuring both discrimination and calibration loss: (1/N) * sum((P - Y)^2)."),
    ("Cost-Sensitive Learning", "Reweighting classification loss inversely to class priors (19.54:1) to heavily penalize false negatives."),
    ("Decision Curve Analysis (DCA)", "Quantifies clinical Net Benefit across decision thresholds, proving clinical utility over treat-all/treat-none."),
    ("Algorithmic Subgroup Fairness", "Stratified demographic audits across Age, Sex, and Hypertension to detect disparate performance."),
    ("NIHSS & mRS Scores", "National Institutes of Health Stroke Scale (acute deficit: 0–42) and modified Rankin Scale (90-day recovery: 0–6).")
]

for i, (kw_t, kw_d) in enumerate(keywords):
    row = i // 2
    col = i % 2
    left = Inches(0.8 + col * 5.95)
    top = Inches(1.6 + row * 1.3)
    add_card(s5, left, top, Inches(5.7), Inches(1.15))
    
    tb = s5.shapes.add_textbox(left + Inches(0.2), top + Inches(0.12), Inches(5.3), Inches(0.9))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = kw_t
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = TEAL_ACCENT
    
    p2 = tf.add_paragraph()
    p2.text = kw_d
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_MAIN
    p2.space_before = Pt(2)

# ==========================================
# SLIDE 6: Technology Stack
# ==========================================
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "Complete Technology Stack & Architectural Toolkit", "Tech Stack")

tech_cards = [
    ("Machine Learning & Modeling", 
     "• CatBoost (Oblivious Trees, Ordered Target Encoding)\n• Scikit-Learn (Logistic Regression, Random Forest)\n• XGBoost (Cost-Sensitive Boosting)\n• NumPy & Pandas (Data pipelines & Imputation)",
     TEAL_ACCENT),
    ("Explainability & Validation", 
     "• TreeSHAP (Local waterfall & global rankings)\n• Platt Scaling (CalibratedClassifierCV 5-fold)\n• Brier Score Metric Evaluation\n• Decision Curve Analysis (Vickers Net Benefit)",
     BLUE_ACCENT),
    ("Backend API Architecture", 
     "• Python 3.14 Runtime\n• FastAPI (High-performance async REST API)\n• Uvicorn ASGI Server\n• Modular routers: prediction, cohort, benchmarks",
     AMBER),
    ("Frontend & UX Interface", 
     "• Modern Glassmorphic CSS3 Design System\n• Vanilla JavaScript (Ultra-responsive)\n• Chart.js (Real-time dynamic visualizations)\n• HTML5 Print Engine (Clinical Audit PDF Export)",
     EMERALD)
]

for i, (t_title, t_items, t_accent) in enumerate(tech_cards):
    left = Inches(0.8 + i * 2.95)
    add_card(s6, left, Inches(1.6), Inches(2.8), Inches(5.1))
    
    bar = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, Inches(1.6), Inches(2.8), Inches(0.1))
    bar.fill.solid()
    bar.fill.fore_color.rgb = t_accent
    bar.line.fill.background()
    
    tb = s6.shapes.add_textbox(left + Inches(0.2), Inches(1.9), Inches(2.4), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p_t = tf.paragraphs[0]
    p_t.text = t_title
    p_t.font.size = Pt(15)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_MAIN
    
    p_b = tf.add_paragraph()
    p_b.text = t_items
    p_b.font.size = Pt(12)
    p_b.font.color.rgb = TEXT_MUTED
    p_b.space_before = Pt(12)

# ==========================================
# SLIDE 7: Tab 1 — Clinical Assessment
# ==========================================
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "Tab 1: Tri-Pillar Clinical Assessment & Certified Audit", "UI Walkthrough")

add_card(s7, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.1))
tb_s7 = s7.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.0), Inches(4.6))
tf_s7 = tb_s7.text_frame
tf_s7.word_wrap = True

p = tf_s7.paragraphs[0]
p.text = "Features & Bedside Capabilities:"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = TEAL_ACCENT

p_body = tf_s7.add_paragraph()
p_body.text = "• Tri-Pillar Input Panel:\n" \
             "   - Pillar 1: Long-term vascular vitals & lifestyle factors.\n" \
             "   - Pillar 2: Acute neurological deficit scoring (NIHSS 0–42).\n" \
             "   - Pillar 3: Reperfusion intervention toggles (IV tPA / EVT).\n\n" \
             "• Live Diagnostic Cards: Instant Platt-calibrated probability gauge, emergency triage badge, and 90-day recovery likelihood.\n\n" \
             "• Certified 1-Page Clinical Audit: Opens an accredited audit modal with full vitals, predictions, SHAP attribution bars, and attending clinician sign-off line for EHR integration."
p_body.font.size = Pt(12.5)
p_body.font.color.rgb = TEXT_MAIN
p_body.space_before = Pt(10)

img_path_s7 = os.path.join(IMAGES_DIR, "after_assessment.png")
if os.path.exists(img_path_s7):
    s7.shapes.add_picture(img_path_s7, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.1))

# ==========================================
# SLIDE 8: Tab 2 — What-If Counterfactual Simulator
# ==========================================
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "Tab 2: Interactive Counterfactual 'What-If' Studio", "UI Walkthrough")

add_card(s8, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.1))
tb_s8 = s8.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.0), Inches(4.6))
tf_s8 = tb_s8.text_frame
tf_s8.word_wrap = True

p = tf_s8.paragraphs[0]
p.text = "Actionable Preventative Simulation:"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = BLUE_ACCENT

p_body = tf_s8.add_paragraph()
p_body.text = "• The Need: Simply telling a patient they are at high risk causes fear; doctors need actionable levers to simulate therapeutic benefits.\n\n" \
             "• Dynamic Re-scoring Engine:\n" \
             "   - Blood Pressure Intervention: Lowering SBP to <130 mmHg projects absolute risk drops of 4.5% to 8.2%.\n" \
             "   - Glycemic Optimization: Normalizing glucose (<100 mg/dL) yields 2.1% to 4.8% risk reduction.\n" \
             "   - Smoking Cessation: Models endothelial recovery, stripping away the tobacco hazard.\n\n" \
             "• Real-time delta cards display exact numerical reduction in stroke likelihood."
p_body.font.size = Pt(12.5)
p_body.font.color.rgb = TEXT_MAIN
p_body.space_before = Pt(10)

img_path_s8 = os.path.join(IMAGES_DIR, "after_whatif.png")
if os.path.exists(img_path_s8):
    s8.shapes.add_picture(img_path_s8, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.1))

# ==========================================
# SLIDE 9: Tab 3 — SHAP Studio (Mechanistic Transparency)
# ==========================================
s9 = prs.slides.add_slide(blank_layout)
add_header(s9, "Tab 3: SHAP Studio — Mechanistic Model Transparency", "UI Walkthrough")

add_card(s9, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.1))
tb_s9 = s9.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.0), Inches(4.6))
tf_s9 = tb_s9.text_frame
tf_s9.word_wrap = True

p = tf_s9.paragraphs[0]
p.text = "Global & Local Explainability:"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = AMBER

p_body = tf_s9.add_paragraph()
p_body.text = "• Global Feature Hierarchy across Kaggle Cohort:\n" \
             "   1. Age (|phi| = 1.3975) — Primary vascular determinant\n" \
             "   2. BMI (|phi| = 0.2056) — Metabolic adiposity\n" \
             "   3. Glucose (|phi| = 0.0921) — Microvascular damage\n" \
             "   4. Hypertension (|phi| = 0.0806) — Wall shear stress\n" \
             "   5. Smoking (|phi| = 0.0373) — Oxidant toxicity\n\n" \
             "• Patient Waterfall Decomposition: Deconstructs an individual's logit score starting from base rate (phi_0) into positive pushes (red) and negative protections (blue).\n\n" \
             "• Age x Glucose Synergy: High glucose produces 5.75x higher stroke log-odds in patients >65 vs <45."
p_body.font.size = Pt(12)
p_body.font.color.rgb = TEXT_MAIN
p_body.space_before = Pt(8)

img_path_s9 = os.path.join(IMAGES_DIR, "after_shap.png")
if os.path.exists(img_path_s9):
    s9.shapes.add_picture(img_path_s9, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.1))

# ==========================================
# SLIDE 10: Tab 4 — Comparative Model Benchmarks
# ==========================================
s10 = prs.slides.add_slide(blank_layout)
add_header(s10, "Tab 4: Comparative Benchmarks on Kaggle Test Set (N=1,022)", "UI Walkthrough")

add_card(s10, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.1))
tb_s10 = s10.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.0), Inches(4.6))
tf_s10 = tb_s10.text_frame
tf_s10.word_wrap = True

p = tf_s10.paragraphs[0]
p.text = "Why CatBoost Outperforms Baselines:"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = EMERALD

p_body = tf_s10.add_paragraph()
p_body.text = "• Highest Minority Recall (84.00%):\n" \
              "   CatBoost detected 42 out of 50 positive strokes in the test cohort, outperforming Random Forest (76.0%) and XGBoost (60.0%).\n\n" \
              "• 5.77x PR-AUC Enrichment (0.2812):\n" \
              "   In extreme imbalance (4.87%), PR-AUC is far more informative than ROC-AUC. CatBoost dramatically outperforms XGBoost (0.1683).\n\n" \
              "• Lowest Calibration Loss (Brier = 0.0416):\n" \
              "   While uncalibrated baselines had Brier scores of 0.17 to 0.18, CatBoost with Platt scaling achieved 0.0416."
p_body.font.size = Pt(12.5)
p_body.font.color.rgb = TEXT_MAIN
p_body.space_before = Pt(10)

img_path_s10 = os.path.join(IMAGES_DIR, "after_benchmarks.png")
if os.path.exists(img_path_s10):
    s10.shapes.add_picture(img_path_s10, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.1))

# ==========================================
# SLIDE 11: Tab 5 — Kaggle 5-Stage Framework Audit
# ==========================================
s11 = prs.slides.add_slide(blank_layout)
add_header(s11, "Tab 5: Kaggle 5-Stage Audit & Methodological Integrity", "UI Walkthrough")

add_card(s11, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.1))
tb_s11 = s11.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.0), Inches(4.6))
tf_s11 = tb_s11.text_frame
tf_s11.word_wrap = True

p = tf_s11.paragraphs[0]
p.text = "Rigorous Multi-Dimensional Audit:"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = TEAL_ACCENT

p_body = tf_s11.add_paragraph()
p_body.text = "• Complete Methodological Transparency:\n" \
              "   Displays full mathematical specifications and hyperparameters for all 5 stages directly in the UI.\n\n" \
              "• Demographic Subgroup Fairness Audit:\n" \
              "   - Biological Sex: Complete parity (0.8389 Male vs 0.8403 Female).\n" \
              "   - Age Window: Peak clinical discrimination in the preventative 55–70 yr bracket (0.7387 AUC).\n\n" \
              "• Decision Curve Analysis (DCA):\n" \
              "   Confirms positive Net Benefit (+0.0185 at 10% threshold) where 'treat-all' policy causes net harm (-0.0568)."
p_body.font.size = Pt(12.5)
p_body.font.color.rgb = TEXT_MAIN
p_body.space_before = Pt(10)

img_path_s11 = os.path.join(IMAGES_DIR, "after_kaggle.png")
if os.path.exists(img_path_s11):
    s11.shapes.add_picture(img_path_s11, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.1))

# ==========================================
# SLIDE 12: Tab 6 — Institutional Cohort Batch Screening
# ==========================================
s12 = prs.slides.add_slide(blank_layout)
add_header(s12, "Tab 6: Institutional Cohort Batch Screening Engine", "UI Walkthrough")

add_card(s12, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.1))
tb_s12 = s12.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.0), Inches(4.6))
tf_s12 = tb_s12.text_frame
tf_s12.word_wrap = True

p = tf_s12.paragraphs[0]
p.text = "Population-Scale Clinical Triage:"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = BLUE_ACCENT

p_body = tf_s12.add_paragraph()
p_body.text = "• High-Throughput Processing:\n" \
              "   Clinicians and hospital administrators can upload multi-patient CSV files for immediate batch screening.\n\n" \
              "• Automated Risk Stratification:\n" \
              "   Instantly categorizes populations into Low, Moderate, High, and Critical risk tiers with visual distribution charts.\n\n" \
              "• Primary Driver Identification:\n" \
              "   Aggregates SHAP values across the entire batch to show dominant population-level risk factors (e.g., uncontrolled hypertension or untreated hyperglycemia)."
p_body.font.size = Pt(12.5)
p_body.font.color.rgb = TEXT_MAIN
p_body.space_before = Pt(10)

img_path_s12 = os.path.join(IMAGES_DIR, "after_cohort.png")
if os.path.exists(img_path_s12):
    s12.shapes.add_picture(img_path_s12, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.1))

# ==========================================
# SLIDE 13: Clinical Effectiveness & Utility (Why It Matters)
# ==========================================
s13 = prs.slides.add_slide(blank_layout)
add_header(s13, "Clinical Effectiveness: Real-World Utility & Bedside Impact", "Clinical Value")

effects = [
    ("Acute Patient Safety", "84.00% Minority Sensitivity", "Detects 42 out of 50 acute strokes, preventing catastrophic missed cases and permanent neurological disability.", ROSE_RED),
    ("Epidemiological Honesty", "75.6% Brier Score Reduction", "Platt scaling aligns predicted risk (4.92%) with actual population prevalence (4.87%), eliminating false alarms.", TEAL_ACCENT),
    ("Actionable Prevention", "Counterfactual Risk Delving", "Empowers doctors with simulated targets (BP, glucose) to counsel patients on quantifiable risk reductions.", BLUE_ACCENT),
    ("Clinical Workflow Ready", "Single-Page Certified Audit", "Direct print/PDF report with vitals, SHAP bars, and clinician sign-off enables immediate EHR integration.", AMBER)
]

for i, (title, stat, desc, accent) in enumerate(effects):
    left = Inches(0.8 + i * 2.95)
    add_card(s13, left, Inches(1.6), Inches(2.8), Inches(5.1))
    
    bar = s13.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, Inches(1.6), Inches(2.8), Inches(0.1))
    bar.fill.solid()
    bar.fill.fore_color.rgb = accent
    bar.line.fill.background()
    
    tb = s13.shapes.add_textbox(left + Inches(0.2), Inches(1.9), Inches(2.4), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p_t = tf.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(15)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_MAIN
    
    p_s = tf.add_paragraph()
    p_s.text = stat
    p_s.font.size = Pt(13)
    p_s.font.bold = True
    p_s.font.color.rgb = accent
    p_s.space_before = Pt(8)
    
    p_d = tf.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(11.5)
    p_d.font.color.rgb = TEXT_MUTED
    p_d.space_before = Pt(8)

# ==========================================
# SLIDE 14: Limitations & Future Roadmap
# ==========================================
s14 = prs.slides.add_slide(blank_layout)
add_header(s14, "Methodological Limitations & Future Research Horizons", "Limitations & Roadmap")

add_card(s14, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
tb_s14_l = s14.shapes.add_textbox(Inches(1.1), Inches(1.85), Inches(5.0), Inches(4.5))
tf_s14_l = tb_s14_l.text_frame
tf_s14_l.word_wrap = True

p_l = tf_s14_l.paragraphs[0]
p_l.text = "Current Limitations"
p_l.font.size = Pt(17)
p_l.font.bold = True
p_l.font.color.rgb = ROSE_RED

p_l_body = tf_s14_l.add_paragraph()
p_l_body.text = "1. Age-Bracket Sample Disparity:\n" \
                "   Low event density in patients <55 yrs (1.20%, 0.6278 AUC) and high baseline saturation in patients >70 yrs (22.79%, 0.5628 AUC) limits automated triage in these tiers.\n\n" \
                "2. Absence of Acute Neuroimaging Data:\n" \
                "   Current pipeline relies exclusively on tabular clinical features; non-contrast CT (NCCT) and MRI DWI scans are not yet incorporated.\n\n" \
                "3. Academic Research Prototype Status:\n" \
                "   Designed as an assistive decision-support tool; not FDA/CE cleared for standalone diagnostic triage."
p_l_body.font.size = Pt(12)
p_l_body.font.color.rgb = TEXT_MAIN
p_l_body.space_before = Pt(10)

add_card(s14, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb_s14_r = s14.shapes.add_textbox(Inches(7.1), Inches(1.85), Inches(5.1), Inches(4.5))
tf_s14_r = tb_s14_r.text_frame
tf_s14_r.word_wrap = True

p_r = tf_s14_r.paragraphs[0]
p_r.text = "Future Research Roadmap"
p_r.font.size = Pt(17)
p_r.font.bold = True
p_r.font.color.rgb = TEAL_ACCENT

p_r_body = tf_s14_r.add_paragraph()
p_r_body.text = "1. Multimodal Neuroimaging Fusion:\n" \
                "   Integrate Vision Transformers (ViT) on brain CT/MRI imaging combined with tabular clinical features via cross-attention mechanisms.\n\n" \
                "2. Hospital EHR Connectivity (HL7 FHIR):\n" \
                "   Build bidirectional connectors to stream real-time patient vitals directly from hospital databases.\n\n" \
                "3. Prospective Multi-Center Clinical Validation:\n" \
                "   Validate the calibrated framework across diverse international healthcare networks to ensure robust demographic generalizability."
p_r_body.font.size = Pt(12)
p_r_body.font.color.rgb = TEXT_MAIN
p_r_body.space_before = Pt(10)

# ==========================================
# SLIDE 15: Conclusion & Thank You (Dark Theme)
# ==========================================
s15 = prs.slides.add_slide(blank_layout)
bg15 = s15.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg15.fill.solid()
bg15.fill.fore_color.rgb = NAVY_DARK
bg15.line.fill.background()

tb15 = s15.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.3), Inches(3.5))
tf15 = tb15.text_frame
tf15.word_wrap = True

p_c1 = tf15.paragraphs[0]
p_c1.text = "Thank You!"
p_c1.font.size = Pt(44)
p_c1.font.bold = True
p_c1.font.color.rgb = RGBColor(255, 255, 255)
p_c1.alignment = PP_ALIGN.CENTER

p_c2 = tf15.add_paragraph()
p_c2.text = "NeuroPulse XAI: Bridging the Gap from Opaque Algorithms to Trustworthy Bedside Clinical Decision Support"
p_c2.font.size = Pt(18)
p_c2.font.color.rgb = CYAN_ACCENT
p_c2.space_before = Pt(12)
p_c2.alignment = PP_ALIGN.CENTER

card_concl = add_card(s15, Inches(2.2), Inches(3.8), Inches(8.9), Inches(2.2), NAVY_MID, CYAN_ACCENT)
tb_concl = s15.shapes.add_textbox(Inches(2.5), Inches(4.0), Inches(8.3), Inches(1.8))
tf_concl = tb_concl.text_frame
tf_concl.word_wrap = True

p_res = tf_concl.paragraphs[0]
p_res.text = "Author: Tanishka Mudgal (RA2311003011560)"
p_res.font.size = Pt(15)
p_res.font.bold = True
p_res.font.color.rgb = RGBColor(255, 255, 255)
p_res.alignment = PP_ALIGN.CENTER

p_dept = tf_concl.add_paragraph()
p_dept.text = "Department of Computing Technologies | SRM Institute of Science and Technology"
p_dept.font.size = Pt(13)
p_dept.font.color.rgb = RGBColor(203, 213, 225)
p_dept.space_before = Pt(4)
p_dept.alignment = PP_ALIGN.CENTER

p_repo = tf_concl.add_paragraph()
p_repo.text = "GitHub: https://github.com/Tanishka-2004/stroke-xai-framework"
p_repo.font.size = Pt(12)
p_repo.font.color.rgb = CYAN_ACCENT
p_repo.space_before = Pt(6)
p_repo.alignment = PP_ALIGN.CENTER

# Save presentation
prs.save(OUTPUT_PPTX)
print(f"Saved PPTX to {OUTPUT_PPTX}")

try:
    prs.save(OUTPUT_DESKTOP)
    print(f"Saved PPTX to Desktop: {OUTPUT_DESKTOP}")
except Exception as e:
    print(f"Desktop save failed: {e}")

try:
    prs.save(OUTPUT_DOWNLOADS)
    print(f"Saved PPTX to Downloads: {OUTPUT_DOWNLOADS}")
except Exception as e:
    print(f"Downloads save failed: {e}")
