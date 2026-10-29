import json
import re
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import gearbox_runner  # noqa: E402
from Onshape_extension import set_values  # noqa: E402

DISPATCH = gearbox_runner.GEARBOXES
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


def fake_onshape(monkeypatch, version_status=200, stored=None, write_status=204, sent=None):
    """Replace src.onshape_client with a recorder; returns the list of calls.
    The variables written are appended to `sent`, if given."""
    calls = []

    class Client:
        def __init__(self, env=None):
            pass

        def request(self, method, path, body=None, log_response=True, **kwargs):
            calls.append((method, path))
            if path.endswith("/versions"):
                return FakeResponse(version_status, {})
            if method == "post":
                if sent is not None:
                    sent.append(body)
                return FakeResponse(write_status, None)
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


def test_push_can_send_a_saved_file(tmp_path, monkeypatch):
    models = write_case(tmp_path, monkeypatch, '"Ns"= 19\n')
    saved = tmp_path / "saved_equations_onshape.txt"
    saved.write_text('"Ns"= 21\n')
    fake_onshape(monkeypatch, stored=[{"name": "Ns", "expression": "21"}])
    assert set_values.push_to_onshape("sspg", models_json=models, eq_file=str(saved)) == []


@pytest.mark.parametrize("case_dir", sorted((REPO_ROOT / "docs" / "cad_issues").glob("*/")), ids=lambda p: p.name)
def test_saved_cad_issue_cases_parse(case_dir):
    from Onshape_extension.parse_variables_txt import parse_variable_file
    files = list(case_dir.glob("*_equations_onshape.txt"))
    assert files and parse_variable_file(str(files[0]))


def _equation_files():
    files = sorted(REPO_ROOT.glob("CADs/*/*_equations_onshape.txt"))
    files += sorted(REPO_ROOT.glob("docs/cad_issues/*/*_equations_onshape.txt"))
    return files


COUNT_NAME = re.compile(r"(^|_)(num|N[a-z]\w*|N\d?)(_|$)|_num$|^num_|_number")


@pytest.mark.parametrize("path", _equation_files(), ids=lambda p: f"{p.parent.name}/{p.name}")
def test_counts_are_sent_as_numbers(path):
    # A count missing from NUMBER_VARS would be sent to Onshape as a length in mm.
    from Onshape_extension.parse_variables_txt import NUMBER_VARS
    names = re.findall(r'^\s*"(.+?)"\s*=', path.read_text(encoding="utf-8"), re.M)
    missing = sorted({n for n in names if COUNT_NAME.search(n)} - NUMBER_VARS)
    assert not missing, f"add to NUMBER_VARS in Onshape_extension/parse_variables_txt.py: {missing}"


# Variants of a family (e.g. incpg_dependent / incpg_independent) share a CAD folder but must
# each write, and push, their own files; they used to overwrite one shared file (ISSUES bug 2).
VARIANTS = {}
for _gb_type in DISPATCH:
    VARIANTS.setdefault(set_values.gearbox_family(_gb_type), []).append(_gb_type)
VARIANT_PAIRS = sorted(tuple(sorted(v)) for v in VARIANTS.values() if len(v) > 1)


@pytest.mark.parametrize("variants", VARIANT_PAIRS, ids="/".join)
def test_variants_of_a_family_write_different_files(variants):
    written = {}
    for gb_type in variants:
        for baseline in BASELINES.glob(f"{gb_type}__*.json"):
            for name in json.loads(baseline.read_text(encoding="utf-8"))["cad_files"]:
                written.setdefault(name, set()).add(gb_type)
    shared = sorted(name for name, by in written.items() if len(by) > 1)
    assert not shared, f"written by more than one variant: {shared}"


@pytest.mark.parametrize("variants", VARIANT_PAIRS, ids="/".join)
def test_each_variant_pushes_its_own_file(variants, tmp_path, monkeypatch):
    from Onshape_extension.parse_variables_txt import parse_variable_file
    models = tmp_path / "onshape_models.json"
    models.write_text(json.dumps({t: f"https://cad.onshape.com/documents/D{i}/w/W{i}/e/E{i}"
                                  for i, t in enumerate(variants)}))
    sent = []
    fake_onshape(monkeypatch, sent=sent)
    for gb_type in variants:
        set_values.push_to_onshape(gb_type, save_version=False, models_json=str(models))
    expected = [parse_variable_file(set_values.equations_file(t)) for t in variants]
    assert sent == expected
    assert sent[0] != sent[1]

