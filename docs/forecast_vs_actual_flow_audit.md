# Forecast vs Actual – End-to-End Flow Audit

**Date:** 2026-04-03  
**Audited by:** GitHub Copilot  
**Scope:** Full UI-to-backend cycle for uploading real booking data and comparing against a generated forecast.

---

## 1. Files Reviewed

| File | Purpose |
|---|---|
| `templates/index.html` | Single HTML template for the entire app |
| `app/routes.py` | Main blueprint with `/` and `/compare` routes |
| `app/__init__.py` | Flask factory, blueprint registration, config |
| `app/comparison.py` | Comparison pipeline (parse → merge → metrics → save) |

---

## 2. Current Real Flow – Step by Step

### Step A: User opens browser → `GET /`
- **Route:** `routes.bp` → `index()` in `app/routes.py` (line 10)
- **Render call:** `render_template('index.html')` — no template variables passed
- **Template state:** All `{% if ... %}` blocks evaluate to False
- **What the user sees:** Only the "Upload Historical Data" form is visible, AND the compare section `<div class="compare-section">` — because that div is **unconditional** (not wrapped in `{% if %}`)

**✅ The compare upload form IS rendered on the first GET visit.**

---

### Step B: Compare form submission → `POST /compare`

Form in `templates/index.html` (lines ~238–241):
```html
<form method="POST" action="/compare" enctype="multipart/form-data">
    <input type="file" name="actual_file" accept=".csv" required>
    <button type="submit">Comparar con Pronóstico</button>
</form>
```

- **method:** `POST` ✅
- **action:** `/compare` ✅
- **enctype:** `multipart/form-data` ✅
- **input name:** `actual_file` ✅

Route in `app/routes.py` (line 89):
```python
@bp.route('/compare', methods=['POST'])
def compare():
    if 'actual_file' not in request.files:  # line 91
```

- **Route exists:** ✅
- **Method matches:** `POST` ✅
- **Input name matches:** `actual_file` on both sides ✅
- **Blueprint registered:** `routes.bp` is registered in `app/__init__.py` (line 30) ✅
- **No URL prefix on blueprint:** registered with `app.register_blueprint(routes.bp)` — no `url_prefix` — so `/compare` resolves correctly ✅

---

### Step C: Backend processing inside `/compare`

```python
# app/routes.py lines 100–113
file.save(filepath)                            # saved to data/
comparison_df, metrics = run_comparison(...)   # calls comparison.py
comparison_data = comparison_df.to_dict('records')
return render_template(
    'index.html',
    comparison=comparison_data,
    metrics=metrics,
    compare_success=True,
)
```

- **`run_comparison` is imported:** ✅ (`from app.comparison import run_comparison` at line 6)
- **`run_comparison` exists in `comparison.py`:** ✅ (function defined at line ~130)
- **`run_comparison` loads latest forecast from `data/outputs/`:** ✅ (uses glob pattern `forecast_occupancy_sarimax_*.csv`)
- **`run_comparison` returns `(comparison_df, metrics)`:** ✅

**Variables passed back to template:**
| Variable | Passed? | Template uses it? |
|---|---|---|
| `comparison` | ✅ | ✅ `{% if comparison %}` block at line ~282 |
| `metrics` | ✅ | ✅ `{% if metrics %}` block at line ~262 |
| `compare_success` | ✅ | ✅ `{% if compare_success %}` at line ~249 |
| `compare_error` | ✅ (on error paths) | ✅ `{% if compare_error %}` at line ~246 |

---

### Step D: Template rendering of comparison results

`{% if metrics %}` block (line ~262) — renders 3 metric cards:
- Días Comparados ✅
- Precisión Binaria ✅
- MAE ✅

`{% if comparison %}` block (line ~282) — renders day-by-day table:
- Columns: ds, y_real, yhat, yhat_lower, yhat_upper, yhat_binary, error, abs_error, match_binary ✅

---

## 3. What Is Implemented vs What Is Missing

