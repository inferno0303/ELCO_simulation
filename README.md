
## 📘 README.md — ELCO\_simulation

### ⚡ Project: **ELCO\_simulation**

> Energy-Latency Collaborative Offloading (ELCO): Simulation Framework for Edge Function Scheduling

---

### 🌐 Overview

**ELCO\_simulation** is a simulation platform that models, evaluates, and optimizes function task scheduling in **serverless edge computing (SEC)** systems. It implements the full-stack decision pipeline proposed in the **ELCO** framework, supporting:

* Three-tier execution: IoT device, local SEC, collaborative SEC
* Cold start modeling, container caching, wireless transmission
* Optimal resource allocation with discrete constraints
* Multi-objective cost model (latency–energy tradeoff)
* Modular and extensible architecture for algorithms and strategies

---

### 🏗️ Directory Structure

```
ELCO_simulation/
├── .venv/                  # Python virtual environment (not tracked)
├── algorithms/             # Custom scheduling algorithms (e.g., LEAO, PGES, baselines)
├── core/                   # Core simulation engine
│   ├── cost_model.py         # Computes cost_i based on α, β, and resource allocation
│   ├── entity_manager.py     # Entity classes: tasks, devices, servers, function types
│   ├── network_model.py      # Inter-SEC graph structure and routing
│   ├── resource_model.py     # Resource allocation optimizer (continuous + discrete)
│   ├── strategic_profile.py  # Encodes α_i, β_ik decisions per task
│   └── strategy_model.py     # Latency and energy computation for each strategy
│
├── datasets/              # Task profiles, IoT device configs, container metadata
├── results/               # Output folder for metrics, logs, and evaluation results
├── utils/                 # Miscellaneous utilities (e.g., logging, plotting)
│
├── config.py              # Global simulation constants and parameters
├── main.py                # Main entry point to run simulations
├── requirements.txt       # Python package dependencies
└── README.md              # You're here!
```

---

### ⚙️ Installation

1. Set up a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Or use .venv\Scripts\activate on Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

### 🚀 How to Run

```bash
python main.py
```

You can modify the simulation settings in `config.py` (e.g., number of devices, memory-CPU ratio, ω tradeoff weight, cold-start parameters, etc.).

---

### 🧠 Key Components

| Module                 | Description                                                                       |
| ---------------------- | --------------------------------------------------------------------------------- |
| `entity_manager.py`    | Defines `FunctionTask`, `FunctionType`, `IoTDevice`, and `SECServer`              |
| `strategy_model.py`    | Implements latency/energy computation for local, SEC, and collaborative execution |
| `resource_model.py`    | Continuous and discretized optimal memory/CPU allocation                          |
| `cost_model.py`        | Computes unified cost\_i using α\_i and β\_ik                                     |
| `strategic_profile.py` | Manages task scheduling decisions (α, β)                                          |
| `network_model.py`     | Models inter-SEC connectivity and routes                                          |

---

### 📊 Output

Simulation results (e.g., per-task latency, energy, and cost) will be saved to `results/` folder. You can implement visualizers or reporters in `utils/` to generate plots and tables for evaluation.

---

### 📌 Customization Tips

* 🔧 To plug in a new algorithm, add it to `algorithms/` and call it from `main.py`
* 🔁 Modify `strategic_profile.py` to generate fixed or dynamic scheduling profiles
* 🧪 Use `datasets/` to store task traces, server topologies, or real-world configurations

---

### 📄 License

This project is for **academic research and simulation purposes** only. For commercial use, please contact the author.

---

### ✍️ Author

Developed by **xbc8118@github.com**

ELCO: A Collaborative Offloading Framework for Latency and Energy Tradeoffs in Serverless Edge Computing

---

### 🔮 Future Work

* Integration with LEAO or game-theoretic solvers
* Real trace-driven evaluation
* Multi-agent reinforcement learning extensions