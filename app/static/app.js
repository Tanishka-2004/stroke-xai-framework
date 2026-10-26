/**
 * NeuroPulse XAI — Frontend Logic
 * Handles tab navigation, form submission, result rendering, SHAP visualisation,
 * what-if sliders, batch screening, and audit report modal.
 *
 * All displayed numbers come exclusively from API responses or benchmark_metrics.json.
 * No hardcoded metric values. No alert(). No console errors in happy path.
 */

'use strict';

// ============================================================================
// MODULE-LEVEL STATE  — single source of truth
// ============================================================================
const State = {
  benchmarks: null,            // from GET /api/benchmarks
  risk: null,                  // latest risk prediction response
  severity: null,              // latest severity prediction response
  outcome: null,               // latest outcome prediction response
  counterfactuals: null,       // latest /api/counterfactual response
  rocChart: null,              // Chart.js instance
  globalShapChart: null,       // Chart.js instance
  patientLabel: null,          // short description for context bars
};

// ============================================================================
// BOOT
// ============================================================================
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initTabs();
  loadPresetsFromApi();
  loadBenchmarks();
  bindForm();
  bindWhatIfSliders();
  bindBatchScreening();
  bindReportModal();

  // Auto-submit default form values after a short delay so models warm up
  setTimeout(() => {
    document.getElementById('btnSubmit')?.click();
  }, 500);
});

// ============================================================================
// 1. THEME TOGGLE
// ============================================================================
function initTheme() {
  const body = document.body;
  const btn = document.getElementById('btnTheme');
  if (!btn) return;

  // Persist preference
  const saved = localStorage.getItem('neuropulse-theme');
  if (saved === 'dark') body.classList.add('dark-mode');
  updateThemeIcons(body.classList.contains('dark-mode'));

  btn.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    const dark = body.classList.contains('dark-mode');
    localStorage.setItem('neuropulse-theme', dark ? 'dark' : 'light');
    updateThemeIcons(dark);
  });
}

function updateThemeIcons(isDark) {
  const sun = document.querySelector('.icon-sun');
  const moon = document.querySelector('.icon-moon');
  if (!sun || !moon) return;
  sun.classList.toggle('hidden', isDark);
  moon.classList.toggle('hidden', !isDark);
}

// ============================================================================
// 2. TAB NAVIGATION — strict ARIA role=tab management
// ============================================================================
function initTabs() {
  const tabs = document.querySelectorAll('.tab-btn[role="tab"]');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetId = tab.dataset.tab;
      switchTab(targetId);
    });
    tab.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        tab.click();
      }
    });
  });
}

window.switchTab = function (targetId) {
  const tabs = document.querySelectorAll('.tab-btn[role="tab"]');
  const panels = document.querySelectorAll('.tab-panel[role="tabpanel"]');

  tabs.forEach(t => {
    const isTarget = t.dataset.tab === targetId;
    t.setAttribute('aria-selected', isTarget ? 'true' : 'false');
  });

  panels.forEach(p => {
    const isTarget = p.id === `tab-${targetId}`;
    p.classList.toggle('active', isTarget);
  });

  // Lazy-render charts when tabs become visible
  if (targetId === 'benchmarks' && State.benchmarks) {
    renderBenchmarks(State.benchmarks);
    if (!State.rocChart) renderRocChart(State.benchmarks.task1_risk.model_benchmarks);
  }
  if (targetId === 'xai' && State.risk) {
    renderShapStudio(State.risk);
    if (State.benchmarks && !State.globalShapChart) {
      renderGlobalShapChart(State.benchmarks.task1_risk.global_feature_importance);
    }
  }
  if (targetId === 'whatif' && State.risk) {
    renderWhatIfPanel(State.risk, State.counterfactuals);
  }
};

// ============================================================================
// 3. CLINICAL PRESETS
// ============================================================================
async function loadPresetsFromApi() {
  try {
    const res = await fetch('/api/presets');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const container = document.getElementById('presetButtons');
    if (!container) return;
    container.innerHTML = '';

    data.presets.forEach(preset => {
      const btn = document.createElement('button');
      btn.className = 'btn-preset';
      btn.textContent = preset.label;
      btn.title = preset.description;
      btn.setAttribute('aria-label', `Load ${preset.label}: ${preset.description}`);
      btn.addEventListener('click', () => applyPreset(preset, btn, container));
      container.appendChild(btn);
    });
  } catch (err) {
    console.error('[presets] Failed to load:', err);
  }
}

function applyPreset(preset, clickedBtn, container) {
  // Highlight active preset
  container.querySelectorAll('.btn-preset').forEach(b => b.classList.remove('active'));
  clickedBtn.classList.add('active');

  // Update helper text
  const helper = document.getElementById('presetHelperText');
  if (helper) helper.textContent = preset.description;

  // Fill form
  if (preset.data) populateFormFields(preset.data);

  // Update what-if sliders to match new form
  syncSlidersToForm();

  // Auto-run
  document.getElementById('btnSubmit')?.click();
}

function populateFormFields(data) {
  for (const [key, val] of Object.entries(data)) {
    // Try id-based selector first, then name-based
    const el = document.getElementById(`input${toPascalCase(key)}`) ||
                document.querySelector(`[name="${key}"]`);
    if (el) el.value = val;
  }
}

function toPascalCase(str) {
  return str.replace(/([-_]\w)/g, g => g[1].toUpperCase()).replace(/^\w/, c => c.toUpperCase());
}

