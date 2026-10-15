# Tests

Install the tools once:

```bash
pip install -r requirements-dev.txt
```

## Fast checks (seconds)

```bash
pytest
```

These check that every gearbox type in `actOpt.py` points to an existing `Opt_*.py`, has exactly one results print block, imports cleanly, supports at least one motor, and has a golden baseline. They also check that every config file is valid JSON. CI runs them on every push.

## Golden-output check (about 20–30 minutes)

`tests/golden/golden.py` runs every gearbox type with every motor its `run()` supports, at one gear ratio per family (6.5 single-stage, 10 compound, 20 double-stage and Wolfrom). It compares the optimiser's returned parameters and the CAD equation files it writes against the baselines in `tests/golden/baselines/`.

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
