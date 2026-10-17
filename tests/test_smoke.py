"""
Fast checks (seconds) that run on every push. The slow golden-output check
lives in tests/golden/golden.py.
"""

import importlib
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tests" / "golden"))

import golden  # noqa: E402

DISPATCH = golden.load_dispatch()


@pytest.mark.parametrize("gb_type", sorted(DISPATCH))
def test_dispatch_target_exists(gb_type):
    assert (REPO_ROOT / f"{DISPATCH[gb_type]}.py").exists()


def test_each_gearbox_type_has_one_print_block():
    source = (REPO_ROOT / "actOpt.py").read_text(encoding="utf-8")
    printed = re.findall(r'gearbox_type\s*==\s*"(\w+)"', source)
    for gb_type in DISPATCH:
        assert printed.count(gb_type) == 1, f"{gb_type}: {printed.count(gb_type)} print blocks"
    assert set(printed) <= set(DISPATCH), f"print blocks for unknown types: {set(printed) - set(DISPATCH)}"


@pytest.mark.parametrize("module_name", sorted(set(DISPATCH.values())))
def test_optimiser_module_imports(module_name):
    module = importlib.import_module(module_name)
    assert callable(getattr(module, "run", None))


@pytest.mark.parametrize("module_name", sorted(set(DISPATCH.values())))
def test_psc_mode_fails_clearly(module_name):
    module = importlib.import_module(module_name)
    optimizer_classes = {
        v if isinstance(v, type) else type(v)
        for v in vars(module).values()
        if hasattr(v, "optimizeActuator")
    }
    assert optimizer_classes, f"no optimizer class found in {module_name}"
    for cls in optimizer_classes:
        # The guard runs before any other attribute is used, so a bare object works as self.
        with pytest.raises(NotImplementedError, match="UsePSCasVariable=1 is not available"):
            cls.optimizeActuator(SimpleNamespace(), UsePSCasVariable=1)


@pytest.mark.parametrize("gb_type", sorted(DISPATCH))
def test_optimiser_supports_at_least_one_motor(gb_type):
    assert golden.supported_motors(DISPATCH[gb_type], gb_type)


@pytest.mark.parametrize(
    "path", sorted((REPO_ROOT / "config_files").glob("*.json")), ids=lambda p: p.name
)
def test_config_file_is_valid_json(path):
    json.loads(path.read_text(encoding="utf-8"))


def test_every_case_has_a_golden_baseline():
    missing = [
        golden.case_id(c)
        for c in golden.all_cases()
        if not (golden.BASELINE_DIR / f"{golden.case_id(c)}.json").exists()
    ]
    assert not missing, (
        "No golden baseline for: " + ", ".join(missing)
        + "\nRecord with: python tests/golden/golden.py record --only <gb_type>"
    )