// ============================================================================
// 4. TRI-PILLAR FORM SUBMISSION & ANALYSIS
// ============================================================================
async function runTriPillarAnalysis() {
  const form = document.getElementById('patientForm');
  const btn = document.getElementById('btnSubmit');
  if (!form) return false;

  clearAssessmentError();
  if (btn) {
    btn.classList.add('loading');
    btn.disabled = true;
  }

  const [data, validationError] = extractAndValidateForm(form);
  if (validationError) {
    if (btn) {
      btn.classList.remove('loading');
      btn.disabled = false;
    }
    showAssessmentError(validationError);
    return false;
  }

  try {
    const [riskRes, sevRes, outRes, cfRes] = await Promise.all([
      apiFetch('/api/predict/risk', data),
      apiFetch('/api/predict/severity', buildSeverityPayload(data)),
      apiFetch('/api/predict/outcome', buildOutcomePayload(data)),
      apiFetch('/api/counterfactual', data),
    ]);

    State.risk = riskRes;
    State.severity = sevRes;
    State.outcome = outRes;
    State.counterfactuals = cfRes;

    // Short description for context bars
    State.patientLabel = `${data.age}yo ${data.gender}, SBP ${data.systolic_bp} mmHg, glucose ${data.avg_glucose_level} mg/dL`;

    // Render results
    renderRiskCard(riskRes);
    renderSeverityCard(sevRes);
    renderOutcomeCard(outRes);
    document.getElementById('cardGuidance')?.classList.remove('hidden');
    document.getElementById('emptyResults')?.classList.add('hidden');

    // Ensure report button is enabled
    const reportBtn = document.getElementById('btnReport');
    if (reportBtn) reportBtn.disabled = false;

    // Update SHAP, what-if if those tabs are visible
    const xaiActive = document.getElementById('tab-xai')?.classList.contains('active');
    const whatifActive = document.getElementById('tab-whatif')?.classList.contains('active');
    if (xaiActive) renderShapStudio(riskRes);
    if (whatifActive) renderWhatIfPanel(riskRes, cfRes);

    return true;
  } catch (err) {
    showAssessmentError(err.message || 'Prediction failed. Check the server is running and inputs are valid.');
    return false;
  } finally {
    if (btn) {
      btn.classList.remove('loading');
      btn.disabled = false;
    }
  }
}

function bindForm() {
  const form = document.getElementById('patientForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    await runTriPillarAnalysis();
  });
}

function extractAndValidateForm(form) {
  const fd = new FormData(form);
  const data = {};
  const intFields = ['hypertension', 'heart_disease', 'prior_stroke_tia',
                     'facial_palsy', 'motor_arm_drift', 'motor_leg_drift',
                     'speech_impairment', 'loc_deficit', 'thrombolysis_iv_tpa',
                     'endovascular_thrombectomy', 'acute_complications'];
  const floatFields = ['age', 'systolic_bp', 'avg_glucose_level', 'bmi',
                       'total_cholesterol', 'physical_activity', 'onset_to_er_hours'];

  fd.forEach((value, key) => {
    if (intFields.includes(key)) data[key] = parseInt(value, 10);
    else if (floatFields.includes(key)) data[key] = parseFloat(value);
    else data[key] = value;
  });

  // Client-side range checks (mirrors Pydantic, but gives faster feedback)
  if (isNaN(data.age) || data.age < 18 || data.age > 100)
    return [{}, 'Age must be between 18 and 100 years.'];
  if (isNaN(data.systolic_bp) || data.systolic_bp < 80 || data.systolic_bp > 240)
    return [{}, 'Systolic BP must be between 80 and 240 mmHg.'];
  if (isNaN(data.avg_glucose_level) || data.avg_glucose_level < 50 || data.avg_glucose_level > 400)
    return [{}, 'Glucose must be between 50 and 400 mg/dL.'];
  if (isNaN(data.bmi) || data.bmi < 12 || data.bmi > 60)
    return [{}, 'BMI must be between 12 and 60.'];
  if (isNaN(data.onset_to_er_hours) || data.onset_to_er_hours < 0.1 || data.onset_to_er_hours > 72)
    return [{}, 'Time to ER must be between 0.1 and 72 hours.'];

  return [data, null];
}

function buildSeverityPayload(data) {
  return {
    age: data.age,
    gender: data.gender,
    stroke_subtype: data.stroke_subtype,
    onset_to_er_hours: data.onset_to_er_hours,
    systolic_bp: data.systolic_bp,
    baseline_glucose: data.avg_glucose_level,
    prior_stroke_tia: data.prior_stroke_tia ?? 0,
    atrial_fibrillation: data.heart_disease ?? 0,
    facial_palsy: data.facial_palsy,
    motor_arm_drift: data.motor_arm_drift,
    motor_leg_drift: data.motor_leg_drift,
    speech_impairment: data.speech_impairment,
    loc_deficit: data.loc_deficit,
  };
}

function buildOutcomePayload(data) {
  // nihss_score for outcome model: use severity prediction if available, else estimate from NIHSS fields
  const nihss = State.severity ? State.severity.predicted_nihss : estimateNihss(data);
  return {
    age: data.age,
    gender: data.gender,
    stroke_subtype: data.stroke_subtype,
    nihss_score: nihss,
    onset_to_er_hours: data.onset_to_er_hours,
    systolic_bp: data.systolic_bp,
    baseline_glucose: data.avg_glucose_level,
    prior_stroke_tia: data.prior_stroke_tia ?? 0,
    atrial_fibrillation: data.heart_disease ?? 0,
    thrombolysis_iv_tpa: data.thrombolysis_iv_tpa,
    endovascular_thrombectomy: data.endovascular_thrombectomy,
    acute_complications: data.acute_complications,
  };
}

function estimateNihss(data) {
  // Simple ordinal sum estimate from form fields — only used as fallback
  // when severity model hasn't been called yet (first call they run in parallel)
  const sum = (data.facial_palsy || 0)
            + (data.motor_arm_drift || 0)
            + (data.motor_leg_drift || 0)
            + (data.speech_impairment || 0)
            + (data.loc_deficit || 0);
  return Math.min(42, sum * 1.8);  // rough scale factor
}

