# NeuroPulse XAI — Presentation Deck & Speaker Notes
**An Explainable Machine Learning Framework for Stroke Risk, Severity, and Functional Outcome Prediction on Imbalanced Clinical Data**

* **Author:** Tanishka Mudgal (Registration: RA2311003011560)
* **Department:** Computing Technologies, SRM Institute of Science and Technology, Chennai, India
* **Presentation File:** `NEUROPULSE_STROKE_XAI_PRESENTATION.pptx` (16:9 Widescreen, 15 Slides)

---

## Slide 1: Title Slide (Dark Theme)
* **Header Badge:** IEEE TRANSACTIONS COMPLIANT RESEARCH
* **Title:** NeuroPulse XAI
* **Subtitle:** An Explainable Machine Learning Framework for Stroke Risk, Severity, and Functional Outcome Prediction on Imbalanced Clinical Data
* **Presenter:** Tanishka Mudgal (RA2311003011560)
* **Institution:** Department of Computing Technologies, SRM Institute of Science and Technology
* **Core Stack:** CatBoost • Platt Calibration • TreeSHAP • Decision Curve Analysis

---

## Slide 2: Executive Summary & Project Mission
* **The Clinical Dilemma:** Stroke is the #2 leading cause of death globally (6.6M deaths, 143M DALYs annually). In acute ischemic stroke, 1.9 million neurons die every minute. Early detection and prophylactic intervention are life-saving, but traditional bedside calculators (Framingham, CHA2DS2-VASc) rely on linear heuristics that miss synergistic biological risks.
* **The AI Translation Barrier:** While machine learning can capture non-linear patterns, existing models fail in three critical dimensions: minority class imbalance (<5%), severely distorted probability calibration, and black-box opacity.
* **The NeuroPulse Solution:** An end-to-end 5-Stage framework evaluated on the Kaggle Stroke cohort ($N=5,110$) delivering high acute sensitivity (84%), honest Platt-calibrated probabilities (75.6% Brier reduction), and actionable TreeSHAP explanations.

---

## Slide 3: The Problem Statement (The 3 Critical Barriers)
1. **Extreme Minority Class Imbalance:**
   * Positive stroke events occur in $<5\%$ of screened cohorts ($4.87\%$ in Kaggle, a $19.54:1$ imbalance ratio).
   * Unweighted algorithms collapse into majority voting: achieving $>95\%$ raw accuracy while failing to detect life-threatening strokes (0% recall).
   * Synthetic oversampling (SMOTE) generates non-physiological artifacts in tabular clinical data.
2. **Distorted Probability Calibration:**
   * When loss weighting or sampling is used to force sensitivity, model output logits are shifted positive.
   * A patient with an actual $5\%$ epidemiological risk receives an uncalibrated raw predicted score of $38.74\%$, creating unnecessary clinical alarm and overtreatment.
3. **Black-Box Opacity & Inscrutability:**
   * Deep models and complex tree ensembles do not expose their internal decision rationale.
   * Attending physicians cannot verify whether a prediction is driven by legitimate biomarkers or dataset bias, preventing bedside clinical adoption.

---

## Slide 4: What The System Does (Core Solution)
* **5-Stage Calibrated Machine Learning Pipeline:**
  1. *Stage 1:* Leakage-free clinical preprocessing with train-median imputation ($28.1\text{ kg/m}^2$) and 80/20 stratified split.
  2. *Stage 2:* Cost-sensitive CatBoost classification with $19.54:1$ inverse class weighting, securing $84.00\%$ acute sensitivity ($42/50$ strokes).
  3. *Stage 3:* 5-fold out-of-fold Platt sigmoid calibration, reducing Brier score by $75.6\%$ ($0.0416$), strictly matching population prevalence ($4.87\%$).
  4. *Stage 4:* Game-theoretic TreeSHAP feature attributions and second-order interaction matrices (Age $\times$ Glucose synergy).
  5. *Stage 5:* Reliable multi-dimensional clinical evaluation: demographic subgroup fairness audits and Decision Curve Analysis.
* **Tri-Pillar Bedside Clinical Scope:**
  * *Pillar 1:* 10-Year Long-Term Stroke Risk Probability & Tiers (Low, Moderate, High, Critical).
  * *Pillar 2:* Acute Neurological Deficit Severity via bedside NIHSS score ($0\text{--}42$).
  * *Pillar 3:* 90-Day Functional Independence Recovery ($\text{mRS} \le 2$) conditioned on reperfusion therapy (IV tPA, EVT).

---

## Slide 5: Domain Keywords & Scientific Glossary
* **Explainable AI (XAI):** Methodologies enabling AI decision pathways to be audited and pathophysiologically verified by clinicians.
* **TreeSHAP (Shapley Additive exPlanations):** Game-theoretic feature attribution allocating credit $\phi_j$ to each biological biomarker.
* **Platt Sigmoid Calibration:** Logistic transformation mapping uncalibrated ensemble logits into reliable posterior probabilities: $\hat{P} = 1 / (1 + e^{A \cdot f + B})$.
* **Brier Score:** Mean squared error between predicted probabilities and binary outcomes; measures calibration accuracy: $\text{BS} = \frac{1}{N}\sum (P_i - Y_i)^2$.
* **Cost-Sensitive Learning:** Directly penalizing minority-class errors via loss reweighting ($19.54:1$) in the log-loss objective.
* **Decision Curve Analysis (DCA):** Evaluates clinical Net Benefit across decision thresholds, proving utility over treat-all and treat-none strategies.
* **Subgroup Algorithmic Fairness:** Stratifying evaluation across demographic brackets to ensure no bias across Age, Sex, or Hypertension.
* **NIHSS & mRS:** National Institutes of Health Stroke Scale (acute deficit: $0\text{--}42$) and modified Rankin Scale (functional independence: $0\text{--}6$).