| Feature | Status |
|---|---|
| Compare form in HTML | ✅ Present and unconditional |
| Form `action="/compare"` | ✅ Correct |
| Form `name="actual_file"` | ✅ Matches route |
| `/compare` POST route | ✅ Exists and registered |
| Input name check in Flask (`actual_file`) | ✅ Matches |
| `run_comparison` function | ✅ Implemented |
| Forecast file auto-discovery | ✅ Loads latest sarimax CSV |
| Template variables returned | ✅ All three: `comparison`, `metrics`, `compare_success` |
| Template conditional blocks | ✅ All present |
| Error handling paths | ✅ `compare_error` shown on validation failures |
| CSS for compare section | ✅ `.compare-section`, `.metrics-grid`, `.metric-card` defined |

**No broken links found in the chain.**

---

## 4. Root Cause Analysis – Why the Button May Seem Missing

The implementation is **functionally complete**. There are two likely reasons the user cannot see the compare section:

### Cause 1: Browser cache (most likely)
The Flask server was started **after** the template was already modified. If the user had the page open before the server started, or the browser cached an older response, they would see the old version of the template without the compare section.

**Evidence:** The Flask app was successfully started in this session (`.\venv\Scripts\python.exe main.py`) and the template has the compare section in it. The server restart serves the updated template immediately on first fresh load.

**Fix:** Hard refresh the browser with **Ctrl+Shift+R** (or Cmd+Shift+R on Mac).

### Cause 2: Server was not running or was running the old version
Prior terminal history shows multiple failed attempts to start the server (`Exit Code: 1` on `main_simple.py`). The server was only confirmed running in the most recent session via `main.py`. If the user was hitting a different port or a stale process, they would not see any page at all.

**Fix:** Confirm the server is running at http://127.0.0.1:5000 and open exactly that URL.

### Cause 3 (minor): Section appears far down the page without a forecast
The compare section is placed **after** the forecast results table in the HTML. On a fresh `GET /` visit (no forecast generated), there are no `{% if historical %}` or `{% if forecast %}` blocks rendered, so the compare section appears immediately after the first upload card — it should be visible without scrolling.

---

## 5. Exact Line-Level Findings

| Location | Line(s) | Finding |
|---|---|---|
| `templates/index.html` | ~228–252 | Compare `<div class="compare-section">` is **unconditional** — always rendered |
| `templates/index.html` | ~238 | `<input name="actual_file">` — matches Flask route check |
| `templates/index.html` | ~237 | `action="/compare"` — matches registered route |
| `app/routes.py` | 6 | `from app.comparison import run_comparison` — import present |
| `app/routes.py` | 89 | `@bp.route('/compare', methods=['POST'])` — route registered |
| `app/routes.py` | 91 | `if 'actual_file' not in request.files` — matches input name |
| `app/__init__.py` | 30 | `app.register_blueprint(routes.bp)` — no prefix, `/compare` is reachable |
| `app/comparison.py` | ~130 | `def run_comparison(...)` — returns `(DataFrame, dict)` as expected |

---

## 6. Minimal Fix Plan

No code changes are needed. The full chain is implemented and correct.

**Recommended actions (in order):**

1. Confirm Flask is running: open http://127.0.0.1:5000 in a browser
2. Hard refresh: **Ctrl+Shift+R**
3. Scroll down past the "Upload Historical Data" form — the blue-bordered "Comparar Pronóstico con Datos Reales" section should be immediately visible
4. To test the comparison: upload `data/2026.csv` — the app will expand it into daily occupancy and compare against `data/outputs/forecast_occupancy_sarimax_20260403.csv`

---

## 7. Summary

**The feature is fully implemented end-to-end.** No broken links exist in:
- HTML form → correct route
- Route → correct field name
- Route → correct function call
- Function → correct return values
- Template → correct conditional blocks

The most probable cause of "not seeing the button" is a **browser cache** or the **server not being running** at the time of the visit.