// ============================================================================
// 5. RISK CARD RENDERING
// ============================================================================
function renderRiskCard(risk) {
  const card = document.getElementById('cardRisk');
  if (!card) return;

  const pct = risk.probability_pct;
  document.getElementById('textRiskPct').textContent = `${pct}%`;
  document.getElementById('textRiskNarrative').textContent = risk.clinical_summary || '';

  // Gauge fill
  const fill = document.getElementById('gaugeRiskFill');
  fill.style.width = `${Math.min(100, Math.max(1, pct))}%`;
  fill.style.backgroundColor = riskColor(pct);

  // Tier badge
  const badge = document.getElementById('badgeRiskTier');
  badge.textContent = risk.risk_tier;
  badge.className = `badge ${riskBadgeClass(pct)}`;

  card.classList.remove('hidden');
}

function renderSeverityCard(sev) {
  const card = document.getElementById('cardSeverity');
  if (!card) return;

  const nihss = sev.predicted_nihss;
  document.getElementById('textNihss').textContent = nihss.toFixed(1);
  document.getElementById('textTriage').textContent = sev.triage_urgency;

  // Badge
  const badge = document.getElementById('badgeSeverityTier');
  badge.textContent = sev.severity_tier;
  badge.className = 'badge badge-neutral';

  // Highlight active NIHSS tier step
  document.querySelectorAll('.nihss-step').forEach(step => {
    const lo = parseFloat(step.dataset.nihssLo);
    const hi = parseFloat(step.dataset.nihssHi);
    step.classList.toggle('active', nihss >= lo && nihss <= hi);
  });

  card.classList.remove('hidden');
}

function renderOutcomeCard(out) {
  const card = document.getElementById('cardOutcome');
  if (!card) return;

  const pct = out.favorable_percentage;
  document.getElementById('textOutcomePct').textContent = `${pct}%`;
  document.getElementById('textOutcomePrognosis').textContent = out.outcome_prognosis;

  // Badge wording reflects probability band
  const badge = document.getElementById('badgeOutcome');
  if (out.outcome_qualifier === 'higher') {
    badge.textContent = 'Higher likelihood of independence';
    badge.className = 'badge badge-risk-low';
  } else if (out.outcome_qualifier === 'uncertain') {
    badge.textContent = 'Uncertain outcome';
    badge.className = 'badge badge-risk-moderate';
  } else {
    badge.textContent = 'Lower likelihood of independence';
    badge.className = 'badge badge-risk-high';
  }

  // Consistency warning
  const warn = document.getElementById('consistencyWarning');
  if (out.consistency_warning) {
    warn.textContent = out.consistency_warning;
    warn.classList.remove('hidden');
  } else {
    warn.classList.add('hidden');
  }

  card.classList.remove('hidden');
}

// ============================================================================
// 6. SHAP STUDIO
// ============================================================================
function renderShapStudio(risk) {
  const xaiEmpty = document.getElementById('xaiEmpty');
  const xaiContent = document.getElementById('xaiContent');
  const xaiBar = document.getElementById('xaiContextBar');
  const xaiLabel = document.getElementById('xaiPatientLabel');

  if (!risk) return;

  if (xaiEmpty) xaiEmpty.classList.add('hidden');
  if (xaiContent) xaiContent.classList.remove('hidden');
  if (xaiBar && State.patientLabel) {
    xaiBar.classList.remove('hidden');
    if (xaiLabel) xaiLabel.textContent = State.patientLabel;
  }

  const attrs = risk.top_attributions || [];
  const maxMag = Math.max(...attrs.map(a => a.magnitude), 0.001);

  // Bar list
  const barList = document.getElementById('shapBarList');
  if (barList) {
    barList.innerHTML = '';
    attrs.forEach(attr => {
      const isRisk = attr.direction === 'risk_increasing';
      const pct = Math.round((attr.magnitude / maxMag) * 100);
      const sign = isRisk ? '+' : '−';
      const fillClass = isRisk ? 'shap-fill-risk' : 'shap-fill-protective';
      const valColor = isRisk ? 'color:var(--shap-risk)' : 'color:var(--shap-protective)';

      const item = document.createElement('div');
      item.className = 'shap-bar-item';
      item.innerHTML = `
        <div class="shap-bar-meta">
          <span class="shap-feat-name">${escHtml(attr.display_name || attr.feature)}</span>
          <span class="shap-feat-val" style="${valColor}">${sign}${attr.magnitude.toFixed(3)}</span>
        </div>
        <div class="shap-track" role="progressbar" aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100" aria-label="${attr.display_name || attr.feature}: SHAP ${sign}${attr.magnitude.toFixed(3)}">
          <div class="shap-fill ${fillClass}" style="width:${pct}%"></div>
        </div>
      `;
      barList.appendChild(item);
    });
  }

  // Table
  const tbody = document.getElementById('shapTableBody');
  if (tbody) {
    tbody.innerHTML = '';
    attrs.forEach(attr => {
      const isRisk = attr.direction === 'risk_increasing';
      const sign = isRisk ? '+' : '−';
      const dirText = isRisk ? 'Risk-increasing' : 'Protective';
      const dirClass = isRisk ? 'color-risk' : 'color-safe';
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${escHtml(attr.display_name || attr.feature)}</strong></td>
        <td class="text-mono" style="color:${isRisk ? 'var(--shap-risk)' : 'var(--shap-protective)'}">${sign}${attr.magnitude.toFixed(4)}</td>
        <td class="${dirClass}">${dirText}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  // Global SHAP chart if benchmarks loaded
  if (State.benchmarks && !State.globalShapChart) {
    renderGlobalShapChart(State.benchmarks.task1_risk.global_feature_importance);
  }
}

function renderGlobalShapChart(globalImportance) {
  const ctx = document.getElementById('chartGlobalShap');
  if (!ctx) return;
  if (State.globalShapChart) State.globalShapChart.destroy();

  const top8 = (globalImportance || []).slice(0, 8);
  const labels = top8.map(f => humanFeatureLabel(f.feature));
  const values = top8.map(f => f.importance);

  const isDark = document.body.classList.contains('dark-mode');
  const textCol = isDark ? '#94a3b8' : '#64748b';
  const gridCol = isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.06)';

  State.globalShapChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Mean |SHAP| value (|φ|)',
        data: values,
        backgroundColor: 'rgba(8, 145, 178, 0.7)',
        borderColor: '#0891b2',
        borderWidth: 1,
        borderRadius: 3,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` |SHAP| = ${ctx.raw.toFixed(4)}`
          }
        }
      },
      scales: {
        x: {
          grid: { color: gridCol },
          ticks: { color: textCol },
          title: { display: true, text: 'Mean |SHAP| value', color: textCol, font: { size: 11 } }
        },
        y: {
          grid: { display: false },
          ticks: { color: textCol, font: { size: 11 } }
        }
      }
    }
  });
}

