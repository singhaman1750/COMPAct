# Tests

Install the tools once:

```bash
pip install -r requirements-dev.txt
```

## Fast checks (seconds)

```bash
pytest
```

These check that every gearbox type in `gearbox_runner.GEARBOXES` names existing classes and config files, builds with one of its golden motors, has a results print layout in `actOpt.py`, and has a golden baseline. `tests/test_motors.py` checks `config_files/motors.json`. They also check that every config file is valid JSON. `tests/test_actuator_map.py` checks the actuator-map tool (`tools/actuator_map/`): a few sweep cases must equal the plain optimiser's golden baselines, and its width/diameter formulas must match the Onshape measurements. `tests/test_actuator_map_e2e.py` runs the whole tool end to end on a small real sweep (RO100, 3dp, 3 types, ratios 4–9; about 15 s): sweep → table → fits → `map.py`, and checks that the map gives back every table row, matches `fit.py`'s fits and switch ratios, and applies the 80 % torque rule. CI runs them on every push.

## Golden-output check (under a minute)

`tests/golden/golden.py` runs every gearbox type with each of its golden motors (`GOLDEN_MOTORS` in `golden.py`), plus one metal-mode case per type (`<case>__metal`), at one gear ratio per family (6.5 single-stage, 10 compound, 20 double-stage and Wolfrom). It compares three things against the baselines in `tests/golden/baselines/`:

- the optimiser's returned parameters (the chosen design),
- the CAD equation files it writes,
- the results CSVs it writes — total mass, efficiency, cost, torque density and the per-part mass breakdown. Run-time lines are left out, since they differ on every run.

A changed results CSV is reported value by value, e.g. `mass: 1.483 -> 1.192`. Each case runs in its own temporary folder and writes its results CSVs and CAD files there (the CAD folder is set with the `COMPACT_CAD_DIR` environment variable, read by `CommonComponents.cad_path`), so the check never touches your `results/` or `CADs/` folders and all cases run in parallel (`--workers`, default up to 12).

```bash
python tests/golden/golden.py check                  # all 58 cases
python tests/golden/golden.py check --only idspg     # one gearbox type
python tests/golden/golden.py list                   # show the cases
```

Run it before merging any refactor. A refactor must not change any number.

The baselines record **current** behaviour, including known bugs. When a commit is meant to change results (for example a bug fix), re-record only the affected cases in that same commit and say so in the commit message:

```bash
python tests/golden/golden.py record --only indspg
```

## Lint and spelling (report-only)

```bash
ruff check .
codespell .
```

CI reports these without failing the build. Settings are in `pyproject.toml`.
