"""
generate_datasets.py

This script generates CSV-format datasets for the ELCO_simulation project.

It creates three predefined dataset scales: small, medium, and large.
Each dataset is stored under datasets/<scale_name>/ and contains the following files:

- base_station.csv          : Mapping of base station IDs to their associated SEC server IDs
- sec_server.csv            : SEC server hardware specifications
- iot_device.csv            : IoT device specifications and associated base stations
- function_type.csv         : Function type definitions and container image sizes
- cached_function.csv       : Mapping of SEC servers to cached function types
- function_task.csv         : Function task details including data size, workload, and associated IoT devices
- sec_network.csv           : SEC interconnection network topology (latency, bandwidth)
- metadata.txt              : Dataset configuration details and generation parameters

All datasets are generated using a fixed random seed per scale to ensure reproducibility.
The script does not require any third-party dependencies and uses Python's built-in csv module.
"""

import csv
import random
from pathlib import Path
from config import *


def write_csv(path, header, rows):
    """Write a CSV file with a given header and row list."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def generate_for_scale(scale_name, cfg):
    """Generate dataset files for a given scale configuration."""
    random.seed(cfg["seed"])
    out_dir = Path(__file__).resolve().parent.parent / "datasets" / scale_name
    out_dir.mkdir(parents=True, exist_ok=True)

    # Base stations and SEC servers: each base station is associated with one SEC server
    base_stations = []
    sec_servers = []
    for i in range(cfg["bs_and_sec"]):
        bs_id = i
        sec_id = i
        associated_sec_id = sec_id
        base_stations.append([bs_id, associated_sec_id])

        comp_resource = random.choice(SEC.get('SEC_CPU'))  # CPU capacity in MHz * cores
        memory = random.choice(SEC.get('SEC_MEM'))  # Memory in MB
        backhaul_bw = random.choice(SEC.get('SEC_BH_BW'))  # Backhaul bandwidth in Mbps
        sec_servers.append([sec_id, comp_resource, memory, backhaul_bw])
    write_csv(out_dir / "base_station.csv", ["id", "associated_sec_id"], base_stations)
    write_csv(out_dir / "sec_server.csv", ["id", "comp_resource", "memory", "backhaul_bw"], sec_servers)

    # IoT devices
    iot_devices = []
    _headers = ["id", "comp_resource", "tx_power", "bandwidth", "channel_gain", "noise_power", "associated_bs_id"]
    for i in range(cfg["iot_device"]):
        iot_id = i
        comp_resource = random.randint(500, 1000)  # CPU capacity in MHz
        tx_power = random.choice([0.1, 0.2])  # Transmission power in W
        bandwidth = int(random.choice([1_000_000, 2_000_000, 5_000_000]))  # Channel bandwidth in Hz
        channel_gain = random.uniform(1e-6, 5e-5)
        noise_power = random.uniform(1e-8, 1e-6)
        associated_bs_id = random.choice([b[0] for b in base_stations])
        iot_devices.append([iot_id, comp_resource, tx_power, bandwidth, channel_gain, noise_power, associated_bs_id])
    write_csv(out_dir / "iot_device.csv", _headers, iot_devices)

    # Function types
    function_types = []
    for i in range(cfg["function_type"]):
        ft_id = i
        image_size = random.randint(50, 150)  # Container image size in MB
        function_types.append([ft_id, image_size])
    write_csv(out_dir / "function_type.csv", ["id", "image_size"], function_types)

    # Cached functions: each SEC caches up to min(3, total_function_types)
    cached_functions = []
    for sec in sec_servers:
        sec_id = sec[0]
        k = min(3, len(function_types))
        sampled = random.sample([ft[0] for ft in function_types], k=k)
        for ft_id in sampled:
            cached_functions.append([sec_id, ft_id])
    write_csv(out_dir / "cached_function.csv", ["sec_id", "function_type_id"], cached_functions)

    # Function tasks
    function_tasks = []
    _headers = ["id", "data_size", "workload", "invocations", "func_type_id", "associated_iot_id"]
    for i in range(cfg["function_task"]):
        task_id = i
        data_size = random.choice(FUNC.get('DATA_SIZE'))  # Input data size in MB
        workload = random.choice(FUNC.get('WORKLOAD'))  # Computation workload in MHz
        invocations = random.choice(FUNC.get('INVOCATION'))  # Invocation count

        # Assign to a random FunctionType
        func_type = random.choice(function_types)[0]

        # Assign to a random IoTDevice
        associated_iot_id = random.choice([iot[0] for iot in iot_devices])

        function_tasks.append([task_id, data_size, workload, invocations, func_type, associated_iot_id])
    write_csv(out_dir / "function_task.csv", _headers, function_tasks)

    # SEC network: undirected edges between SEC servers (fully connected)
    sec_network = []
    for i in range(len(sec_servers)):
        for j in range(i + 1, len(sec_servers)):
            s1 = sec_servers[i][0]
            s2 = sec_servers[j][0]
            latency = round(random.uniform(0.02, 0.5), 6)  # Latency in seconds
            bandwidth = random.randint(100, 1000)  # Bandwidth in Mbps
            sec_network.append([s1, s2, latency, bandwidth])
    write_csv(out_dir / "sec_network.csv", ["server_id1", "server_id2", "latency", "bandwidth"], sec_network)

    # Metadata file
    metadata = [["seed", cfg["seed"]],
                ["bs_and_sec", cfg["bs_and_sec"]],
                ["iot_device", cfg["iot_device"]],
                ["function_type", cfg["function_type"]],
                ["function_task", cfg["function_task"]]]

    with open(out_dir / "metadata.txt", 'w', encoding='utf-8') as f:
        for key, value in metadata:
            f.write(f"{key}: {value}\n")

    print(f"Generated dataset '{scale_name}' in {out_dir}")


def main():
    for scale, cfg in DATASET_SIZES.items():
        generate_for_scale(scale, cfg)


if __name__ == "__main__":
    main()