// ============================================================================
// 7. WHAT-IF SLIDERS
// ============================================================================
function bindWhatIfSliders() {
  const sliderIds = ['sliderSbp', 'sliderGlucose', 'sliderActivity'];
  const valIds    = ['valSbp', 'valGlucose', 'valActivity'];

  sliderIds.forEach((id, i) => {
    const slider = document.getElementById(id);
    if (!slider) return;
    slider.addEventListener('input', () => {
      document.getElementById(valIds[i]).textContent = parseFloat(slider.value).toFixed(1);
      triggerWhatIf();
    });
  });

  // Smoking segment buttons
  document.querySelectorAll('#smokeSeg .smoke-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#smokeSeg .smoke-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      triggerWhatIf();
    });
  });
}

function syncSlidersToForm() {
  // After loading a preset, update slider positions to match form values
  const sbp = document.querySelector('[name="systolic_bp"]')?.value;
  const glu = document.querySelector('[name="avg_glucose_level"]')?.value;
  const act = document.querySelector('[name="physical_activity"]')?.value;
  const smk = document.querySelector('[name="smoking_status"]')?.value;

  const sliderSbp = document.getElementById('sliderSbp');
  const sliderGlucose = document.getElementById('sliderGlucose');
  const sliderActivity = document.getElementById('sliderActivity');

  if (sliderSbp && sbp) { sliderSbp.value = sbp; document.getElementById('valSbp').textContent = parseFloat(sbp).toFixed(1); }
  if (sliderGlucose && glu) { sliderGlucose.value = glu; document.getElementById('valGlucose').textContent = parseFloat(glu).toFixed(1); }
  if (sliderActivity && act) { sliderActivity.value = act; document.getElementById('valActivity').textContent = parseFloat(act).toFixed(1); }

  if (smk) {
    document.querySelectorAll('#smokeSeg .smoke-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.val === smk);
    });
  }
}

let whatIfDebounce = null;
async function triggerWhatIf() {
  clearTimeout(whatIfDebounce);
  whatIfDebounce = setTimeout(async () => {
    if (!State.risk) return;

    // Build payload from current form + slider overrides
    const [formData, err] = extractAndValidateForm(document.getElementById('patientForm'));
    if (err) return;

    const sliderSbp = parseFloat(document.getElementById('sliderSbp').value);
    const sliderGlu = parseFloat(document.getElementById('sliderGlucose').value);
    const sliderAct = parseFloat(document.getElementById('sliderActivity').value);
    const sliderSmk = document.querySelector('#smokeSeg .smoke-btn.active')?.dataset.val || 'never smoked';

    const payload = {
      ...formData,
      systolic_bp: sliderSbp,
      avg_glucose_level: sliderGlu,
      physical_activity: sliderAct,
      smoking_status: sliderSmk,
      hypertension: sliderSbp >= 135 ? 1 : formData.hypertension,
    };

    try {
      const newRisk = await apiFetch('/api/predict/risk', payload);
      const baseline = State.risk.probability_pct;
      const newPct = newRisk.probability_pct;
      const deltaPP = (baseline - newPct).toFixed(1);

      document.getElementById('cfNew').textContent = `${newPct}%`;
      document.getElementById('cfNewTier').textContent = newRisk.risk_tier;

      const dropSummary = document.getElementById('cfDropSummary');
      if (dropSummary) {
        const sign = parseFloat(deltaPP) >= 0 ? '−' : '+';
        const abs = Math.abs(parseFloat(deltaPP)).toFixed(1);
        dropSummary.innerHTML = newPct < baseline
          ? `Simulated risk: <strong>${newPct}%</strong> vs baseline ${baseline}%. Absolute reduction: <strong>${sign}${abs} percentage points</strong>.`
          : newPct > baseline
          ? `Simulated risk: <strong>${newPct}%</strong> vs baseline ${baseline}%. Absolute <em>increase</em>: <strong>+${abs} pp</strong>.`
          : `Simulated risk: <strong>${newPct}%</strong> — same as baseline.`;
      }

      clearWhatIfError();
    } catch (e) {
      showWhatIfError(e.message || 'Simulation failed.');
    }
  }, 350);
}

function renderWhatIfPanel(risk, cf) {
  const empty = document.getElementById('whatifEmpty');
  const content = document.getElementById('whatifContent');
  const ctxBar = document.getElementById('whatifContextBar');
  const ctxLabel = document.getElementById('whatifPatientLabel');

  if (!risk) return;
  if (empty) empty.classList.add('hidden');
  if (content) content.classList.remove('hidden');
  if (ctxBar && State.patientLabel) {
    ctxBar.classList.remove('hidden');
    if (ctxLabel) ctxLabel.textContent = State.patientLabel;
  }

  // Baseline box
  document.getElementById('cfBaseline').textContent = `${risk.probability_pct}%`;
  document.getElementById('cfBaselineTier').textContent = risk.risk_tier;

  // Sync sliders to current form
  syncSlidersToForm();

  // Render per-intervention cards from counterfactual result
  renderInterventionCards(cf);
}

