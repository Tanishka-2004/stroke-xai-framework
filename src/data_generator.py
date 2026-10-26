"""
Clinical Data Synthesis Engine for Stroke Risk, Severity, and Functional Outcome
Grounded in epidemiological data distributions from AHA/ASA, Framingham, and stroke registry standards.
Author: RA2311003011560 Research Framework
"""

import numpy as np
import pandas as pd
import os

SEED = 42
np.random.seed(SEED)

def generate_stroke_risk_dataset(n_samples=5000):
    """
    Generates a cohort for Task 1: Stroke Risk Prediction.
    Captures multi-factorial cardiovascular risk factors.
    """
    np.random.seed(SEED)
    
    # Age distribution: adult population skewed towards middle/elderly
    age = np.clip(np.random.normal(loc=55, scale=17, size=n_samples), 18, 92).round().astype(int)
    
    gender = np.random.choice(['Male', 'Female'], size=n_samples, p=[0.48, 0.52])
    
    # Hypertension probability rises with age and BMI
    htn_prob = 1 / (1 + np.exp(-(0.05 * (age - 50) + np.random.normal(0, 0.4, n_samples))))
    hypertension = (np.random.rand(n_samples) < htn_prob).astype(int)
    
    # Systolic blood pressure (mmHg)
    sbp = np.where(hypertension == 1, 
                   np.random.normal(150, 16, n_samples), 
                   np.random.normal(122, 10, n_samples)).round().astype(int)
    sbp = np.clip(sbp, 95, 220)
    
    # Heart disease (Coronary artery disease / Atrial Fibrillation)
    hd_prob = 1 / (1 + np.exp(-(0.06 * (age - 60) + 0.8 * hypertension - 1.8)))
    heart_disease = (np.random.rand(n_samples) < hd_prob).astype(int)
    
    # Ever married
    ever_married = np.where(age > 28, np.random.choice(['Yes', 'No'], size=n_samples, p=[0.78, 0.22]), 'No')
    
    # Work type
    work_type = []
    for a in age:
        if a < 22:
            work_type.append('children' if a < 18 else 'Govt_job')
        elif a > 65:
            work_type.append(np.random.choice(['Self-employed', 'Private'], p=[0.3, 0.7]))
        else:
            work_type.append(np.random.choice(['Private', 'Self-employed', 'Govt_job'], p=[0.62, 0.23, 0.15]))
    
    residence_type = np.random.choice(['Urban', 'Rural'], size=n_samples, p=[0.53, 0.47])
    
    # BMI (Body Mass Index)
    bmi = np.random.normal(28.5, 5.8, n_samples).round(1)
    bmi = np.clip(bmi, 15.0, 52.0)
    
    # Average glucose level (mg/dL): bimodal (normoglycemic vs diabetic)
    is_diabetic = (np.random.rand(n_samples) < (0.12 + 0.003 * (age - 40) + 0.015 * (bmi - 25))).astype(int)
    is_diabetic = np.clip(is_diabetic, 0, 1)
    avg_glucose = np.where(is_diabetic == 1, 
                           np.random.normal(175, 38, n_samples), 
                           np.random.normal(95, 14, n_samples)).round(1)
    avg_glucose = np.clip(avg_glucose, 60.0, 310.0)
    
    # Total cholesterol (mg/dL)
    cholesterol = np.random.normal(205, 38, n_samples).round(1)
    cholesterol = np.clip(cholesterol, 110.0, 340.0)
    
    # Smoking status
    smoking_status = np.random.choice(['never smoked', 'formerly smoked', 'smokes', 'Unknown'], 
                                      size=n_samples, p=[0.42, 0.20, 0.22, 0.16])
    smoke_risk = np.select(
        [smoking_status == 'smokes', smoking_status == 'formerly smoked', smoking_status == 'never smoked'],
        [0.85, 0.4, 0.0],
        default=0.1
    )
    
    # Physical activity score (0-10)
    physical_activity = np.clip(np.random.normal(5.0 - 0.04 * (age - 40) - 0.05 * (bmi - 25), 2.0, n_samples), 0, 10).round(1)
    
    # Calculate Latent Log-Odds of Stroke using Framingham-like weight coefficients
    # Log-odds components
    logit = (
        -4.5
        + 0.075 * (age - 45)
        + 0.95 * hypertension
        + 0.018 * (sbp - 120)
        + 1.15 * heart_disease
        + 0.008 * (avg_glucose - 100)
        + 0.035 * (bmi - 25)
        + 0.005 * (cholesterol - 190)
        + smoke_risk
        - 0.12 * physical_activity
    )
    
    stroke_prob = 1 / (1 + np.exp(-logit))
    # Controlled realistic incidence: ~14% positive in this clinical cohort
    stroke_prob = np.clip(stroke_prob, 0.002, 0.96)
    stroke = (np.random.rand(n_samples) < stroke_prob).astype(int)
    
    df = pd.DataFrame({
        'patient_id': [f'P-RSK-{10000+i}' for i in range(n_samples)],
        'age': age,
        'gender': gender,
        'hypertension': hypertension,
        'systolic_bp': sbp,
        'heart_disease': heart_disease,
        'ever_married': ever_married,
        'work_type': work_type,
        'residence_type': residence_type,
        'avg_glucose_level': avg_glucose,
        'bmi': bmi,
        'total_cholesterol': cholesterol,
        'smoking_status': smoking_status,
        'physical_activity': physical_activity,
        'stroke_risk_probability': stroke_prob.round(4),
        'stroke': stroke
    })
    
    return df

