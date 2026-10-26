"""
NeuroPulse XAI — FastAPI REST API
Explainable Machine Learning Framework for Stroke Risk, Severity, and Functional Outcome Prediction

Research prototype evaluated on the public Kaggle stroke dataset (N=5,110, 4.87% prevalence).
Not validated for clinical use. Not a medical device.
"""

import os
import io
import json
import pandas as pd
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator
import time

from src.xai_engine import engine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

app = FastAPI(
    title="NeuroPulse XAI — Stroke Clinical Decision Support System",
    description=(
        "Research prototype. Explainable ML for stroke risk, NIHSS severity, and 90-day mRS outcome. "
        "Not validated for clinical use. Not a medical device."
    ),
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Return structured validation errors instead of 422 detail blobs
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if errors:
        first = errors[0]
        field = ".".join(str(l) for l in first.get("loc", []) if l != "body")
        msg = str(first.get("msg", "Invalid value"))
        return JSONResponse(
            status_code=422,
            content={"error": msg, "field": field}
        )
    return JSONResponse(status_code=422, content={"error": "Validation error", "field": ""})

# Valid categorical values
VALID_GENDERS = {"Male", "Female"}
VALID_MARRIED = {"Yes", "No"}
VALID_WORK_TYPES = {"Private", "Self-employed", "Govt_job", "Never_worked", "children"}
VALID_RESIDENCE = {"Urban", "Rural"}
VALID_SMOKING = {"smokes", "formerly smoked", "never smoked", "Unknown"}
VALID_SUBTYPES = {
    "Large Artery Atherosclerosis", "Cardioembolic",
    "Small Vessel Occlusion (Lacunar)", "Other/Cryptogenic"
}

# -------------------------------------------------------------
# PYDANTIC DATA MODELS with clinical validation
# -------------------------------------------------------------
class StrokeRiskInput(BaseModel):
    age: float = Field(..., ge=18, le=100, description="Age in years (18-100)")
    gender: str = Field("Male")
    hypertension: int = Field(0, ge=0, le=1)
    systolic_bp: float = Field(120.0, ge=80, le=240, description="Systolic BP in mmHg")
    heart_disease: int = Field(0, ge=0, le=1)
    ever_married: str = Field("Yes")
    work_type: str = Field("Private")
    residence_type: str = Field("Urban")
    avg_glucose_level: float = Field(100.0, ge=50, le=400, description="Average glucose mg/dL")
    bmi: float = Field(25.0, ge=12, le=60, description="Body mass index")
    total_cholesterol: float = Field(200.0, ge=80, le=450, description="Total cholesterol mg/dL")
    smoking_status: str = Field("never smoked")
    physical_activity: float = Field(5.0, ge=0.0, le=10.0, description="Activity 0-10 scale")

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v not in VALID_GENDERS:
            raise ValueError(f"gender must be one of {sorted(VALID_GENDERS)}")
        return v

    @field_validator('smoking_status')
    @classmethod
    def validate_smoking(cls, v):
        if v not in VALID_SMOKING:
            raise ValueError(f"smoking_status must be one of {sorted(VALID_SMOKING)}")
        return v

    @field_validator('work_type')
    @classmethod
    def validate_work_type(cls, v):
        if v not in VALID_WORK_TYPES:
            raise ValueError(f"work_type must be one of {sorted(VALID_WORK_TYPES)}")
        return v

    @field_validator('residence_type')
    @classmethod
    def validate_residence(cls, v):
        if v not in VALID_RESIDENCE:
            raise ValueError(f"residence_type must be one of {sorted(VALID_RESIDENCE)}")
        return v


class StrokeSeverityInput(BaseModel):
    age: float = Field(..., ge=18, le=100)
    gender: str = Field("Male")
    stroke_subtype: str = Field("Large Artery Atherosclerosis")
    onset_to_er_hours: float = Field(2.5, ge=0.1, le=72.0)
    systolic_bp: float = Field(140.0, ge=80, le=260)
    baseline_glucose: float = Field(120.0, ge=50, le=400)
    prior_stroke_tia: int = Field(0, ge=0, le=1)
    atrial_fibrillation: int = Field(0, ge=0, le=1)
    facial_palsy: int = Field(0, ge=0, le=3)
    motor_arm_drift: int = Field(0, ge=0, le=4)
    motor_leg_drift: int = Field(0, ge=0, le=4)
    speech_impairment: int = Field(0, ge=0, le=2)
    loc_deficit: int = Field(0, ge=0, le=3)

    @field_validator('stroke_subtype')
    @classmethod
    def validate_subtype(cls, v):
        if v not in VALID_SUBTYPES:
            raise ValueError(f"stroke_subtype must be one of {sorted(VALID_SUBTYPES)}")
        return v


class StrokeOutcomeInput(BaseModel):
    age: float = Field(..., ge=18, le=100)
    gender: str = Field("Male")
    stroke_subtype: str = Field("Large Artery Atherosclerosis")
    nihss_score: float = Field(10.0, ge=0, le=42)
    onset_to_er_hours: float = Field(2.5, ge=0.1, le=72.0)
    systolic_bp: float = Field(140.0, ge=80, le=260)
    baseline_glucose: float = Field(120.0, ge=50, le=400)
    prior_stroke_tia: int = Field(0, ge=0, le=1)
    atrial_fibrillation: int = Field(0, ge=0, le=1)
    thrombolysis_iv_tpa: int = Field(0, ge=0, le=1)
    endovascular_thrombectomy: int = Field(0, ge=0, le=1)
    acute_complications: int = Field(0, ge=0, le=1)

    @field_validator('stroke_subtype')
    @classmethod
    def validate_subtype(cls, v):
        if v not in VALID_SUBTYPES:
            raise ValueError(f"stroke_subtype must be one of {sorted(VALID_SUBTYPES)}")
        return v


# -------------------------------------------------------------
# API ROUTES
# -------------------------------------------------------------
@app.get("/health")
def health_check():
    """Health check endpoint. Returns 200 when server and models are loaded."""
    return {
        "status": "ok",
        "timestamp": time.time(),
        "models_loaded": ["task1_risk", "task2_severity", "task3_outcome"],
        "disclaimer": (
            "Research prototype evaluated on the public Kaggle stroke dataset (N=5,110, 4.87% prevalence). "
            "Not validated for clinical use. Not a medical device."
        )
    }


@app.post("/api/predict/risk")
def predict_stroke_risk(data: StrokeRiskInput):
    """Predict long-term stroke risk probability with SHAP attributions."""
    patient_dict = data.model_dump()
    try:
        result = engine.explain_stroke_risk(patient_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "endpoint": "/api/predict/risk"})


