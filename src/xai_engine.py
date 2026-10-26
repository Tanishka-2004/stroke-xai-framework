"""
NeuroPulse XAI — Explainable AI Engine
Provides SHAP local/global explanations, counterfactual what-if simulations,
and clinical result summaries for the three-pillar stroke prediction framework.

Research prototype evaluated on the public Kaggle stroke dataset (N=5,110, 4.87% prevalence). Not validated for clinical use.
"""

import os
import joblib
import numpy as np
import pandas as pd
import shap

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# -------------------------------------------------------------
# SHARED CONSTANTS — single source of truth for all tiers
# -------------------------------------------------------------
# NIHSS standard severity bands (used in UI, engine, and report)
NIHSS_TIERS = [
    (0, 0, 'No deficit (NIHSS 0)', 'Observation; follow neurology protocol'),
    (1, 4, 'Minor (NIHSS 1-4)', 'Stroke evaluation; consider observation or early intervention'),
    (5, 15, 'Moderate (NIHSS 5-15)', 'Urgent acute stroke protocol; neuroimaging and team evaluation'),
    (16, 20, 'Moderate-to-severe (NIHSS 16-20)', 'Stat stroke-team evaluation; consider endovascular workup'),
    (21, 42, 'Severe (NIHSS 21-42)', 'Severe deficit; consider urgent stroke-team evaluation'),
]

# Risk probability thresholds
RISK_TIERS = [
    (0.0, 0.15, 'Low Risk', 'green'),
    (0.15, 0.40, 'Moderate Risk', 'yellow'),
    (0.40, 0.70, 'High Risk', 'orange'),
    (0.70, 1.01, 'Critical / Very High Risk', 'red'),
]

# Human-readable feature display names — used everywhere, no snake_case on screen
FEATURE_LABEL_MAP = {
    'age': 'Age',
    'systolic_bp': 'Systolic BP (mmHg)',
    'avg_glucose_level': 'Average glucose (mg/dL)',
    'bmi': 'BMI',
    'total_cholesterol': 'Total cholesterol (mg/dL)',
    'physical_activity': 'Physical activity (0-10)',
    'onset_to_er_hours': 'Time to ER (hours)',
    'baseline_glucose': 'Baseline glucose (mg/dL)',
    'nihss_score': 'NIHSS score',
    # One-hot encoded booleans (value = 1 category)
    'gender_Male': 'Sex: male',
    'gender_Female': 'Sex: female',
    'hypertension_0': 'Hypertension: no',
    'hypertension_1': 'Hypertension: yes',
    'heart_disease_0': 'Heart disease: no',
    'heart_disease_1': 'Heart disease / AFib: yes',
    'ever_married_No': 'Marital status: single',
    'ever_married_Yes': 'Marital status: married',
    'work_type_Govt_job': 'Work type: government',
    'work_type_Never_worked': 'Work type: never worked',
    'work_type_Private': 'Work type: private sector',
    'work_type_Self-employed': 'Work type: self-employed',
    'work_type_children': 'Work type: child',
    'residence_type_Rural': 'Residence: rural',
    'residence_type_Urban': 'Residence: urban',
    'smoking_status_formerly smoked': 'Smoking: formerly smoked',
    'smoking_status_never smoked': 'Smoking: never smoked',
    'smoking_status_smokes': 'Smoking: current smoker',
    'smoking_status_Unknown': 'Smoking: unknown',
    'stroke_subtype_Cardioembolic': 'Subtype: cardioembolic',
    'stroke_subtype_Large Artery Atherosclerosis': 'Subtype: large artery atherosclerosis',
    'stroke_subtype_Other/Cryptogenic': 'Subtype: cryptogenic',
    'stroke_subtype_Small Vessel Occlusion (Lacunar)': 'Subtype: small vessel (lacunar)',
    'prior_stroke_tia_0': 'Prior TIA/stroke: no',
    'prior_stroke_tia_1': 'Prior TIA/stroke: yes',
    'atrial_fibrillation_0': 'Atrial fibrillation: no',
    'atrial_fibrillation_1': 'Atrial fibrillation: yes',
    'facial_palsy_0': 'Facial palsy: none',
    'facial_palsy_1': 'Facial palsy: minor',
    'facial_palsy_2': 'Facial palsy: partial',
    'facial_palsy_3': 'Facial palsy: complete',
    'motor_arm_drift_0': 'Motor arm: no drift',
    'motor_arm_drift_1': 'Motor arm: drift <10s',
    'motor_arm_drift_2': 'Motor arm: falls <10s',
    'motor_arm_drift_3': 'Motor arm: no anti-gravity',
    'motor_arm_drift_4': 'Motor arm: no movement',
    'motor_leg_drift_0': 'Motor leg: no drift',
    'motor_leg_drift_1': 'Motor leg: drift <5s',
    'motor_leg_drift_2': 'Motor leg: falls <5s',
    'motor_leg_drift_3': 'Motor leg: no anti-gravity',
    'motor_leg_drift_4': 'Motor leg: no movement',
    'speech_impairment_0': 'Speech: normal',
    'speech_impairment_1': 'Speech: mild-moderate',
    'speech_impairment_2': 'Speech: severe/aphasia',
    'loc_deficit_0': 'Consciousness: alert',
    'loc_deficit_1': 'Consciousness: arousable',
    'loc_deficit_2': 'Consciousness: obtunded',
    'loc_deficit_3': 'Consciousness: comatose',
    'thrombolysis_iv_tpa_0': 'IV tPA: not given',
    'thrombolysis_iv_tpa_1': 'IV tPA thrombolysis',
    'endovascular_thrombectomy_0': 'EVT: not performed',
    'endovascular_thrombectomy_1': 'Endovascular thrombectomy',
    'acute_complications_0': 'Complications: none',
    'acute_complications_1': 'Acute complications present',
}


