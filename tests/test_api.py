import io
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "models_loaded" in data
    assert len(data["models_loaded"]) == 3
    assert "disclaimer" in data

def test_presets_endpoint():
    response = client.get("/api/presets")
    assert response.status_code == 200
    data = response.json()
    assert "presets" in data
    assert len(data["presets"]) == 4
    for p in data["presets"]:
        assert "id" in p
        assert "title" in p
        assert "data" in p

def test_benchmarks_endpoint():
    response = client.get("/api/benchmarks")
    assert response.status_code == 200
    data = response.json()
    assert "task1_risk" in data
    assert "task2_severity" in data
    assert "task3_outcome" in data

def test_all_presets_on_all_prediction_tasks():
    presets_res = client.get("/api/presets").json()["presets"]
    for preset in presets_res:
        payload = preset["data"]
        
        # Task 1: Risk
        risk_res = client.post("/api/predict/risk", json=payload)
        assert risk_res.status_code == 200, f"Preset {preset['id']} failed risk: {risk_res.text}"
        risk_data = risk_res.json()
        assert "probability" in risk_data
        assert "probability_pct" in risk_data
        assert "risk_tier" in risk_data
        assert "top_attributions" in risk_data
        
        # Check SHAP sign agreement
        for feat in risk_data["top_attributions"]:
            shap_val = feat["shap_value"]
            direction = feat["direction"]
            if shap_val > 0:
                assert direction == "risk_increasing", f"Feature {feat['feature']} shap {shap_val} has wrong direction {direction}"
            elif shap_val < 0:
                assert direction == "protective", f"Feature {feat['feature']} shap {shap_val} has wrong direction {direction}"

        # Task 2: Severity
        sev_res = client.post("/api/predict/severity", json=payload)
        assert sev_res.status_code == 200, f"Preset {preset['id']} failed severity: {sev_res.text}"
        sev_data = sev_res.json()
        assert "predicted_nihss" in sev_data
        assert "severity_tier" in sev_data
        assert 0 <= sev_data["predicted_nihss"] <= 42

        # Task 3: Outcome
        out_res = client.post("/api/predict/outcome", json=payload)
        assert out_res.status_code == 200, f"Preset {preset['id']} failed outcome: {out_res.text}"
        out_data = out_res.json()
        assert "favorable_probability" in out_data
        assert "outcome_prognosis" in out_data

        # Counterfactual
        cf_res = client.post("/api/counterfactual", json=payload)
        assert cf_res.status_code == 200, f"Preset {preset['id']} failed counterfactual: {cf_res.text}"
        cf_data = cf_res.json()
        assert "baseline_risk_pct" in cf_data
        assert "optimized_risk_pct" in cf_data
        assert "individual_interventions" in cf_data

def test_clinical_edge_cases_valid():
    base_case = {
        "age": 18,
        "gender": "Male",
        "hypertension": 0,
        "systolic_bp": 80.0,
        "heart_disease": 0,
        "ever_married": "No",
        "work_type": "Never_worked",
        "residence_type": "Rural",
        "avg_glucose_level": 50.0,
        "bmi": 12.0,
        "total_cholesterol": 120.0,
        "smoking_status": "never smoked",
        "physical_activity": 10.0
    }
    r1 = client.post("/api/predict/risk", json=base_case)
    assert r1.status_code == 200

    upper_case = {
        "age": 100,
        "gender": "Female",
        "hypertension": 1,
        "systolic_bp": 240.0,
        "heart_disease": 1,
        "ever_married": "Yes",
        "work_type": "Private",
        "residence_type": "Urban",
        "avg_glucose_level": 400.0,
        "bmi": 60.0,
        "total_cholesterol": 400.0,
        "smoking_status": "smokes",
        "physical_activity": 0.0
    }
    r2 = client.post("/api/predict/risk", json=upper_case)
    assert r2.status_code == 200

def test_clinical_edge_cases_invalid():
    # Under age 18
    r = client.post("/api/predict/risk", json={"age": 15})
    assert r.status_code == 422
    err = r.json()
    assert "error" in err
    assert "field" in err

    # Over age 100
    r = client.post("/api/predict/risk", json={"age": 105})
    assert r.status_code == 422

    # SBP too low (<80)
    r = client.post("/api/predict/risk", json={"age": 50, "systolic_bp": 60})
    assert r.status_code == 422

    # SBP too high (>240)
    r = client.post("/api/predict/risk", json={"age": 50, "systolic_bp": 260})
    assert r.status_code == 422

    # Glucose too low (<50)
    r = client.post("/api/predict/risk", json={"age": 50, "avg_glucose_level": 40})
    assert r.status_code == 422

    # BMI too low (<12)
    r = client.post("/api/predict/risk", json={"age": 50, "bmi": 10})
    assert r.status_code == 422

    # Invalid categorical gender
    r = client.post("/api/predict/risk", json={"age": 50, "gender": "Alien"})
    assert r.status_code == 422

def test_batch_sample():
    response = client.post("/api/batch")
    assert response.status_code == 200
    data = response.json()
    assert data["total_evaluated"] == 25
    total = data["high_critical_count"] + data["moderate_count"] + data["low_count"]
    assert total == data["total_evaluated"]
    assert len(data["patients"]) == 25

def test_batch_empty_csv():
    files = {"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
    response = client.post("/api/batch", files=files)
    assert response.status_code == 422
    assert "error" in response.json()

def test_batch_malformed_csv():
    bad_csv = b"colA,colB,colC\n1,2,3\n4,5,6\n"
    files = {"file": ("malformed.csv", io.BytesIO(bad_csv), "text/csv")}
    response = client.post("/api/batch", files=files)
    assert response.status_code == 422
    assert "error" in response.json()

def test_counterfactual_simulation():
    case = {
        "age": 65,
        "gender": "Male",
        "hypertension": 1,
        "systolic_bp": 170.0,
        "heart_disease": 0,
        "avg_glucose_level": 200.0,
        "bmi": 32.0,
        "smoking_status": "smokes",
        "physical_activity": 1.0
    }
    res = client.post("/api/counterfactual", json=case)
    assert res.status_code == 200
    data = res.json()
    assert data["baseline_risk_pct"] > 0
    assert "individual_interventions" in data
    for inter in data["individual_interventions"]:
        assert "parameter" in inter
        assert "abs_drop_pp" in inter
        assert "new_probability_pct" in inter

def test_kaggle_framework_endpoint():
    res = client.get("/api/kaggle-framework")
    assert res.status_code == 200
    data = res.json()
    assert "stage1_preprocessing" in data
    assert "stage2_benchmarks" in data
    assert "stage3_calibration" in data
    assert "stage4_shap" in data
    assert "stage5_subgroups" in data

def test_download_clinical_report_endpoint():
    res = client.get("/api/download/clinical-report")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert "NeuroPulse_Clinical_Audit_Report.pdf" in res.headers.get("content-disposition", "")
    assert len(res.content) > 100000
