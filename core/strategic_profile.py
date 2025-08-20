import math
from typing import List

from core.system_models.cost_model import *
from core.system_state import SystemState


class StrategicProfile:
    def __init__(self, ss: SystemState):
        self.ss = ss

        # 策略剖面存储：初始化时默认本地IoT执行：offloading = 0, scheduling = None
        self.strategy = {
            func_id: {
                'offloading': 0,
                'scheduling': None
            }
            for func_id in ss.functions.keys()
        }

    # === setter方法 ===

    # 初始化策略剖面：offloading = 0, scheduling = None
    def reset_strategy(self):
        self.strategy = {
            func_id: {
                'offloading': 0,
                'scheduling': None
            }
            for func_id in self.ss.functions.keys()
        }

    # 策略1：在本地IoT执行
    def execution_on_iot(self, func_id: int | str):
        self.strategy[func_id]['offloading'] = 0
        self.strategy[func_id]['scheduling'] = None

    # 策略2：在本地SEC执行
    def offload_to_loc_sec(self, func_id: int | str):
        loc_sec: SECServer = self.ss.f2s_mapping(func_id=func_id)
        self.strategy[func_id]['offloading'] = 1
        self.strategy[func_id]['scheduling'] = loc_sec.id

    # 策略3：在协作SEC执行
    def schedule_to_target_sec(self, func_id: int | str, target_sec_id: int | str):
        self.strategy[func_id]['offloading'] = 1
        self.strategy[func_id]['scheduling'] = target_sec_id

    # === getter方法 ===

    # 判断函数任务的策略 -> 返回策略 1/2/3
    def get_func_strategy(self, func_id: int | str) -> int:
        if self.strategy[func_id]['offloading'] == 0:
            return 1
        else:
            if self.strategy[func_id]['scheduling'] == self.ss.f2s_mapping(func_id=func_id).id:
                return 2
            else:
                return 3

    # 获取当前函数的执行SEC
    def get_func_current_sec(self, func_id: int | str) -> SECServer | None:
        if self.strategy[func_id]['offloading'] == 0:
            return None
        else:
            curr_sec_id = self.strategy[func_id]['scheduling']
            return self.ss.get_sec_server_instance(sec_id=curr_sec_id)

    # === 复杂属性计算 ===

    # 获取卸载的函数个数
    def get_offload_count(self) -> int:
        return sum(1 for val in self.strategy.values() if val.get('offloading', 0) == 1)

    # 获取卸载比例
    def get_offload_ratio(self) -> float:
        total_count = len(self.strategy.keys())
        if total_count == 0:
            return 0.0
        return self.get_offload_count() / total_count

    # 获取某个sec的函数数量
    def get_sec_func_count(self, sec: SECServer) -> int:
        count = 0
        for func_id, _val in self.strategy.items():
            if _val['offloading'] == 1 and _val['scheduling'] == sec.id:
                count += 1
        return count

    # 获取某个sec的函数任务列表
    def get_sec_func_list(self, sec: SECServer) -> List[FunctionTask]:
        func_list = []
        for func_id, _val in self.strategy.items():
            if _val['offloading'] == 1 and _val['scheduling'] == sec.id:
                func: FunctionTask = self.ss.functions[func_id]['instance']
                func_list.append(func)
        return func_list

    # 获取某个sec的负载量（单位：MHz）
    def get_sec_workload(self, sec: SECServer) -> float:
        workload = 0.0
        for func_id, _val in self.strategy.items():
            if _val['offloading'] == 1 and _val['scheduling'] == sec.id:
                func = self.ss.get_function_instance(func_id)
                workload += (func.invocations * func.workload)
        return workload

    # 获取某个sec的负载因子（单位：MHz） C_k = sum(sqrt(n_i * c*i))
    def get_sec_workload_factor(self, sec: SECServer) -> float:
        workload_factor = 0.0
        for func_id, _val in self.strategy.items():
            if _val['offloading'] == 1 and _val['scheduling'] == sec.id:
                func = self.ss.get_function_instance(func_id)
                workload_factor += math.sqrt(func.invocations * func.workload)
        return workload_factor

    # 获取所有已卸载的函数的负载量 (单位: MHz)
    def get_offload_workload(self) -> float:
        workload = 0.0
        for func_id, _val in self.strategy.items():
            if _val['offloading'] == 1:
                func: FunctionTask = self.ss.get_function_instance(func_id)
                workload += func.invocations * func.workload
        return workload

    # 获取所有已卸载的函数的负载因子 (单位: MHz)
    def get_offload_workload_factor(self) -> float:
        workload_factor = 0.0
        for func_id, _val in self.strategy.items():
            if _val['offloading'] == 1:
                func: FunctionTask = self.ss.get_function_instance(func_id)
                workload_factor += math.sqrt(func.invocations * func.workload)
        return workload_factor

    # 根据当前策略剖面，获取函数在某资源分配策略+某sec下能被分配的计算资源（单位：MHz）
    def get_cr_ik(self, func: FunctionTask, sec: SECServer, alloc_method: str = 'WF') -> float:
        # ES-平均分配资源
        if alloc_method == 'ES':
            CR_k = self.ss.get_sec_available_cr(sec)
            func_count = self.get_sec_func_count(sec=sec)
            cr_ik = CR_k / func_count

        # LP-线性负载比例
        elif alloc_method == 'LP':
            CR_k = self.ss.get_sec_available_cr(sec)
            sec_workload = self.get_sec_workload(sec=sec)
            func_workload = func.invocations * func.workload
            cr_ik = func_workload / sec_workload * CR_k

        # WF-注水算法
        elif alloc_method == 'WF':
            CR_k = self.ss.get_sec_available_cr(sec)
            sec_workload_factor = self.get_sec_workload_factor(sec=sec)
            func_workload_factor = math.sqrt(func.invocations * func.workload)
            cr_ik = func_workload_factor / sec_workload_factor * CR_k

        # FIXED-固定分配
        else:
            func_count = self.get_sec_func_count(sec=sec)
            CR_k = self.ss.get_sec_available_cr(sec)
            cr_ik = int(alloc_method.split('-')[1]) * RATIO
            if (cr_ik * func_count) > CR_k:  # 如果SEC满载，则不分资源
                return 1  # 防止除 0
        return cr_ik

    # 根据当前策略剖面计算系统 cost
    def get_cost(self, alloc_method: str = 'WF') -> float:
        cost = 0.0
        for func_id, _val in self.strategy.items():
            func: FunctionTask = self.ss.get_function_instance(func_id)
            iot = self.ss.f2u_mapping(func.id)
            loc_sec = self.ss.f2s_mapping(func.id)
            strategy = self.get_func_strategy(func.id)

            # 策略1
            if strategy == 1:
                latency, energy = iot_execution(func=func, iot=iot)
                # print(f'*决策: 函数{func.id}在本地IoT运行，延迟 {latency:.2f}s，能耗 {energy:.2f}J')

            # 策略2
            elif strategy == 2:
                cr_ik = self.get_cr_ik(func=func, sec=loc_sec, alloc_method=alloc_method)
                latency, energy = loc_sec_execution(func=func, iot=iot, loc_sec=loc_sec, cr_ik=cr_ik)
                # print(f'*决策: 函数{func.id}在本地SEC运行，延迟 {latency:.2f}s，能耗 {energy:.2f}J')

            # 策略3
            else:
                target_sec_id = self.strategy[func.id]['scheduling']
                target_sec = self.ss.get_sec_server_instance(target_sec_id)
                cr_ik = self.get_cr_ik(func=func, sec=target_sec, alloc_method=alloc_method)
                latency, energy = collab_sec_execution(func=func, iot=iot, loc_sec=loc_sec, target_sec=target_sec,
                                                       sec_network=self.ss.sec_network, cr_ik=cr_ik)
                # print(f'*决策: 函数{func.id}在协作SEC运行，延迟 {latency:.2f}s，能耗 {energy:.2f}J')

            # 计算归一化cost并累加
            cost += norm_to_cost(latency=latency, energy=energy)
        return cost

    # 获取当前策略剖面的计算总延迟和总能耗（真实值，单位：latency in s，Energy in J）
    def get_real_latency_energy(self, alloc_method: str = 'WF') -> tuple[float, float]:
        total_latency = 0.0
        total_energy = 0.0

        for func_id, _val in self.strategy.items():
            func: FunctionTask = self.ss.get_function_instance(func_id)
            iot = self.ss.f2u_mapping(func.id)
            loc_sec = self.ss.f2s_mapping(func.id)
            strategy = self.get_func_strategy(func.id)

            # 策略1
            if strategy == 1:
                latency, energy = iot_execution(func=func, iot=iot)

            # 策略2
            elif strategy == 2:
                cr_ik = self.get_cr_ik(func=func, sec=loc_sec, alloc_method=alloc_method)
                latency, energy = loc_sec_execution(func=func, iot=iot, loc_sec=loc_sec, cr_ik=cr_ik)

            # 策略3
            else:
                target_sec_id = self.strategy[func.id]['scheduling']
                target_sec = self.ss.get_sec_server_instance(target_sec_id)
                cr_ik = self.get_cr_ik(func=func, sec=target_sec, alloc_method=alloc_method)
                latency, energy = collab_sec_execution(func=func, iot=iot, loc_sec=loc_sec, target_sec=target_sec,
                                                       sec_network=self.ss.sec_network, cr_ik=cr_ik)

            # 计算累加
            total_latency += latency
            total_energy += energy

        return total_latency, total_energy

    def get_ref_latency_energy(self, alloc_method: str = 'WF'):
        latency, energy = self.get_real_latency_energy(alloc_method=alloc_method)
        return latency / T_ref * OMEGA, energy / E_ref * OMEGA
