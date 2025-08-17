import math

from core.strategic_profile import StrategicProfile
from core.system_models.cost_model import iot_execution, loc_sec_execution, norm_to_cost
from core.system_state import SystemState
from config import *


# Algorithm 1: Latency-Energy-Aware Offloading
class LEAO:
    def __init__(self, ss: SystemState, alloc_method: str = 'WF'):
        self.ss = ss
        self.sp = StrategicProfile(ss)  # 初始化一个策略
        self.alloc_method = alloc_method  # 使用的资源分配方法：ES-平均分配，LP-线性负载比例，WF-注水算法

        # 函数列表
        self.func_lst = ss.get_function_list()
        self.func_lst = sorted(self.func_lst, key=lambda f: (f.invocations * f.workload), reverse=True)

    def __repr__(self):
        return f'Algorithm {self.__class__.__name__} with {self.alloc_method} resource alloc method'

    def run(self) -> StrategicProfile:
        for func in self.func_lst:
            # 计算 prev_cost
            prev_cost = self._calc_cost_with_global_resource_pool()

            # 模拟将当前任务卸载到本地SEC，然后计算 after_cost
            self.sp.offload_to_loc_sec(func.id)
            after_cost = self._calc_cost_with_global_resource_pool()

            # 判断是否获得正收益，如果是负收益，则回退策略至本地IoT执行
            if prev_cost < after_cost:
                self.sp.execution_on_iot(func.id)
        return self.sp

    # 将SEC侧看作一个全局资源池, 计算cost
    def _calc_cost_with_global_resource_pool(self):
        cost = 0.0

        # 计算总的资源池
        CR_total = self.ss.get_system_available_cr()

        for func in self.func_lst:
            iot = self.ss.f2u_mapping(func.id)
            loc_sec = self.ss.f2s_mapping(func.id)
            strategy = self.sp.get_func_strategy(func.id)

            # 策略1
            if strategy == 1:
                latency, energy = iot_execution(func=func, iot=iot)
            # 策略2
            elif strategy == 2:
                # ES-平均分配资源
                if self.alloc_method == 'ES':
                    offload_count = self.sp.get_offload_count()
                    cr_ik = CR_total / offload_count
                # LP-线性负载比例
                elif self.alloc_method == 'LP':
                    total_workload = self.sp.get_offload_workload()
                    func_workload = func.invocations * func.workload
                    cr_ik = func_workload / total_workload * CR_total
                # WF-注水算法
                elif self.alloc_method == 'WF':
                    total_workload_factor = self.sp.get_offload_workload_factor()
                    func_workload_factor = math.sqrt(func.invocations * func.workload)
                    cr_ik = func_workload_factor / total_workload_factor * CR_total
                # FIXED-固定分配
                else:
                    offload_count = self.sp.get_offload_count()
                    cr_ik = int(self.alloc_method.split('-')[1]) * RATIO
                    if (cr_ik * offload_count) > CR_total:
                        return float('inf')
                latency, energy = loc_sec_execution(func=func, iot=iot, loc_sec=loc_sec, cr_ik=cr_ik)
            # 没有策略3
            else:
                raise KeyError
            # 计算归一化cost并累加
            cost += norm_to_cost(latency=latency, energy=energy)
        return cost

    def get_cost(self):
        return self.sp.get_cost(alloc_method=self.alloc_method)
