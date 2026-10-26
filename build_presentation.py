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

# Color Palette
NAVY_DARK = RGBColor(15, 23, 42)        # #0F172A
NAVY_MID = RGBColor(30, 41, 59)         # #1E293B
TEAL_ACCENT = RGBColor(13, 148, 136)    # #0D9488
CYAN_ACCENT = RGBColor(6, 182, 212)     # #06B6D4
BLUE_ACCENT = RGBColor(37, 99, 235)     # #2563EB
SLATE_BG = RGBColor(248, 250, 252)      # #F8FAFC
SLATE_CARD = RGBColor(255, 255, 255)    # #FFFFFF
SLATE_BORDER = RGBColor(226, 232, 240)  # #E2E8F0
TEXT_MAIN = RGBColor(15, 23, 42)        # #0F172A
TEXT_MUTED = RGBColor(71, 85, 105)      # #475569
TEXT_LIGHT = RGBColor(248, 250, 252)    # #F8FAFC
EMERALD = RGBColor(16, 185, 129)        # #10B981
ROSE_RED = RGBColor(239, 68, 68)        # #EF4444
AMBER = RGBColor(245, 158, 11)          # #F59E0B

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def add_header(slide, title_text, category_text, dark_mode=False):
    # Category tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.35))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = CYAN_ACCENT if dark_mode else TEAL_ACCENT

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.5), Inches(0.65))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(23)
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
# SLIDE 1: Title Slide (Simple & Clean)
# ==========================================
s1 = prs.slides.add_slide(blank_layout)
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg1.fill.solid()
bg1.fill.fore_color.rgb = NAVY_DARK
bg1.line.fill.background()

badge1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.1), Inches(4.5), Inches(0.42))
badge1.fill.solid()
badge1.fill.fore_color.rgb = NAVY_MID
badge1.line.color.rgb = CYAN_ACCENT
badge1.line.width = Pt(1)
p_b1 = badge1.text_frame.paragraphs[0]
p_b1.text = "SMART HEALTHCARE AI PROJECT"
p_b1.font.size = Pt(11)
p_b1.font.bold = True
p_b1.font.color.rgb = CYAN_ACCENT
p_b1.alignment = PP_ALIGN.CENTER

tb1 = s1.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(11.5), Inches(2.6))
tf1 = tb1.text_frame
tf1.word_wrap = True
tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = 0

p1 = tf1.paragraphs[0]
p1.text = "NeuroPulse XAI"
p1.font.size = Pt(46)
p1.font.bold = True
p1.font.color.rgb = RGBColor(255, 255, 255)

p1_sub = tf1.add_paragraph()
p1_sub.text = "A Smart, Trustworthy AI Tool for Stroke Risk Prediction, Severity Check, and Recovery Odds"
p1_sub.font.size = Pt(18)
p1_sub.font.color.rgb = RGBColor(203, 213, 225)
p1_sub.space_before = Pt(10)

card_auth = add_card(s1, Inches(0.9), Inches(4.7), Inches(11.5), Inches(1.8), NAVY_MID, CYAN_ACCENT)
tb_a = s1.shapes.add_textbox(Inches(1.2), Inches(4.85), Inches(10.9), Inches(1.5))
tf_a = tb_a.text_frame
tf_a.word_wrap = True
tf_a.margin_left = tf_a.margin_top = tf_a.margin_right = tf_a.margin_bottom = 0

p_a1 = tf_a.paragraphs[0]
p_a1.text = "Project By: Tanishka Mudgal (Reg. No: RA2311003011560)"
p_a1.font.size = Pt(16)
p_a1.font.bold = True
p_a1.font.color.rgb = RGBColor(255, 255, 255)

p_a2 = tf_a.add_paragraph()
p_a2.text = "Department of Computing Technologies | SRM Institute of Science and Technology"
p_a2.font.size = Pt(13)
p_a2.font.color.rgb = CYAN_ACCENT
p_a2.space_before = Pt(4)

p_a3 = tf_a.add_paragraph()
p_a3.text = "Goal: Helping doctors spot stroke dangers early with honest odds and clear explanations they can actually trust."
p_a3.font.size = Pt(12)
p_a3.font.color.rgb = RGBColor(148, 163, 184)
p_a3.space_before = Pt(6)

# ==========================================
# SLIDE 2: Executive Overview (The Big Picture)
# ==========================================
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "The Big Picture: Why Did We Build This?", "Simple Overview")

