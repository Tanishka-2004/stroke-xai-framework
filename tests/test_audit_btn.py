from playwright.sync_api import sync_playwright
import time

def test_export_clinical_audit():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        print("Navigating to http://127.0.0.1:8000/ ...")
        page.goto("http://127.0.0.1:8000/", wait_until="networkidle")

        # Verify no IEEE download buttons or links anywhere on the page
        ieee_elements = page.locator("text='IEEE'").all()
        print(f"IEEE text elements found: {len(ieee_elements)}")
        for el in ieee_elements:
            print("Found text:", el.text_content())
        assert len(ieee_elements) == 0, f"Found unexpected IEEE elements: {len(ieee_elements)}"

        # Check export clinical audit button
        btn_report = page.locator("#btnReport")
        assert btn_report.is_visible(), "#btnReport should be visible"
        assert btn_report.is_enabled(), "#btnReport should be enabled"

        # Click Export Clinical Audit directly
        print("Clicking #btnReport...")
        btn_report.click()

        # Wait for modal to open
        page.wait_for_selector("#reportModal:not(.hidden)", timeout=5000)
        modal = page.locator("#reportModal")
        assert modal.is_visible(), "Modal should be visible after clicking #btnReport"

        # Verify modal content is fully populated
        patient_grid = page.locator("#reportPatientGrid .report-cell")
        assert patient_grid.count() > 0, "Patient grid should have cells"
        print(f"Patient grid cells: {patient_grid.count()}")

        pred_grid = page.locator("#reportPredGrid .report-cell")
        assert pred_grid.count() > 0, "Prediction grid should have cells"
        print(f"Prediction grid cells: {pred_grid.count()}")

        shap_rows = page.locator("#reportShapBody tr")
        assert shap_rows.count() > 0, "SHAP table should have rows"
        print(f"SHAP table rows: {shap_rows.count()}")

        # Check modal footer buttons: should have Print Clinical Audit and Download Audit PDF, but NO IEEE
        footer_text = page.locator("#reportModal .modal-footer").inner_text()
        print("Modal footer text:", footer_text)
        assert "IEEE" not in footer_text, "Modal footer must not mention IEEE"
        assert "Print Clinical Audit" in footer_text, "Should have Print Clinical Audit"
        assert "Download Audit PDF" in footer_text, "Should have Download Audit PDF"

        # Take screenshot of the opened modal
        page.screenshot(path="audit_modal_verified.png")
        print("Screenshot saved to audit_modal_verified.png")

        assert len(console_errors) == 0, f"Console errors: {console_errors}"
        print("ALL AUDIT BUTTON & NO-IEEE CHECKS PASSED!")
        browser.close()

if __name__ == "__main__":
    test_export_clinical_audit()
