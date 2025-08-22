import time
from typing import List, Tuple

from core.algorithm_ELCO.algo_01_LEAO import LEAO
from core.algorithm_ELCO.algo_02_PGES import PGES
from core.baseline_algorithms.offloading.baseline_algo_01_IoTOnly import IoTOnly
from core.baseline_algorithms.offloading.baseline_algo_02_LocalSECOnly import LocalSECOnly
from core.baseline_algorithms.offloading.baseline_algo_03_RandomOffloading import RandomOffloading
from core.baseline_algorithms.offloading.baseline_algo_04_MyopicLEAO import MyopicLEAO
from core.baseline_algorithms.offloading.baseline_algo_05_CostGreedyOffloading import CostGreedyOffloading
from core.baseline_algorithms.scheduling.baseline_algo_06_NoScheduling import NoScheduling
from core.baseline_algorithms.scheduling.baseline_algo_07_RandomScheduling import RandomScheduling
from core.baseline_algorithms.scheduling.baseline_algo_08_RoundRobinScheduling import RoundRobinScheduling
from core.baseline_algorithms.scheduling.baseline_algo_09_LeastLoadedFirstScheduling import LeastLoadedFirstScheduling
from core.baseline_algorithms.scheduling.baseline_algo_10_MinExecutionTimeScheduling import MinExecutionTimeScheduling
from core.baseline_algorithms.scheduling.baseline_algo_11_CostGreedyScheduling import CostGreedyScheduling
from core.system_state import SystemState
from config import *

# 实验结果表头
header = [
    'Base Station Count', 'SEC Server Count', 'IoT Device Count', 'Function Type Count', 'Function Task Count',
    'Latency Weight (OMEGA)', 'CPU MEM RATIO', 'Latency REF (s)', 'Energy REF (J)',
    'Algorithm Full Name', 'Offloading Algorithm', 'Scheduling Algorithm', 'Resource Allocation Algorithm',
    'System Cost', 'Real Latency (s)', 'Real Energy (J)', 'Offloading Ratio', 'Execution Time (s)'
]


# 实验1：证明WF注水算法的有效性
def experimental_01(ss: SystemState) -> List[List]:
    bs_count = ss.get_base_station_count()
    sec_count = ss.get_sec_server_count()
    iot_count = ss.get_iot_device_count()
    func_type_count = ss.get_function_type_count()
    func_count = ss.get_function_count()

    results = []

    '''
    数据组01：IoTOnly：本地IoT执行作为基线
    '''
    # 运行算法
    start_time = time.time()
    algo = IoTOnly(ss)
    algo.run()
    end_time = time.time()

    # 收集数据
    algo_name = algo.__class__.__name__
    full_name = f'{algo_name}'
    cost = algo.get_cost()
    ratio = algo.sp.get_offload_ratio()
    latency, energy = algo.sp.get_real_latency_energy()
    duration_time = end_time - start_time

    # 记录结果
    print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {duration_time:.2f}s')
    results.append([
        bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
        f'{full_name}', f'{algo_name}', f'', f'',
        cost, latency, energy, ratio, duration_time
    ])

    '''
    数据组02：LocalSECOnly 分别运行在 FIXED-256 / LP / ES / WF
    '''
    for alloc_method in ['FIXED-256', 'LP', 'ES', 'WF']:
        # 运行算法
        start_time = time.time()
        algo = LocalSECOnly(ss, alloc_method)
        algo.run()
        end_time = time.time()

        # 收集数据
        algo_name = algo.__class__.__name__
        full_name = f'{algo_name} + {alloc_method}'
        cost = algo.get_cost()
        ratio = algo.sp.get_offload_ratio()
        latency, energy = algo.sp.get_real_latency_energy()
        duration_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio:.2f}, time {duration_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_name}', f'', f'{alloc_method}',
            cost, latency, energy, ratio, duration_time
        ])

    '''
    数据组03：RandomOffloading 分别运行在 FIXED-256 / LP / ES / WF
    '''
    for alloc_method in ['FIXED-256', 'LP', 'ES', 'WF']:
        # 运行算法
        start_time = time.time()
        algo = RandomOffloading(ss, alloc_method)
        algo.run()
        end_time = time.time()

        # 收集数据
        algo_name = algo.__class__.__name__
        full_name = f'{algo_name} + {alloc_method}'
        cost = algo.get_cost()
        ratio = algo.sp.get_offload_ratio()
        latency, energy = algo.sp.get_real_latency_energy()
        duration_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio:.2f}, time {duration_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_name}', f'', f'{alloc_method}',
            cost, latency, energy, ratio, duration_time
        ])

    '''
    数据组04：MyopicLEAO 分别运行在 FIXED-256 / LP / ES / WF
    '''
    for alloc_method in ['FIXED-256', 'LP', 'ES', 'WF']:
        # 运行算法
        start_time = time.time()
        algo = MyopicLEAO(ss, alloc_method)
        algo.run()
        end_time = time.time()

        # 收集数据
        algo_name = algo.__class__.__name__
        full_name = f'{algo_name} + {alloc_method}'
        cost = algo.get_cost()
        ratio = algo.sp.get_offload_ratio()
        latency, energy = algo.sp.get_real_latency_energy()
        duration_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio:.2f}, time {duration_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_name}', f'', f'{alloc_method}',
            cost, latency, energy, ratio, duration_time
        ])

    '''
    数据组05：CostGreedyOffloading 分别运行在 FIXED-256 / LP / ES / WF
    '''
    for alloc_method in ['FIXED-256', 'LP', 'ES', 'WF']:
        # 运行算法
        start_time = time.time()
        algo = CostGreedyOffloading(ss, alloc_method)
        algo.run()
        end_time = time.time()

        # 收集数据
        algo_name = algo.__class__.__name__
        full_name = f'{algo_name} + {alloc_method}'
        cost = algo.get_cost()
        ratio = algo.sp.get_offload_ratio()
        latency, energy = algo.sp.get_real_latency_energy()
        duration_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio:.2f}, time {duration_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_name}', f'', f'{alloc_method}',
            cost, latency, energy, ratio, duration_time
        ])

    return results


