# ELCO Simulation Framework

**ELCO** (Energy–Latency Collaborative Offloading) is a simulation framework for evaluating and optimizing task offloading strategies in **SEC (Smart Edge Computing)** networks.
It models IoT devices, base stations, and SEC servers, and implements optimization algorithms to minimize system cost under energy and latency constraints.

---

## 📂 Project Structure

```
ELCO_simulation/
│
├── core/                         # Core simulation logic
│   ├── system_models/            # Mathematical models of system entities
│   │   ├── network_model.py      # SEC network topology, devices, servers, links
│   │   └── ...                   # Other entity definitions
│   ├── system_state.py           # Maintains all instances & their relationships
│   ├── strategic_profile.py      # Decision profile (offloading, scheduling, resource allocation)
│   └── algorithm/                # Optimization algorithms
│       ├── algo_1_LEAO.py        # Latency–Energy Aware Offloading (LEAO)
│       └── algo_2_PGES.py        # Progressive Greedy Energy Scheduling (PGES)
│
├── utils/
│   └── dataset_loader.py         # Loads CSV datasets into SystemState
│
├── scripts/
│   └── generate_datasets.py      # Generates datasets in CSV format
│
├── datasets/                     # Generated datasets
│   ├── small/                    # Small-scale dataset
│   ├── medium/                   # Medium-scale dataset
│   └── large/                    # Large-scale dataset
│
└── main.py                       # Main simulation entry point
```

---

## ⚙️ Workflow

1. **Generate datasets**
   Use the dataset generator to produce network, device, and task configurations.

   ```bash
   python scripts/generate_datasets.py
   ```

   This will create datasets under `datasets/` with three scales: **small**, **medium**, and **large**.

2. **Load dataset & initialize system state**
   The dataset loader reads the CSV files and builds a `SystemState` object containing all entities and their connections.

3. **Run optimization algorithms**
   The framework supports multiple optimization strategies:

   * **LEAO**: Determines whether to offload tasks to SEC servers.
   * **PGES**: Allocates resources and schedules tasks to minimize cost.

4. **Evaluate results**
   After each algorithm step, the system cost and offloading ratio are reported.

---

## 🚀 Example Usage

```bash
python main.py
```

Example output:

```
* IoT_Only total system cost: 1831.8661
* LEAO total system cost: 1431.3511
* Offloading to SEC ratio: 33.00%, 330 / 1000
* PGES total system cost: 1291.2973
```

---

## 📜 Main Components

* **`SystemState`**
  Stores all entities (IoT devices, base stations, SEC servers) and maintains mapping relationships.

* **`StrategicProfile`**
  Manages decision variables (offloading flags, scheduling targets, resource allocations).
  Optimization algorithms modify this profile to improve performance.

* **Algorithms**

  * `algo_1_LEAO`: Selects tasks for offloading to SEC.
  * `algo_2_PGES`: Allocates CPU & memory resources for scheduled tasks.

---
