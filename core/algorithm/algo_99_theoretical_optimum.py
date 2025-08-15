import math
from typing import List

from core.system_models.network_model import SECServer, IoTDevice, FunctionTask
from core.system_models.resource_model import calc_effective_res
from core.system_models.cost_model import iot_execution, loc_sec_execution, collab_sec_execution, norm_to_cost
from core.system_state import SystemState
from core.strategic_profile import StrategicProfile
from config import *


# 用于消融实验的算法1：LEAO
class TheoreticalOptimal:
    def __init__(self, ss: SystemState, sp: StrategicProfile, alloc_method: str = 'WF'):
        self.ss = ss
        self.sp = sp
        self.alloc_method = alloc_method  # 使用的资源分配方法：FAIR-平均分配，LP-线性负载比例，WF-注水算法

        # 函数列表
        self.func_lst = ss.get_function_list()
        self.func_lst = sorted(self.func_lst, key=lambda f: (f.invocations * f.workload), reverse=True)

    def __repr__(self):
        return f'Algorithm {self.__class__.__name__} with {self.alloc_method} resource alloc method'

    def _theo_schedule_optimal(self):
        # Init: 计算资源池
        S_total = self.ss.get_sec_total_mem()
        CR_total = self.ss.get_sec_total_comp_res()

        # Init: 已卸载的函数列表
        offload_fun_lst: List[FunctionTask] = []
        for func_id, _val in self.sp.strategy.items():
            if _val['offloading'] == 1:
                func = self.ss.get_function_instance(func_id)
                offload_fun_lst.append(func)

        # 计算理论值
        cost = 0.0
        total_workload_factor = self.sp.get_offload_workload_factor()
        for func in offload_fun_lst:
            iot = self.ss.f2u_mapping(func.id)
            loc_sec = self.ss.f2s_mapping(func.id)

            func_workload_factor = math.sqrt(func.invocations * func.workload)
            cr_ik = func_workload_factor / total_workload_factor * CR_total

            latency, energy = loc_sec_execution(func=func, iot=iot, loc_sec=loc_sec, cr_ik=cr_ik)
            # 计算归一化cost并累加
            cost += norm_to_cost(latency=latency, energy=energy)
        return cost

    def run(self) -> StrategicProfile:
        return self.sp

    def get_cost(self) -> float:
        cost = self._theo_schedule_optimal()
        for func_id, _val in self.sp.strategy.items():
            if _val['offloading'] == 0:
                func = self.ss.get_function_instance(func_id)
                iot = self.ss.f2u_mapping(func.id)
                latency, energy = iot_execution(func, iot)
                cost += norm_to_cost(latency=latency, energy=energy)
        return cost
