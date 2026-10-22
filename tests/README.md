# Tests

Install the tools once:

```bash
pip install -r requirements-dev.txt
```

## Fast checks (seconds)

```bash
pytest
```

These check that every gearbox type in `gearbox_runner.GEARBOXES` names existing classes and config files, builds with one of its golden motors, has a results print layout in `actOpt.py`, and has a golden baseline. `tests/test_motors.py` checks `config_files/motors.json`. They also check that every config file is valid JSON. CI runs them on every push.

## Golden-output check (about 20–30 minutes)

`tests/golden/golden.py` runs every gearbox type with each of its golden motors (`GOLDEN_MOTORS` in `golden.py`), plus one metal-mode case per type (`<case>__metal`), at one gear ratio per family (6.5 single-stage, 10 compound, 20 double-stage and Wolfrom). It compares three things against the baselines in `tests/golden/baselines/`:

- the optimiser's returned parameters (the chosen design),
- the CAD equation files it writes,
- the results CSVs it writes — total mass, efficiency, cost, torque density and the per-part mass breakdown. Run-time lines are left out, since they differ on every run.

A changed results CSV is reported value by value, e.g. `mass: 1.483 -> 1.192`. Each case runs in its own temporary folder, so the check never touches your `results/` folder.

```bash
python tests/golden/golden.py check                  # all 46 cases
python tests/golden/golden.py check --only idspg     # one gearbox type
python tests/golden/golden.py list                   # show the cases
```

Run it before merging any refactor. A refactor must not change any number.

The baselines record **current** behaviour, including known bugs. When a commit is meant to change results (for example a bug fix), re-record only the affected cases in that same commit and say so in the commit message:

```bash
python tests/golden/golden.py record --only indspg
```

Running the check rewrites the tracked `CADs/*/*_equations*.txt` files. Afterwards, `git checkout -- CADs` puts them back.

## Lint and spelling (report-only)

```bash
ruff check .
codespell .
```

CI reports these without failing the build. Settings are in `pyproject.toml`.
