"""Executable Streamlit smoke + regression tests using lightweight local stubs.

Run with: pytest -q tests/01_Dashboard_Logic_Tests.py

Two kinds of coverage here:
1. Smoke tests (test_dashboard_smoke_suite) - every page/segment/filter
   combination executes without raising. This catches crashes.
2. Value-based regression tests - assert that filtering/selecting actually
   CHANGES the displayed numbers, not just that nothing crashed. This is
   the class of check that would have caught two real bugs found during
   review (Segment Insights ignoring sidebar filters; the Buyer
   Segmentation "Focus on a segment" selector not filtering its charts) -
   neither of those bugs raised an exception, they silently showed wrong
   numbers, so a smoke test alone would have passed on both.
"""
import runpy
import sys
import traceback
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests" / "stubs"))

import streamlit as st  # noqa: E402

APP_PATH = ROOT / "app" / "Real_Estate_Buyer_Intelligence_Dashboard.py"
PAGES = [
    "Executive Overview", "Buyer Segmentation", "Geographic Intelligence",
    "Investment Profiling", "Segment Insights", "Customer Explorer", "Model Information",
]
SEGMENTS = [
    "Value-Conscious Home Buyers", "High-Volume / Frequent Buyers",
    "Premium / High-Value Buyers", "Corporate Buyers",
]


@pytest.fixture
def master_df():
    return pd.read_csv(ROOT / "data" / "processed" / "Buyer_Segmentation_Results.csv")


@pytest.fixture(autouse=True)
def reset_stub_state():
    st.sidebar._radio_value = None
    st.sidebar._multiselect_values = {}
    st._selectbox_override = {}
    st._radio_override = {}
    st._metric_log.clear()
    st._markdown_log.clear()
    yield


def run_once(page, segment=None, multiselects=None, radio_overrides=None):
    st.sidebar._radio_value = page
    st.sidebar._multiselect_values = multiselects or {}
    st._selectbox_override = {"Focus on a segment": "All", "Focus on a segment (optional)": "All",
                               "Select a segment": segment or SEGMENTS[0]}
    st._radio_override = radio_overrides or {}
    try:
        runpy.run_path(str(APP_PATH), run_name="__main__")
        return "OK"
    except st.StopScript:
        return "OK (st.stop reached - empty filter)"
    except Exception as exc:
        traceback.print_exc()
        return f"FAIL: {type(exc).__name__}: {exc}"


def as_int(metric_value):
    return int(str(metric_value).replace(",", ""))


def get_metric(label):
    return dict(st._metric_log).get(label)


def get_kpi(label):
    """Parse a KPI card's value out of the raw HTML this app renders via
    st.markdown() (custom .kpi divs), since this Real_Estate_Buyer_Intelligence_Dashboard.py doesn't use the
    native st.metric() widget at all for its KPI cards."""
    import re
    pattern = re.compile(
        rf'<div class="kpi-label">{re.escape(label)}</div><div class="kpi-value">([^<]*)</div>'
    )
    for text in st._markdown_log:
        m = pattern.search(text)
        if m:
            return m.group(1)
    return None


# ---------------------------------------------------------------------------
# Smoke suite (unchanged coverage from the original test, kept as-is)
# ---------------------------------------------------------------------------
def test_dashboard_smoke_suite():
    results = []
    for page in PAGES:
        results.append((page, run_once(page)))
    for seg in SEGMENTS:
        results.append((f"Segment Insights / {seg}", run_once("Segment Insights", segment=seg)))
    results.extend([
        ("Executive filtered", run_once("Executive Overview", multiselects={"Country": ["USA"], "Client Type": ["Individual"]})),
        ("Buyer Segmentation filtered", run_once("Buyer Segmentation", multiselects={"Buyer Segment": ["Corporate Buyers"]})),
        ("Geographic filtered", run_once("Geographic Intelligence", multiselects={"Acquisition Purpose": ["Investment"]})),
        ("Investment filtered", run_once("Investment Profiling", multiselects={"Region": []})),
        ("Zero-result handling", run_once("Executive Overview", multiselects={"Country": ["USA"], "Client Type": ["Company"], "Buyer Segment": ["Value-Conscious Home Buyers"]})),
    ])
    for metric in ["Client count", "Investment rate", "Avg total spend"]:
        results.append((f"Geographic / {metric}", run_once("Geographic Intelligence", radio_overrides={"Map metric": metric})))

    failures = [(name, status) for name, status in results if status.startswith("FAIL")]
    assert not failures, f"Dashboard smoke failures: {failures}"
    assert len(results) == 19


