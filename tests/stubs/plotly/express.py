"""Minimal stand-in for plotly.express, validating call signatures against
real pandas objects (catches wrong/renamed column names) without the real
plotly package (no network access to pip install it)."""


class _Fig:
    def update_layout(self, *a, **k): return self
    def update_traces(self, *a, **k): return self
    def update_xaxes(self, *a, **k): return self
    def update_yaxes(self, *a, **k): return self
    def add_annotation(self, *a, **k): return self
    def add_trace(self, *a, **k): return self


def _cols(data_frame):
    return list(getattr(data_frame, "columns", []))


def _check(data_frame, **named_args):
    if data_frame is None:
        return
    _ = data_frame.shape if hasattr(data_frame, "shape") else len(data_frame)
    cols = _cols(data_frame)
    index_name = getattr(getattr(data_frame, "index", None), "name", None)
    for argname, val in named_args.items():
        if isinstance(val, str) and cols:
            assert val in cols or val == index_name, (
                f"{argname}='{val}' not found in columns {cols} (or index name)"
            )
        if isinstance(val, dict):
            for key in val:
                assert key in cols, f"{argname} key '{key}' not found in columns {cols}"


def pie(data_frame=None, names=None, values=None, **k):
    _check(data_frame, names=names, values=values)
    return _Fig()


def bar(data_frame=None, x=None, y=None, color=None, text=None, **k):
    _check(data_frame, x=x, y=y, color=color, text=text)
    return _Fig()


def box(data_frame=None, x=None, y=None, color=None, **k):
    _check(data_frame, x=x, y=y, color=color)
    return _Fig()


def violin(data_frame=None, x=None, y=None, color=None, **k):
    return box(data_frame=data_frame, x=x, y=y, color=color, **k)


def scatter(data_frame=None, x=None, y=None, size=None, color=None, hover_data=None, **k):
    _check(data_frame, x=x, y=y, size=size, color=color, hover_data=hover_data)
    return _Fig()


def choropleth(data_frame=None, locations=None, color=None, hover_name=None, hover_data=None, **k):
    _check(data_frame, locations=locations, color=color, hover_name=hover_name, hover_data=hover_data)
    return _Fig()


def imshow(img, **k):
    # img is typically a pandas DataFrame (pivoted matrix) in Real_Estate_Buyer_Intelligence_Dashboard.py's usage
    _ = img.shape if hasattr(img, "shape") else None
    return _Fig()
