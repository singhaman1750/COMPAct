# COMPAct: Actuator design framework

This repository provides an implementation of the paper:

<td style="padding:20px;width:75%;vertical-align:middle">
      <a href="https://arxiv.org/abs/2510.07197" target="_blank">
      <b> COMPAct: Computational Optimization and Automated Modular design of Planetary Actuators </b>
      </a>
      <br>
      <a href="https://singhaman1750.github.io/" target="_blank">Aman Singh</a>, <a href="https://www.linkedin.com/in/deepak-kapa-iitr26/" target="_blank">Deepak Kapa</a>, <a href="https://www.linkedin.com/in/suryank-joshi/" target="_blank">Suryank Joshi</a>, and <a href="https://www.shishirny.com/" target="_blank">Shishir Kolathaya</a>
      <br>
      <em>IEEE International Conference on Robotics and Automation</em>, 2026
      <br>
      <a href="https://youtu.be/99zOKgxsDho?si=5hyMySFOMPunLLCl">Video-Overview</a>
    <br>
</td>

<br>

---

## Quick Start Guide

1. [Step 1: Setup & Requirements](https://github.com/singhaman1750/COMPAct/edit/main/README.md#step-1-setup--requirements)
2. [Step 2: Installation](https://github.com/singhaman1750/COMPAct/edit/main/README.md#step-2-installation)
3. [Step 3: Extract CAD Files](https://github.com/singhaman1750/COMPAct/edit/main/README.md#step-3-extract-cad-files-optional)
4. [Step 4: Run Optimization](https://github.com/singhaman1750/COMPAct/edit/main/README.md#step-4-run-optimization)
5. [Step 5: View Results](https://github.com/singhaman1750/COMPAct/edit/main/README.md#step-5-view-results)
6. [Step 6: CAD Automation](https://github.com/singhaman1750/COMPAct/edit/main/README.md#step-6-cad-automation)
7. [Step 7: 3D-print and Assemble](https://github.com/singhaman1750/COMPAct/edit/main/README.md#step-7-3d-print-and-assemble)

---

### Step 1: Setup & Requirements

#### System Requirements
* **Python 3.x**
* **SolidWorks 2024** (or higher) – *Required for CAD automation features.*

#### Recommended Terminal
* **Windows:** [Git Bash](https://git-scm.com/downloads) is highly recommended.
* **Linux/macOS:** Default terminal.

---

### Step 2: Installation
Clone the repository and install the dependencies:

```bash
# Clone the repository
git clone https://github.com/singhaman1750/COMPAct.git
```

```bash
# Enter the directory
cd COMPAct
```

```bash
# Install required packages
pip install numpy matplotlib pandas requests
```

---

### Step 3: Extract CAD Files (Optional)
Due to file size limits, CAD files are zipped. You must extract them before running the framework.

**NOTE:** _If you only need the optimized gear parameters (teeth count, module, etc.), you can skip this step. Extraction is only required if you intend to use the **automated 3D modeling**._

1.  Navigate to the `CADs` directory.
2.  Inside each gearbox folder (e.g., `CADs/SSPG/`), unzip the archive (e.g., `sspg_actuator.zip`) into the **same directory**.

Your directory structure should look like this after extraction:
```text
COMPAct-Actuator_design_framework/
└── CADs/
    ├── SSPG/sspg_actuator/sspg_actuator/...
    ├── CPG/cpg_actuator/cpg_actuator/...
    ├── DSPG/dspg_actuator/dspg_actuator/...
    └── WPG/wpg_actuator/wpg_actuator/...
```

#### Onshape CAD Files (Cloud Alternative)

If you prefer not to use SolidWorks, the CAD models are also available on Onshape. No extraction or local files needed.

##### 1. SSPG

👉 **[Open SSPG in Onshape](https://cad.onshape.com/documents/c1aac326515ba734f63b9b3f/w/f9cccd7b90ce6d7934076c7c/e/11d494d64974a13f1ae2def2?renderMode=0&leftPanel=false&uiState=69ba77262aa7d6ac3cb56ff9)**

To get your own editable copy:
1. Open the link above — you will see the model in view-only mode
2. Click the **Onshape logo / menu icon** in the top-left corner
3. Select **"Make a copy"**
4. Give it a name and save it to your own Onshape workspace

> ✅ Your copy is fully independent — any changes you make will **not** affect the original shared document. You can now edit the Variable Studio, modify geometry, and run the automation script against your own copy.

---

### Step 4: Run Optimization
Run the Python script from the root directory to generate optimal gear parameters.

**Syntax:**
```bash
python actOpt.py <motor> <gearbox> <ratio>
```
* **`<motor>`**: U8, U10, U12, MN8014, VT8020, MAD_M6C12
* **`<gearbox>`**: sspg, cpg, dspg, wpg
* **`<ratio>`**: Must be a value > 2.

**Example:**
To optimize a **T-motor U8** with a **Single-Stage Planetary Gearbox** and a **ratio of 6.5**:

```bash
python actOpt.py U8 sspg 6.5
```

---

### Step 5: View Results
The script will output the optimal geometric parameters directly in the terminal:

```text
Running optimization:
  Motor       : U8
  Gearbox     : sspg
  Gear Ratio  : 6.5
Time taken: 0.0196 sec
Optimization Completed.
-------------------------------
Optimal Parameters:
Number of teeth: Sun(Ns): 23 , Planet(Np): 52 , Ring(Nr): 127 , Module(m): 0.6 , NumPlanet(n_p): 3
---
Gear Ratio(GR): 6.52 : 1
-------------------------------
```

Detailed parameter files are automatically generated in the following locations:

* **SSPG:** `CADs/SSPG/sspg_equations.txt`
* **CPG:** `CADs/CPG/cpg_equations.txt`
* **DSPG:** `CADs/DSPG/dspg_equations.txt`
* **WPG:** `CADs/WPG/wpg_equations.txt`

---

### Step 6: CAD Automation

There are two ways to apply the optimization results to a CAD model — using **SolidWorks** (local) or **Onshape** (cloud-based). Both use the same equations file generated in Step 2.

---

#### Option A: SolidWorks (Local)

**NOTE:** _If you skipped the CAD extraction in Step 2, you cannot use this option._

1.  Open **SolidWorks**.
2.  Open the assembly file (`.SLDASM`) for your specific gearbox type:
    * **SSPG:** `CADs/SSPG/sspg_actuator/sspg_actuator/sspg_actuator.SLDASM`
    * *(Paths for CPG, DSPG, and WPG follow the same folder pattern)*
3.  Click the **Rebuild** (Traffic Light) icon.
4.  The 3D model will automatically update to reflect the calculated parameters.

---

#### Option B: Onshape Automation (Cloud-based)

This extension lets you push optimization results directly to a parametric Onshape CAD model via the Onshape REST API — no SolidWorks or local CAD files required.

##### i. Make a Copy of the Onshape Document

If you haven't already done so in the extraction step above, open the shared Onshape document and make your own copy:

👉 **[Open SSPG in Onshape](https://cad.onshape.com/documents/c1aac326515ba734f63b9b3f/w/f9cccd7b90ce6d7934076c7c/e/11d494d64974a13f1ae2def2?renderMode=0&leftPanel=false&uiState=69ba77262aa7d6ac3cb56ff9)**

1. Click the **Onshape logo / menu icon** in the top-left corner
2. Select **"Make a copy"**
3. Give it a name and save it to your own Onshape workspace

> ✅ Your copy is fully independent — any changes the script makes will **not** affect the original shared document.

##### ii. Generate Onshape API Keys

The script authenticates with the Onshape REST API using personal API keys.

1. Go to [dev-portal.onshape.com](https://dev-portal.onshape.com) and sign in
2. Navigate to **API Keys** → **Create New API Key**
3. Copy the **Access Key** and **Secret Key**
4. Create a file named `.env` inside the `Onshape_extension/` folder with the following content:

```env
ONSHAPE_ACCESS_KEY=your_access_key
ONSHAPE_SECRET_KEY=your_secret_key
```

> 🔒 **Never commit your `.env` file.** Make sure `.env` is listed in your `.gitignore`.

##### iii. Get Your Variable Studio URL

The script needs to know which Onshape document and Variable Studio to update. This is done via the URL in your browser.

1. Open your **copied** Onshape document
2. Click on the **Variable Studio** tab at the bottom of the screen (it appears alongside part studios and assemblies)
3. Once you are on the Variable Studio page, copy the **full URL** from your browser's address bar — it will look something like:
   ```
   https://cad.onshape.com/documents/abc123.../w/def456.../e/ghi789...
   ```
4. Open `Onshape_extension/set_values.py` and paste the URL into the `url` field:
   ```python
   doc = Document.from_url(
       url="https://cad.onshape.com/documents/<your-url-here>"
   )
   ```

> 💡 This URL encodes your document ID, workspace ID, and element ID — it is unique to your copy. Using the original shared link will fail as you do not have write access to it.

<!-- ##### iv. Set the Equations File

In `set_values.py`, make sure the equations file name matches the one generated by the optimizer in Step 2. For SSPG this will be:

```python
variables_to_set = parse_variable_file("sspg_equations.txt")
```

Update the filename if you are running a different gearbox type (e.g., `cpg_equations.txt`). -->

##### iv. Run the Script

From the root of the repository:

```bash
cd Onshape_extension
python3 set_values.py
```

The script will print the variable values before and after the update so you can confirm the changes were applied correctly:

```text
=== BEFORE ===
{ ... current variable values ... }

=== SETTING VARIABLE ===
[POST] /api/variables/d/.../w/.../e/.../variables  →  200

=== AFTER ===
{ ... updated variable values ... }
```

> ⚠️ A `200` status does not always mean the update succeeded — Onshape returns 200 even for malformed payloads. Always check the `AFTER` output to confirm your variables were updated as expected.

---

### Step 7: 3D-print and Assemble
* **3D Printing:** Export the updated plastic parts to `.STL` format.
* **Bearings:** Check the updated CAD model to identify which standard bearings are required for your specific configuration.

----

This framework provides the following features:
1. **Optimize planetary gearbox** parameters for a **given motor** across the following gearbox types:
      - Single Stage Planetary Gearbox (SSPG),
      - Compound Planetary Gearbox (CPG),
      - Wolfrom Planetary Gearbox (3K)(WPG), and
      - Double Stage Planetary Gearbox (DSPG).

2. Perform multi-objective optimization to **minimize actuator mass** and **axial width** while **maximizing efficiency**.
3. **Automatically generate parametric actuator CAD** from optimization results, enabling direct **3D printing without manual redesign**.

----

## ✅ Supported Hardware

### Supported Motors
| Motor Code | Description |
| :--- | :--- |
| **U8** | T-motor U8 |
| **U10** | T-motor U10+ |
| **U12** | T-motor U12 |
| **MN8014** | T-motor MN8014 |
| **VT8020** | Vector Techniques 8020 |
| **MAD_M6C12**| MAD Components M6C12 |

### Supported Gearbox Topologies
| Type | Description |
| :--- | :--- |
| **sspg** | Single-Stage Planetary Gearbox |
| **cpg** | Compound Planetary Gearbox |
| **wpg** | Wolfrom Planetary Gearbox (3K) |
| **dspg** | Double-Stage Planetary Gearbox |

---

## 📄 Citation

If you use this framework in your research, please cite:

```bibtex
@misc{singh2025compact,
      title={COMPAct: Computational Optimization and Automated Modular design of Planetary Actuators}, 
      author={Aman Singh and Deepak Kapa and Suryank Joshi and Shishir Kolathaya},
      year={2025},
      eprint={2510.07197},
      archivePrefix={arXiv},
      primaryClass={cs.RO},
      url={https://arxiv.org/abs/2510.07197}, 
}
```
