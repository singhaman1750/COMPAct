"""sun_hub_clearance_multiple (config) is the margin around the sun hub's bolt circle, in multiples of
standard_clearance_1_5mm: 4 in SSPG, CPG, DSPG, ISSPG (compact, inside) and ICPG, 5 in IDSPG (its CAD's
value). Raising it on each type's first golden design changes the sun-hub variable it drives (in ISSPG
inside: the input bearing, which then sets the hub) and nothing outside what depends on the key; in
SSPG, CPG, DSPG and IDSPG the mass code uses the same key, so the mass changes too."""
import json

import pytest

from variable_helpers import CONFIG, GEARBOXES, SPECS, downstream_of, equation_lines, golden_design, write_design

KEY = "sun_hub_clearance_multiple"
DRIVES = {"sspg": "sun_hub_dia", "cpg": "sun_hub_dia", "dspg": "a1_sun_hub_dia", "isspg_compact": "sun_hub_dia",
          "isspg_inside": "input_bearing_ID", "icpg": "sun_hub_dia", "idspg": "a1_sun_hub_dia"}
VALUE = {gb: 5 if gb == "idspg" else 4 for gb in DRIVES}
MASS_USES_KEY = {"sspg", "cpg", "dspg", "idspg"}


def run(monkeypatch, folder, gb, value=None):
    _, motor, material, gears, _ = golden_design(GEARBOXES[gb].golden()[0])
    actuator, _, _, onshape = write_design(monkeypatch, folder, gb, motor, material, gears)
    if value is not None:
        actuator.design_params[KEY] = value
        actuator.setVariables()
        actuator.updateFacewidth()
        actuator.setVariables()
        actuator.genEquationFile_editCADdirectly()
        spec = GEARBOXES[gb]
        onshape = equation_lines((folder / spec.cad_folder / f"{spec.cad_file}_onshape.txt").read_text())
    return actuator, {n: float(x) for n, x in onshape}, actuator.getMassKG_3DP()


@pytest.mark.parametrize("gb", DRIVES)
def test_the_config_value_is_the_old_hard_coded_one(gb):
    source = next(e for e in SPECS[gb]["code_only"] if e["name"] == KEY)["source"]
    params = json.loads((CONFIG / source["file"]).read_text(encoding="utf-8"))
    assert params[source["block"]][KEY] == VALUE[gb]


@pytest.mark.parametrize("gb", DRIVES)
def test_sun_hub_clearance_comes_from_the_config(monkeypatch, tmp_path, gb):
    (tmp_path / "a").mkdir(), (tmp_path / "b").mkdir()
    a, base, mass = run(monkeypatch, tmp_path / "a", gb)
    assert a.sun_hub_clearance_multiple == VALUE[gb]
    b, more, mass_more = run(monkeypatch, tmp_path / "b", gb, VALUE[gb] + 4)
    assert b.sun_hub_clearance_multiple == VALUE[gb] + 4
    changed = {k for k in base if base[k] != more[k]}
    assert DRIVES[gb] in changed and changed <= downstream_of(gb, KEY)
    if gb in MASS_USES_KEY:
        assert mass_more != mass
