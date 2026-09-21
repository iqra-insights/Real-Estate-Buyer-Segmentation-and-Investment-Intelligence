# Streamlit App Verification

## What was NOT possible
This sandbox has no network egress (confirmed via `curl` returning
"Host not in allowlist"), so neither `streamlit`/`plotly` nor `pytest`
itself can be installed here. The app has never been visually rendered
with a real `streamlit run`, and the test suite below has never been run
under the real `pytest`.

## What WAS done instead
1. **`app/Real_Estate_Buyer_Intelligence_Dashboard.py`** is executed for real (not just read/reviewed) via
   minimal stand-in modules (`tests/stubs/streamlit.py`,
   `tests/stubs/plotly/express.py`) that mimic the real APIs' call
   signatures closely enough to catch data-flow bugs: KeyErrors, bad
   column references, wrong crosstab/groupby shapes.
2. **`tests/01_Dashboard_Logic_Tests.py`** is a genuine `pytest` test file
   (fixtures, `monkeypatch`, `pytest.raises`) — this is the file to run
   once you have network access:
   ```
   pip install pytest
   pytest tests/01_Dashboard_Logic_Tests.py -v
   ```
3. Until then, **`tests/Run_Offline_Tests.py`** runs that *exact same file*
   through `tests/stubs/pytest_offline_shim.py`, a small compatibility
   shim implementing just enough of pytest's API to execute it. Only the
   runner is a stand-in — the test file itself is unmodified and portable.

## Results (via the offline shim)
**5 test functions pass, 0 failed:**

- `test_dashboard_smoke_suite` — 19 sub-scenarios in one assertion: all 7
  dashboard pages unfiltered (Executive Overview, Buyer Segmentation,
  Geographic Intelligence, Investment Profiling, Segment Insights,
  Customer Explorer, Model Information), Segment Insights for all 4
  segments, 4 different filter combinations, the zero-result filter case,
  and the Geographic choropleth for all 3 map-metric options.
- `test_segment_insights_zero_result_stops_cleanly` — a segment/filter
  combination with zero matching clients hits `st.stop()` cleanly rather
  than crashing on an empty-slice `.mean()` producing NaN.
- `test_segment_insights_respects_sidebar_filters` — **value-based**
  regression test: asserts the "Segment Size" KPI for Corporate Buyers
  strictly *decreases* when a country filter is applied. (Regression
  guard for a real bug found during review: `seg_df_filtered` was
  computed but never used, so this number never changed regardless of
  sidebar filters.)
- `test_buyer_segmentation_selector_actually_filters` — **value-based**
  regression test: asserts that switching "Focus on a segment" from
  "All" to "Corporate Buyers" actually changes which segment(s) appear
  in the page's charts, by spying on `groupby("segment_name")` calls.
  (Regression guard for a real bug: the selector was computed but every
  chart used the unfiltered dataframe instead, making it a no-op.)
- `test_geographic_choropleth_uses_iso3_not_raw_country_names` —
  regression guard asserting the choropleth uses explicit ISO-3 codes,
  not `locationmode="country names"` with raw strings like "USA"/"UK",
  which is not guaranteed to resolve abbreviations and can silently drop
  countries off the map with no error.

The last three tests check actual output values or code structure, not
just "no exception was raised" — the two regression-guarded bugs would
not have raised exceptions either; they silently showed wrong numbers.

## What this does NOT prove
- Real Streamlit widget behavior (session state across reruns, exact
  layout/CSS rendering of the dark premium UI)
- Real Plotly chart correctness (i.e., that a chart looks sensible, not
  just that the call didn't raise) — including whether the ISO-3
  choropleth actually renders every country's shading correctly
- Performance at real widget-interaction speed
- That the shim (`pytest_offline_shim.py`) behaves identically to real
  pytest in every edge case — it implements only what
  `01_Dashboard_Logic_Tests.py` actually uses (fixtures incl. autouse, `raises`,
  `monkeypatch`), not the full pytest API

**Recommendation:** run `pip install -r requirements.txt && streamlit
run app/Real_Estate_Buyer_Intelligence_Dashboard.py`, and separately `pip install pytest && pytest
tests/01_Dashboard_Logic_Tests.py -v`, in an environment with network access
before presenting this to stakeholders. Report back any error and it
can be fixed directly against the real traceback.


## Final local runtime verification

The automated suite validates the dashboard logic with offline Streamlit/Plotly stubs. A real Streamlit runtime must still be smoke-tested in the target Windows/Anaconda environment because this repository cannot certify the user's local package installation remotely.

Run from the project root:

```bash
python --version
pip install -r requirements.txt
streamlit run app/Real_Estate_Buyer_Intelligence_Dashboard.py
```

Expected Python version: **3.11+**. In the browser, verify all seven pages load and test the sidebar filters for Country, Region, Acquisition Purpose, Client Type, and Segment. On Segment Insights, verify the new **Recommended Business Action** panel appears. On Geographic Intelligence, verify both the country map and regional concentration chart render.