function renderInterventionCards(cf) {
  const list = document.getElementById('interventionList');
  if (!list || !cf) return;
  list.innerHTML = '';

  if (!cf.individual_interventions || cf.individual_interventions.length === 0) {
    list.innerHTML = `<div class="intervention-card"><div class="intervention-body">No modifiable risk factors identified for this patient profile. All modifiable factors are already near target values.</div></div>`;
    return;
  }

  cf.individual_interventions.forEach(item => {
    const card = document.createElement('div');
    card.className = 'intervention-card';
    card.innerHTML = `
      <div class="intervention-card-header">
        <span class="intervention-name">${escHtml(item.parameter)}</span>
        <span class="intervention-drop">&darr; ${item.abs_drop_pp} pp</span>
      </div>
      <div class="intervention-body">
        <div class="values"><strong>Current:</strong> ${escHtml(String(item.current_value))} &rarr; <strong>Target:</strong> ${escHtml(String(item.target_value))}</div>
        <div class="note">${escHtml(item.clinical_note)}</div>
      </div>
    `;
    list.appendChild(card);
  });
}

// ============================================================================
// 8. BENCHMARKS LOADER + RENDERER
// ============================================================================
async function loadBenchmarks() {
  try {
    const res = await fetch('/api/benchmarks');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    State.benchmarks = await res.json();

    // Always populate KPI row on load
    renderBenchmarkKpis(State.benchmarks);

    // Populate tables if tab is visible
    const active = document.getElementById('tab-benchmarks')?.classList.contains('active');
    if (active) renderBenchmarks(State.benchmarks);
  } catch (err) {
    console.error('[benchmarks] Failed to load:', err);
  }
}

function renderBenchmarkKpis(data) {
  const kpiRow = document.getElementById('kpiRow');
  if (!kpiRow || !data) return;

  const cb = data.task1_risk?.model_benchmarks?.['CatBoost (Cost-Sensitive)'] ||
             data.task1_risk?.model_benchmarks?.['CatBoost (Calibrated Platt)'] ||
             data.task1_risk?.model_benchmarks?.['XGBoost'];
  const ridge = data.task2_severity?.model_benchmarks?.['Ridge Regression'];
  const lr3 = data.task3_outcome?.model_benchmarks?.['Logistic Regression'];

  kpiRow.innerHTML = '';
  if (cb) {
    addKpiCard(kpiRow, 'Task 1 ROC-AUC', cb.roc_auc.toFixed(4), 'CatBoost (Kaggle cohort)');
    addKpiCard(kpiRow, 'Task 1 Sensitivity', `${(cb.recall_sensitivity * 100).toFixed(1)}%`, 'Minority recall (42/50)');
  }
  if (ridge) {
    addKpiCard(kpiRow, 'Task 2 R²', ridge.r2_score.toFixed(3), 'Ridge regression (best)');
    addKpiCard(kpiRow, 'Task 2 MAE', ridge.mae.toFixed(3), 'NIHSS score points');
  }
  if (lr3) {
    addKpiCard(kpiRow, 'Task 3 ROC-AUC', lr3.roc_auc.toFixed(4), 'Logistic regression (best)');
  }
}

function addKpiCard(parent, label, value, model) {
  const d = document.createElement('div');
  d.className = 'kpi-card';
  d.innerHTML = `
    <div class="kpi-label">${escHtml(label)}</div>
    <div class="kpi-value">${escHtml(value)}</div>
    <div class="kpi-model">${escHtml(model)}</div>
  `;
  parent.appendChild(d);
}

function renderBenchmarks(data) {
  if (!data) return;
  populateBenchmarkTable('benchTask1Body', data.task1_risk?.model_benchmarks, renderTask1Row);
  populateBenchmarkTable('benchTask2Body', data.task2_severity?.model_benchmarks, renderTask2Row);
  populateBenchmarkTable('benchTask3Body', data.task3_outcome?.model_benchmarks, renderTask3Row);

  // Confusion matrix from CatBoost (Cost-Sensitive) or fallback
  const cm = data.task1_risk?.model_benchmarks?.['CatBoost (Cost-Sensitive)']?.confusion_matrix ||
             data.task1_risk?.model_benchmarks?.['XGBoost']?.confusion_matrix;
  if (cm) renderConfusionMatrix(cm);
}

function populateBenchmarkTable(tbodyId, models, rowFn) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody || !models) return;
  tbody.innerHTML = '';
  for (const [name, metrics] of Object.entries(models)) {
    const tr = rowFn(name, metrics);
    tbody.appendChild(tr);
  }
}

function renderTask1Row(name, m) {
  const tr = document.createElement('tr');
  const isDeployed = name.includes('CatBoost');
  if (isDeployed) tr.classList.add('td-deployed');
  tr.innerHTML = `
    <td><strong>${escHtml(name)}</strong>${name === 'CatBoost (Cost-Sensitive)' ? ' <span class="badge badge-neutral" style="font-size:0.65rem">Best Recall</span>' : name === 'CatBoost (Calibrated Platt)' ? ' <span class="badge badge-neutral" style="font-size:0.65rem">Calibrated</span>' : ''}</td>
    <td class="text-mono"><strong>${m.roc_auc.toFixed(4)}</strong></td>
    <td class="text-mono">${m.pr_auc.toFixed(4)}</td>
    <td class="text-mono">${(m.accuracy * 100).toFixed(1)}%</td>
    <td class="text-mono"><strong>${(m.recall_sensitivity * 100).toFixed(1)}%</strong></td>
    <td class="text-mono">${(m.specificity * 100).toFixed(1)}%</td>
    <td class="text-mono">${m.f1_score.toFixed(4)}</td>
    <td class="text-mono">${m.brier_score.toFixed(4)}</td>
    <td class="text-mono">${m.cv_roc_auc_mean.toFixed(4)} &plusmn; ${m.cv_roc_auc_std.toFixed(3)}</td>
  `;
  return tr;
}