@app.post("/api/predict/severity")
def predict_stroke_severity(data: StrokeSeverityInput):
    """Predict acute NIHSS stroke severity score with SHAP attributions."""
    patient_dict = data.model_dump()
    try:
        result = engine.explain_severity(patient_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "endpoint": "/api/predict/severity"})


@app.post("/api/predict/outcome")
def predict_functional_outcome(data: StrokeOutcomeInput):
    """Predict 90-day functional outcome (mRS 0-2 probability) with SHAP attributions."""
    patient_dict = data.model_dump()
    try:
        result = engine.explain_functional_outcome(patient_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "endpoint": "/api/predict/outcome"})


@app.post("/api/counterfactual")
def get_counterfactual_recommendations(data: StrokeRiskInput):
    """Compute counterfactual what-if interventions for stroke risk reduction."""
    patient_dict = data.model_dump()
    try:
        result = engine.generate_counterfactuals(patient_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "endpoint": "/api/counterfactual"})


@app.get("/api/benchmarks")
def get_model_benchmarks():
    """Return comparative model benchmark metrics from benchmark_metrics.json."""
    meta_path = os.path.join(MODELS_DIR, 'benchmark_metrics.json')
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="Benchmark metrics file not found.")
    with open(meta_path, 'r') as f:
        data = json.load(f)
    return data


@app.get("/api/kaggle-framework")
def get_kaggle_framework_results():
    """Return Kaggle 5-stage CatBoost framework results."""
    path = os.path.join(MODELS_DIR, 'kaggle_framework_results.json')
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Kaggle framework results not found.")
    with open(path, 'r') as f:
        data = json.load(f)
    return data




