# NeuroPulse XAI — Presentation Deck & Simple Speaking Guide
**A Smart, Trustworthy AI Tool for Stroke Risk, Severity Check, and Recovery Odds**

* **Author:** Tanishka Mudgal (Registration: RA2311003011560)
* **Department:** Computing Technologies, SRM Institute of Science and Technology
* **File:** `NEUROPULSE_STROKE_XAI_PRESENTATION.pptx` (16:9 Widescreen, 15 Slides)

---

## Slide 1: Title Slide
* **Title:** NeuroPulse XAI
* **Subtitle:** A Smart, Trustworthy AI Tool for Stroke Risk Prediction, Severity Check, and Recovery Odds
* **Presenter:** Tanishka Mudgal (RA2311003011560), Department of Computing Technologies, SRMIST
* **One-Sentence Goal:** Helping doctors spot stroke dangers early with honest odds and clear explanations they can actually trust.

---

## Slide 2: The Big Picture (Why Did We Build This?)
1. **The Medical Danger:** Stroke is the #2 killer in the world. When a blood clot blocks blood to the brain, about 2 million brain cells die every single minute! Catching it early saves lives and prevents paralysis.
2. **Why Old Methods Fail:** Doctors today still use basic point-based score sheets on paper. These simple sheets add numbers one by one, so they completely miss combined dangers — like how high blood pressure becomes 5x more dangerous when mixed with high blood sugar in older people.
3. **Why Regular AI Fails:** Standard machine learning models either miss strokes completely (because strokes are rare), exaggerate and give scary fake percentages (like telling a healthy person they have a 40% risk), or refuse to explain *why* they gave an answer.

---

## Slide 3: The Problem Statement (3 Big Roadblocks)
1. **Problem 1: Strokes Are Rare in Screenings:** Less than 5 out of 100 people screened have had a stroke. If an AI model simply guesses "No stroke" for everyone, it looks 95% accurate on paper, but it missed 100% of the sick patients!
2. **Problem 2: Exaggerated Odds:** When programmers try to force the AI to catch strokes, the computer panics. A person whose actual risk is 5% gets told they have a 40% risk, causing panic and expensive hospital tests they never needed.
3. **Problem 3: The "Black Box":** Most AI models can't explain why they gave a prediction. Doctors cannot risk patient lives on mystery computer guesses.

---

## Slide 4: What Does Our System Do? (The Solution)
* **Our 5-Stage Smart Pipeline (Tested on 5,110 real patient records from Kaggle):**
  1. *Clean Data:* Fills in missing health numbers cleanly without peeking at the test set.
  2. *Fair Training:* Heavily penalizes the AI whenever it misses a stroke, training it never to ignore rare cases.
  3. *Honest Percentages:* Recalibrates the probabilities so 5% really means 5%, not 40%.
  4. *Full Explanations:* Tells doctors exactly which body factors pushed the risk up or down.
  5. *Quality Check:* Proves the model is equally fair to men, women, young, and old alike.
* **3 Clinical Predictions in One Single Tool:**
  1. *Long-Term Stroke Risk:* Honest 10-year stroke chance (Low, Moderate, High, or Critical).
  2. *Acute Stroke Severity (NIHSS):* Scores current emergency symptoms (face droop, arm weakness, speech trouble) from 0 to 42.
  3. *90-Day Recovery Odds:* Predicts if the patient will walk and live normally after 3 months if given clot-busting medicine or surgery.

---

## Slide 5: Key Concepts Explained in Plain English
* **Explainable AI (XAI):** AI that shows its work and explains its reasons instead of guessing in secret.
* **SHAP (The Explainer):** A tool that gives credit to each body feature (like age, smoking, or sugar) for pushing risk up or down.
* **Calibration (Honest Odds):** Fixing the AI's math so its percentages are real: if it says 5% risk, 5 out of 100 people actually have it.
* **Brier Score (Error Meter):** Measures how honest the AI's percentages are. A lower score means much more trustworthy odds.
* **Class Imbalance:** When sick cases are rare (only 5 in 100). The AI needs special rules so it doesn't ignore them.
* **What-If (Counterfactual):** Asking: "What if this patient drops their blood pressure by 20 points? How much safer will they be?"
* **Decision Curve (Net Benefit):** Mathematical proof that using this tool helps more patients than treating everyone or doing nothing.
* **NIHSS & Recovery Score:** Standard medical checklists doctors use to measure stroke damage and 3-month recovery.