---

## Slide 6: Complete Technology Stack
* **Machine Learning & Modeling:**
  * CatBoost (Oblivious Trees, Ordered Target Encoding, native categorical handling)
  * Scikit-Learn (Logistic Regression, Random Forest, CalibratedClassifierCV)
  * XGBoost (Cost-sensitive gradient boosting)
  * NumPy & Pandas (Data pipelines, imputation)
* **Explainability & Validation:**
  * TreeSHAP (Local waterfall breakdowns & global importance rankings)
  * Platt Sigmoid Calibration (5-fold out-of-fold CV)
  * Decision Curve Analysis (Vickers Net Benefit)
* **Backend Architecture:**
  * Python 3.14 runtime
  * FastAPI (Asynchronous high-performance REST API)
  * Uvicorn ASGI server
* **Frontend & UX:**
  * Vanilla CSS3 with glassmorphic modern design system
  * Responsive Vanilla JavaScript
  * Chart.js (Real-time dynamic visualizations)
  * HTML5 Print Emulation Engine (Single-page certified audit PDF export)

---

## Slides 7–12: Tab-by-Tab Walkthrough (With UI Screenshots)

### Tab 1: Tri-Pillar Clinical Assessment & Certified Audit
* **Inputs:** Patient demographics, vitals, acute deficit checklist (NIHSS items), and emergency intervention toggles (tPA / EVT).
* **Outputs:** Real-time Platt-calibrated risk gauge, emergency triage badge, and 90-day recovery likelihood.
* **Export:** One-click single-page certified clinical audit report with vitals, predictions, SHAP attribution bars, and attending physician sign-off line.

### Tab 2: Interactive Counterfactual "What-If" Studio
* **Purpose:** Translates abstract probabilities into actionable preventative guidance.
* **Interventions:**
  * Blood pressure optimization ($<130\text{ mmHg}$) $\rightarrow$ $4.5\%$ to $8.2\%$ absolute risk reduction.
  * Glycemic regulation ($<100\text{ mg/dL}$) $\rightarrow$ $2.1\%$ to $4.8\%$ absolute risk reduction.
  * Smoking cessation $\rightarrow$ removes tobacco hazard.

### Tab 3: SHAP Studio (Mechanistic Transparency)
* **Global Rankings:** Age ($|\phi|=1.3975$) $>$ BMI ($0.2056$) $>$ Avg Glucose ($0.0921$) $>$ Hypertension ($0.0806$) $>$ Smoking ($0.0373$).
* **Local Waterfall:** Shows exact positive (red) and negative (blue) forces moving patient log-odds from baseline ($\phi_0$).
* **Synergy Insight:** Age $\times$ Glucose interaction proves high glucose amplifies stroke log-odds by $5.75\times$ in patients $>65$ vs $<45$.

### Tab 4: Comparative Model Benchmarks
* **Held-Out Test Set ($N=1,022$, 50 events):**
  * CatBoost achieves highest acute sensitivity: **$84.00\%$** ($42/50$ strokes detected).
  * $5.77\times$ PR-AUC enrichment: **$0.2812$** vs XGBoost ($0.1683$) and Random Forest ($0.2261$).
  * Lowest calibration loss: **$0.0416$** Brier score.

### Tab 5: Kaggle 5-Stage Framework Audit
* **Methodological Integrity:** Exposes all 5 stages directly in the interface.
* **Fairness Audit:** Confirms biological sex parity ($0.8389$ male vs $0.8403$ female) and highlights the $55\text{--}70$ yr preventative sweet spot ($0.7387$ AUC).
* **DCA Curve:** Shows positive Net Benefit ($+0.0185$ at $10\%$ threshold) where blanket treatment causes net harm ($-0.0568$).

### Tab 6: Institutional Batch Screening Engine
* **Capability:** Upload multi-patient CSV files for institutional health screening.
* **Triage:** Automatically stratifies cohorts into Low, Moderate, High, and Critical risk tiers.
* **Population Drivers:** Aggregates SHAP attributions across batches to reveal prevalent community risk factors.

---

## Slide 13: Clinical Effectiveness & Real-World Utility
1. **Safety-First Sensitivity:** $84\%$ acute recall minimizes missed diagnoses of catastrophic vascular events.
2. **Epidemiological Honesty:** $75.6\%$ Brier score reduction prevents clinical false alarms.
3. **Actionable Counseling:** Counterfactual simulations provide clear targets for preventative patient care.
4. **Bedside Workflow Ready:** Certified 1-page report integrates smoothly into EHR workflows.

---

## Slide 14: Limitations & Future Horizons
* **Limitations:** Age-bracket sample disparity in extreme age groups ($<55$ and $>70$ yrs); absence of acute neuroimaging (CT/MRI); research prototype regulatory status.
* **Roadmap:** Multimodal fusion with Vision Transformers (ViT) on brain CT/MRI; hospital EHR integration via HL7 FHIR; prospective multi-center trials.

---

## Slide 15: Conclusion & Contact
* **Researcher:** Tanishka Mudgal (RA2311003011560)
* **Institution:** Department of Computing Technologies, SRM Institute of Science and Technology
* **Repository:** `https://github.com/Tanishka-2004/stroke-xai-framework`
