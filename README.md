# # Smart City Traffic Signal Optimization
### # AI-Driven Traffic Management using Constraint Satisfaction Problems (CSP)

This repository features a CSP model designed to manage real-time traffic signal control across 20 major city intersections. The goal is to minimize urban congestion, prevent gridlocks, and ensure "green waves" for emergency vehicles through adaptive AI control.

---

# # Key Features
* **Priority Routing**: Implements hard constraints to ensure emergency vehicles (ambulances, fire trucks) receive minimum-delay routes.
* **Adaptive Signal Timings**: Dynamically calculates optimal green, red, and yellow durations every 5 minutes based on vehicle counts and speeds.
* **Constraint Engineering**:
    * **Hard Constraints**: No conflicting green lights, bus schedule adherence, and maximum wait cycle limits.
    * **Soft Constraints**: Minimizing fuel consumption and maintaining fairness across city districts.
* **Visual Simulation**: Includes an animated solution representing the $4\times4$ intersection grid and vehicle flow.

---

# # Technical Toolbox
* **Modeling**: Constraint Satisfaction Problems (CSP).
* **Dynamic Variables**: Real-time traffic volume, weather conditions, and road closures.

---

# # Developer Information
* **Developer**: Muhammad Subhan Shahid
* **Affiliation**: FAST-NUCES