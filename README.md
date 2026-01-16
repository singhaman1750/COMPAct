# COMPAct Framework

**Paper:** *COMPAct: Computational Optimization and Automated Modular design of Planetary Actuators*

---

## ⚙️ Requirements
1. `numpy`, `sys`, `os`, `json` – for optimization framework  
2. `matplotlib`, `pandas` – for plotting  
3. **SolidWorks 2024 or higher** – for CAD automation  

---

## ▶️ Running Instructions

### 🔹 Run Optimization Only
```bash
python Opt_singleStagePlanetaryGBOptimization.py
python Opt_doubleStagePlanetaryGBOptimization.py
python Opt_compoundPlanetaryGBOptimization.py
python Opt_wolfromPlanetaryGBOptimization.py
```
Results will be saved in the **`results/` folder** under each motor subfolder.

---

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