def generate_stroke_severity_and_outcome_dataset(n_samples=4000):
    """
    Generates cohort for:
    - Task 2: Acute Stroke Severity (NIHSS continuous score and 4-tier category)
    - Task 3: 90-Day Functional Outcome (mRS 0-2 Favorable Independence vs 3-6 Poor/Dependent)
    """
    np.random.seed(SEED + 101)
    
    age = np.clip(np.random.normal(loc=64, scale=12, size=n_samples), 30, 93).round().astype(int)
    gender = np.random.choice(['Male', 'Female'], size=n_samples, p=[0.52, 0.48])
    
    # Stroke Subtype (TOAST classification)
    stroke_subtype = np.random.choice(
        ['Large Artery Atherosclerosis', 'Cardioembolic', 'Small Vessel Occlusion (Lacunar)', 'Other/Cryptogenic'],
        size=n_samples,
        p=[0.32, 0.28, 0.24, 0.16]
    )
    
    # Time from symptom onset to emergency department arrival (hours)
    # Lognormal distribution
    onset_to_er_hours = np.clip(np.random.lognormal(mean=1.2, sigma=0.8, size=n_samples), 0.5, 24.0).round(1)
    
    baseline_glucose = np.clip(np.random.normal(135, 45, size=n_samples), 70, 320).round(1)
    systolic_bp = np.clip(np.random.normal(158, 24, size=n_samples), 105, 230).round().astype(int)
    
    prior_stroke_tia = np.random.choice([0, 1], size=n_samples, p=[0.77, 0.23])
    atrial_fibrillation = np.random.choice([0, 1], size=n_samples, p=[0.74, 0.26])
    
    # Specific acute focal neurological signs
    # Facial palsy (0: Normal, 1: Minor, 2: Partial, 3: Complete)
    facial_palsy = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.20, 0.35, 0.35, 0.10])
    
    # Motor arm weakness (0: No drift to 4: No movement)
    motor_arm_drift = np.random.choice([0, 1, 2, 3, 4], size=n_samples, p=[0.15, 0.25, 0.30, 0.20, 0.10])
    
    # Motor leg weakness (0-4)
    motor_leg_drift = np.random.choice([0, 1, 2, 3, 4], size=n_samples, p=[0.18, 0.27, 0.30, 0.15, 0.10])
    
    # Dysarthria / Speech impairment (0: Normal, 1: Mild-Moderate, 2: Severe/Mute)
    speech_impairment = np.random.choice([0, 1, 2], size=n_samples, p=[0.30, 0.50, 0.20])
    
    # Level of Consciousness deficit (0: Alert, 1: Not alert/arousable, 2: Not alert/obtunded, 3: Coma/unresponsive)
    loc_deficit = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.68, 0.22, 0.08, 0.02])
    
    # Calculate Ground Truth NIHSS Score (0 to 42)
    # Based on neurological deficits plus subtype severity (cardioembolic & large vessel typically higher)
    subtype_boost = np.select(
        [stroke_subtype == 'Large Artery Atherosclerosis', 
         stroke_subtype == 'Cardioembolic', 
         stroke_subtype == 'Small Vessel Occlusion (Lacunar)'],
        [4.5, 5.0, -1.5],
        default=0.0
    )
    
    raw_nihss = (
        1.5
        + 1.8 * facial_palsy
        + 2.6 * motor_arm_drift
        + 2.4 * motor_leg_drift
        + 2.2 * speech_impairment
        + 4.0 * loc_deficit
        + subtype_boost
        + 0.03 * (age - 60)
        + 0.015 * (baseline_glucose - 120)
        + np.random.normal(0, 1.8, n_samples)
    )
    nihss_score = np.clip(np.round(raw_nihss), 1, 38).astype(int)
    
    # Categorical severity classification
    # Mild (1-4), Moderate (5-15), Moderate-Severe (16-20), Severe (21+)
    severity_category = np.select(
        [nihss_score <= 4, nihss_score <= 15, nihss_score <= 20],
        ['Mild', 'Moderate', 'Moderate-Severe'],
        default='Severe'
    )
    
    # Reperfusion Therapies:
    # IV Thrombolysis (tPA): Eligible if ER arrival <= 4.5 hours and systolic BP manageable
    tpa_eligible = (onset_to_er_hours <= 4.5) & (nihss_score >= 4)
    thrombolysis_iv_tpa = np.where(tpa_eligible, np.random.choice([1, 0], size=n_samples, p=[0.75, 0.25]), 0)
    
    # Endovascular Thrombectomy (EVT): For high NIHSS and large vessel within 24h
    is_large_vessel = np.isin(stroke_subtype, ['Large Artery Atherosclerosis', 'Cardioembolic'])
    evt_eligible = (onset_to_er_hours <= 6.0) & (nihss_score >= 6) & is_large_vessel
    endovascular_thrombectomy = np.where(evt_eligible, np.random.choice([1, 0], size=n_samples, p=[0.68, 0.32]), 0)
    
    # Complications in acute phase
    complication_prob = 1 / (1 + np.exp(-(0.15 * nihss_score + 0.04 * (age - 60) - 2.8)))
    acute_complications = (np.random.rand(n_samples) < complication_prob).astype(int)
    
    # Task 3: 90-Day Functional Outcome (mRS 0-2 = Favorable Independence)
    # Higher NIHSS, older age, hyperglycemia, complications decrease odds of favorable outcome
    # Reperfusion (tPA, EVT) and early arrival increase odds of favorable outcome
    outcome_logit = (
        3.2
        - 0.19 * nihss_score
        - 0.045 * (age - 55)
        - 0.012 * (baseline_glucose - 110)
        + 1.10 * thrombolysis_iv_tpa
        + 1.35 * endovascular_thrombectomy
        - 0.08 * onset_to_er_hours
        - 1.45 * acute_complications
        - 0.65 * prior_stroke_tia
        + np.random.normal(0, 0.4, n_samples)
    )
    
    favorable_outcome_prob = 1 / (1 + np.exp(-outcome_logit))
    favorable_outcome_prob = np.clip(favorable_outcome_prob, 0.02, 0.98)
    
    # 1 = Good / Favorable (mRS 0-2), 0 = Poor / Dependent (mRS 3-6)
    favorable_90d_outcome = (np.random.rand(n_samples) < favorable_outcome_prob).astype(int)
    
    # Estimate exact 90-day mRS score (0 to 6)
    # 0: No symptoms, 1: No significant disability, 2: Slight disability (independent)
    # 3: Moderate disability, 4: Moderately severe disability, 5: Severe disability, 6: Dead
    mrs_estimated = []
    for fav, p in zip(favorable_90d_outcome, favorable_outcome_prob):
        if fav == 1:
            mrs = np.random.choice([0, 1, 2], p=[0.35, 0.45, 0.20])
        else:
            mrs = np.random.choice([3, 4, 5, 6], p=[0.35, 0.30, 0.20, 0.15])
        mrs_estimated.append(int(mrs))
    
    df = pd.DataFrame({
        'patient_id': [f'P-ACU-{20000+i}' for i in range(n_samples)],
        'age': age,
        'gender': gender,
        'stroke_subtype': stroke_subtype,
        'onset_to_er_hours': onset_to_er_hours,
        'systolic_bp': systolic_bp,
        'baseline_glucose': baseline_glucose,
        'prior_stroke_tia': prior_stroke_tia,
        'atrial_fibrillation': atrial_fibrillation,
        'facial_palsy': facial_palsy,
        'motor_arm_drift': motor_arm_drift,
        'motor_leg_drift': motor_leg_drift,
        'speech_impairment': speech_impairment,
        'loc_deficit': loc_deficit,
        'nihss_score': nihss_score,
        'severity_category': severity_category,
        'thrombolysis_iv_tpa': thrombolysis_iv_tpa,
        'endovascular_thrombectomy': endovascular_thrombectomy,
        'acute_complications': acute_complications,
        'favorable_outcome_probability': favorable_outcome_prob.round(4),
        'favorable_90d_outcome': favorable_90d_outcome,
        'estimated_mrs_90d': mrs_estimated
    })
    
    return df

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    print("[1/2] Synthesizing Stroke Risk Dataset (Task 1)...")
    df_risk = generate_stroke_risk_dataset(5000)
    risk_path = os.path.join(data_dir, 'stroke_risk_cohort.csv')
    df_risk.to_csv(risk_path, index=False)
    print(f" -> Saved {len(df_risk)} records to {risk_path}")
    print(f" -> Stroke incidence: {df_risk['stroke'].mean():.2%}")
    
    print("[2/2] Synthesizing Acute Stroke Severity & Functional Outcome Dataset (Tasks 2 & 3)...")
    df_acute = generate_stroke_severity_and_outcome_dataset(4000)
    acute_path = os.path.join(data_dir, 'acute_stroke_outcomes.csv')
    df_acute.to_csv(acute_path, index=False)
    print(f" -> Saved {len(df_acute)} records to {acute_path}")
    print(f" -> Mean NIHSS Score: {df_acute['nihss_score'].mean():.1f}")
    print(f" -> Favorable 90-day outcome rate: {df_acute['favorable_90d_outcome'].mean():.2%}")
    
    # Save a small sample batch test file for UI demonstrations
    sample_path = os.path.join(data_dir, 'sample_test_batch.csv')
    df_risk.head(25).drop(columns=['stroke_risk_probability', 'stroke']).to_csv(sample_path, index=False)
    print(f" -> Created sample test batch file at {sample_path}")
    print("Data synthesis complete successfully.")

if __name__ == '__main__':
    main()
