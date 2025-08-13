import math
from typing import List

from core.system_models.cost_model import local_device_execution, local_sec_execution
from core.system_models.network_model import SECServer, IoTDevice, FunctionTask
from core.system_models.resource_model import calc_effective_res
from core.system_state import SystemState
from core.strategic_profile import StrategicProfile
from config import *


class WorkloadPriorityOffloadingWF:
    def __init__(self, ss: SystemState):
        self.ss = ss

        # 初始化一个策略剖面
        self.sp = StrategicProfile(system_state=ss)
        self.sp.reset_strategy()

        # 获取函数列表
        self.func_list: List[FunctionTask] = ss.get_function_list()

        # 统计每个SEC服务器上 offloading 负载因子总量 C_k = sqrt(ni*c*i)
        self.sec_total_workload_factor = dict.fromkeys([sec.id for sec in self.ss.get_sec_list()], 0.0)

    def run(self) -> StrategicProfile:
        # 按函数负载降序排列
        sorted_func_list = sorted(self.func_list, key=lambda _func: (_func.invocations * _func.workload), reverse=True)

        # 按顺序卸载到本地SEC，直到本地SEC资源限制
        for func in sorted_func_list:

            # 获取本地SEC
            loc_sec: SECServer = self.ss.f2s_mapping(func_id=func.id)

            # 判断本地SEC是否超载
            S_k = calc_effective_res(loc_sec)
            sqrt_nc = math.sqrt(func.invocations * func.workload)
            c_i = func.invocations * func.workload
            cr_ik = RATIO * S_k * sqrt_nc / (self.sec_total_workload_factor[loc_sec.id] + sqrt_nc)
            # if cr_ik < 128 * RATIO:
            #     continue

            # 计算卸载前的cost
            prev_cost = self.calc_cost()

            # 卸载当前函数
            self.sp.strategy[func.id]['offloading'] = 1
            self.sp.strategy[func.id]['scheduling'] = loc_sec.id
            self.sec_total_workload_factor[loc_sec.id] += math.sqrt(func.invocations * func.workload)

            # 计算卸载后的cost
            next_cost = self.calc_cost()

            # 如果cost劣化了，则回退至卸载前的策略剖面
            if next_cost > prev_cost:
                self.sp.strategy[func.id]['offloading'] = 0
                self.sp.strategy[func.id]['scheduling'] = None
                self.sec_total_workload_factor[loc_sec.id] -= math.sqrt(func.invocations * func.workload)

        return self.sp

    def calc_cost(self) -> float:
        cost = 0.0

        for func in self.func_list:
            iot: IoTDevice = self.ss.f2u_mapping(func_id=func.id)
            if self.sp.strategy[func.id]['offloading'] == 0:
                latency, energy = local_device_execution(func=func, iot=iot)
            else:
                loc_sec: SECServer = self.ss.f2s_mapping(func_id=func.id)

                # 按每个函数的任务量线根据注水算法分配计算资源
                S_k = calc_effective_res(loc_sec)
                sqrt_nc = math.sqrt(func.invocations * func.workload)
                cr_ik = RATIO * S_k * sqrt_nc / self.sec_total_workload_factor[loc_sec.id]
                latency, energy = local_sec_execution(func=func, iot=iot, sec=loc_sec, cr_ik=cr_ik)

            # 计算归一化成本 (公式33)
            cost += OMEGA * (latency / T_ref) + (1 - OMEGA) * (energy / E_ref)

        return cost