# 实验2：证明PGES的有效性
def experimental_02(ss: SystemState) -> List[List]:
    bs_count = ss.get_base_station_count()
    sec_count = ss.get_sec_server_count()
    iot_count = ss.get_iot_device_count()
    func_type_count = ss.get_function_type_count()
    func_count = ss.get_function_count()

    results = []

    alloc_method = 'WF'
    algo_1 = CostGreedyOffloading(ss, alloc_method)
    sp = algo_1.run()

    for SchedulingAlgorithm in [NoScheduling, RandomScheduling, RoundRobinScheduling, LeastLoadedFirstScheduling,
                                MinExecutionTimeScheduling, CostGreedyScheduling, PGES]:
        # 运行算法
        start_time = time.time()
        algo_2 = SchedulingAlgorithm(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name} + {algo_2_name} + {alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy()
        duration_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio:.2f}, time {duration_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', f'{alloc_method}',
            cost, latency, energy, ratio, duration_time
        ])

    # LEAO + PGES
    # 运行算法
    algo_1 = LEAO(ss, alloc_method)
    sp = algo_1.run()
    start_time = time.time()
    algo_2 = PGES(ss, sp, alloc_method)
    algo_2.run()
    end_time = time.time()

    # 收集数据
    algo_1_name = algo_1.__class__.__name__
    algo_2_name = algo_2.__class__.__name__
    full_name = f'{algo_1_name} + {algo_2_name} + {alloc_method}'
    cost = algo_2.get_cost()
    ratio = algo_2.sp.get_offload_ratio()
    latency, energy = algo_2.sp.get_real_latency_energy()
    duration_time = end_time - start_time

    # 记录结果
    print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio:.2f}, time {duration_time:.2f}s')
    results.append([
        bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
        f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', f'{alloc_method}',
        cost, latency, energy, ratio, duration_time
    ])

    return results


# 实验3：记录LEAO+PGES的博弈收敛过程，记录每一次博弈动作的cost、latency_cost、energy_cost参考值，会输出文件 PGES_game_process_*_.csv
def experimental_03(ss: SystemState) -> List[List]:
    bs_count = ss.get_base_station_count()
    sec_count = ss.get_sec_server_count()
    iot_count = ss.get_iot_device_count()
    func_type_count = ss.get_function_type_count()
    func_count = ss.get_function_count()

    results = []
    alloc_method = 'WF'

    # LEAO + PGES
    # 运行算法
    algo_1 = LEAO(ss, alloc_method)
    sp = algo_1.run()
    start_time = time.time()
    algo_2 = PGES(ss, sp, alloc_method)
    algo_2.run()
    end_time = time.time()

    # 收集数据
    algo_1_name = algo_1.__class__.__name__
    algo_2_name = algo_2.__class__.__name__
    full_name = f'{algo_1_name} + {algo_2_name} + {alloc_method}'
    cost = algo_2.get_cost()
    ratio = algo_2.sp.get_offload_ratio()
    latency, energy = algo_2.sp.get_real_latency_energy()
    duration_time = end_time - start_time

    # 记录结果
    print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio:.2f}, time {duration_time:.2f}s')
    results.append([
        bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
        f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', f'{alloc_method}',
        cost, latency, energy, ratio, duration_time
    ])

    # （与之前不同）博弈过程，写入额外的csv文件
    from utils.results_recorder import new_csv_file, write_csv
    now_time = time.strftime('%Y%m%d_%H%M%S')
    file_name = f'PGES_game_process_{ss.get_function_count()}_{now_time}.csv'
    new_csv_file(file_name, header)
    write_csv(file_name, results)

    write_csv(file_name, [[]])
    write_csv(file_name, [['cost'] + algo_2.cost_changes])
    write_csv(file_name, [['latency_cost'] + algo_2.latency_cost_changes])
    write_csv(file_name, [['energy_cost'] + algo_2.energy_cost_change])

    return results


