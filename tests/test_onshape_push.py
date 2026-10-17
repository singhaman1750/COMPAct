import json
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import actOpt  # noqa: E402
from Onshape_extension import set_values  # noqa: E402

DISPATCH = actOpt.GEARBOX_DISPATCH
BASELINES = REPO_ROOT / "tests" / "golden" / "baselines"


@pytest.mark.parametrize("gb_type", sorted(DISPATCH))
def test_equations_file_is_the_one_the_optimiser_writes(gb_type):
    written = set()
    for baseline in BASELINES.glob(f"{gb_type}__*.json"):
        written.update(json.loads(baseline.read_text(encoding="utf-8"))["cad_files"])
    expected = Path(set_values.equations_file(gb_type)).relative_to(REPO_ROOT).as_posix()
    assert expected in written


def test_example_models_file_lists_every_gearbox_type():
    example = json.loads((REPO_ROOT / "Onshape_extension" / "onshape_models.example.json").read_text())
    assert set(DISPATCH) <= set(example)


def test_model_url_needs_the_models_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="onshape_models.example.json"):
        set_values.model_url("sspg", str(tmp_path / "onshape_models.json"))


def test_model_url_needs_an_entry(tmp_path):
    models = tmp_path / "onshape_models.json"
    models.write_text(json.dumps({"sspg": "", "cpg": "https://cad.onshape.com/documents/d/w/w1/e/e1"}))
    with pytest.raises(ValueError, match="No Onshape model set for 'sspg'"):
        set_values.model_url("sspg", str(models))
    assert set_values.model_url("cpg", str(models)).startswith("https://")


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload
        self.text = json.dumps(payload)

    def json(self):
        return self._payload


def fake_onshape(monkeypatch, version_status=200, stored=None):
    """Replace src.onshape_client with a recorder; returns the list of calls."""
    calls = []

    class Client:
        def __init__(self, env=None):
            pass

        def request(self, method, path, body=None, log_response=True, **kwargs):
            calls.append((method, path))
            if path.endswith("/versions"):
                return FakeResponse(version_status, {})
            if method == "post":
                return FakeResponse(200, {})
            return FakeResponse(200, [{"variables": stored or []}])

    real_client = sys.modules.get("src.onshape_client")
    sys.path.insert(0, set_values.EXT_DIR)
    from src.onshape_client import HTTP, Document  # the real URL parser and enum
    module = types.ModuleType("src.onshape_client")
    module.Client, module.HTTP, module.Document = Client, HTTP, Document
    monkeypatch.setitem(sys.modules, "src.onshape_client", module)
    if real_client is not None:
        monkeypatch.setattr(sys.modules["src"], "onshape_client", module, raising=False)
    return calls


def write_case(tmp_path, monkeypatch, equations):
    models = tmp_path / "onshape_models.json"
    models.write_text(json.dumps({"sspg": "https://cad.onshape.com/documents/D1/w/W1/e/E1"}))
    eq = tmp_path / "sspg_equations_onshape.txt"
    eq.write_text(equations)
    monkeypatch.setattr(set_values, "equations_file", lambda gb_type: str(eq))
    return str(models)


def test_push_saves_a_version_then_writes_then_checks(tmp_path, monkeypatch):
    models = write_case(tmp_path, monkeypatch, '"Ns"= 19\n"module"= 0.7\n')
    calls = fake_onshape(monkeypatch, stored=[{"name": "Ns", "expression": "19"},
                                              {"name": "module", "expression": "0.7 mm"}])
    assert set_values.push_to_onshape("sspg", models_json=models) == []
    assert [path.rsplit("/", 1)[-1] for _, path in calls] == ["versions", "variables", "variables"]
    assert [method for method, _ in calls] == ["post", "post", "get"]


def test_push_reports_variables_that_did_not_take(tmp_path, monkeypatch):
    models = write_case(tmp_path, monkeypatch, '"Ns"= 19\n"module"= 0.7\n')
    fake_onshape(monkeypatch, stored=[{"name": "Ns", "expression": "20"}])
    assert set_values.push_to_onshape("sspg", models_json=models) == ["Ns", "module"]


def test_push_writes_nothing_if_the_version_cannot_be_saved(tmp_path, monkeypatch):
    models = write_case(tmp_path, monkeypatch, '"Ns"= 19\n')
    calls = fake_onshape(monkeypatch, version_status=403)
    with pytest.raises(RuntimeError, match="Nothing was changed"):
        set_values.push_to_onshape("sspg", models_json=models)
    assert len(calls) == 1


def test_push_refuses_a_version_url(tmp_path, monkeypatch):
    models = tmp_path / "onshape_models.json"
    models.write_text(json.dumps({"sspg": "https://cad.onshape.com/documents/D1/v/V1/e/E1"}))
    fake_onshape(monkeypatch)
    with pytest.raises(ValueError, match="not a workspace"):
        set_values.push_to_onshape("sspg", models_json=str(models))
