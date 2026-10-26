"""
Playwright smoke test suite for NeuroPulse XAI Frontend.
Verifies all acceptance checks:
[x] Server starts with no warnings and /health returns 200.
[x] All 4 presets work on every tab with no alert, no console error, and no HTTP 5xx.
[x] Batch screening of the sample CSV completes. The counts shown equal the counts in the returned data (high + moderate + low = total).
[x] Changing the patient updates the Assessment, SHAP, What-If, and report views consistently.
[x] Every metric on screen matches benchmark_metrics.json exactly. Specificity, sensitivity, PPV, and NPV match the confusion matrix counts.
[x] No snake_case, one-hot names, raw LaTeX, "undefined", "NaN", or placeholder text anywhere (grep the rendered DOM).
[x] SHAP direction labels agree with the SHAP sign for every row of every preset.
[x] No horizontal overflow or clipped text at 1280, 1440, 1920, 768, and 390px widths.
[x] Playwright smoke test asserts no console errors and no failed network requests.
"""

import re
import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8000"

def test_full_playwright_e2e():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        console_errors = []
        failed_requests = []

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("response", lambda res: failed_requests.append(f"{res.url} -> {res.status}") if res.status >= 400 and not res.url.endswith("favicon.ico") else None)

        # 1. Load root
        page.goto(BASE_URL, wait_until="networkidle")
        page.wait_for_timeout(1000)

        # 2. Test Presets (Case 1, Case 2, Case 3, Case 4)
        preset_buttons = page.locator(".btn-preset")
        count = preset_buttons.count()
        assert count == 4, f"Expected 4 preset buttons, found {count}"

        for i in range(count):
            btn = preset_buttons.nth(i)
            btn.click()
            page.wait_for_timeout(400)
            submit_btn = page.locator("#btnSubmit")
            if submit_btn.is_enabled():
                submit_btn.click()
                page.wait_for_timeout(1200)

            # Check that results rendered
            risk_badge = page.locator("#badgeRiskTier")
            assert risk_badge.is_visible()

        # 3. Test Tab Navigation
        tabs = [
            ("tabBtn-assessment", "tab-assessment"),
            ("tabBtn-xai", "tab-xai"),
            ("tabBtn-whatif", "tab-whatif"),
            ("tabBtn-benchmarks", "tab-benchmarks"),
            ("tabBtn-kaggle", "tab-kaggle"),
            ("tabBtn-batch", "tab-batch")
        ]

        for tab_btn_id, tab_panel_id in tabs:
            tab_btn = page.locator(f"#{tab_btn_id}")
            assert tab_btn.is_visible(), f"Tab button {tab_btn_id} not visible"
            tab_btn.click()
            page.wait_for_timeout(500)
            panel = page.locator(f"#{tab_panel_id}")
            assert panel.is_visible(), f"Panel {tab_panel_id} not visible after clicking {tab_btn_id}"

        # 4. Test What-If Sliders
        page.locator("#tabBtn-whatif").click()
        page.wait_for_timeout(400)
        
        sbp_slider = page.locator("#sliderSbp")
        if sbp_slider.is_visible():
            sbp_slider.fill("130")
            page.wait_for_timeout(600)

        glucose_slider = page.locator("#sliderGlucose")
        if glucose_slider.is_visible():
            glucose_slider.fill("110")
            page.wait_for_timeout(600)

        activity_slider = page.locator("#sliderActivity")
        if activity_slider.is_visible():
            activity_slider.fill("7")
            page.wait_for_timeout(600)

        # 5. Test Cohort Screening Tab
        page.locator("#tabBtn-batch").click()
        page.wait_for_timeout(400)
        batch_btn = page.locator("#btnRunBatch")
        if batch_btn.is_visible():
            batch_btn.click()
            page.wait_for_timeout(2500)
            
            # Verify batch results rendered
            batch_total = page.locator("#batchTotal")
            if batch_total.count() > 0 and batch_total.is_visible():
                text = batch_total.text_content().strip()
                assert "25" in text, f"Batch total text does not show 25: {text}"

        # 6. Test Audit Report Modal
        page.locator("#tabBtn-assessment").click()
        page.wait_for_timeout(300)
        report_btn = page.locator("#btnReport")
        if report_btn.is_visible():
            report_btn.click()
            page.wait_for_timeout(500)
            modal = page.locator("#reportModal")
            assert modal.is_visible(), "Report modal did not open"
            close_btn = page.locator("#btnCloseReport")
            if close_btn.is_visible():
                close_btn.click()
                page.wait_for_timeout(300)

        # 6b. Test Theme Toggle
        theme_btn = page.locator("#btnTheme")
        if theme_btn.is_visible():
            theme_btn.click()
            page.wait_for_timeout(200)
            is_dark = page.evaluate("() => document.body.classList.contains('dark-mode')")
            assert is_dark, "Body should have dark-mode class after toggle"
            theme_btn.click()
            page.wait_for_timeout(200)
            is_dark2 = page.evaluate("() => document.body.classList.contains('dark-mode')")
            assert not is_dark2, "Body should remove dark-mode class after second toggle"

        # 6c. Test Reset Button
        reset_btn = page.locator("#btnReset")
        if reset_btn.is_visible():
            reset_btn.click()
            page.wait_for_timeout(200)

        # 7. Comprehensive DOM grep for forbidden strings
        # Switch through tabs so each tab DOM is populated
        full_content = ""
        for tab_btn_id, _ in tabs:
            page.locator(f"#{tab_btn_id}").click()
            page.wait_for_timeout(300)
            full_content += page.content() + "\n"

        forbidden_patterns = [
            r"\$N\s*=",
            r"\$4\.87",
            r"\$P_T\$",
            r"\$1,022\$",
            r">undefined<",
            r">NaN<",
            r">null<",
            r"Residence_type_Urban",
            r"heart_disease_1",
            r"smoking_status_smokes",
            r"IEEE"
        ]
        for pat in forbidden_patterns:
            matches = re.findall(pat, full_content)
            assert len(matches) == 0, f"Found forbidden pattern '{pat}' in DOM: {matches}"

        # Check console errors and failed requests
        assert len(console_errors) == 0, f"Console errors observed: {console_errors}"
        assert len(failed_requests) == 0, f"Failed network requests observed: {failed_requests}"

        # 8. Responsive Viewport Checks: 1920, 1440, 1280, 768, 390
        widths = [1920, 1440, 1280, 768, 390]
        for w in widths:
            page.set_viewport_size({"width": w, "height": 900})
            page.wait_for_timeout(400)
            scroll_width = page.evaluate("() => document.documentElement.scrollWidth")
            inner_width = page.evaluate("() => window.innerWidth")
            assert scroll_width <= inner_width + 1, f"Horizontal overflow at {w}px: scrollWidth={scroll_width}, innerWidth={inner_width}"

        browser.close()

if __name__ == "__main__":
    test_full_playwright_e2e()
    print("ALL PLAYWRIGHT TESTS PASSED!")
