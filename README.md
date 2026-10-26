# NeuroPulse XAI: An Explainable Machine Learning Framework for Stroke Risk, Severity, and Functional Outcome Prediction

> **Disclaimer:** Research prototype trained on synthetic and public datasets. Not validated for clinical use. Not a medical device.

[![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Uvicorn-a855f7?style=flat-square)](http://127.0.0.1:8000)
[![Model Engine: XGBoost + TreeSHAP](https://img.shields.io/badge/ML%20Engine-XGBoost%20%7C%20TreeSHAP-10b981?style=flat-square)](models/benchmark_metrics.json)
[![Tests: Pytest & Playwright](https://img.shields.io/badge/Tests-100%25%20Passing-success?style=flat-square)](tests/)

---

## 📌 Executive Overview

**NeuroPulse XAI** is an end-to-end, clinically grounded artificial intelligence system designed to predict and explain cerebrovascular accident trajectories across three critical medical care stages using **deployed XGBoost models** and TreeSHAP explainability:

1. **Pillar 1 — Long-Term Stroke Risk Prediction (Deployed XGBoost):** 
   - ROC-AUC: **0.892** (0.8917)
   - Confusion Matrix (N=1,000): TN 740, FP 82, FN 65, TP 113
   - Sensitivity (Recall): **63.5%** | Specificity: **90.0%** (740/822) | PPV: **57.9%** | NPV: **91.9%**
2. **Pillar 2 — Acute Stroke Severity NIHSS (Deployed XGBoost Regressor):**
   - $R^2$: **0.905** | MAE: **1.572** points on standard NIHSS 0–42 scale
   - Standard 5-tier NIHSS stratification: No deficit (0), Minor (1–4), Moderate (5–15), Moderate-to-severe (16–20), Severe (21–42)
3. **Pillar 3 — 90-Day Functional Outcome Prognosis mRS (Deployed XGBoost Classifier):**
   - ROC-AUC: **0.837** (0.8369) | Sensitivity: **59.2%** | Specificity: **85.9%** | F1: **0.617**
   - Forecasts functional independence (mRS 0–2) vs moderate-to-severe disability (mRS 3–6) with model calibration caveats.

Every prediction is made transparent through **TreeSHAP (SHapley Additive exPlanations)**, decomposing model outputs into per-biomarker attributions ($\phi_i$), paired with an interactive **Counterfactual What-If Simulation Engine** that computes real-time model output variations under guideline-directed interventions (AHA/ASA targets).

---

## ⚡ Quick Start Guide

### 1. Requirements
- Python 3.10+
- Dependencies in virtual environment (fastapi, uvicorn, pydantic, scikit-learn, xgboost, shap, pandas, numpy, joblib, pytest, playwright)

### 2. Start Application Server
**Using Command Prompt or PowerShell:**
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Or run `run.bat` on Windows.

### 3. Open Interactive Web Application
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 🧪 Testing and Validation

All acceptance criteria are backed by automated tests:

### 1. Backend API & Edge Cases (pytest)
Runs 10 unit and integration tests covering `/health`, `/api/presets`, `/api/benchmarks`, all presets across all 3 tasks, clinical edge-cases (valid & invalid boundaries), empty CSV, and malformed CSV:
```powershell
python -m pytest tests/test_api.py -v
```

### 2. End-to-End Smoke & Consistency Test (Playwright)
Validates all 6 tabs, clicks all 4 presets, verifies live updates across Assessment, SHAP, What-If, and Report views, runs cohort batch screening, tests What-If sliders, verifies zero horizontal overflow at 1920, 1440, 1280, 768, and 390px, and verifies zero forbidden tokens (no raw LaTeX, no snake_case leaks, no NaN/undefined):
```powershell
python tests/test_playwright.py
```

### 3. Accessibility & Theme Audit (Playwright)
Audits WCAG AA form labels, accessible names on all interactive elements, and ARIA roles across both Light and Dark modes:
```powershell
python tests/test_a11y.py
```

---

## 📡 REST API Reference

All error responses return structured JSON `{"error": "...", "field": "..."}` with standard HTTP 4xx status codes.

| Endpoint | Method | Status | Description |
| :--- | :--- | :---: | :--- |
| `GET /health` | `GET` | `200` | Health check endpoint returning loaded model status and disclaimer |
| `GET /` | `GET` | `200` | Serves clinical single-page application |
| `GET /api/presets` | `GET` | `200` | Returns 4 structured clinical case profiles |
| `GET /api/benchmarks` | `GET` | `200` | Returns deployed and baseline model metrics, ROC coordinates, and confusion matrices |
| `POST /api/predict/risk` | `POST` | `200 / 422` | Computes long-term stroke risk probability & TreeSHAP attributions |
| `POST /api/predict/severity` | `POST` | `200 / 422` | Predicts continuous NIHSS deficit & triage recommendation |
| `POST /api/predict/outcome` | `POST` | `200 / 422` | Forecasts 90-day functional independence probability (mRS 0–2) |
| `POST /api/counterfactual` | `POST` | `200 / 422` | Simulates absolute & relative risk reduction under AHA/ASA guideline targets |
| `POST /api/batch` | `POST` | `200 / 422` | Screens cohort CSV (uploaded file or default N=25 sample) |

---

## 🔬 Benchmark Comparison (Validation Set)

All metrics are loaded directly from `models/benchmark_metrics.json`:

| Task | Model | Primary Metric | Sensitivity | Specificity | F1 / $R^2$ | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Task 1: Long-Term Risk** | **XGBoost** | **0.892 ROC-AUC** | **63.5%** | **90.0%** | **0.606 F1** | **Deployed** |
| | Logistic Regression | 0.908 ROC-AUC | 67.4% | 90.0% | 0.632 F1 | Baseline |
| | Random Forest | 0.901 ROC-AUC | 68.5% | 89.8% | 0.639 F1 | Baseline |
| **Task 2: NIHSS Severity** | **XGBoost Regressor** | **1.572 MAE** | — | — | **0.905 $R^2$** | **Deployed** |
| | Ridge Regression | 1.428 MAE | — | — | 0.922 $R^2$ | Baseline |
| **Task 3: 90-Day Outcome** | **XGBoost Classifier** | **0.837 ROC-AUC** | **59.2%** | **85.9%** | **0.617 F1** | **Deployed** |
| | Logistic Regression | 0.853 ROC-AUC | 56.7% | 87.7% | 0.610 F1 | Baseline |

---

## 👨‍🎓 Project Metadata

- **Project Title:** *An Explainable Machine Learning Framework for Stroke Risk, Severity, and Functional Outcome Prediction*
- **Candidate Registration Number:** `RA2311003011560`
- **Institution:** SRM Institute of Science and Technology
- **Department:** Department of Computer Science and Engineering
