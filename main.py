"""
main.py

Main entry point for running the ELCO (Energy-Latency Collaborative Offloading) simulation.

Workflow:
    1. Load the dataset and initialize the system state.
    2. Initialize the baseline strategy (IoT execution only) and evaluate the total cost.
    3. Apply Algorithm 1: LEAO (Latency-Energy-Aware Offloading) to optimize offloading decisions.
    4. Apply Algorithm 2: PGES (Parallel Gradient-based Execution Scheduling) to optimize scheduling and resource allocation.
    5. Output evaluation metrics including total system cost and SEC-side offloading ratio.

Modules used:
    - core.system_models: Definitions of BaseStation, SECServer, IoTDevice, and network entities.
    - core.system_state: SystemState class to represent the entire system snapshot.
    - core.strategic_profile: StrategicProfile class to maintain and update strategies.
    - core.algorithm: Offloading and scheduling optimization algorithms.
    - utils.dataset_loader: Utilities to load datasets from CSV files.

Author: xbc8118
"""

from typing import Dict

from core.system_models.network_model import BaseStation, SECServer, IoTDevice, FunctionType, FunctionTask, SECNetwork
from core.system_state import SystemState
from core.strategic_profile import StrategicProfile
from utils.dataset_loader import load_dataset

from core.algorithm.algo_1_LEAO import algo_1_LEAO
from core.algorithm.algo_2_PGES import algo_2_PGES
from core.other_algorithms.randomly_offloading import RandomlyOffloading


def main():
    """Run the ELCO simulation with a predefined dataset and optimization workflow."""

    # === Step 1: Load dataset and initialize system state ===
    ss: SystemState = load_dataset("large", datasets_root="datasets")

    # === Step 2: Baseline evaluation (IoT execution only) ===
    sp = StrategicProfile(system_state=ss)
    sp.reset_strategy()  # All IoT devices execute tasks locally
    print(f'* IoT_Only total system cost: {sp.calc_total_cost():.4f}')

    # === Step 3: Algorithm 1 - LEAO: Optimize offloading decisions ===
    alpha: Dict[str, int] = algo_1_LEAO(ss=ss)

    # Update strategy profile based on LEAO results
    for func_id, offloading in alpha.items():
        if offloading == 1:
            sp.strategy[func_id]['offloading'] = offloading
            sp.strategy[func_id]['scheduling'] = ss.f2s_mapping(func_id=func_id).id  # Assign to local SEC
    print(f'* LEAO total system cost: {sp.calc_total_cost():.4f}')

    # Offloading ratio statistics
    offloading_count = sum(1 for _, val in sp.strategy.items() if val['offloading'] == 1)
    print(f'* Offloading to SEC ratio: {offloading_count / len(sp.strategy) * 100:.2f}%, '
          f'{offloading_count} / {len(sp.strategy)}')

    # === Step 4: Algorithm 2 - PGES: Optimize scheduling & resource allocation ===
    beta, mem_alloc, cr_alloc = algo_2_PGES(ss=ss, sp=sp)

    # Update strategy profile based on PGES results
    for func_id, scheduling in beta.items():
        if sp.strategy[func_id]['offloading'] == 1:
            sp.strategy[func_id]['scheduling'] = scheduling
    print(f'* PGES total system cost: {sp.calc_total_cost():.4f}')

    # 其他算法：随机卸载
    print("============")
    print("* 执行随机卸载方法 RandomlyOffloading")
    ro: RandomlyOffloading = RandomlyOffloading(ss=ss, const_cr=1024)
    ro.run()
    ro_cost = ro.calc_cost()
    print(f"* 结果：随机卸载方法成本：{ro_cost}")

    # Offloading ratio statistics
    offloading_count = sum(1 for _, val in ro.sp.strategy.items() if val['offloading'] == 1)
    print(f'* Offloading to SEC ratio: {offloading_count / len(ro.sp.strategy) * 100:.2f}%, '
          f'{offloading_count} / {len(sp.strategy)}')


if __name__ == '__main__':
    main()