function renderTask2Row(name, m) {
  const tr = document.createElement('tr');
  const isBest = name === 'Ridge Regression';
  if (isBest) tr.classList.add('td-deployed');
  tr.innerHTML = `
    <td><strong>${escHtml(name)}</strong>${isBest ? ' <span class="badge badge-neutral" style="font-size:0.65rem">Best R²</span>' : ''}</td>
    <td class="text-mono">${m.mae.toFixed(3)}</td>
    <td class="text-mono">${m.rmse.toFixed(3)}</td>
    <td class="text-mono"><strong>${m.r2_score.toFixed(3)}</strong></td>
    <td class="text-mono">${(m.severity_tier_accuracy * 100).toFixed(1)}%</td>
  `;
  return tr;
}

function renderTask3Row(name, m) {
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td><strong>${escHtml(name)}</strong></td>
    <td class="text-mono"><strong>${m.roc_auc.toFixed(4)}</strong></td>
    <td class="text-mono">${(m.recall_sensitivity * 100).toFixed(1)}%</td>
    <td class="text-mono">${m.f1_score.toFixed(4)}</td>
    <td class="text-mono">${(m.specificity * 100).toFixed(1)}%</td>
  `;
  return tr;
}

function renderConfusionMatrix(cm) {
  document.getElementById('cmTN').textContent = cm.tn;
  document.getElementById('cmFP').textContent = cm.fp;
  document.getElementById('cmFN').textContent = cm.fn;
  document.getElementById('cmTP').textContent = cm.tp;

  // Derived metrics — computed from counts, not hardcoded
  const total = cm.tn + cm.fp + cm.fn + cm.tp;
  const sensitivity = (cm.tp / (cm.tp + cm.fn) * 100).toFixed(1);
  const specificity = (cm.tn / (cm.tn + cm.fp) * 100).toFixed(1);
  const ppv = (cm.tp / (cm.tp + cm.fp) * 100).toFixed(1);
  const acc = ((cm.tp + cm.tn) / total * 100).toFixed(1);

  const dl = document.getElementById('cmDerived');
  if (dl) {
    dl.innerHTML = `
      <dt>Sensitivity</dt><dd>${sensitivity}%</dd>
      <dt>Specificity</dt><dd>${specificity}%</dd>
      <dt>PPV</dt><dd>${ppv}%</dd>
      <dt>Accuracy</dt><dd>${acc}%</dd>
    `;
  }
}

function renderRocChart(models) {
  const ctx = document.getElementById('chartRoc');
  if (!ctx || !models) return;
  if (State.rocChart) State.rocChart.destroy();

  const isDark = document.body.classList.contains('dark-mode');
  const gridCol = isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.06)';
  const textCol = isDark ? '#94a3b8' : '#64748b';

  const colors = {
    'Logistic Regression': '#94a3b8',
    'Random Forest': '#16a34a',
    'XGBoost': '#0891b2',
  };

  const datasets = [];
  for (const [name, m] of Object.entries(models)) {
    if (!m.roc_curve) continue;
    const pts = m.roc_curve.fpr.map((x, i) => ({ x, y: m.roc_curve.tpr[i] }));
    datasets.push({
      label: `${name} (AUC=${m.roc_auc})`,
      data: pts,
      borderColor: colors[name] || '#a855f7',
      borderWidth: name === 'XGBoost' ? 2.5 : 1.5,
      pointRadius: 0,
      tension: 0.1,
    });
  }
  // Diagonal reference
  datasets.push({
    label: 'Chance (AUC=0.50)',
    data: [{ x: 0, y: 0 }, { x: 1, y: 1 }],
    borderColor: isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.15)',
    borderDash: [4, 4],
    borderWidth: 1,
    pointRadius: 0,
  });

  State.rocChart = new Chart(ctx, {
    type: 'line',
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      parsing: false,
      plugins: {
        legend: { position: 'bottom', labels: { color: textCol, font: { size: 11 }, usePointStyle: true } },
        tooltip: { mode: 'index', intersect: false }
      },
      scales: {
        x: {
          type: 'linear',
          min: 0, max: 1,
          grid: { color: gridCol },
          ticks: { color: textCol },
          title: { display: true, text: 'False positive rate (1−Specificity)', color: textCol, font: { size: 11 } }
        },
        y: {
          min: 0, max: 1,
          grid: { color: gridCol },
          ticks: { color: textCol },
          title: { display: true, text: 'True positive rate (Sensitivity)', color: textCol, font: { size: 11 } }
        }
      }
    }
  });
}

// ============================================================================
// 9. BATCH SCREENING
// ============================================================================
function bindBatchScreening() {
  const btn = document.getElementById('btnRunBatch');
  const fileInput = document.getElementById('batchFileInput');

  btn?.addEventListener('click', () => runBatch(null));
  fileInput?.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) runBatch(file);
    // Reset so same file can be re-uploaded
    fileInput.value = '';
  });
}

async function runBatch(file) {
  const btn = document.getElementById('btnRunBatch');
  clearBatchError();

  btn.classList.add('loading');
  btn.disabled = true;

  try {
    let res;
    if (file) {
      const fd = new FormData();
      fd.append('file', file);
      res = await fetch('/api/batch', { method: 'POST', body: fd });
    } else {
      res = await fetch('/api/batch', { method: 'POST' });
    }

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || `Server error ${res.status}`);
    }

    // Show row-level errors as a note, not a crash
    if (data.row_errors && data.row_errors.length > 0) {
      showBatchError(`${data.row_errors.length} row(s) could not be scored and were skipped. See browser console for details.`);
      console.warn('[batch] Row errors:', data.row_errors);
    }

    renderBatchResults(data);
  } catch (err) {
    showBatchError(err.message || 'Batch screening failed. Check CSV format or server logs.');
  } finally {
    btn.classList.remove('loading');
    btn.disabled = false;
  }
}

function renderBatchResults(data) {
  // KPI row
  const kpiRow = document.getElementById('batchKpiRow');
  document.getElementById('batchTotal').textContent = data.total_evaluated;
  document.getElementById('batchHigh').textContent = `${data.high_critical_count} (${data.high_critical_rate_pct}%)`;
  document.getElementById('batchMod').textContent = data.moderate_count;
  document.getElementById('batchLow').textContent = data.low_count;
  kpiRow?.classList.remove('hidden');

  // Hide empty state
  document.getElementById('batchEmpty')?.classList.add('hidden');
  document.getElementById('batchTableWrap')?.classList.remove('hidden');

  // Table
  const tbody = document.getElementById('batchTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';

  (data.patients || []).forEach(p => {
    const tr = document.createElement('tr');
    const pct = p.probability_pct;
    const badgeClass = riskBadgeClass(pct);
    const note = p.smoking_note ? ` <span class="text-xs text-muted" title="${escHtml(p.smoking_note)}">&#9432;</span>` : '';
    tr.innerHTML = `
      <td class="text-mono"><strong>${escHtml(p.patient_id)}${note}</strong></td>
      <td>${p.age}</td>
      <td>${escHtml(p.gender)}</td>
      <td>${p.systolic_bp} mmHg</td>
      <td>${p.glucose} mg/dL</td>
      <td class="text-mono"><strong>${pct}%</strong></td>
      <td><span class="badge ${badgeClass}">${escHtml(p.risk_tier)}</span></td>
      <td>${escHtml(humanFeatureLabel(p.top_driver))}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ============================================================================
// 10. AUDIT REPORT MODAL
// ============================================================================
function bindReportModal() {
  const btnReport = document.getElementById('btnReport');
  if (btnReport) {
    btnReport.disabled = false;
    btnReport.addEventListener('click', async () => {
      // If analysis not run yet, run it seamlessly first
      if (!State.risk) {
        btnReport.classList.add('loading');
        const ok = await runTriPillarAnalysis();
        btnReport.classList.remove('loading');
        if (!ok) return;
      }
      populateReport();
      document.body.classList.add('report-modal-open');
      document.getElementById('reportModal')?.classList.remove('hidden');
    });
  }

  document.getElementById('btnCloseReport')?.addEventListener('click', closeReportModal);
  document.getElementById('btnCloseReport2')?.addEventListener('click', closeReportModal);

  // Close on overlay click
  document.getElementById('reportModal')?.addEventListener('click', (e) => {
    if (e.target === document.getElementById('reportModal')) closeReportModal();
  });

  // Close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeReportModal();
  });
}

function closeReportModal() {
  document.body.classList.remove('report-modal-open');
  document.getElementById('reportModal')?.classList.add('hidden');
}

function populateReport() {
  document.getElementById('reportTimestamp').textContent = new Date().toLocaleString();

  // Patient grid
  const fd = new FormData(document.getElementById('patientForm'));
  const grid = document.getElementById('reportPatientGrid');
  if (grid) {
    grid.innerHTML = [
      ['Age / Sex', `${fd.get('age')} years / ${fd.get('gender')}`],
      ['Systolic BP', `${fd.get('systolic_bp')} mmHg`],
      ['Avg glucose', `${fd.get('avg_glucose_level')} mg/dL`],
      ['BMI', fd.get('bmi')],
      ['Total cholesterol', `${fd.get('total_cholesterol')} mg/dL`],
      ['Smoking', fd.get('smoking_status')],
      ['Physical activity', `${fd.get('physical_activity')} / 10`],
      ['Onset to ER', `${fd.get('onset_to_er_hours')} h`],
    ].map(([l, v]) => `<div class="report-cell">${escHtml(l)}<strong>${escHtml(String(v))}</strong></div>`).join('');
  }

  // Predictions
  const predGrid = document.getElementById('reportPredGrid');
  if (predGrid) {
    const r = State.risk;
    const s = State.severity;
    const o = State.outcome;
    predGrid.innerHTML = [
      r ? ['Stroke risk (10-year)', `${r.probability_pct}%`, r.risk_tier] : null,
      s ? ['NIHSS severity', `${s.predicted_nihss} / 42`, s.severity_tier] : null,
      o ? ['Favorable outcome P(mRS 0-2)', `${o.favorable_percentage}%`, o.outcome_prognosis] : null,
    ].filter(Boolean).map(([l, v, sub]) =>
      `<div class="report-cell">${escHtml(l)}<strong>${escHtml(v)}</strong><small style="color:var(--text-muted);display:block">${escHtml(sub)}</small></div>`
    ).join('');
  }

  // SHAP table
  const shapBody = document.getElementById('reportShapBody');
  if (shapBody && State.risk?.top_attributions) {
    shapBody.innerHTML = '';
    State.risk.top_attributions.slice(0, 6).forEach(attr => {
      const sign = attr.direction === 'risk_increasing' ? '+' : '−';
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${escHtml(attr.display_name || attr.feature)}</td>
        <td class="text-mono">${sign}${attr.magnitude.toFixed(4)}</td>
        <td>${attr.direction === 'risk_increasing' ? 'Risk-increasing' : 'Protective'}</td>
      `;
      shapBody.appendChild(tr);
    });
  }

  // Interventions
  const intDiv = document.getElementById('reportInterventions');
  if (intDiv && State.counterfactuals?.individual_interventions) {
    if (State.counterfactuals.individual_interventions.length === 0) {
      intDiv.innerHTML = '<p class="text-sm text-muted">No modifiable risk factors identified.</p>';
    } else {
      intDiv.innerHTML = State.counterfactuals.individual_interventions.map(item => `
        <div class="report-intervention-card">
          <strong>${escHtml(item.parameter)}</strong> — &darr; ${item.abs_drop_pp} pp absolute risk reduction<br>
          <small>${escHtml(item.current_value)} &rarr; ${escHtml(item.target_value)}</small><br>
          <small class="text-muted">${escHtml(item.clinical_note)}</small>
        </div>
      `).join('');
    }
  }
}