# ---------------------------------------------------------------------------
# Value-based regression tests
# ---------------------------------------------------------------------------
def test_segment_insights_zero_result_stops_cleanly():
    """Selecting a segment with zero rows under the current filters must
    show the empty-state message and stop, not crash on an empty-slice NaN."""
    st.sidebar._radio_value = "Segment Insights"
    st.sidebar._multiselect_values = {"Client Type": ["Individual"]}
    st._selectbox_override = {"Select a segment": "Corporate Buyers"}
    with pytest.raises(st.StopScript):
        runpy.run_path(str(APP_PATH), run_name="__main__")


def test_segment_insights_respects_sidebar_filters(master_df):
    """Filtering by this segment's dominant country must strictly reduce
    the 'Segment Size' KPI shown on the Segment Insights page."""
    full_corp_size = len(master_df[master_df["segment_name"] == "Corporate Buyers"])
    top_country = master_df[master_df["segment_name"] == "Corporate Buyers"]["country"].mode()[0]

    run_once("Segment Insights", segment="Corporate Buyers", multiselects={"Country": [top_country]})
    filtered_size = as_int(get_kpi("Segment Size"))

    assert filtered_size < full_corp_size, (
        f"Segment Insights is not respecting the Country filter "
        f"(got {filtered_size}, expected < {full_corp_size})"
    )


def test_buyer_segmentation_selector_actually_filters(monkeypatch):
    """'Focus on a segment' must change which segment(s) appear in the
    Segment Landscape chart, not just render identically regardless of
    the selector's value."""
    captured = {}
    original_groupby = pd.DataFrame.groupby

    def spy_groupby(self, by, *a, **k):
        if by == "segment_name":
            captured["segments_seen"] = sorted(set(self["segment_name"]))
        return original_groupby(self, by, *a, **k)

    monkeypatch.setattr(pd.DataFrame, "groupby", spy_groupby)

    st.sidebar._radio_value = "Buyer Segmentation"
    st.sidebar._multiselect_values = {}
    st._selectbox_override = {"Focus on a segment": "All"}
    runpy.run_path(str(APP_PATH), run_name="__main__")
    all_segments = captured.get("segments_seen")

    st._selectbox_override = {"Focus on a segment": "Corporate Buyers"}
    runpy.run_path(str(APP_PATH), run_name="__main__")
    focused_segments = captured.get("segments_seen")

    assert focused_segments == ["Corporate Buyers"], (
        f"'Focus on a segment' selector is not filtering the segment landscape chart "
        f"(got {focused_segments})"
    )
    assert all_segments != focused_segments


def test_geographic_choropleth_uses_iso3_not_raw_country_names():
    """Regression guard: the choropleth must map to explicit ISO-3 codes
    rather than passing raw country strings ('USA'/'UK') to Plotly's
    'country names' locationmode, which is not guaranteed to resolve
    abbreviations and can silently drop countries off the map."""
    code_lines = [line for line in APP_PATH.read_text(encoding="utf-8").splitlines()
                  if not line.strip().startswith("#")]
    code_only = "\n".join(code_lines)
    assert 'locationmode="country names"' not in code_only, (
        "Real_Estate_Buyer_Intelligence_Dashboard.py still uses locationmode='country names' with raw country "
        "strings in actual code - switch to explicit ISO-3 codes (see ISO3 dict in Real_Estate_Buyer_Intelligence_Dashboard.py)"
    )
    assert 'locationmode="ISO-3"' in code_only