cols_data_s2 = [
    ("1. The Medical Danger", 
     "Stroke is the #2 killer in the world. When a blood clot blocks blood to the brain, about 2 million brain cells die every minute!\n\nIf doctors can catch the danger signs early, strokes can be prevented before permanent damage happens.", 
     ROSE_RED),
    ("2. Why Old Methods Fail", 
     "Doctors today still use basic point-based charts on paper. These simple charts add up numbers one by one, so they completely miss combined dangers — like how high blood pressure becomes 5x more dangerous when mixed with high blood sugar in older people.", 
     AMBER),
    ("3. Why Regular AI Fails", 
     "Normal AI models either:\n• Miss the real stroke patients completely because strokes are rare.\n• Exaggerate and give scary, fake high numbers.\n• Refuse to explain their answers, so doctors can't trust them.\n\nWe solved all three problems!", 
     TEAL_ACCENT)
]

for i, (title, desc, accent) in enumerate(cols_data_s2):
    left = Inches(0.8 + i * 3.95)
    add_card(s2, left, Inches(1.6), Inches(3.8), Inches(5.1))
    
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
# SLIDE 3: The Problem Statement (In Plain English)
# ==========================================
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "The Problem Statement: 3 Big Roadblocks in Stroke AI", "What Was Broken?")

problems = [
    ("Problem 1: Strokes Are Rare", 
     "Out of 100 people screened, less than 5 have had a stroke (under 5% prevalence).\n\n• If a computer program simply guesses 'No Stroke' for every single person, it looks 95% accurate on paper!\n• But in reality, it missed 100% of the sick people who needed urgent medical care.", 
     ROSE_RED),
    ("Problem 2: Exaggerated Odds", 
     "To force the computer to find strokes, programmers make it panic. But this breaks the numbers!\n\n• A patient whose real risk is only 5% gets told by the AI: 'You have a 40% chance of stroke!'\n• This terrifies healthy patients and sends them for expensive, painful hospital tests they never needed.", 
     AMBER),
    ("Problem 3: The 'Black Box'", 
     "Most AI tools give a score but won't explain why.\n\n• A doctor asks: 'Why did you say 35%? Is it their blood pressure, weight, or age?'\n• The AI can't answer. No doctor will risk a human life on computer advice they cannot understand.", 
     BLUE_ACCENT)
]

for i, (p_title, p_desc, p_accent) in enumerate(problems):
    left = Inches(0.8 + i * 3.95)
    add_card(s3, left, Inches(1.6), Inches(3.8), Inches(5.1))
    
    tag = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.25), Inches(1.85), Inches(3.3), Inches(0.55))
    tag.fill.solid()
    tag.fill.fore_color.rgb = p_accent
    tag.line.fill.background()
    p_tag = tag.text_frame.paragraphs[0]
    p_tag.text = p_title
    p_tag.font.size = Pt(12)
    p_tag.font.bold = True
    p_tag.font.color.rgb = RGBColor(255, 255, 255)
    p_tag.alignment = PP_ALIGN.CENTER
    
    tb = s3.shapes.add_textbox(left + Inches(0.3), Inches(2.6), Inches(3.2), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = p_desc
    p.font.size = Pt(12.5)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(6)

# ==========================================
# SLIDE 4: What Does Our System Do?
# ==========================================
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "What Does Our System Do? (The Solution)", "How It Works")