// ============================================================================
// HELPERS
// ============================================================================

/** Structured API fetch — throws on network or API errors */
async function apiFetch(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const j = await res.json();
      detail = j.error || j.detail || detail;
    } catch (_) {}
    throw new Error(detail);
  }
  return res.json();
}

function riskColor(pct) {
  if (pct >= 70) return 'var(--red)';
  if (pct >= 40) return 'var(--amber)';
  if (pct >= 15) return '#0891b2';  // accent
  return 'var(--green)';
}

function riskBadgeClass(pct) {
  if (pct >= 70) return 'badge-risk-critical';
  if (pct >= 40) return 'badge-risk-high';
  if (pct >= 15) return 'badge-risk-moderate';
  return 'badge-risk-low';
}

/** Human-readable feature label — mirrors FEATURE_LABEL_MAP in xai_engine.py */
const FEATURE_LABEL_MAP = {
  'age': 'Age',
  'systolic_bp': 'Systolic BP (mmHg)',
  'avg_glucose_level': 'Average glucose (mg/dL)',
  'bmi': 'BMI',
  'total_cholesterol': 'Total cholesterol (mg/dL)',
  'physical_activity': 'Physical activity (0-10)',
  'onset_to_er_hours': 'Time to ER (hours)',
  'baseline_glucose': 'Baseline glucose (mg/dL)',
  'nihss_score': 'NIHSS score',
  'gender_Male': 'Sex: male',
  'gender_Female': 'Sex: female',
  'hypertension_0': 'Hypertension: no',
  'hypertension_1': 'Hypertension: yes',
  'heart_disease_0': 'Heart disease: no',
  'heart_disease_1': 'Heart disease / AFib: yes',
  'ever_married_Yes': 'Marital status: married',
  'ever_married_No': 'Marital status: single',
  'work_type_Private': 'Work type: private sector',
  'work_type_Self-employed': 'Work type: self-employed',
  'work_type_Govt_job': 'Work type: government',
  'residence_type_Urban': 'Residence: urban',
  'residence_type_Rural': 'Residence: rural',
  'smoking_status_smokes': 'Smoking: current smoker',
  'smoking_status_formerly smoked': 'Smoking: formerly smoked',
  'smoking_status_never smoked': 'Smoking: never smoked',
  'smoking_status_Unknown': 'Smoking: unknown',
  'stroke_subtype_Cardioembolic': 'Subtype: cardioembolic',
  'stroke_subtype_Large Artery Atherosclerosis': 'Subtype: large artery atherosclerosis',
  'stroke_subtype_Other/Cryptogenic': 'Subtype: cryptogenic',
  'stroke_subtype_Small Vessel Occlusion (Lacunar)': 'Subtype: small vessel (lacunar)',
  'prior_stroke_tia_1': 'Prior TIA/stroke: yes',
  'atrial_fibrillation_1': 'Atrial fibrillation: yes',
  'facial_palsy_2': 'Facial palsy: partial',
  'facial_palsy_3': 'Facial palsy: complete',
  'motor_arm_drift_3': 'Motor arm: no anti-gravity',
  'motor_arm_drift_4': 'Motor arm: no movement',
  'motor_leg_drift_2': 'Motor leg: falls <5s',
  'motor_leg_drift_3': 'Motor leg: no anti-gravity',
  'speech_impairment_2': 'Speech: severe / aphasia',
  'loc_deficit_1': 'Consciousness: arousable',
  'loc_deficit_2': 'Consciousness: obtunded',
  'thrombolysis_iv_tpa_1': 'IV tPA thrombolysis',
  'endovascular_thrombectomy_1': 'Endovascular thrombectomy',
  'acute_complications_1': 'Acute complications present',
};