@app.get("/api/presets")
def get_clinical_presets():
    """Return clinical preset patient profiles for demonstration."""
    return {
        "presets": [
            {
                "id": "critical_risk",
                "title": "High-risk elderly",
                "label": "Case 1",
                "description": "72yo male, hypertension (SBP 175), CAD, glucose 225 mg/dL, current smoker, sedentary.",
                "data": {
                    "age": 72,
                    "gender": "Male",
                    "hypertension": 1,
                    "systolic_bp": 175,
                    "heart_disease": 1,
                    "ever_married": "Yes",
                    "work_type": "Private",
                    "residence_type": "Urban",
                    "avg_glucose_level": 225.0,
                    "bmi": 32.5,
                    "total_cholesterol": 260.0,
                    "smoking_status": "smokes",
                    "physical_activity": 1.5,
                    "stroke_subtype": "Large Artery Atherosclerosis",
                    "onset_to_er_hours": 3.0,
                    "prior_stroke_tia": 1,
                    "atrial_fibrillation": 1,
                    "facial_palsy": 2,
                    "motor_arm_drift": 3,
                    "motor_leg_drift": 3,
                    "speech_impairment": 2,
                    "loc_deficit": 1,
                    "thrombolysis_iv_tpa": 1,
                    "endovascular_thrombectomy": 0,
                    "acute_complications": 1
                }
            },
            {
                "id": "moderate_risk",
                "title": "Pre-hypertensive",
                "label": "Case 2",
                "description": "54yo female, borderline BP (142), glucose 135 mg/dL, former smoker, BMI 28.5.",
                "data": {
                    "age": 54,
                    "gender": "Female",
                    "hypertension": 0,
                    "systolic_bp": 142,
                    "heart_disease": 0,
                    "ever_married": "Yes",
                    "work_type": "Govt_job",
                    "residence_type": "Urban",
                    "avg_glucose_level": 135.0,
                    "bmi": 28.5,
                    "total_cholesterol": 215.0,
                    "smoking_status": "formerly smoked",
                    "physical_activity": 4.0,
                    "stroke_subtype": "Small Vessel Occlusion (Lacunar)",
                    "onset_to_er_hours": 4.0,
                    "prior_stroke_tia": 0,
                    "atrial_fibrillation": 0,
                    "facial_palsy": 1,
                    "motor_arm_drift": 1,
                    "motor_leg_drift": 1,
                    "speech_impairment": 1,
                    "loc_deficit": 0,
                    "thrombolysis_iv_tpa": 1,
                    "endovascular_thrombectomy": 0,
                    "acute_complications": 0
                }
            },
            {
                "id": "low_risk",
                "title": "Healthy adult",
                "label": "Case 3",
                "description": "36yo female, normotensive (118), glucose 88 mg/dL, non-smoker, regular exercise.",
                "data": {
                    "age": 36,
                    "gender": "Female",
                    "hypertension": 0,
                    "systolic_bp": 118,
                    "heart_disease": 0,
                    "ever_married": "Yes",
                    "work_type": "Private",
                    "residence_type": "Rural",
                    "avg_glucose_level": 88.0,
                    "bmi": 22.4,
                    "total_cholesterol": 175.0,
                    "smoking_status": "never smoked",
                    "physical_activity": 8.0,
                    "stroke_subtype": "Other/Cryptogenic",
                    "onset_to_er_hours": 12.0,
                    "prior_stroke_tia": 0,
                    "atrial_fibrillation": 0,
                    "facial_palsy": 0,
                    "motor_arm_drift": 0,
                    "motor_leg_drift": 0,
                    "speech_impairment": 0,
                    "loc_deficit": 0,
                    "thrombolysis_iv_tpa": 0,
                    "endovascular_thrombectomy": 0,
                    "acute_complications": 0
                }
            },
            {
                "id": "acute_mca_stroke",
                "title": "Acute MCA occlusion",
                "label": "Case 4",
                "description": "67yo male, 1.8h onset, dense hemiparesis, facial droop, dysarthria, tPA + EVT candidate.",
                "data": {
                    "age": 67,
                    "gender": "Male",
                    "hypertension": 1,
                    "systolic_bp": 168,
                    "heart_disease": 1,
                    "ever_married": "Yes",
                    "work_type": "Private",
                    "residence_type": "Urban",
                    "avg_glucose_level": 142.0,
                    "bmi": 27.8,
                    "total_cholesterol": 210.0,
                    "smoking_status": "formerly smoked",
                    "physical_activity": 3.0,
                    "stroke_subtype": "Large Artery Atherosclerosis",
                    "onset_to_er_hours": 1.8,
                    "prior_stroke_tia": 1,
                    "atrial_fibrillation": 1,
                    "facial_palsy": 2,
                    "motor_arm_drift": 3,
                    "motor_leg_drift": 3,
                    "speech_impairment": 2,
                    "loc_deficit": 1,
                    "thrombolysis_iv_tpa": 1,
                    "endovascular_thrombectomy": 1,
                    "acute_complications": 0
                }
            }
        ]
    }


