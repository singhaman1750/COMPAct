## Quick Start (Run the Project)


### 1. Go to the project root
```bash
cd onshape_toolkit
```
### 2. Activate the virtual environment
```bash
source venv/bin/activate
```
### 4. pip install
```bash
pip install onshape-robotics-toolkit
pip install numpy matplotlib pandas
```

### NOTE 
```bash
AFTER INSTALLING THE "onshape-robotics-toolkit"
Go to connect.py in the library and add the print response statement in the "set_variables" method to see the error
```

### 5. Run the script
```bash
set_values.py
```




# Onshape CAD Automation Toolkit

A Python-based toolkit for programmatic control of Onshape CAD models — enabling parametric variable updates, design automation, and CAD-driven engineering pipelines via the Onshape REST API.

---

## Why This Exists

Most CAD workflows are still manual. Even in parametric design, engineers are left clicking through menus to update dimensions, run sweeps, or test variants.

This toolkit breaks that bottleneck. It lets you treat your CAD model as a programmable object — read variables, push updates, run iterations — all from Python.

Built while working on actuator and mechanism design, where manually updating link lengths across dozens of configurations wasn't sustainable.

---

## Features

- Authenticate with the Onshape API (v9)
- Traverse documents and retrieve elements
- Access and parse Variable Studios
- Read variable names, types, and expressions
- Update variables programmatically with API-compliant payloads
- Handle type-aware updates (`LENGTH`, `ANGLE`, `NUMBER`)
- Structured logging for debugging API responses

---

## Repository Structure

```
onshape-toolkit/
│
├── connect.py              # API client initialization and auth
├── variables.py            # Core variable read/write logic
├── set_values.py           # Script: update specific variables
├── update_variables.py     # Script: batch parametric updates
├── utils/                  # Shared helpers and formatting
├── .env                    # API credentials (not committed)
└── README.md
```

---

## Setup

### 1. Clone

```bash
git clone https://github.com/sakethvegesna/onshape-toolkit.git
cd onshape-toolkit
```

### 2. Install Dependencies

```bash
pip install requests python-dotenv
```

### 3. Configure Credentials

Create a `.env` file in the project root:

```env
ONSHAPE_ACCESS_KEY=your_access_key
ONSHAPE_SECRET_KEY=your_secret_key
ONSHAPE_BASE_URL=https://cad.onshape.com
```

API keys can be generated at [dev-portal.onshape.com](https://dev-portal.onshape.com).

---

## Usage

### Reading Variables

```python
from variables import get_variables

variables = get_variables(document_id, workspace_id, element_id)
print(variables)
```

### Updating Variables

```python
from variables import set_variables

set_variables(
    document_id,
    workspace_id,
    element_id,
    {
        "link_length": "250 mm",
        "joint_width": "40 mm",
        "clearance_angle": "15 deg"
    }
)
```

---

## API Notes

The Onshape Variables API requires strictly formatted payloads. Key implementation details:

- Variables must be sent as **expressions**, not raw numbers (e.g., `"250 mm"` not `250`)
- Each variable requires an explicit **type** field (`LENGTH`, `ANGLE`, `NUMBER`)
- Malformed payloads return 200 OK but silently fail — this toolkit validates before sending
- Developed and tested against Onshape API v9

---

## Use Cases

- Parametric dimension sweeps for mechanism design
- Actuator geometry iteration (link lengths, joint offsets)
- CAD integration into optimization or ML pipelines
- Batch geometry generation for simulation datasets
- Robotics leg/arm configuration studies

---

## Roadmap

- [ ] Assembly-level parameter control
- [ ] Feature creation and suppression
- [ ] STEP/STL export automation
- [ ] Optimization loop integration (e.g., SciPy, Optuna)
- [ ] CLI interface for quick variable updates

---

## Security

Never commit your `.env` file. Add it to `.gitignore`:

```
.env
```

---

## Author

**Saketh Vegesna**  
Mechanical Engineering — Robotics  
Focused on automation, mechanism design, and computational engineering.