add_card(s4, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
tb_s4_l = s4.shapes.add_textbox(Inches(1.1), Inches(1.85), Inches(5.0), Inches(4.5))
tf_s4_l = tb_s4_l.text_frame
tf_s4_l.word_wrap = True

p = tf_s4_l.paragraphs[0]
p.text = "A 5-Stage Smart Pipeline"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = TEAL_ACCENT

p2 = tf_s4_l.add_paragraph()
p2.text = "Tested on 5,110 real hospital patient records from Kaggle, doing 5 simple things:\n\n" \
          "1. Clean Data: Fills in missing health values cleanly without peeking at the test set.\n" \
          "2. Fair Training: Punishes the AI heavily whenever it misses a stroke, teaching it not to ignore rare cases.\n" \
          "3. Honest Percentages: Automatically recalibrates probabilities so 5% really means 5%, not 40%.\n" \
          "4. Full Explanations: Breaks down every single factor pushing a patient's risk up or down.\n" \
          "5. Quality Check: Double-checks that the model is fair to men, women, young, and old alike."
p2.font.size = Pt(12.5)
p2.font.color.rgb = TEXT_MAIN
p2.space_before = Pt(8)

add_card(s4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb_s4_r = s4.shapes.add_textbox(Inches(7.1), Inches(1.85), Inches(5.1), Inches(4.5))
tf_s4_r = tb_s4_r.text_frame
tf_s4_r.word_wrap = True

p_r = tf_s4_r.paragraphs[0]
p_r.text = "3 Clinical Predictions in One Place"
p_r.font.size = Pt(17)
p_r.font.bold = True
p_r.font.color.rgb = BLUE_ACCENT

pillars_text = [
    ("1. Long-Term Stroke Risk", "Tells the patient their honest 10-year stroke chance (Low, Moderate, High, or Critical) based on their body vitals."),
    ("2. Acute Stroke Severity (NIHSS)", "If an emergency happens right now, it scores their symptoms (face drooping, arm weakness, speech trouble) on a scale of 0 to 42."),
    ("3. 90-Day Recovery Odds", "Predicts if the patient will walk and live normally after 3 months if given clot-busting medicine or surgery.")
]

for p_title, p_body in pillars_text:
    p_t = tf_s4_r.add_paragraph()
    p_t.text = p_title
    p_t.font.size = Pt(13.5)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_MAIN
    p_t.space_before = Pt(10)
    
    p_b = tf_s4_r.add_paragraph()
    p_b.text = p_body
    p_b.font.size = Pt(12)
    p_b.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 5: Key Words (In Plain English)
# ==========================================
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "Key Concepts Explained in Plain English", "No Fancy Jargon")

keywords = [
    ("Explainable AI (XAI)", "AI that shows its work and gives reasons for its answers, so doctors can double-check everything."),
    ("SHAP (The Explainer)", "A method that gives credit to each body feature (like age or smoking) for pushing the risk up or down."),
    ("Calibration (Honest Odds)", "Fixing the AI so its percentages are real: if it says 5% risk, 5 out of 100 people actually have it."),
    ("Brier Score (Error Meter)", "A scoreboard for how honest the AI's percentages are. Lower score = much more honest and accurate."),
    ("Class Imbalance", "When the sick cases are rare (only 5 in 100). The AI needs special rules so it doesn't ignore them."),
    ("What-If (Counterfactual)", "Testing: 'What if this patient drops their blood pressure by 20 points? How much safer will they be?'"),
    ("Decision Curve (Net Benefit)", "Mathematical proof that using this tool helps more patients than treating everyone or doing nothing."),
    ("NIHSS & Recovery Score", "Standard medical checklists doctors use to measure stroke damage and 3-month recovery.")
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
    p1.font.size = Pt(13.5)
    p1.font.bold = True
    p1.font.color.rgb = TEAL_ACCENT
    
    p2 = tf.add_paragraph()
    p2.text = kw_d
    p2.font.size = Pt(11.5)
    p2.font.color.rgb = TEXT_MAIN
    p2.space_before = Pt(2)

# ==========================================
# SLIDE 6: Tech Stack (What Tools Did We Use?)
# ==========================================
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "What Tech Did We Use to Build This?", "Under the Hood")

tech_cards = [
    ("Machine Learning Core", 
     "• CatBoost: A top-tier decision tree model that excels with medical tables.\n• Scikit-Learn: Used for baseline models and cross-validation.\n• XGBoost & Random Forest: Used to benchmark and compare.",
     TEAL_ACCENT),
    ("Explainability & Math", 
     "• TreeSHAP: Breaks open the AI to show green/red risk factors.\n• Platt Scaling: Mathematical formula to fix inflated probabilities.\n• Decision Curve Analysis: Proves real clinical benefit.",
     BLUE_ACCENT),
    ("Backend Web Server", 
     "• Python 3.14: Fast, modern execution.\n• FastAPI: Lightning-fast web engine to handle patient data in milliseconds.\n• Uvicorn: Server hosting the live application.",
     AMBER),
    ("User Interface & Design", 
     "• Clean HTML & CSS: Modern, beautiful interface that doctors love.\n• JavaScript: Dynamic instant updates without page refreshing.\n• Chart.js: Interactive risk charts.\n• PDF Engine: 1-click printable doctor reports.",
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
add_header(s7, "Tab 1: Patient Checkup & Printable Doctor Report", "What Each Tab Does")

add_card(s7, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.1))
tb_s7 = s7.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.0), Inches(4.6))
tf_s7 = tb_s7.text_frame
tf_s7.word_wrap = True

