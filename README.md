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

## COMPAct Flowchart

<p align="center">
  <img src="images/COMPAct_intro_full.png" alt="Flowchart of COMPAct: Actuator Design Framework">
</p>


---

## Quick Start Guide

#### **Setup & Installations**
* **Step 1:** [Setup & Requirements](#step-1-setup--requirements)
* **Step 2:** [Installation](#step-2-installation)
* **Step 3:** [CAD Automation Setup](#step-3-cad-automation-setup-optional)

#### **Optimization & Automated design generation**
* **Step 4:** [Run Optimization](#step-4-run-optimization)
* **Step 5:** [View Results](#step-5-view-results)
* **Step 6:** [Generate Automated CAD designs](#step-6-generate-automated-cad-designs)
* **Step 7:** [3D-print and Assemble](#step-7-3d-print-and-assemble)

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
pip install -r requirements.txt
```

---

### Step 3: CAD Automation Setup (Optional)

### Option A: *SolidWorks (Local)*

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

### Option B: *Onshape (Cloud-based)*

If you prefer not to use SolidWorks, the CAD models are also available on Onshape. No extraction or local files needed.

#### 1. SSPG (Single-Stage Planetary Gearbox)
[COPY PASTE THE LINK IF HYPERLINK DOESN'T OPEN] 

👉 **[Open SSPG in Onshape](https://cad.onshape.com/documents/c1aac326515ba734f63b9b3f/w/f9cccd7b90ce6d7934076c7c/e/11d494d64974a13f1ae2def2?renderMode=0&leftPanel=false&uiState=69ba77262aa7d6ac3cb56ff9)**


👉 **[Open CPG in Onshape](https://cad.onshape.com/documents/dabf50453c93c1c427cef77a/w/58e59ba240adf6d2a07794cc/e/2fd7bc338e9316193d1a2f79)**


👉 **[Open WPG in Onshape](https://cad.onshape.com/documents/f63553f1c266228274914c8c/w/f5b45617c0141f8d43fbf21e/e/1c09941ddaf2e9f39000d746?renderMode=0&uiState=6aba11dd60649941dfd86f04)**


👉 **[Open DSPG in Onshape](https://cad.onshape.com/documents/b8d43d150fb932ea649dcd0f/w/aaa3fcc8da584cc207374389/e/12e148469fa8eb5b917f5bb1?renderMode=0&uiState=69e2408b879d9edde70b5d36)**

👉 **[Open IDSPG in Onshape](https://cad.onshape.com/documents/bfc847aa97321639994fa267/w/e42f2a8d3124414ae728bb05/e/19b7631b19424696aeb05c64?renderMode=0&uiState=6ad0b2d2fb0e57926652caba)**

👉 **[Open ISSPG OutBearing in Onshape](https://cad.onshape.com/documents/bf5f13d9187efab731a95ba7/w/1261f6088846b1d6dd38ea32/e/9442fa2e352d23d6eb88bc6e?renderMode=0&uiState=6a4e2ba1c2bd25dd66621fae)**
```
https://cad.onshape.com/documents/bf5f13d9187efab731a95ba7/w/1261f6088846b1d6dd38ea32/e/9442fa2e352d23d6eb88bc6e?renderMode=0&uiState=6a4e2ba1c2bd25dd66621fae
```

👉 **[Open ISSPG InBearing in Onshape](https://cad.onshape.com/documents/9fa91e98fe82c4e544284d41/w/828f637e6a1fef0940224c5c/e/c80b77fbcf87c09b3b593c8a?renderMode=0&uiState=6a4e2b7864f03bde749b5369)**
```
https://cad.onshape.com/documents/9fa91e98fe82c4e544284d41/w/828f637e6a1fef0940224c5c/e/c80b77fbcf87c09b3b593c8a?renderMode=0&uiState=6a4e2b7864f03bde749b5369
```

👉 **[Open INCPG Dependent in Onshape](https://cad.onshape.com/documents/3e794c46f172f3b02cfa18e7/w/dfc878270d998ca1ea8223c8/e/c324bd70f7c31566e927c1f7?renderMode=0&uiState=6a4e2aa99c74fab5cc5dc0f1)**
```
https://cad.onshape.com/documents/3e794c46f172f3b02cfa18e7/w/dfc878270d998ca1ea8223c8/e/c324bd70f7c31566e927c1f7?renderMode=0&uiState=6a4e2aa99c74fab5cc5dc0f1
```

👉 **[Open INCPG Independent in Onshape](https://cad.onshape.com/documents/2519b08c3c51bbdac1923e25/w/095a9ef04c28fad58dcdbe6c/e/7335150ff09908ff2cd1b9b2?renderMode=0&uiState=6a4e2b048984a6ae63298aa8)**
```
https://cad.onshape.com/documents/2519b08c3c51bbdac1923e25/w/095a9ef04c28fad58dcdbe6c/e/7335150ff09908ff2cd1b9b2?renderMode=0&uiState=6a4e2b048984a6ae63298aa8
```

👉 **[Open INSSPG_Dependent in Onshape](https://cad.onshape.com/documents/97af418b118f30715235cd6a/w/253f8dd6e8e424cb9f7bb1dd/e/bcd4cd4dc6121c4e6915a50e?renderMode=0&leftPanel=false&uiState=6a4e2b9a82db92af62774962)**
```
https://cad.onshape.com/documents/97af418b118f30715235cd6a/w/253f8dd6e8e424cb9f7bb1dd/e/bcd4cd4dc6121c4e6915a50e?renderMode=0&leftPanel=false&uiState=6a4e2b9a82db92af62774962
```

👉 **[Open INSSPG_Independent in Onshape](https://cad.onshape.com/documents/e0cb8ed6bb2b36cfcadffcf4/w/a5de456488f59701ab182711/e/b8af8d5da69957495c24591f?renderMode=0&leftPanel=false&uiState=6a4e2ac13b9f34e29a45f140)**
```
https://cad.onshape.com/documents/e0cb8ed6bb2b36cfcadffcf4/w/a5de456488f59701ab182711/e/b8af8d5da69957495c24591f?renderMode=0&leftPanel=false&uiState=6a4e2ac13b9f34e29a45f140 
```

👉 **[Open ICPG in Onshape](https://cad.onshape.com/documents/1cec852caa1080765682d3d0/w/9b7913f319aab1fd6ef5de45/e/f9d06c56e5c97df7f6c68aa9?renderMode=0&uiState=6a4e2d38c2bd25dd666223f5)** 
```
https://cad.onshape.com/documents/1cec852caa1080765682d3d0/w/9b7913f319aab1fd6ef5de45/e/f9d06c56e5c97df7f6c68aa9?renderMode=0&uiState=6a4e2d38c2bd25dd666223f5 
```
👉 **[Open INWPG_Dependent in Onshape](https://cad.onshape.com/documents/a5e4d1f2afed2d53000ac6c5/w/fa005d0cbd6ffa3820332b7d/e/64e86c89d3ac5b23fd7711ba?renderMode=0&uiState=6abdf521224826f406f22e25)**
```
https://cad.onshape.com/documents/a5e4d1f2afed2d53000ac6c5/w/fa005d0cbd6ffa3820332b7d/e/64e86c89d3ac5b23fd7711ba?renderMode=0&uiState=6abdf521224826f406f22e25
```

👉 **[Open INWPG_Independent in Onshape](https://cad.onshape.com/documents/a5ebf8aa022054aedcbab90e/w/226eaf19e9c48cb8a6efbe49/e/e7a9e7fa0a60f50822757623?renderMode=0&uiState=6abdf8eba830cf066b5e0314)**
```
https://cad.onshape.com/documents/a5ebf8aa022054aedcbab90e/w/226eaf19e9c48cb8a6efbe49/e/e7a9e7fa0a60f50822757623?renderMode=0&uiState=6abdf8eba830cf066b5e0314
```

👉 **[Open INDSPG in Onshape](https://cad.onshape.com/documents/082ad023b75b2274bed0f04d/w/29fd6b162304a5c614568daf/e/f5c1a1cba8355822de1c14c1?renderMode=0&uiState=6aaa9fc1dca6951f9bcace74)** 
```
https://cad.onshape.com/documents/082ad023b75b2274bed0f04d/w/29fd6b162304a5c614568daf/e/f5c1a1cba8355822de1c14c1?renderMode=0&uiState=6aaa9fc1dca6951f9bcace74
```

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
python actOpt.py --motor <motor> --gb_type <gearbox_type> --gr <ratio>
```
* **`--motor`**: any motor name in [`config_files/motors.json`](config_files/motors.json):
  framed motors (e.g. U8_Lite, U10_Plus_KV80, MN8014, VT8020_PRO, MAD_M6C12_KV170) for sspg, cpg, wpg, dspg;
  frameless outrunners (RO100, RO80, RO60) for icpg, isspg, idspg;
  frameless inrunners (RI100, RI80) for insspg, incpg, inwpg, indspg
* **`--gb_type`**: sspg, cpg, dspg, wpg , icpg , insspg_type_1 {Independent} , insspg_type_2 {Dependent} 
* **`--gr`**: Must be a value > 2.

**Example:**
To optimize a **RO100** with a **Internal-Compound-Planetary Gearbox** and a **ratio of 6.5**:

```bash
python actOpt.py --motor RO100 --gb_type icpg --gr 6.5
```

---
**Example:**
To optimize a **RI100** with a **Inrunner-Dependent-Single-Stage Planetary Gearbox** and a **ratio of 6.5**:

```bash
python actOpt.py --motor RI100 --gb_type insspg_type_2 --gr 6.5
```

---
**Example:**
To optimize a **RI100** with a **Inrunner-Independent-Single-Stage Planetary Gearbox** and a **ratio of 6.5**:

```bash
python actOpt.py --motor RI100 --gb_type insspg_type_1 --gr 6.5
```

**Syntax for ISSPG:**  
```bash
python actOpt.py --motor <motor> --gb_type <gearbox_type> --gr <ratio>
```
* **`--gb_type`**: isspg_inside (InBearing design), isspg_compact (OutBearing design)
* **`--motor`**: RO80, RO100
* **`--gr`**: Must be a value > 2.

**Example:**
To optimize **RO100** with an **Internal Single-Stage Planetary Gearbox InBearing** and a **ratio of 6.5**:

```bash
python actOpt.py --motor RO100 --gb_type isspg_inside --gr 6.5
```

**Syntax for INCPG:**
```bash
python actOpt.py --motor <motor> --gb_type <gearbox_type> --gr <ratio>
```
* **`--gb_type`**: incpg_independent, incpg_dependent
* **`--motor`**: RI100
* **`--gr`**: Must be a value > 2.
  
**Example:**
To optimize **RI100** with an **Inrunner Compound Planetary Gearbox Independent** and a **ratio of 6.5**:

```bash
python actOpt.py --motor RI100 --gb_type incpg_independent --gr 6.5
```

---

### Step 5: View Results
The script will output the optimal geometric parameters directly in the terminal:

```text
Running optimization:
  Motor       : U8_Lite
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
  
#### MASS ANALYSIS
```
https://docs.google.com/spreadsheets/d/1QYUox6946nNlciWFAQ1L-EqQNLNdAT6GV0OtC5uI0eU/edit?usp=sharing
```
---

### Step 6: Generate Automated CAD designs

There are two ways to apply the optimization results to a CAD model — using **SolidWorks** (local) or **Onshape** (cloud-based). Both use the same equations file generated in Step 2.

#### Option A: SolidWorks (Local)

**NOTE:** _If you skipped the CAD extraction in Step 2, you cannot use this option._

1.  Open **SolidWorks**.
2.  Open the assembly file (`.SLDASM`) for your specific gearbox type:
    * **SSPG:** `CADs/SSPG/sspg_actuator/sspg_actuator/sspg_actuator.SLDASM`
    * *(Paths for CPG, DSPG, and WPG follow the same folder pattern)*
3.  Click the **Rebuild** (Traffic Light) icon.
4.  The 3D model will automatically update to reflect the calculated parameters.

---

#### Option B: Onshape (Cloud-based)

This extension lets you push optimization results directly to a parametric Onshape CAD model via the Onshape REST API — no SolidWorks or local CAD files required.

##### i. Make a Copy of the Onshape Document

If you haven't already done so in the extraction step above, open the shared Onshape document and make your own copy:

👉 **[Open SSPG in Onshape](https://cad.onshape.com/documents/c1aac326515ba734f63b9b3f/w/f9cccd7b90ce6d7934076c7c/e/11d494d64974a13f1ae2def2?renderMode=0&leftPanel=false&uiState=69ba77262aa7d6ac3cb56ff9)**

👉 **[Open CPG in Onshape](https://cad.onshape.com/documents/dabf50453c93c1c427cef77a/w/58e59ba240adf6d2a07794cc/e/2fd7bc338e9316193d1a2f79)**

👉 **[Open WPG in Onshape (old)](https://cad.onshape.com/documents/ad699ddbc25bac5c32e33135/w/758de9a639163030bca8fa73/e/4cb254c85cc1f2d31a39a63a?renderMode=0&uiState=69d8cb5213bdc8529ffa3f3c)**

👉 **[Open DSPG in Onshape](https://cad.onshape.com/documents/b8d43d150fb932ea649dcd0f/w/aaa3fcc8da584cc207374389/e/12e148469fa8eb5b917f5bb1?renderMode=0&uiState=69e2408b879d9edde70b5d36)**

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

##### iii. List Your Models Once

Each gearbox type has its own Onshape model. Tell the script where your copies are — once:

1. Copy `Onshape_extension/onshape_models.example.json` to `Onshape_extension/onshape_models.json`
   (this file is personal and is not committed).
2. For each gearbox type you use: open your **copied** document, click the **Variable Studio** tab at
   the bottom of the screen, copy the **full URL** from the address bar and paste it next to that
   gearbox type:
   ```json
   "sspg": "https://cad.onshape.com/documents/<did>/w/<wid>/e/<eid>",
   ```
   Leave types you don't use empty. Variants (e.g. `isspg_inside` / `isspg_compact`) each need their own model.

> 💡 The URL must be from your copy and contain `/w/` (a workspace). The original shared link will fail
> because you do not have write access to it.

##### iv. Optimise and Update the CAD in One Command

Add `--onshape` to the optimisation command:

```bash
python actOpt.py --motor U8_Lite --gb_type sspg --gr 6.5 --onshape
```

After a successful run the script:
1. saves an Onshape **version** of your model (a snapshot you can roll back to from the version history),
2. writes the new values into the model's Variable Studio,
3. reads them back and lists any variable that did not take (`Onshape: 87 of 87 variables set`).

If no design is found, or the model is not set up, the optimisation result is still saved and Onshape is
left unchanged. To push an existing result again without re-optimising:

```bash
python Onshape_extension/set_values.py --gb_type sspg
```

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
All motors and their data (with sources) are in [`config_files/motors.json`](config_files/motors.json).
Gears are sized with each motor's peak torque at its no-load speed (48 V); set `"rating"` in that file to change it.

| Motor type | Motors |
| :--- | :--- |
| **Framed outrunner** (sspg, cpg, wpg, dspg) | T-Motor U8 Lite / Lite L / II / II Lite / II PRO, U10 Plus KV80, U10 II, MN5008, MN6007 II, MN7005, MN8012, MN8014, MN8017, MN1005 V2; MAD M6C12, M6C10, M6C08, M6C06, M6C06 V3, 1005, 7005, 8118, 5008, 5010; Vector 8008 SL, 8015 SL, 10005 SL, 8020 PRO |
| **Frameless outrunner** (icpg, isspg, idspg) | RO100, RO80, RO60 |
| **Frameless inrunner** (insspg, incpg, inwpg, indspg) | RI100, RI80 |

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
