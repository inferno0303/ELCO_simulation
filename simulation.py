import time

from config import *
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


class Simulation:
    def __init__(self, ss: SystemState):
        self.ss = ss

    def run(self):
        print(f'============ 实验1：证明 WF 注水算法的有效性 ============')
        yield self.experiment_01(ss=self.ss)

        print(f'============ 实验2：证明 PGES 算法的有效性 ============')
        yield self.experiment_02(ss=self.ss)

        print(f'============ 实验3：证明 LEAO 算法的有效性 ============')
        yield self.experiment_03(ss=self.ss)

    # 实验1：证明注水算法的有效性
    @staticmethod
    def experiment_01(ss: SystemState):
        bs_count = ss.get_base_station_count()
        sec_count = ss.get_sec_server_count()
        iot_count = ss.get_iot_device_count()
        func_type_count = ss.get_function_type_count()
        func_count = ss.get_function_count()

        results = []

        '''
        LEAO + PGES 分别在 WF、ES、LP、FIXED-512下对比
        '''

        '''（1.1）'''
        # 运行算法
        alloc_method = 'WF'
        start_time = time.time()
        algo_1 = LEAO(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = PGES(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（1.2）'''
        # 运行算法
        alloc_method = 'ES'
        start_time = time.time()
        algo_1 = LEAO(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = PGES(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（1.3）'''
        # 运行算法
        alloc_method = 'LP'
        start_time = time.time()
        algo_1 = LEAO(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = PGES(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（1.4）'''
        # 运行算法
        alloc_method = 'FIX-512'
        start_time = time.time()
        algo_1 = LEAO(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = PGES(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''
        LocalSECOnly + NoScheduling 在 WF、ES、LP、FIXED-512 下对比
        '''

        '''（1.5）'''
        # 运行算法
        alloc_method = 'WF'
        start_time = time.time()
        algo_1 = LocalSECOnly(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = NoScheduling(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（1.6）'''
        alloc_method = 'ES'
        start_time = time.time()
        algo_1 = LocalSECOnly(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = NoScheduling(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（1.7）'''
        alloc_method = 'LP'
        start_time = time.time()
        algo_1 = LocalSECOnly(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = NoScheduling(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（1.8）'''
        alloc_method = 'FIXED-512'
        start_time = time.time()
        algo_1 = LocalSECOnly(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = NoScheduling(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''
        CostGreedyOffloading + CostGreedyScheduling 分别在 WF、ES、LP、FIXED-512 下对比
        '''

        '''（1.9）'''
        alloc_method = 'WF'
        start_time = time.time()
        algo_1 = CostGreedyOffloading(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = CostGreedyScheduling(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（1.10）'''
        alloc_method = 'ES'
        start_time = time.time()
        algo_1 = CostGreedyOffloading(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = CostGreedyScheduling(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（1.11）'''
        alloc_method = 'LP'
        start_time = time.time()
        algo_1 = CostGreedyOffloading(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = CostGreedyScheduling(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（1.12）'''
        alloc_method = 'FIXED-512'
        start_time = time.time()
        algo_1 = CostGreedyOffloading(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = CostGreedyScheduling(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''
        返回结果
        '''
        return results

    # 实验2：证明 PGES 的有效性
    @staticmethod
    def experiment_02(ss: SystemState):
        bs_count = ss.get_base_station_count()
        sec_count = ss.get_sec_server_count()
        iot_count = ss.get_iot_device_count()
        func_type_count = ss.get_function_type_count()
        func_count = ss.get_function_count()

        results = []

        '''
        LEAO + NoScheduling / RandomScheduling 在 WF 下对比
        '''

        '''（2.1）'''
        # 运行算法
        alloc_method = 'WF'
        start_time = time.time()
        algo_1 = LEAO(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = NoScheduling(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（2.2）'''
        # 运行算法
        alloc_method = 'WF'
        start_time = time.time()
        algo_1 = LEAO(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = RandomScheduling(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（2.3）'''
        # 运行算法
        alloc_method = 'WF'
        start_time = time.time()
        algo_1 = LEAO(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = RoundRobinScheduling(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（2.4）'''
        # 运行算法
        alloc_method = 'WF'
        start_time = time.time()
        algo_1 = LEAO(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = LeastLoadedFirstScheduling(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（2.5）'''
        # 运行算法
        alloc_method = 'WF'
        start_time = time.time()
        algo_1 = LEAO(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = MinExecutionTimeScheduling(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（2.6）'''
        # 运行算法
        alloc_method = 'WF'
        start_time = time.time()
        algo_1 = LEAO(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = CostGreedyScheduling(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''
        返回结果
        '''
        return results

    # 实验3：证明 LEAO 算法的有效性
    @staticmethod
    def experiment_03(ss: SystemState):
        bs_count = ss.get_base_station_count()
        sec_count = ss.get_sec_server_count()
        iot_count = ss.get_iot_device_count()
        func_type_count = ss.get_function_type_count()
        func_count = ss.get_function_count()

        results = []

        '''
        IoTOnly / LocalSECOnly / RandomOffloading / MyopicLEAO / CostGreedyOffloading + PGES 在 WF 下对比
        '''

        '''（3.1）'''
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
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_name}', f'', '',
            cost, latency, energy, ratio, execution_time
        ])

        '''（3.2）'''
        # 运行算法
        alloc_method = 'WF'
        start_time = time.time()
        algo_1 = LocalSECOnly(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = PGES(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（3.3）'''
        # 运行算法
        alloc_method = 'WF'
        start_time = time.time()
        algo_1 = RandomOffloading(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = PGES(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（3.4）'''
        # 运行算法
        alloc_method = 'WF'
        start_time = time.time()
        algo_1 = MyopicLEAO(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = PGES(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''（3.5）'''
        # 运行算法
        alloc_method = 'WF'
        start_time = time.time()
        algo_1 = CostGreedyOffloading(ss, alloc_method)
        sp = algo_1.run()
        algo_2 = PGES(ss, sp, alloc_method)
        algo_2.run()
        end_time = time.time()

        # 收集数据
        algo_1_name = algo_1.__class__.__name__
        algo_2_name = algo_2.__class__.__name__
        full_name = f'{algo_1_name}+{algo_2_name}+{alloc_method}'
        cost = algo_2.get_cost()
        ratio = algo_2.sp.get_offload_ratio()
        latency, energy = algo_2.sp.get_real_latency_energy(alloc_method=alloc_method)
        execution_time = end_time - start_time

        # 记录结果
        print(f'*结果：{full_name}, cost {cost:.2f}, offloading ratio {ratio * 100:.2f}%, time {execution_time:.2f}s')
        results.append([
            bs_count, sec_count, iot_count, func_type_count, func_count, OMEGA, RATIO, T_ref, E_ref,
            f'{full_name}', f'{algo_1_name}', f'{algo_2_name}', alloc_method,
            cost, latency, energy, ratio, execution_time
        ])

        '''
        返回结果
        '''
        return results
