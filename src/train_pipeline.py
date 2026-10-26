"""
Multi-Task Machine Learning Training & XAI Explainer Pipeline
Project: An Explainable Machine Learning Framework for Stroke Risk, Severity, and Functional Outcome Prediction
Author: RA2311003011560
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    roc_auc_score, average_precision_score, accuracy_score,
    precision_score, recall_score, f1_score, confusion_matrix,
    roc_curve, precision_recall_curve, mean_absolute_error,
    mean_squared_error, r2_score, brier_score_loss
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, VotingClassifier
from sklearn.linear_model import LogisticRegression, Ridge
import xgboost as xgb
import shap

SEED = 42
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

# -------------------------------------------------------------
# TASK 1: STROKE RISK PREDICTION
# -------------------------------------------------------------
def train_stroke_risk_pipeline():
    print("=" * 60)
    print(">>> TRAINING TASK 1: Stroke Risk Prediction Pipeline")
    print("=" * 60)
    
    df = pd.read_csv(os.path.join(DATA_DIR, 'stroke_risk_cohort.csv'))
    
    numeric_features = ['age', 'systolic_bp', 'avg_glucose_level', 'bmi', 'total_cholesterol', 'physical_activity']
    categorical_features = ['gender', 'hypertension', 'heart_disease', 'ever_married', 'work_type', 'residence_type', 'smoking_status']
    
    X = df[numeric_features + categorical_features]
    y = df['stroke']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=SEED, stratify=y
    )
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), categorical_features)
        ]
    )
    
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)
    
    # Get encoded feature names
    cat_encoder = preprocessor.named_transformers_['cat']
    cat_feature_names = list(cat_encoder.get_feature_names_out(categorical_features))
    all_feature_names = numeric_features + cat_feature_names
    
    # Candidate models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=SEED),
        'Random Forest': RandomForestClassifier(n_estimators=180, max_depth=8, random_state=SEED, n_jobs=-1),
        'XGBoost': xgb.XGBClassifier(
            n_estimators=160, max_depth=5, learning_rate=0.08,
            subsample=0.85, colsample_bytree=0.85, eval_metric='logloss',
            random_state=SEED
        )
    }
    
    results = {}
    fitted_models = {}
    
    for name, model in models.items():
        model.fit(X_train_proc, y_train)
        fitted_models[name] = model
        
        y_prob = model.predict_proba(X_test_proc)[:, 1]
        y_pred = (y_prob >= 0.35).astype(int)  # clinically tuned decision threshold for stroke triage
        
        roc_auc = float(roc_auc_score(y_test, y_prob))
        pr_auc = float(average_precision_score(y_test, y_prob))
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred))
        f1 = float(f1_score(y_test, y_pred))
        brier = float(brier_score_loss(y_test, y_prob))
        
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        spec = float(tn / (tn + fp))
        
        # Cross validation AUC
        cv_scores = cross_val_score(model, X_train_proc, y_train, cv=5, scoring='roc_auc')
        
        # ROC Curve points for frontend graphing
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        fpr_pts = [round(float(x), 4) for x in fpr[::max(1, len(fpr)//40)]]
        tpr_pts = [round(float(x), 4) for x in tpr[::max(1, len(tpr)//40)]]
        
        results[name] = {
            'roc_auc': round(roc_auc, 4),
            'pr_auc': round(pr_auc, 4),
            'accuracy': round(acc, 4),
            'precision': round(prec, 4),
            'recall_sensitivity': round(rec, 4),
            'specificity': round(spec, 4),
            'f1_score': round(f1, 4),
            'brier_score': round(brier, 4),
            'cv_roc_auc_mean': round(float(cv_scores.mean()), 4),
            'cv_roc_auc_std': round(float(cv_scores.std()), 4),
            'confusion_matrix': {'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp)},
            'roc_curve': {'fpr': fpr_pts, 'tpr': tpr_pts}
        }
        print(f" -> {name:20s} | ROC-AUC: {roc_auc:.4f} | Recall: {rec:.4f} | F1: {f1:.4f}")
    
    # Select Best Model for production serving: XGBoost
    best_model = fitted_models['XGBoost']
    
    # SHAP Explainer
    print(" -> Computing SHAP values and TreeExplainer...")
    explainer = shap.TreeExplainer(best_model)
    shap_sample = X_test_proc[:250]
    shap_values = explainer.shap_values(shap_sample)
    
    # Global feature importance (mean absolute SHAP)
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    top_feature_importance = [
        {'feature': feat, 'importance': round(float(val), 4)}
        for feat, val in sorted(zip(all_feature_names, mean_abs_shap), key=lambda x: x[1], reverse=True)
    ]
    
    # Save artifacts
    joblib.dump(best_model, os.path.join(MODELS_DIR, 'task1_risk_model.joblib'))
    joblib.dump(preprocessor, os.path.join(MODELS_DIR, 'task1_preprocessor.joblib'))
    
    return {
        'model_benchmarks': results,
        'global_feature_importance': top_feature_importance,
        'feature_names': all_feature_names,
        'expected_value': float(explainer.expected_value) if np.isscalar(explainer.expected_value) else float(explainer.expected_value[0])
    }

# -------------------------------------------------------------
# TASK 2: ACUTE STROKE SEVERITY (NIHSS) PREDICTION
# -------------------------------------------------------------
def train_stroke_severity_pipeline():
    print("=" * 60)
    print(">>> TRAINING TASK 2: Acute Stroke Severity (NIHSS) Pipeline")
    print("=" * 60)
    
    df = pd.read_csv(os.path.join(DATA_DIR, 'acute_stroke_outcomes.csv'))
    
    numeric_features = ['age', 'onset_to_er_hours', 'systolic_bp', 'baseline_glucose']
    categorical_features = ['gender', 'stroke_subtype', 'prior_stroke_tia', 'atrial_fibrillation',
                            'facial_palsy', 'motor_arm_drift', 'motor_leg_drift', 'speech_impairment', 'loc_deficit']
    
    X = df[numeric_features + categorical_features]
    y = df['nihss_score']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=SEED
    )
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), categorical_features)
        ]
    )
    
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)
    
    cat_encoder = preprocessor.named_transformers_['cat']
    cat_feature_names = list(cat_encoder.get_feature_names_out(categorical_features))
    all_feature_names = numeric_features + cat_feature_names
    
    models = {
        'Ridge Regression': Ridge(alpha=1.0, random_state=SEED),
        'Random Forest Regressor': RandomForestRegressor(n_estimators=180, max_depth=8, random_state=SEED, n_jobs=-1),
        'XGBoost Regressor': xgb.XGBRegressor(
            n_estimators=160, max_depth=5, learning_rate=0.08,
            subsample=0.85, colsample_bytree=0.85, random_state=SEED
        )
    }
    
    results = {}
    fitted_models = {}
    
    for name, model in models.items():
        model.fit(X_train_proc, y_train)
        fitted_models[name] = model
        
        y_pred = model.predict(X_test_proc)
        
        mae = float(mean_absolute_error(y_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2 = float(r2_score(y_test, y_pred))
        
        # Categorical classification accuracy based on NIHSS tiers (Mild: 1-4, Mod: 5-15, Mod-Sev: 16-20, Sev: 21+)
        y_test_tier = np.select([y_test <= 4, y_test <= 15, y_test <= 20], [0, 1, 2], default=3)
        y_pred_tier = np.select([y_pred <= 4, y_pred <= 15, y_pred <= 20], [0, 1, 2], default=3)
        tier_acc = float(accuracy_score(y_test_tier, y_pred_tier))
        
        results[name] = {
            'mae': round(mae, 4),
            'rmse': round(rmse, 4),
            'r2_score': round(r2, 4),
            'severity_tier_accuracy': round(tier_acc, 4)
        }
        print(f" -> {name:25s} | MAE: {mae:.3f} | RMSE: {rmse:.3f} | R2: {r2:.3f} | Tier Acc: {tier_acc:.2%}")
    
    best_model = fitted_models['XGBoost Regressor']
    
    # SHAP Explainer
    explainer = shap.TreeExplainer(best_model)
    shap_sample = X_test_proc[:250]
    shap_values = explainer.shap_values(shap_sample)
    
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    top_feature_importance = [
        {'feature': feat, 'importance': round(float(val), 4)}
        for feat, val in sorted(zip(all_feature_names, mean_abs_shap), key=lambda x: x[1], reverse=True)
    ]
    
    joblib.dump(best_model, os.path.join(MODELS_DIR, 'task2_severity_model.joblib'))
    joblib.dump(preprocessor, os.path.join(MODELS_DIR, 'task2_preprocessor.joblib'))
    
    return {
        'model_benchmarks': results,
        'global_feature_importance': top_feature_importance,
        'feature_names': all_feature_names,
        'expected_value': float(explainer.expected_value) if np.isscalar(explainer.expected_value) else float(explainer.expected_value[0])
    }

# -------------------------------------------------------------
# TASK 3: 90-DAY FUNCTIONAL OUTCOME (mRS 0-2 FAVORABLE INDEPENDENCE)
# -------------------------------------------------------------
def train_stroke_outcome_pipeline():
    print("=" * 60)
    print(">>> TRAINING TASK 3: 90-Day Functional Outcome Prediction")
    print("=" * 60)
    
    df = pd.read_csv(os.path.join(DATA_DIR, 'acute_stroke_outcomes.csv'))
    
    numeric_features = ['age', 'nihss_score', 'onset_to_er_hours', 'systolic_bp', 'baseline_glucose']
    categorical_features = ['gender', 'stroke_subtype', 'prior_stroke_tia', 'atrial_fibrillation',
                            'thrombolysis_iv_tpa', 'endovascular_thrombectomy', 'acute_complications']
    
    X = df[numeric_features + categorical_features]
    y = df['favorable_90d_outcome']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=SEED, stratify=y
    )
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), categorical_features)
        ]
    )
    
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)
    
    cat_encoder = preprocessor.named_transformers_['cat']
    cat_feature_names = list(cat_encoder.get_feature_names_out(categorical_features))
    all_feature_names = numeric_features + cat_feature_names
    
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=SEED),
        'Random Forest': RandomForestClassifier(n_estimators=180, max_depth=8, random_state=SEED, n_jobs=-1),
        'XGBoost': xgb.XGBClassifier(
            n_estimators=160, max_depth=5, learning_rate=0.08,
            subsample=0.85, colsample_bytree=0.85, eval_metric='logloss',
            random_state=SEED
        )
    }
    
    results = {}
    fitted_models = {}
    
    for name, model in models.items():
        model.fit(X_train_proc, y_train)
        fitted_models[name] = model
        
        y_prob = model.predict_proba(X_test_proc)[:, 1]
        y_pred = (y_prob >= 0.50).astype(int)
        
        roc_auc = float(roc_auc_score(y_test, y_prob))
        pr_auc = float(average_precision_score(y_test, y_prob))
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred))
        f1 = float(f1_score(y_test, y_pred))
        brier = float(brier_score_loss(y_test, y_prob))
        
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        spec = float(tn / (tn + fp))
        
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        fpr_pts = [round(float(x), 4) for x in fpr[::max(1, len(fpr)//40)]]
        tpr_pts = [round(float(x), 4) for x in tpr[::max(1, len(tpr)//40)]]
        
        results[name] = {
            'roc_auc': round(roc_auc, 4),
            'pr_auc': round(pr_auc, 4),
            'accuracy': round(acc, 4),
            'precision': round(prec, 4),
            'recall_sensitivity': round(rec, 4),
            'specificity': round(spec, 4),
            'f1_score': round(f1, 4),
            'brier_score': round(brier, 4),
            'confusion_matrix': {'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp)},
            'roc_curve': {'fpr': fpr_pts, 'tpr': tpr_pts}
        }
        print(f" -> {name:20s} | ROC-AUC: {roc_auc:.4f} | F1: {f1:.4f} | Recall: {rec:.4f}")
    
    best_model = fitted_models['XGBoost']
    
    explainer = shap.TreeExplainer(best_model)
    shap_sample = X_test_proc[:250]
    shap_values = explainer.shap_values(shap_sample)
    
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    top_feature_importance = [
        {'feature': feat, 'importance': round(float(val), 4)}
        for feat, val in sorted(zip(all_feature_names, mean_abs_shap), key=lambda x: x[1], reverse=True)
    ]
    
    joblib.dump(best_model, os.path.join(MODELS_DIR, 'task3_outcome_model.joblib'))
    joblib.dump(preprocessor, os.path.join(MODELS_DIR, 'task3_preprocessor.joblib'))
    
    return {
        'model_benchmarks': results,
        'global_feature_importance': top_feature_importance,
        'feature_names': all_feature_names,
        'expected_value': float(explainer.expected_value) if np.isscalar(explainer.expected_value) else float(explainer.expected_value[0])
    }

def main():
    print("=" * 70)
    print("STARTING FULL MACHINE LEARNING & XAI FRAMEWORK TRAINING")
    print("Registration No: RA2311003011560")
    print("=" * 70)
    
    task1_meta = train_stroke_risk_pipeline()
    task2_meta = train_stroke_severity_pipeline()
    task3_meta = train_stroke_outcome_pipeline()
    
    full_metadata = {
        'project_title': 'An Explainable Machine Learning Framework for Stroke Risk, Severity, and Functional Outcome Prediction',
        'student_id': 'RA2311003011560',
        'task1_risk': task1_meta,
        'task2_severity': task2_meta,
        'task3_outcome': task3_meta
    }
    
    meta_path = os.path.join(MODELS_DIR, 'benchmark_metrics.json')
    with open(meta_path, 'w') as f:
        json.dump(full_metadata, f, indent=2)
    
    print("=" * 70)
    print(f"TRAINING COMPLETE. Metadata & benchmark saved to {meta_path}")
    print("=" * 70)

if __name__ == '__main__':
    main()
