# Onshape: update a CAD model from an optimisation

COMPAct writes each design's parameters to `CADs/<TYPE>/<type>_equations_onshape.txt`. The Onshape
extension pushes that file into the **Variable Studio** of your copy of the gearbox's Onshape model;
the model then rebuilds with the new design.

## One-time setup

### 1. API keys
1. Sign in at [dev-portal.onshape.com](https://dev-portal.onshape.com) → **API Keys** → **Create New
   API Key** with read and write permission.
2. Create `Onshape_extension/.env`:
   ```env
   ONSHAPE_ACCESS_KEY=your_access_key
   ONSHAPE_SECRET_KEY=your_secret_key
   ```
   `.env` is gitignored — never commit or share it.

The extension needs `requests` and `python-dotenv` (both in `requirements.txt`).

### 2. Your own copy of each model
The shared models are read-only for you. For each gearbox type you use:
1. Open its link in the README's [gearbox table](../README.md#gearbox-types).
2. Onshape menu (top left) → **Copy workspace** (or **Make a copy**) → give it a name.
3. In your copy, open the **Variable Studio** tab (bottom tab bar) and copy the full browser URL.
   It looks like `https://cad.onshape.com/documents/<did>/w/<wid>/e/<eid>` and must contain `/w/`.

### 3. List the models once
Copy `Onshape_extension/onshape_models.example.json` to `Onshape_extension/onshape_models.json`
(personal, gitignored) and paste each Variable Studio URL next to its gearbox type:
```json
"sspg": "https://cad.onshape.com/documents/<did>/w/<wid>/e/<eid>",
```
Leave types you don't use empty. Variants that share a CAD folder still need their own model:
`isspg_inside` (InBearing) / `isspg_compact` (OutBearing), `incpg_dependent` / `incpg_independent`,
`inwpg_dependent` / `inwpg_independent`, `insspg_type_1` (independent) / `insspg_type_2` (dependent).

## Use

Optimise and update the model in one command:
```bash
python actOpt.py --motor U8_Lite --gb_type sspg --gr 6.5 --onshape
```
Push the latest result again, without re-optimising:
```bash
python Onshape_extension/set_values.py --gb_type sspg
```
Push a saved equations file (e.g. a case kept for a bug report in `docs/cad_issues/`):
```bash
python Onshape_extension/set_values.py --gb_type dspg --file docs/cad_issues/CAD3_dspg_MAD_M6C06_KV140_gr20/dspg_equations_onshape.txt
```

Each push:
1. saves an Onshape **version** first (`before sspg push <date>`), so you can roll back from the
   document's version history (skip with `--no-version`);
2. writes the variables;
3. reads them back and prints `Onshape: N of N variables set`, or one line per variable that did
   not take.

If the optimiser finds no design, the model is not set up, or the API fails, the optimisation result
is still saved and the model is left unchanged.

Both variants of a family write the same equations file (e.g. `isspg_inside` and `isspg_compact` →
`CADs/ISSPG/isspg_equations_onshape.txt`), so push a variant before optimising the other one; with
`--onshape` this happens automatically.

## Troubleshooting

| Message | Meaning / fix |
|---|---|
| `onshape_models.json not found` | Do setup step 3. |
| `No Onshape model set for 'icpg'` | That type's entry is empty in `onshape_models.json`. |
| `points to a version, not a workspace (/w/)` | Copy the URL while in the workspace, not in a version (`/v/`). |
| `Could not save a version ... (HTTP 403)` | No write access: the URL is the shared model, not your copy. Nothing was changed. |
| `Environment file not found` / `Key 'ONSHAPE_ACCESS_KEY' not found` | `Onshape_extension/.env` is missing, or a key name is misspelt (setup step 1). |
| `not set as expected: <name> = ...` | The model has no such variable, or it has a different type there (e.g. a count sent as a length). Report the name; it may be a CAD issue (see [ISSUES.md](../ISSUES.md), "CAD issues"). |
| Model shows red features after a push | The CAD model can't build that design — log it as a CAD issue and save the equations file under `docs/cad_issues/<case>/` so it can be replayed with `--file`. |

Variables are sent as lengths (mm) unless their value has `deg`/`rad` (angles) or their name is in
the count list in `Onshape_extension/parse_variables_txt.py` (teeth, planets, hole counts). A test
checks that every count in the equations files is in that list.
