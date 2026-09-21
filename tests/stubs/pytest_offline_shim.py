"""
Minimal pytest-API shim, used ONLY because this sandbox has no network
access to `pip install pytest`. It implements just enough of pytest's
surface (fixture, mark.parametrize, raises, monkeypatch, a runner) to
actually EXECUTE tests/01_Dashboard_Logic_Tests.py and prove its assertions pass -
this is not a pytest replacement and tests/01_Dashboard_Logic_Tests.py should be
run with the real `pytest` once it's installable in your environment:

    pip install pytest
    pytest tests/01_Dashboard_Logic_Tests.py -v

Until then:

    python3 tests/Run_Offline_Tests.py
"""
import sys
import inspect
import traceback


class _Mark:
    def parametrize(self, argnames, argvalues):
        def decorator(func):
            names = [n.strip() for n in argnames.split(",")]
            func._parametrize = (names, argvalues)
            return func
        return decorator


mark = _Mark()


class _RaisesContext:
    def __init__(self, exc_type):
        self.exc_type = exc_type
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            raise AssertionError(f"pytest.raises({self.exc_type.__name__}): no exception was raised")
        if not issubclass(exc_type, self.exc_type):
            return False  # let it propagate - wrong exception type
        return True  # suppress the expected exception


def raises(exc_type):
    return _RaisesContext(exc_type)


_fixtures = {}

def fixture(func=None, *, autouse=False):
    def register(f):
        f._is_fixture = True
        f._autouse = autouse
        _fixtures[f.__name__] = f
        return f
    if func is not None:
        return register(func)
    return register


class _Monkeypatch:
    def __init__(self):
        self._undo = []
    def setattr(self, target, name, value):
        original = getattr(target, name)
        self._undo.append((target, name, original))
        setattr(target, name, value)
    def undo(self):
        for target, name, original in reversed(self._undo):
            setattr(target, name, original)
        self._undo.clear()


def _resolve_fixture(name, cache):
    if name == "monkeypatch":
        if name not in cache:
            cache[name] = _Monkeypatch()
        return cache[name]
    if name in cache:
        return cache[name]
    fixture_func = _fixtures[name]
    params = [p for p in inspect.signature(fixture_func).parameters]
    kwargs = {p: _resolve_fixture(p, cache) for p in params}
    result = fixture_func(**kwargs)
    if inspect.isgenerator(result):
        value = next(result)
        cache[name] = value
        cache.setdefault("_generators", []).append(result)
        return value
    cache[name] = result
    return result


def run_module(module):
    test_funcs = [(n, f) for n, f in vars(module).items()
                  if n.startswith("test_") and callable(f)]
    autouse_fixtures = [n for n, f in _fixtures.items() if getattr(f, "_autouse", False)]

    passed, failed = [], []
    for name, func in test_funcs:
        param_sets = [{}]
        if hasattr(func, "_parametrize"):
            names, values = func._parametrize
            param_sets = [dict(zip(names, (v,) if len(names) == 1 else v)) for v in values]

        for params in param_sets:
            cache = {}
            for auto in autouse_fixtures:
                _resolve_fixture(auto, cache)
            sig_params = [p for p in inspect.signature(func).parameters if p not in params]
            for p in sig_params:
                if p in _fixtures or p == "monkeypatch":
                    params[p] = _resolve_fixture(p, cache)
            label = f"{name}{ {k: v for k, v in params.items() if not hasattr(v, 'shape') and 'Monkeypatch' not in type(v).__name__} if params else ''}"
            try:
                func(**params)
                passed.append(label)
            except Exception as e:
                failed.append((label, e))
                traceback.print_exc()
            finally:
                for gen in cache.get("_generators", []):
                    try:
                        next(gen)
                    except StopIteration:
                        pass
                mp = cache.get("monkeypatch")
                if mp:
                    mp.undo()

    return passed, failed
