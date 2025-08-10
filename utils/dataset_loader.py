"""
data_loader.py

Load CSV-format datasets into a SystemState object for ELCO_simulation.
This script reads pre-generated datasets (small, medium, large) from the specified root path,
instantiates all system entities (SEC servers, base stations, IoT devices, functions, tasks, and network topology),
and assembles them into a SystemState object for simulation.

Author: Your Name
"""

import csv
from pathlib import Path
from core.system_models.network_model import BaseStation, SECServer, IoTDevice, FunctionType, FunctionTask, SECNetwork
from core.system_state import SystemState


def load_dataset(scale: str = "large", datasets_root: str = "datasets") -> SystemState:
    """
    Load a dataset of the given scale into a SystemState object.

    Args:
        scale (str): Dataset scale ("small", "medium", or "large"). Default is "large".
        datasets_root (str): Path to the root folder containing datasets.

    Returns:
        SystemState: Fully populated system state ready for simulation.
    """
    root = Path(datasets_root) / scale
    ss = SystemState()

    # 1) Load SEC server data
    sec_path = root / "sec_server.csv"
    with open(sec_path, newline='') as f:
        for r in csv.DictReader(f):
            sec = SECServer(id=int(r["id"]),
                            comp_resource=float(r["comp_resource"]),
                            memory=float(r["memory"]),
                            backhaul_bw=float(r["backhaul_bw"]))
            ss.add_sec_server(sec)

    # 2) Load base station data and associate with SEC servers
    bs_path = root / "base_station.csv"
    with open(bs_path, newline='') as f:
        for r in csv.DictReader(f):
            bs = BaseStation(id=int(r["id"]))
            ss.add_base_station(bs=bs, associated_sec_id=int(r["associated_sec_id"]))

    # 3) Load IoT device data and associate with base stations
    iot_path = root / "iot_device.csv"
    with open(iot_path, newline='') as f:
        for r in csv.DictReader(f):
            iot = IoTDevice(id=int(r["id"]),
                            comp_resource=float(r["comp_resource"]),
                            tx_power=float(r["tx_power"]),
                            bandwidth=float(r["bandwidth"]),  # Hz
                            channel_gain=float(r["channel_gain"]),
                            noise_power=float(r["noise_power"]))
            ss.add_iot_device(iot=iot, associated_bs_id=int(r["associated_bs_id"]))

    # 4) Load function type metadata
    ft_path = root / "function_type.csv"
    with open(ft_path, newline='') as f:
        for r in csv.DictReader(f):
            ft = FunctionType(id=int(r["id"]), image_size=float(r["image_size"]))
            ss.add_function_type(ft)

    # 5) Load cached function info for SEC servers
    cf_path = root / "cached_function.csv"
    if cf_path.exists():
        with open(cf_path, newline='') as f:
            for r in csv.DictReader(f):
                sec = ss.get_sec_server_instance(int(r["sec_id"]))
                sec.cached_functions.add(int(r["function_type_id"]))

    # 6) Load function task data and associate with IoT devices
    tasks_path = root / "function_task.csv"
    with open(tasks_path, newline='') as f:
        for r in csv.DictReader(f):
            func_type = ss.function_types[int(r["func_type_id"])]["instance"]
            func = FunctionTask(id=int(r["id"]),
                                data_size=float(r["data_size"]),
                                workload=float(r["workload"]),
                                invocations=int(r["invocations"]),
                                func_type=func_type)
            ss.add_function(func=func, associated_iot_id=int(r["associated_iot_id"]))

    # 7) Load SEC network topology (servers + connections)
    sn = SECNetwork()
    # Add SEC server objects to the network
    for sec_id, sec_record in ss.sec_servers.items():
        sn.add_server(server=sec_record["instance"])

    net_path = root / "sec_network.csv"
    if net_path.exists():
        with open(net_path, newline='') as f:
            for r in csv.DictReader(f):
                sn.add_connection(int(r["server_id1"]), int(r["server_id2"]),
                                  float(r["latency"]), float(r["bandwidth"]))
    ss.set_sec_network(sn)

    return ss