---

## Slide 6: What Tech Did We Use? (Under the Hood)
* **Machine Learning Core:**
  * *CatBoost:* A top-tier decision-tree model designed specifically for medical tables that handles rare stroke cases without getting confused.
  * *Scikit-Learn & XGBoost:* Used for baseline comparisons and cross-validation.
* **Explainability & Math:**
  * *TreeSHAP:* Breaks open the AI to show green/red factor bars.
  * *Platt Scaling:* The formula that fixes inflated percentages.
* **Backend Web Engine:**
  * *Python 3.14 + FastAPI:* Fast, lightweight server handling patient calculations in milliseconds.
* **User Interface & Design:**
  * *Modern HTML & CSS:* Clean, beautiful glass-styled interface.
  * *JavaScript + Chart.js:* Smooth interactive sliders and live risk dials.
  * *PDF Engine:* 1-click printable doctor reports.

---

## Slides 7–12: What Each Tab Does (Walkthrough With Screenshots)

### Tab 1: Patient Checkup & Printable Doctor Report
* Enter simple patient details: age, blood pressure, glucose, smoking, and symptoms.
* Get instant risk % dial, emergency NIHSS score, and 3-month recovery odds.
* Click **"Clinical Audit Report"** to open a clean 1-page paper report with doctor signature line ready for hospital charts.

### Tab 2: "What-If" Simulator (Actionable Goals)
* Shows patients how to lower their risk:
  * Lowering blood pressure drops stroke risk by 4% to 8%.
  * Controlling blood sugar drops risk by 2% to 5%.
  * Quitting smoking erases the tobacco danger completely.
* Gives doctors a clear roadmap to motivate patients during checkups.

### Tab 3: SHAP Explainer (Peeking Inside the AI)
* Ranked biggest health factors: Age $>$ Body Mass (BMI) $>$ Blood Sugar $>$ High Blood Pressure $>$ Smoking.
* Waterfall chart: Red bars push the patient into danger; Blue bars protect them.
* Key discovery: High sugar is almost 6x more dangerous in seniors over 65 than in young people!

### Tab 4: Model Benchmarks (Proving It Works)
* Tested on 1,022 unseen real patients from Kaggle.
* CatBoost caught **84% of real strokes** (42 out of 50), beating Random Forest (76%) and XGBoost (60%).
* Cut percentage errors by **75%**, proving our odds are honest and dependable.

### Tab 5: Framework Audit (Proving It's Fair & Honest)
* Proves the AI was trained cleanly without peeking at test answers.
* Proves zero gender bias: accuracy is identical between men (0.8389) and women (0.8403).
* Net Benefit curve proves this tool catches 1.85 extra true strokes per 100 people without false alarms.

### Tab 6: Hospital Group Screening (Batch Upload)
* Allows clinics and hospitals to upload a spreadsheet (CSV) of hundreds of patients at once.
* Automatically sorts people into Green (Low), Yellow (Moderate), Orange (High), and Red (Critical).
* Shows the community's biggest problem (e.g., "65% of your high-risk patients have uncontrolled blood pressure").

---

## Slide 13: Why Is This Truly Useful in Real Life?
1. **Saves Real Lives:** 84% stroke detection means doctors don't send high-risk patients home by mistake.
2. **Honest Percentages:** 75% error reduction stops false alarms and eliminates patient panic.
3. **Actionable Health Goals:** Shows patients exact proof that lifestyle changes cut their danger.
4. **Hospital Ready:** 1-page printable medical report is ready to sign and file in under 2 minutes.

---

## Slide 14: Honest Limitations & Next Steps
* **Current Limitations:**
  1. Works best for ages 55–70 (strokes in people under 55 are very rare, so data is sparse).
  2. Uses clinical numbers only; doesn't look at brain picture scans (CT/MRI) yet.
  3. It's a decision-support assistant to help doctors, not replace them.
* **Future Plans:**
  1. Add Brain CT & MRI scan image AI.
  2. Connect directly to hospital computer record systems (EHR).
  3. Test across hospitals in multiple cities and countries.

---

## Slide 15: Conclusion & Contact
* **Researcher:** Tanishka Mudgal (RA2311003011560)
* **Department:** Computing Technologies, SRM Institute of Science and Technology
* **Project Code:** `https://github.com/Tanishka-2004/stroke-xai-framework`
* **Takeaway:** Turning complicated AI into simple, honest, life-saving advice doctors can actually trust.
