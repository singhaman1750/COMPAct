# COMPAct Framework

**Paper:** [*COMPAct: Computational Optimization and Automated Modular design of Planetary Actuators*](https://www.arxiv.org/abs/2510.07197)

---

## Recommended Software Setup

- **Windows:** Required for **CAD automation**  
  - Terminal: **Git Bash** ([Install video](https://youtu.be/UdhAb0t5iHw?si=pdl7PfhMkCZuKOgV))
- **Linux / macOS:** Use if **not** running CAD automation  
  - Terminal: **Default terminal**

---

## ⚙️ Requirements
1. `numpy`, `sys`, `os`, `json` – for optimization framework  
2. `matplotlib`, `pandas` – for plotting  
3. **SolidWorks 2024 or higher** – for _**CAD automation**_  

---

## 🚀 Quick Start Guide (Actuator Optimization Without CAD Automation)

#### 1. Install Prerequisites

Ensure you have **Python 3** installed. Install the required Python packages using:

    pip install numpy matplotlib pandas

**Note:** `sys`, `os`, and `json` are part of Python’s standard library and do not need separate installation.

#### 2. Clone this Repository

```
git clone https://github.com/singhaman1750/COMPAct-Actuator_design_framework.git
```

#### 3. Running the Optimization Script

```
python actOpt.py <motor_name> <gearbox_type> <gear_ratio>
```

Replace `<motor_name>` with name of motors, `<gearbox_type>` with types of gearbox, and `<gear_ratio>` with gear ratio numbers

1. `<motor_name>`: U8, U10, U12, MN8014, VT8020, MAD_M6C12
2. `<gearbox_type>`: sspg, cpg, wpg, dspg
3. `<gear_ratio>`: $2 <$ `<gear_ratio>` < $\infty$

#### Example

    python actOpt.py U8 sspg 6.5

This command runs the optimization for a **T-motor U8** with a **Single-Stage Planetary Gearbox** and a **gear ratio of 6.5**.

---

### 3. Available Options

#### ✅ Supported Motors

| Motor Code | Motor Description |
|------------|------------------|
| U8 | T-motor U8 |
| U10 | T-motor U10+ |
| U12 | T-motor U12 |
| MN8014 | T-motor MN8014 |
| VT8020 | Vector Techniques 8020 |
| MAD_M6C12 | MAD Components M6C12 |

#### ⚙️ Supported Gearbox Types

| Gearbox Code | Gearbox Description |
|--------------|--------------------|
| sspg | Single-Stage Planetary Gearbox |
| cpg | Compound Planetary Gearbox |
| wpg | Wolfrom Planetary Gearbox (3K) |
| dspg | Double-Stage Planetary Gearbox |

Results will be saved in the **`results/` folder** under each motor subfolder.

---

### 2. Unzip the CAD files

1. Go to the CADs folder

2. Unzip the CAD files:  
   - `CADs/SSPG/sspg_actuator.zip`  
   - `CADs/DSPG/dspg_actuator.zip`  
   - `CADs/CPG/cpg_actuator.zip`  
   - `CADs/WPG/wpg_actuator.zip` 

### 🔹 Automate CAD
1. Unzip the CAD files:  
   - `CADs/SSPG/SSPG.zip`  
   - `CADs/DSPG/DSPG.zip`  
   - `CADs/CPG/CPG.zip`  
   - `CADs/WPG/WPG.zip`  

2. Running any of the optimization scripts (e.g. `python <filename>`) generates:  
   - **Results**  
   - A **parameter text file** in  
     `CADs/<Gearbox_type>/Equations_files/<motor_name>/`

3. To build the CAD:  
   - Copy the generated parameter file  
   - Paste it into:  
     ```
     CADs/<Gearbox_type>/<gearbox_type>_equations.txt
     ```
4. Open the corresponding CAD model in **SolidWorks 2024 (or higher)**, and rebuild.  
   SolidWorks will automatically update the model using the pasted parameters, generating the optimized gearbox design.

---

### 🔹 Plots
- Plots generated during optimization are stored in the **`plots/` folder**.

### Citations:
```
@misc{singh2025compactcomputationaloptimizationautomated,
      title={COMPAct: Computational Optimization and Automated Modular design of Planetary Actuators}, 
      author={Aman Singh and Deepak Kapa and Suryank Joshi and Shishir Kolathaya},
      year={2025},
      eprint={2510.07197},
      archivePrefix={arXiv},
      primaryClass={cs.RO},
      url={https://arxiv.org/abs/2510.07197}, 
}
```
