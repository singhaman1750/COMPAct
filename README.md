# COMPAct Framework

**Paper:** [*COMPAct: Computational Optimization and Automated Modular design of Planetary Actuators*](https://www.arxiv.org/abs/2510.07197)

The **COMPAct Framework** streamlines the design of robotic actuators by automating the calculation of optimal gear parameters and updating 3D CAD models.

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

## 💻 Setup & Requirements

### System Requirements
* **Python 3.x**
* **SolidWorks 2024** (or higher) – *Required for CAD automation features.*

### Recommended Terminal
* **Windows:** [Git Bash](https://git-scm.com/downloads) is highly recommended.
* **Linux/macOS:** Default terminal.

### 1. Installation
Clone the repository and install the dependencies:

```bash
# Clone the repository
git clone https://github.com/singhaman1750/COMPAct-Actuator_design_framework.git

# Enter the directory
cd COMPAct-Actuator_design_framework 

# Install required packages
pip install numpy matplotlib pandas
```

### 2. Extract CAD Files (Optional)
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

---

## 🚀 Usage

### Step 1: Run Optimization
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

### Step 2: View Results
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

Detailed parameter files (used by SolidWorks) are automatically generated in the following locations:

* **SSPG:** `CADs/SSPG/sspg_equations.txt`
* **CPG:** `CADs/CPG/cpg_equations.txt`
* **DSPG:** `CADs/DSPG/dspg_equations.txt`
* **WPG:** `CADs/WPG/wpg_equations.txt`

### Step 3: CAD Automation
**NOTE:** _If you skipped the CAD extraction, you can stop at Step 2._

1.  Open **SolidWorks**.
2.  Open the assembly file (`.SLDASM`) for your specific gearbox type:
    * **SSPG:** `CADs/SSPG/sspg_actuator/sspg_actuator/sspg_actuator.SLDASM`
    * *(Paths for CPG, DSPG, and WPG follow the same folder pattern)*
3.  Click the **Rebuild** (Traffic Light) icon.
4.  The 3D model will automatically update to reflect the calculated parameters.

### Step 4: Manufacturing
* **3D Printing:** Export the updated plastic parts to `.STL` format.
* **Bearings:** Check the updated CAD model to identify which standard bearings are required for your specific configuration.

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
      url={[https://arxiv.org/abs/2510.07197](https://arxiv.org/abs/2510.07197)}, 
}
```