def label_feature(raw_name: str) -> str:
    """Return human-readable label for a feature name, without any snake_case on screen."""
    # Direct lookup
    if raw_name in FEATURE_LABEL_MAP:
        return FEATURE_LABEL_MAP[raw_name]
    # Strip preprocessor prefixes from scikit-learn pipelines
    cleaned = raw_name.replace('cat__', '').replace('num__', '').strip()
    if cleaned in FEATURE_LABEL_MAP:
        return FEATURE_LABEL_MAP[cleaned]
    # Fallback: humanise by replacing _ with space, title-case
    return cleaned.replace('_', ' ').title()


def classify_nihss(score: float):
    """Classify an NIHSS score into standard tier using shared NIHSS_TIERS constant."""
    for lo, hi, tier, triage in NIHSS_TIERS:
        if lo <= score <= hi:
            return tier, triage
    return NIHSS_TIERS[-1][2], NIHSS_TIERS[-1][3]


def classify_risk(prob: float):
    """Classify a risk probability into a tier using shared RISK_TIERS constant."""
    for lo, hi, tier, color in RISK_TIERS:
        if lo <= prob < hi:
            return tier, color
    return RISK_TIERS[-1][2], RISK_TIERS[-1][3]


class StrokeXAIEngine:
    def __init__(self):
        # --- Task 1: Stroke Risk (XGBoost classifier) ---
        self.risk_model = joblib.load(os.path.join(MODELS_DIR, 'task1_risk_model.joblib'))
        self.risk_preprocessor = joblib.load(os.path.join(MODELS_DIR, 'task1_preprocessor.joblib'))
        self.risk_explainer = shap.TreeExplainer(self.risk_model)

        # --- Task 2: NIHSS Severity (XGBoost regressor) ---
        self.severity_model = joblib.load(os.path.join(MODELS_DIR, 'task2_severity_model.joblib'))
        self.severity_preprocessor = joblib.load(os.path.join(MODELS_DIR, 'task2_preprocessor.joblib'))
        self.severity_explainer = shap.TreeExplainer(self.severity_model)

        # --- Task 3: 90-Day Outcome (XGBoost classifier) ---
        self.outcome_model = joblib.load(os.path.join(MODELS_DIR, 'task3_outcome_model.joblib'))
        self.outcome_preprocessor = joblib.load(os.path.join(MODELS_DIR, 'task3_preprocessor.joblib'))
        self.outcome_explainer = shap.TreeExplainer(self.outcome_model)

        # Cache post-encoding feature names for all three tasks
        self.risk_feat_names = self._get_feature_names(
            self.risk_preprocessor,
            ['age', 'systolic_bp', 'avg_glucose_level', 'bmi', 'total_cholesterol', 'physical_activity'],
            ['gender', 'hypertension', 'heart_disease', 'ever_married', 'work_type', 'residence_type', 'smoking_status']
        )

        self.sev_feat_names = self._get_feature_names(
            self.severity_preprocessor,
            ['age', 'onset_to_er_hours', 'systolic_bp', 'baseline_glucose'],
            ['gender', 'stroke_subtype', 'prior_stroke_tia', 'atrial_fibrillation',
             'facial_palsy', 'motor_arm_drift', 'motor_leg_drift', 'speech_impairment', 'loc_deficit']
        )

        self.out_feat_names = self._get_feature_names(
            self.outcome_preprocessor,
            ['age', 'nihss_score', 'onset_to_er_hours', 'systolic_bp', 'baseline_glucose'],
            ['gender', 'stroke_subtype', 'prior_stroke_tia', 'atrial_fibrillation',
             'thrombolysis_iv_tpa', 'endovascular_thrombectomy', 'acute_complications']
        )

    def _get_feature_names(self, preprocessor, num_feats, cat_feats):
        """Return the full list of feature names after one-hot encoding."""
        cat_encoder = preprocessor.named_transformers_['cat']
        encoded_cats = list(cat_encoder.get_feature_names_out(cat_feats))
        return num_feats + encoded_cats

    def _build_attributions(self, feat_names, shap_vals):
        """
        Build sorted attribution list from SHAP values.
        Direction is derived strictly from the sign of shap_value (positive = risk/severity increasing).
        Label is derived from FEATURE_LABEL_MAP.
        """
        attributions = []
        for raw_name, val in zip(feat_names, shap_vals):
            # Strip pipeline prefixes before label lookup
            clean = raw_name.replace('cat__', '').replace('num__', '')
            display_name = label_feature(clean)
            shap_v = float(val)
            attributions.append({
                'feature': clean,          # cleaned internal name, no pipeline prefix
                'display_name': display_name,  # human label used everywhere on screen
                'shap_value': round(shap_v, 4),
                'direction': 'risk_increasing' if shap_v > 0 else 'protective',
                'magnitude': round(abs(shap_v), 4)
            })
        attributions.sort(key=lambda x: x['magnitude'], reverse=True)
        return attributions

    # ----------------------------------------------------------
    # TASK 1: STROKE RISK PREDICTION
    # ----------------------------------------------------------
    def explain_stroke_risk(self, patient_dict: dict):
        df = pd.DataFrame([patient_dict])
        X_proc = self.risk_preprocessor.transform(df)

        prob = float(self.risk_model.predict_proba(X_proc)[0, 1])
        shap_raw = self.risk_explainer.shap_values(X_proc)
        # shap_values may return list [neg_class, pos_class] for classifiers
        if isinstance(shap_raw, list):
            shap_vals = shap_raw[1][0]
        else:
            shap_vals = shap_raw[0]

        attributions = self._build_attributions(self.risk_feat_names, shap_vals)

        risk_tier, badge_color = classify_risk(prob)

        base_val = self.risk_explainer.expected_value
        if isinstance(base_val, (list, np.ndarray)):
            base_val = float(base_val[1] if len(base_val) > 1 else base_val[0])
        else:
            base_val = float(base_val)

        return {
            'task': 'Stroke Risk Prediction',
            'probability': round(prob, 4),
            'probability_pct': round(prob * 100, 1),
            'risk_tier': risk_tier,
            'badge_color': badge_color,
            'base_value': round(base_val, 4),
            'top_attributions': attributions[:10],
            'clinical_summary': self._synthesize_risk_narrative(patient_dict, prob, attributions[:5])
        }

    # ----------------------------------------------------------
    # TASK 2: ACUTE NIHSS SEVERITY PREDICTION
    # ----------------------------------------------------------
    def explain_severity(self, patient_dict: dict):
        df = pd.DataFrame([patient_dict])
        X_proc = self.severity_preprocessor.transform(df)

        predicted_nihss = float(self.severity_model.predict(X_proc)[0])
        predicted_nihss = max(0.0, min(42.0, round(predicted_nihss, 1)))

        shap_raw = self.severity_explainer.shap_values(X_proc)
        if isinstance(shap_raw, list):
            shap_vals = shap_raw[0]
        else:
            shap_vals = shap_raw[0]

        attributions = self._build_attributions(self.sev_feat_names, shap_vals)
        # For severity (regression): positive = higher NIHSS = more severe
        for a in attributions:
            a['direction'] = 'severity_increasing' if a['shap_value'] > 0 else 'attenuating'

        tier, triage = classify_nihss(predicted_nihss)

        return {
            'task': 'Acute Stroke Severity (NIHSS)',
            'predicted_nihss': predicted_nihss,
            'severity_tier': tier,
            'triage_urgency': triage,
            'top_attributions': attributions[:8]
        }

    # ----------------------------------------------------------
    # TASK 3: 90-DAY FUNCTIONAL OUTCOME PREDICTION
    # ----------------------------------------------------------
    def explain_functional_outcome(self, patient_dict: dict):
        df = pd.DataFrame([patient_dict])
        X_proc = self.outcome_preprocessor.transform(df)

        prob_favorable = float(self.outcome_model.predict_proba(X_proc)[0, 1])

        shap_raw = self.outcome_explainer.shap_values(X_proc)
        if isinstance(shap_raw, list):
            shap_vals = shap_raw[1][0]
        else:
            shap_vals = shap_raw[0]

        attributions = self._build_attributions(self.out_feat_names, shap_vals)
        # For outcome: positive SHAP = promotes favorable independence
        for a in attributions:
            a['direction'] = 'promotes_favorable' if a['shap_value'] > 0 else 'promotes_disability'

        pct = round(prob_favorable * 100, 1)

        # Calibrated wording by probability band
        if pct >= 60:
            outcome_label = 'Higher likelihood of functional independence (mRS 0-2)'
            outcome_qualifier = 'higher'
        elif pct >= 40:
            outcome_label = 'Uncertain functional outcome (mRS score uncertain)'
            outcome_qualifier = 'uncertain'
        else:
            outcome_label = 'Lower likelihood of functional independence (mRS 3-6 possible)'
            outcome_qualifier = 'lower'

        # Consistency flag: high NIHSS + high independence probability is contradictory
        nihss_input = patient_dict.get('nihss_score', 0)
        consistency_warning = None
        if nihss_input >= 21 and prob_favorable > 0.50:
            consistency_warning = (
                "Note: Predicted NIHSS ≥21 with >50% independence probability. "
                "Check inputs or consider model uncertainty on this clinical case."
            )

        return {
            'task': '90-Day Functional Outcome Prediction',
            'favorable_probability': round(prob_favorable, 4),
            'favorable_percentage': pct,
            'outcome_prognosis': outcome_label,
            'outcome_qualifier': outcome_qualifier,
            'consistency_warning': consistency_warning,
            'top_attributions': attributions[:8]
        }

    # ----------------------------------------------------------
    # COUNTERFACTUAL WHAT-IF SIMULATOR
    # ----------------------------------------------------------
    def generate_counterfactuals(self, patient_dict: dict):
        """
        Evaluate the effect of individual and combined modifiable interventions on stroke risk.
        Each intervention is scored by a real model call, not a heuristic.
        Returns absolute probability changes (percentage points), not relative reductions.
        """
        baseline_result = self.explain_stroke_risk(patient_dict)
        base_prob = baseline_result['probability']
        base_pct = round(base_prob * 100, 1)

        interventions = []
        modified = dict(patient_dict)

        # 1. Blood pressure normalisation
        if modified.get('systolic_bp', 120) > 130:
            curr_sbp = modified['systolic_bp']
            test = modified.copy()
            test['systolic_bp'] = 120
            test['hypertension'] = 0
            X_mod = self.risk_preprocessor.transform(pd.DataFrame([test]))
            new_prob = float(self.risk_model.predict_proba(X_mod)[0, 1])
            abs_drop = round(max(0.0, base_prob - new_prob) * 100, 1)
            interventions.append({
                'parameter': 'Blood pressure normalisation',
                'current_value': f'{curr_sbp} mmHg',
                'target_value': '120 mmHg (normotensive)',
                'abs_drop_pp': abs_drop,
                'new_probability_pct': round(new_prob * 100, 1),
                'clinical_note': (
                    'AHA guideline: first-line antihypertensive (ACEi/ARB or CCB). '
                    'SBP <130 mmHg reduces cerebrovascular shear stress.'
                )
            })

        # 2. Glycaemic normalisation
        if modified.get('avg_glucose_level', 90) > 125:
            curr_glu = modified['avg_glucose_level']
            test = modified.copy()
            test['avg_glucose_level'] = 95.0
            X_mod = self.risk_preprocessor.transform(pd.DataFrame([test]))
            new_prob = float(self.risk_model.predict_proba(X_mod)[0, 1])
            abs_drop = round(max(0.0, base_prob - new_prob) * 100, 1)
            interventions.append({
                'parameter': 'Glycaemic normalisation',
                'current_value': f'{curr_glu} mg/dL',
                'target_value': '95 mg/dL (euglycaemic)',
                'abs_drop_pp': abs_drop,
                'new_probability_pct': round(new_prob * 100, 1),
                'clinical_note': (
                    'ADA/AHA target: HbA1c <7.0%, fasting glucose <100 mg/dL. '
                    'Reduces microvascular and macrovascular angiopathy.'
                )
            })

        # 3. Smoking cessation
        if modified.get('smoking_status') in ['smokes', 'formerly smoked']:
            curr_smoke = modified['smoking_status']
            test = modified.copy()
            test['smoking_status'] = 'never smoked'
            X_mod = self.risk_preprocessor.transform(pd.DataFrame([test]))
            new_prob = float(self.risk_model.predict_proba(X_mod)[0, 1])
            abs_drop = round(max(0.0, base_prob - new_prob) * 100, 1)
            interventions.append({
                'parameter': 'Tobacco cessation',
                'current_value': curr_smoke,
                'target_value': 'non-smoker',
                'abs_drop_pp': abs_drop,
                'new_probability_pct': round(new_prob * 100, 1),
                'clinical_note': (
                    'Cessation reduces platelet hyperaggregability. '
                    'Stroke hazard reduction observed over 2-5 years post-cessation.'
                )
            })

        # 4. Physical activity and weight management
        if modified.get('physical_activity', 5) < 7.0 or modified.get('bmi', 24) > 27.0:
            curr_act = modified.get('physical_activity', 3.0)
            curr_bmi = modified.get('bmi', 29.0)
            test = modified.copy()
            test['physical_activity'] = 7.5
            test['bmi'] = 23.5
            X_mod = self.risk_preprocessor.transform(pd.DataFrame([test]))
            new_prob = float(self.risk_model.predict_proba(X_mod)[0, 1])
            abs_drop = round(max(0.0, base_prob - new_prob) * 100, 1)
            interventions.append({
                'parameter': 'Physical conditioning and weight reduction',
                'current_value': f'Activity {curr_act}/10, BMI {curr_bmi}',
                'target_value': 'Activity 7.5/10 (≥150 min/wk), BMI 23.5',
                'abs_drop_pp': abs_drop,
                'new_probability_pct': round(new_prob * 100, 1),
                'clinical_note': (
                    'Aerobic exercise improves cerebral blood-flow autoregulation '
                    'and lowers arterial stiffness.'
                )
            })

        # Combined optimal scenario
        optimal = modified.copy()
        optimal['systolic_bp'] = 120
        optimal['hypertension'] = 0
        optimal['avg_glucose_level'] = 95.0
        optimal['smoking_status'] = 'never smoked'
        optimal['physical_activity'] = 7.5
        optimal['bmi'] = 23.5
        X_opt = self.risk_preprocessor.transform(pd.DataFrame([optimal]))
        opt_prob = float(self.risk_model.predict_proba(X_opt)[0, 1])
        opt_pct = round(opt_prob * 100, 1)
        combined_abs_drop = round(max(0.0, base_prob - opt_prob) * 100, 1)

        return {
            'baseline_risk_pct': base_pct,
            'optimized_risk_pct': opt_pct,
            'combined_abs_drop_pp': combined_abs_drop,
            'individual_interventions': interventions,
            'simulation_note': (
                'Combined effect is not the sum of individual effects because '
                'interventions interact non-linearly through the model. '
                'These are model output simulations, not treatment effect estimates.'
            )
        }

    # ----------------------------------------------------------
    # CLINICAL NARRATIVE SYNTHESIS
    # ----------------------------------------------------------
    def _synthesize_risk_narrative(self, patient_dict, prob, top_shap):
        """
        Generate a factual, template-based narrative from patient values and SHAP results.
        No hype, no exclamation marks, no invented numbers.
        """
        pct = prob * 100
        top_risk_drivers = [
            a['display_name'] for a in top_shap
            if a['direction'] == 'risk_increasing'
        ][:3]

        if pct >= 70:
            risk_sentence = f"Estimated 10-year stroke risk: {pct:.1f}% (critical tier)."
        elif pct >= 40:
            risk_sentence = f"Estimated 10-year stroke risk: {pct:.1f}% (high tier)."
        elif pct >= 15:
            risk_sentence = f"Estimated 10-year stroke risk: {pct:.1f}% (moderate tier)."
        else:
            risk_sentence = f"Estimated 10-year stroke risk: {pct:.1f}% (low tier)."

        if top_risk_drivers:
            driver_sentence = f"Largest contributors: {', '.join(top_risk_drivers)}."
        else:
            driver_sentence = "No dominant risk-increasing features identified."

        return f"{risk_sentence} {driver_sentence}"


# Singleton — loaded once at startup
engine = StrokeXAIEngine()