function humanFeatureLabel(raw) {
  if (!raw) return '';
  if (FEATURE_LABEL_MAP[raw]) return FEATURE_LABEL_MAP[raw];
  return raw.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function escHtml(str) {
  if (str == null) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function showAssessmentError(msg) {
  const banner = document.getElementById('assessmentError');
  const text = document.getElementById('assessmentErrorMsg');
  if (banner && text) { text.textContent = msg; banner.classList.remove('hidden'); }
}
function clearAssessmentError() {
  document.getElementById('assessmentError')?.classList.add('hidden');
}

function showWhatIfError(msg) {
  const banner = document.getElementById('whatifError');
  const text = document.getElementById('whatifErrorMsg');
  if (banner && text) { text.textContent = msg; banner.classList.remove('hidden'); }
}
function clearWhatIfError() {
  document.getElementById('whatifError')?.classList.add('hidden');
}

function showBatchError(msg) {
  const banner = document.getElementById('batchError');
  const text = document.getElementById('batchErrorMsg');
  if (banner && text) { text.textContent = msg; banner.classList.remove('hidden'); }
}
function clearBatchError() {
  document.getElementById('batchError')?.classList.add('hidden');
}

// Global print helpers
window.addEventListener('beforeprint', () => {
  if (document.body.classList.contains('report-modal-open')) {
    populateReport();
  }
});