@app.post("/api/batch")
async def process_batch_screening(file: UploadFile = File(None)):
    """
    Batch risk screening endpoint.
    Accepts a CSV file upload or evaluates the built-in 25-patient sample cohort.
    Rows with Unknown/missing values are sanitized before scoring.
    Returns per-patient risk predictions plus summary counts.
    """
    if file and file.filename:
        try:
            content = await file.read()
            if len(content) == 0:
                return JSONResponse(
                    status_code=422,
                    content={"error": "Uploaded CSV file is empty.", "field": "file"}
                )
            df = pd.read_csv(io.BytesIO(content))
        except Exception as e:
            return JSONResponse(
                status_code=422,
                content={"error": f"Could not parse CSV: {str(e)}", "field": "file"}
            )
    else:
        sample_path = os.path.join(DATA_DIR, 'sample_test_batch.csv')
        if not os.path.exists(sample_path):
            raise HTTPException(status_code=404, detail="Sample batch file not found.")
        df = pd.read_csv(sample_path)

    # Validate required columns
    required_cols = {'age', 'gender', 'hypertension', 'systolic_bp', 'heart_disease',
                     'ever_married', 'work_type', 'residence_type',
                     'avg_glucose_level', 'bmi', 'smoking_status'}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        return JSONResponse(
            status_code=422,
            content={
                "error": f"CSV is missing required columns: {sorted(missing_cols)}",
                "field": "file"
            }
        )

    if len(df) == 0:
        return JSONResponse(
            status_code=422,
            content={"error": "CSV contains no data rows.", "field": "file"}
        )

    records = df.to_dict(orient='records')
    evaluated = []
    errors = []

    for i, r in enumerate(records):
        try:
            # Sanitize: map Unknown smoking to "never smoked" for inference
            smoking = str(r.get('smoking_status', 'never smoked')).strip()
            if smoking not in VALID_SMOKING - {'Unknown'}:
                smoking = 'never smoked'

            # Sanitize: fill missing optional fields with defaults
            patient = {
                'age': float(r.get('age', 50)),
                'gender': str(r.get('gender', 'Male')).strip(),
                'hypertension': int(r.get('hypertension', 0)),
                'systolic_bp': float(r.get('systolic_bp', 120)),
                'heart_disease': int(r.get('heart_disease', 0)),
                'ever_married': str(r.get('ever_married', 'Yes')).strip(),
                'work_type': str(r.get('work_type', 'Private')).strip(),
                'residence_type': str(r.get('residence_type', 'Urban')).strip(),
                'avg_glucose_level': float(r.get('avg_glucose_level', 100)),
                'bmi': float(r.get('bmi', 25)),
                'total_cholesterol': float(r.get('total_cholesterol', 200)),
                'smoking_status': smoking,
                'physical_activity': float(r.get('physical_activity', 5)),
            }

            # Clamp to valid ranges
            patient['age'] = max(18, min(100, patient['age']))
            patient['systolic_bp'] = max(80, min(240, patient['systolic_bp']))
            patient['avg_glucose_level'] = max(50, min(400, patient['avg_glucose_level']))
            patient['bmi'] = max(12, min(60, patient['bmi']))

            # Validate categoricals, fall back to defaults
            if patient['gender'] not in VALID_GENDERS:
                patient['gender'] = 'Male'
            if patient['work_type'] not in VALID_WORK_TYPES:
                patient['work_type'] = 'Private'
            if patient['residence_type'] not in VALID_RESIDENCE:
                patient['residence_type'] = 'Urban'
            if patient['ever_married'] not in VALID_MARRIED:
                patient['ever_married'] = 'Yes'

            res = engine.explain_stroke_risk(patient)
            top_driver = res['top_attributions'][0]['feature'] if res['top_attributions'] else 'N/A'

            evaluated.append({
                'patient_id': str(r.get('patient_id', f'P-{i+1}')),
                'age': patient['age'],
                'gender': patient['gender'],
                'systolic_bp': patient['systolic_bp'],
                'glucose': patient['avg_glucose_level'],
                'probability_pct': res['probability_pct'],
                'risk_tier': res['risk_tier'],
                'top_driver': top_driver,
                'smoking_note': '(Unknown mapped to never smoked)' if str(r.get('smoking_status', '')).strip() == 'Unknown' else ''
            })
        except Exception as e:
            errors.append({'row': i + 1, 'patient_id': str(r.get('patient_id', f'P-{i+1}')), 'error': str(e)})
            continue

    total = len(evaluated)
    high_critical = sum(1 for e in evaluated if 'High' in e['risk_tier'] or 'Critical' in e['risk_tier'])
    moderate = sum(1 for e in evaluated if 'Moderate' in e['risk_tier'])
    low = sum(1 for e in evaluated if 'Low' in e['risk_tier'])

    return {
        'total_evaluated': total,
        'high_critical_count': high_critical,
        'moderate_count': moderate,
        'low_count': low,
        'high_critical_rate_pct': round((high_critical / max(1, total)) * 100, 1),
        'patients': evaluated,
        'row_errors': errors
    }


# -------------------------------------------------------------
# PDF DOWNLOAD ROUTES
# -------------------------------------------------------------
@app.get("/api/download/clinical-report")
async def download_clinical_report():
    pdf_path = os.path.join(BASE_DIR, "clinical_report.pdf")
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join(STATIC_DIR, "clinical_report.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Clinical audit report PDF not found.")
    return FileResponse(
        path=pdf_path,
        filename="NeuroPulse_Clinical_Audit_Report.pdf",
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=\"NeuroPulse_Clinical_Audit_Report.pdf\""}
    )


# Mount static files and serve index
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def get_index():
    return FileResponse(os.path.join(STATIC_DIR, 'index.html'))
