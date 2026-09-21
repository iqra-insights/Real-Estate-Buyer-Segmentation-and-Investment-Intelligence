"""Minimal stand-in for plotly.graph_objects, covering go.Figure/go.Bar/go.Pie
as used by Real_Estate_Buyer_Intelligence_Dashboard.py."""


class Bar:
    def __init__(self, y=None, x=None, **k):
        self.y, self.x = y, x


class Pie:
    def __init__(self, labels=None, values=None, **k):
        assert labels is not None and values is not None
        assert len(list(labels)) == len(list(values)), "Pie(): labels/values length mismatch"


class Figure:
    def __init__(self, data=None, **k):
        self._traces = [data] if data is not None else []

    def add_trace(self, trace, **k):
        self._traces.append(trace)
        return self

    def add_annotation(self, *a, **k): return self
    def update_layout(self, *a, **k): return self
    def update_traces(self, *a, **k): return self
    def update_xaxes(self, *a, **k): return self
    def update_yaxes(self, *a, **k): return self