# 实验4：证明LEAO的有效性
def experimental_04(ss: SystemState) -> List[List]:
    bs_count = ss.get_base_station_count()
    sec_count = ss.get_sec_server_count()
    iot_count = ss.get_iot_device_count()
    func_type_count = ss.get_function_type_count()
    func_count = ss.get_function_count()

    results = []

    '''
    数据组01：LocalSECOnly, RandomOffloading, MyopicLEAO, CostGreedyOffloading, LEAO 与 PGES
    '''

    alloc_method = 'WF'
    for OffloadingAlgorithm in [LocalSECOnly, RandomOffloading, MyopicLEAO, CostGreedyOffloading, LEAO]:
        # 运行算法1
        start_time = time.time()
        algo_1 = OffloadingAlgorithm(ss, alloc_method)
        sp = algo_1.run()

        # 运行算法2：PGES
        algo_2 = PGES(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name} + {algo_2_name} + {alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy()
        duration_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio:.2f}, time {duration_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', f'{alloc_method}',
            cost, latency, energy, ratio, duration_time
        ])

    '''
    数据组02：基线方法 IotOnly
    '''
    # 运行算法
    start_time = time.time()
    algo = IoTOnly(ss)
    algo.run()
    end_time = time.time()

    # 收集数据
    algo_name = algo.__class__.__name__
    full_name = f'{algo_name}'
    cost = algo.get_cost()
    ratio = algo.sp.get_offload_ratio()
    latency, energy = algo.sp.get_real_latency_energy()
    duration_time = end_time - start_time

    # 记录结果
    print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {duration_time:.2f}s')
    results.append([
        bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
        f'{full_name}', f'{algo_name}', f'', f'',
        cost, latency, energy, ratio, duration_time
    ])

    return results


# 实验5：证明 LEAO+PGES+WF 的有效性，对比组：IOTOnly（基线）、RAND-O+RR+ES、LSO+LLF+ES、M-LEAO+MET+WF、M-LEAO+PGES+WF、CGO+CGS+WF
def experimental_05(ss: SystemState) -> List[List]:
    bs_count = ss.get_base_station_count()
    sec_count = ss.get_sec_server_count()
    iot_count = ss.get_iot_device_count()
    func_type_count = ss.get_function_type_count()
    func_count = ss.get_function_count()

    results = []

    '''
    数据组01：IoTOnly：本地IoT执行作为基线
    '''
    # 运行算法
    start_time = time.time()
    algo = IoTOnly(ss)
    algo.run()
    end_time = time.time()

    # 收集数据
    algo_name = algo.__class__.__name__
    full_name = f'{algo_name}'
    cost = algo.get_cost()
    ratio = algo.sp.get_offload_ratio()
    latency, energy = algo.sp.get_real_latency_energy()
    duration_time = end_time - start_time

    # 记录结果
    print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {duration_time:.2f}s')
    results.append([
        bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
        f'{full_name}', f'{algo_name}', f'', f'',
        cost, latency, energy, ratio, duration_time
    ])

    alloc_method = 'WF'
    for ALGO_1 in [LocalSECOnly, RandomOffloading, MyopicLEAO, CostGreedyOffloading, LEAO]:
        print()
        start_time = time.time()
        algo_1 = ALGO_1(ss, alloc_method)
        sp = algo_1.run()
        for ALGO_2 in [NoScheduling, RandomScheduling, RoundRobinScheduling, LeastLoadedFirstScheduling,
                       MinExecutionTimeScheduling, CostGreedyScheduling, PGES]:

            algo_2 = ALGO_2(ss, sp, alloc_method)
            algo_2.run()
            end_time = time.time()

            # 收集数据
            algo_1_name = algo_1.__class__.__name__
            algo_2_name = algo_2.__class__.__name__
            full_name = f'{algo_1_name} + {algo_2_name} + {alloc_method}'
            cost = algo_2.get_cost()
            ratio = algo_2.sp.get_offload_ratio()
            latency, energy = algo_2.sp.get_real_latency_energy()
            duration_time = end_time - start_time

            # 记录结果
            print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio:.2f}, time {duration_time:.2f}s')
            results.append([
                bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
                f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', f'{alloc_method}',
                cost, latency, energy, ratio, duration_time
            ])

    return results
