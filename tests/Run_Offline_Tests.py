"""
Runs tests/01_Dashboard_Logic_Tests.py without needing the real pytest package
installed (this sandbox has no network access to pip install it).
Injects a minimal shim as `sys.modules["pytest"]` so the SAME test file
that a real `pytest tests/01_Dashboard_Logic_Tests.py` would run is executed here
unmodified - only the runner is a stand-in, not the tests themselves.

Usage: python3 tests/Run_Offline_Tests.py
"""
import sys
import importlib.util
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "tests" / "stubs"))

# Try the real pytest first - if it's actually installed, prefer it and
# tell the user to just run it directly instead of this shim.
try:
    import pytest  # noqa: F401
    print("Real pytest is installed - run it directly instead:")
    print("    pytest tests/01_Dashboard_Logic_Tests.py -v")
    sys.exit(0)
except ImportError:
    pass

import pytest_offline_shim as shim

fake_pytest = type(sys)("pytest")
fake_pytest.fixture = shim.fixture
fake_pytest.mark = shim.mark
fake_pytest.raises = shim.raises
sys.modules["pytest"] = fake_pytest

spec = importlib.util.spec_from_file_location(
    "test_app_logic", str(BASE / "tests" / "01_Dashboard_Logic_Tests.py")
)
test_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_module)

passed, failed = shim.run_module(test_module)

print(f"\n{'='*70}\n{len(passed)} passed, {len(failed)} failed\n{'='*70}")
for label in passed:
    print(f"  [PASS] {label}")
for label, exc in failed:
    print(f"  [FAIL] {label}: {type(exc).__name__}: {exc}")

print(f"\nNOTE: this ran via tests/stubs/pytest_offline_shim.py, a minimal "
      f"stand-in used only because pytest could not be installed in this "
      f"sandbox (no network access). Run the real `pytest "
      f"tests/01_Dashboard_Logic_Tests.py -v` in any environment with network access "
      f"to confirm with the actual framework.")

sys.exit(1 if failed else 0)
