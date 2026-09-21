"""Minimal stand-in for the streamlit API surface used by Real_Estate_Buyer_Intelligence_Dashboard.py, so the
app's actual data-flow logic can be executed and checked for exceptions
without the real streamlit package (no network access to pip install it)."""

class StopScript(Exception):
    pass

class _Col:
    def metric(self, label, value, *a, **k):
        _metric_log.append((label, value))
    def subheader(self, *a, **k): pass
    def dataframe(self, *a, **k): pass
    def plotly_chart(self, *a, **k): pass
    def markdown(self, *a, **k): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False

class _Sidebar:
    def __init__(self):
        self._radio_value = None
        self._multiselect_values = {}
    def title(self, *a, **k): pass
    def caption(self, *a, **k): pass
    def markdown(self, *a, **k): pass
    def metric(self, *a, **k): pass
    def multiselect(self, label, options=None, **k):
        return self._multiselect_values.get(label, [])
    def radio(self, label, options, **k):
        return self._radio_value if self._radio_value is not None else options[0]

sidebar = _Sidebar()

def set_page_config(*a, **k): pass
def title(*a, **k): pass
def header(*a, **k): pass
def subheader(*a, **k): pass
def markdown(text="", *a, **k):
    _markdown_log.append(text)

_markdown_log = []
def dataframe(*a, **k): pass
def plotly_chart(*a, **k): pass
def image(*a, **k): pass
def info(*a, **k): pass
def success(*a, **k): pass
def warning(*a, **k): pass
def error(*a, **k): pass
def caption(*a, **k): pass
def metric(label, value, *a, **k):
    _metric_log.append((label, value))

_metric_log = []

_radio_override = {}
def radio(label, options, **k):
    if label in _radio_override:
        return _radio_override[label]
    return options[0]

_selectbox_override = {}
def selectbox(label, options, **k):
    if label in _selectbox_override:
        return _selectbox_override[label]
    return options[0]

def stop():
    raise StopScript("st.stop() called")

def columns(spec):
    n = spec if isinstance(spec, int) else len(spec)
    return [_Col() for _ in range(n)]

def cache_data(func=None, **kwargs):
    # Support both @st.cache_data and @st.cache_data(...)
    if func is not None and callable(func):
        return func
    def decorator(f):
        return f
    return decorator

def write(*a, **k): pass
def text_input(label, **k): return ""
def download_button(*a, **k): pass
def cache_resource(func=None, **kwargs):
    if func is not None and callable(func): return func
    def decorator(f): return f
    return decorator
