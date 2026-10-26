import io
import time
from playwright.sync_api import sync_playwright

def test_deep_checks():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        print("[1/8] Loading application...")
        page.goto("http://127.0.0.1:8000/", wait_until="networkidle")
        page.wait_for_timeout(500)

        # 1. Test each of the 4 Presets
        print("[2/8] Testing all 4 presets...")
        presets = page.locator(".btn-preset").all()
        assert len(presets) == 4, f"Expected 4 presets, got {len(presets)}"
        for idx, btn in enumerate(presets):
            label = btn.text_content().strip()
            print(f"  -> Testing preset {idx+1}: {label}")
            btn.click()
            page.wait_for_timeout(300)
            page.locator("#btnSubmit").click()
            page.wait_for_timeout(800)
            risk_tier = page.locator("#badgeRiskTier").text_content().strip()
            assert risk_tier in ["Low Risk", "Moderate Risk", "High Risk", "Critical / Very High Risk"], f"Unexpected risk tier: {risk_tier}"

        # 2. Test What-If Sliders
        print("[3/8] Testing What-If interactive sliders...")
        page.locator("#tabBtn-whatif").click()
        page.wait_for_timeout(400)
        
        # Test SBP slider
        sbp_slider = page.locator("#sliderSbp")
        assert sbp_slider.is_visible()
        sbp_slider.fill("120")
        page.wait_for_timeout(400)
        assert page.locator("#valSbp").text_content().strip() == "120.0"

        # Test Glucose slider
        glu_slider = page.locator("#sliderGlucose")
        assert glu_slider.is_visible()
        glu_slider.fill("95")
        page.wait_for_timeout(400)
        assert page.locator("#valGlucose").text_content().strip() == "95.0"

        # Test Smoking toggle
        never_smoke_btn = page.locator('#smokeSeg .smoke-btn[data-val="never smoked"]')
        if never_smoke_btn.is_visible():
            never_smoke_btn.click()
            page.wait_for_timeout(500)
            assert "active" in (never_smoke_btn.get_attribute("class") or "")

        # Check simulated risk delta updated
        cf_drop = page.locator("#cfDropSummary")
        assert cf_drop.is_visible()
        assert "Simulated risk" in cf_drop.text_content()

        # 3. Test Cohort Batch Screening with sample data
        print("[4/8] Testing Cohort Batch Screening with built-in sample...")
        page.locator("#tabBtn-batch").click()
        page.wait_for_timeout(400)
        page.locator("#btnRunBatch").click()
        page.wait_for_timeout(2000)

        batch_total = page.locator("#batchTotal").text_content().strip()
        assert batch_total == "25", f"Expected 25 patients screened, got {batch_total}"
        import re
        high_cnt = int(re.search(r'\d+', page.locator("#batchHigh").text_content().strip()).group(0))
        mod_cnt = int(re.search(r'\d+', page.locator("#batchMod").text_content().strip()).group(0))
        low_cnt = int(re.search(r'\d+', page.locator("#batchLow").text_content().strip()).group(0))
        assert high_cnt + mod_cnt + low_cnt == 25, f"Sum mismatch: {high_cnt}+{mod_cnt}+{low_cnt} != 25"

        rows = page.locator("#batchTableBody tr").count()
        assert rows == 25, f"Expected 25 table rows, got {rows}"

        # 4. Test Custom CSV Upload
        print("[5/8] Testing Cohort CSV File Upload...")
        csv_content = (
            "age,gender,hypertension,systolic_bp,heart_disease,ever_married,work_type,residence_type,avg_glucose_level,bmi,smoking_status\n"
            "62,Female,1,160,0,Yes,Private,Urban,180,29.5,formerly smoked\n"
            "45,Male,0,120,0,Yes,Govt_job,Rural,85,24.0,never smoked\n"
            "75,Male,1,185,1,Yes,Self-employed,Urban,240,32.1,smokes\n"
        )
        page.set_input_files("#batchFileInput", {
            "name": "custom_cohort.csv",
            "mimeType": "text/csv",
            "buffer": csv_content.encode("utf-8")
        })
        page.wait_for_timeout(2000)
        custom_total = page.locator("#batchTotal").text_content().strip()
        assert custom_total == "3", f"Expected 3 patients screened from custom CSV, got {custom_total}"
        assert page.locator("#batchTableBody tr").count() == 3

        # 5. Test Benchmarks Tab & Visual Consistency
        print("[6/8] Testing Benchmarks Tab & Kaggle Model Consistency...")
        page.locator("#tabBtn-benchmarks").click()
        page.wait_for_timeout(400)
        
        # Check KPI cards
        kpis = page.locator(".kpi-card").all()
        assert len(kpis) >= 4, f"Expected at least 4 KPI cards, got {len(kpis)}"
        kpi_text = page.locator("#kpiRow").text_content()
        assert "CatBoost (Kaggle cohort)" in kpi_text or "Task 1 ROC-AUC" in kpi_text
        assert "0.8402" in kpi_text

        # 6. Test Kaggle Tab
        print("[7/8] Testing Kaggle Framework Tab...")
        page.locator("#tabBtn-kaggle").click()
        page.wait_for_timeout(400)
        assert page.locator("h3", has_text="Stage 2 & 5: held-out test cohort results").is_visible()
        assert page.locator("h3", has_text="Stage 5: subgroup demographic audit").is_visible()
        assert page.locator("h3", has_text="Stage 5: decision-curve analysis").is_visible()

        # 7. Test Export Clinical Audit & Download
        print("[8/8] Testing Export Clinical Audit Modal & Download Button...")
        page.locator("#tabBtn-assessment").click()
        page.wait_for_timeout(300)
        page.locator("#btnReport").click()
        page.wait_for_selector("#reportModal:not(.hidden)", timeout=5000)
        
        modal = page.locator("#reportModal")
        assert modal.is_visible()
        assert page.locator("#reportPatientGrid .report-cell").count() == 8
        assert page.locator("#reportPredGrid .report-cell").count() == 3
        assert page.locator("#reportShapBody tr").count() == 6

        # Download button assertion
        dl_btn = page.locator("#btnDownloadAudit")
        assert dl_btn.is_visible()
        assert dl_btn.get_attribute("href") == "/api/download/clinical-report"
        
        # Close modal
        page.locator("#btnCloseReport").click()
        page.wait_for_timeout(300)
        assert not modal.is_visible()

        # Assert no console errors
        assert len(console_errors) == 0, f"Observed console errors: {console_errors}"
        print(">>> ALL DEEP INTEGRATION CHECKS PASSED WITH 0 ERRORS! <<<")
        browser.close()

if __name__ == "__main__":
    test_deep_checks()