p = tf_s7.paragraphs[0]
p.text = "What Happens in Tab 1:"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = TEAL_ACCENT

p_body = tf_s7.add_paragraph()
p_body.text = "• Easy Patient Entry:\n" \
             "   Enter simple details: age, blood pressure, sugar, smoking status, and current symptoms.\n\n" \
             "• Instant Results Cards:\n" \
             "   - Dial gauge showing honest 10-year stroke risk %.\n" \
             "   - Acute emergency score (NIHSS 0–42).\n" \
             "   - Likelihood of walking/recovering in 3 months.\n\n" \
             "• 1-Click Printable Medical Report:\n" \
             "   Clicking 'Clinical Audit Report' pops up a clean 1-page summary with all vitals, risk bars, and a doctor signature line ready for paper medical files!"
p_body.font.size = Pt(12.5)
p_body.font.color.rgb = TEXT_MAIN
p_body.space_before = Pt(10)

img_path_s7 = os.path.join(IMAGES_DIR, "after_assessment.png")
if os.path.exists(img_path_s7):
    s7.shapes.add_picture(img_path_s7, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.1))

# ==========================================
# SLIDE 8: Tab 2 — What-If Simulator
# ==========================================
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "Tab 2: 'What-If' Simulator — Actionable Health Goals", "What Each Tab Does")

add_card(s8, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.1))
tb_s8 = s8.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.0), Inches(4.6))
tf_s8 = tb_s8.text_frame
tf_s8.word_wrap = True

p = tf_s8.paragraphs[0]
p.text = "Showing Patients How to Lower Risk:"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = BLUE_ACCENT

p_body = tf_s8.add_paragraph()
p_body.text = "• The Big Problem It Solves:\n" \
             "   Telling patients 'You have a 15% stroke risk' just scares them. They want to know: 'What can I do to fix it?'\n\n" \
             "• Interactive Sliders:\n" \
             "   - Drop Blood Pressure: Shows an immediate 4% to 8% drop in stroke danger.\n" \
             "   - Control Blood Sugar: Shows a 2% to 5% risk drop.\n" \
             "   - Quit Smoking: Erases the toxic tobacco hazard immediately.\n\n" \
             "• Gives doctors an exact roadmap to counsel and motivate their patients."
p_body.font.size = Pt(12.5)
p_body.font.color.rgb = TEXT_MAIN
p_body.space_before = Pt(10)

img_path_s8 = os.path.join(IMAGES_DIR, "after_whatif.png")
if os.path.exists(img_path_s8):
    s8.shapes.add_picture(img_path_s8, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.1))

# ==========================================
# SLIDE 9: Tab 3 — SHAP Explainer
# ==========================================
s9 = prs.slides.add_slide(blank_layout)
add_header(s9, "Tab 3: SHAP Explainer — Peeking Inside the AI", "What Each Tab Does")

add_card(s9, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.1))
tb_s9 = s9.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.0), Inches(4.6))
tf_s9 = tb_s9.text_frame
tf_s9.word_wrap = True

p = tf_s9.paragraphs[0]
p.text = "Explaining Exactly WHY the AI Made Its Call:"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = AMBER

p_body = tf_s9.add_paragraph()
p_body.text = "• Ranked Body Factors (From Biggest to Smallest):\n" \
             "   1. Age — The biggest factor in blood vessel wear\n" \
             "   2. BMI (Body Mass) — Weight and metabolic strain\n" \
             "   3. Blood Glucose — Sugar damaging vessel walls\n" \
             "   4. Hypertension — High pressure stressing arteries\n" \
             "   5. Smoking — Toxin damage to vessel linings\n\n" \
             "• Waterfall Chart: Shows red bars pushing the patient toward danger and blue bars protecting them.\n\n" \
             "• Discovered Synergy: High sugar is almost 6x more dangerous in people over 65 than in young adults."
p_body.font.size = Pt(12)
p_body.font.color.rgb = TEXT_MAIN
p_body.space_before = Pt(8)

img_path_s9 = os.path.join(IMAGES_DIR, "after_shap.png")
if os.path.exists(img_path_s9):
    s9.shapes.add_picture(img_path_s9, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.1))

# ==========================================
# SLIDE 10: Tab 4 — Model Benchmarks
# ==========================================
s10 = prs.slides.add_slide(blank_layout)
add_header(s10, "Tab 4: Model Benchmarks — Proving It Works", "What Each Tab Does")

add_card(s10, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.1))
tb_s10 = s10.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.0), Inches(4.6))
tf_s10 = tb_s10.text_frame
tf_s10.word_wrap = True

p = tf_s10.paragraphs[0]
p.text = "How Does It Compare to Other AI Models?"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = EMERALD

p_body = tf_s10.add_paragraph()
p_body.text = "• Tested on 1,022 Unseen Real Patients:\n" \
              "   We compared our CatBoost model against standard models (Logistic Regression, Random Forest, XGBoost).\n\n" \
              "• Catches 84% of Stroke Patients:\n" \
              "   Out of 50 real strokes in the test group, our model caught 42 of them! Other models only caught 30 or 38.\n\n" \
              "• 75% Reduction in Probability Errors:\n" \
              "   Our calibration dropped probability error from 0.17 down to 0.04, giving real, dependable percentages."
p_body.font.size = Pt(12.5)
p_body.font.color.rgb = TEXT_MAIN
p_body.space_before = Pt(10)

img_path_s10 = os.path.join(IMAGES_DIR, "after_benchmarks.png")
if os.path.exists(img_path_s10):
    s10.shapes.add_picture(img_path_s10, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.1))

# ==========================================
# SLIDE 11: Tab 5 — Kaggle 5-Stage Audit
# ==========================================
s11 = prs.slides.add_slide(blank_layout)
add_header(s11, "Tab 5: Framework Audit — Proving It's Fair & Honest", "What Each Tab Does")

add_card(s11, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.1))
tb_s11 = s11.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.0), Inches(4.6))
tf_s11 = tb_s11.text_frame
tf_s11.word_wrap = True

p = tf_s11.paragraphs[0]
p.text = "Auditing Fairness and Clinical Value:"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = TEAL_ACCENT

p_body = tf_s11.add_paragraph()
p_body.text = "• No Cheating (Leakage-Free):\n" \
              "   Proves step-by-step that the AI was trained strictly without seeing test answers in advance.\n\n" \
              "• Equal Fairness to Men & Women:\n" \
              "   Model accuracy is practically identical between males (0.8389) and females (0.8403) — zero gender bias!\n\n" \
              "• Net Benefit (Decision Curve):\n" \
              "   Proves that using this tool detects 1.85 extra true strokes per 100 people without causing unnecessary false alarms."
p_body.font.size = Pt(12.5)
p_body.font.color.rgb = TEXT_MAIN
p_body.space_before = Pt(10)

img_path_s11 = os.path.join(IMAGES_DIR, "after_kaggle.png")
if os.path.exists(img_path_s11):
    s11.shapes.add_picture(img_path_s11, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.1))

# ==========================================
# SLIDE 12: Tab 6 — Group Batch Screening
# ==========================================
s12 = prs.slides.add_slide(blank_layout)
add_header(s12, "Tab 6: Hospital Group Screening (Batch Upload)", "What Each Tab Does")

add_card(s12, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.1))
tb_s12 = s12.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.0), Inches(4.6))
tf_s12 = tb_s12.text_frame
tf_s12.word_wrap = True

p = tf_s12.paragraphs[0]
p.text = "Screening Hundreds of Patients at Once:"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = BLUE_ACCENT

p_body = tf_s12.add_paragraph()
p_body.text = "• Built for Hospitals and Clinics:\n" \
              "   Instead of typing patients one by one, doctors can upload an entire spreadsheet (CSV) of hundreds of patients.\n\n" \
              "• Color-Coded Risk Sorting:\n" \
              "   Instantly separates patients into Green (Low), Yellow (Moderate), Orange (High), and Red (Critical Danger).\n\n" \
              "• Community Health Insights:\n" \
              "   Shows doctors the biggest problem in their community (e.g., '65% of your high-risk patients have untreated high blood pressure')."
p_body.font.size = Pt(12.5)
p_body.font.color.rgb = TEXT_MAIN
p_body.space_before = Pt(10)

img_path_s12 = os.path.join(IMAGES_DIR, "after_cohort.png")
if os.path.exists(img_path_s12):
    s12.shapes.add_picture(img_path_s12, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.1))

# ==========================================
# SLIDE 13: Clinical Effectiveness & Why It Matters
# ==========================================
s13 = prs.slides.add_slide(blank_layout)
add_header(s13, "Why Is This System Truly Useful in Real Life?", "Real-World Impact")

effects = [
    ("Saves Real Lives", "84% Stroke Detection", "Catches 42 out of 50 stroke cases, ensuring doctors don't accidentally send high-risk patients home.", ROSE_RED),
    ("Honest Percentages", "75% Error Reduction", "No more scary false numbers. If it says 5% risk, it really is 5%, stopping hospital panic.", TEAL_ACCENT),
    ("Actionable Health Goals", "'What-If' Simulation", "Patients see exact proof that lowering blood pressure or quitting smoking cuts stroke danger.", BLUE_ACCENT),
    ("Ready for Hospitals", "1-Page Printable Report", "Generates a clean paper report with test results, risk charts, and doctor sign-off line in 1 click.", AMBER)
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
    p_t.font.size = Pt(16)
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
    p_d.font.size = Pt(12)
    p_d.font.color.rgb = TEXT_MUTED
    p_d.space_before = Pt(8)

# ==========================================
# SLIDE 14: Limitations & Future Plans
# ==========================================
s14 = prs.slides.add_slide(blank_layout)
add_header(s14, "Honest Limitations & Next Steps", "Future Roadmap")

add_card(s14, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
tb_s14_l = s14.shapes.add_textbox(Inches(1.1), Inches(1.85), Inches(5.0), Inches(4.5))
tf_s14_l = tb_s14_l.text_frame
tf_s14_l.word_wrap = True

p_l = tf_s14_l.paragraphs[0]
p_l.text = "Current Limitations (Being Honest)"
p_l.font.size = Pt(17)
p_l.font.bold = True
p_l.font.color.rgb = ROSE_RED

p_l_body = tf_s14_l.add_paragraph()
p_l_body.text = "1. Works Best for Ages 55–70:\n" \
                "   Very few young people under 55 have strokes (only 1%), making it harder for the AI to predict in that group.\n\n" \
                "2. No Brain Scans (CT/MRI) Yet:\n" \
                "   Currently uses clinical numbers (blood pressure, sugar, age). It does not yet look at brain picture scans.\n\n" \
                "3. Research Prototype:\n" \
                "   This is an academic research assistant to help doctors make decisions, not a replacement for a human doctor."
p_l_body.font.size = Pt(12.5)
p_l_body.font.color.rgb = TEXT_MAIN
p_l_body.space_before = Pt(10)

add_card(s14, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb_s14_r = s14.shapes.add_textbox(Inches(7.1), Inches(1.85), Inches(5.1), Inches(4.5))
tf_s14_r = tb_s14_r.text_frame
tf_s14_r.word_wrap = True

p_r = tf_s14_r.paragraphs[0]
p_r.text = "What We Plan to Build Next"
p_r.font.size = Pt(17)
p_r.font.bold = True
p_r.font.color.rgb = TEAL_ACCENT

p_r_body = tf_s14_r.add_paragraph()
p_r_body.text = "1. Add Brain CT & MRI Scan AI:\n" \
                "   Combine picture scans with clinical numbers for even sharper accuracy.\n\n" \
                "2. Connect Directly to Hospital Records:\n" \
                "   Allow the tool to automatically pull patient numbers from hospital computer systems (EHR).\n\n" \
                "3. Multi-Hospital Testing:\n" \
                "   Test the software across hospitals in multiple cities and countries to make sure it helps everyone."
p_r_body.font.size = Pt(12.5)
p_r_body.font.color.rgb = TEXT_MAIN
p_r_body.space_before = Pt(10)

# ==========================================
# SLIDE 15: Conclusion (Simple & Strong)
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
p_c2.text = "NeuroPulse XAI: Turning Complicated AI Into Simple, Honest, Life-Saving Advice Doctors Can Trust"
p_c2.font.size = Pt(18)
p_c2.font.color.rgb = CYAN_ACCENT
p_c2.space_before = Pt(12)
p_c2.alignment = PP_ALIGN.CENTER

card_concl = add_card(s15, Inches(2.2), Inches(3.8), Inches(8.9), Inches(2.2), NAVY_MID, CYAN_ACCENT)
tb_concl = s15.shapes.add_textbox(Inches(2.5), Inches(4.0), Inches(8.3), Inches(1.8))
tf_concl = tb_concl.text_frame
tf_concl.word_wrap = True

p_res = tf_concl.paragraphs[0]
p_res.text = "Researcher: Tanishka Mudgal (RA2311003011560)"
p_res.font.size = Pt(16)
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
p_repo.text = "Project Code: https://github.com/Tanishka-2004/stroke-xai-framework"
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
