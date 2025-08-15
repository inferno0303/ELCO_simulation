import math

from core.system_models.network_model import SECServer, IoTDevice, FunctionTask
from core.system_models.resource_model import calc_effective_res
from core.system_models.cost_model import iot_execution, loc_sec_execution, collab_sec_execution, norm_to_cost
from core.system_state import SystemState
from core.strategic_profile import StrategicProfile
from config import *


# 用于消融实验的算法1：LEAO
class LEAO:
    def __init__(self, ss: SystemState, alloc_method: str = 'WF'):
        self.ss = ss
        self.sp = StrategicProfile(ss)
        self.alloc_method = alloc_method  # 使用的资源分配方法：FAIR-平均分配，LP-线性负载比例，WF-注水算法

        # 函数列表
        self.func_lst = ss.get_function_list()
        self.func_lst = sorted(self.func_lst, key=lambda f: (f.invocations * f.workload), reverse=True)

    def __repr__(self):
        return f'Algorithm {self.__class__.__name__} with {self.alloc_method} resource alloc method'

    def _algo_1_leao(self):
        # Init: 计算资源池
        S_total = self.ss.get_sec_total_mem()
        CR_total = self.ss.get_sec_total_comp_res()

        # Init: 将SEC侧看作一个资源池, 计算cost
        def _calc_cost():
            cost = 0.0
            for func_id, _ in self.sp.strategy.items():
                f: FunctionTask = self.ss.get_function_instance(func_id)
                iot = self.ss.f2u_mapping(f.id)
                loc_sec = self.ss.f2s_mapping(f.id)
                strategy = self.sp.get_func_strategy(f.id)

                # 策略1
                if strategy == 1:
                    latency, energy = iot_execution(func=f, iot=iot)
                # 策略2
                elif strategy == 2:
                    # FAIR-平均分配资源
                    if self.alloc_method == 'FAIR':
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
                        fixed_mem = int(self.alloc_method.split('-')[1])
                        offload_count = self.sp.get_offload_count()
                        if fixed_mem * offload_count > S_total:
                            return float('inf')
                        cr_ik = fixed_mem * RATIO
                    latency, energy = loc_sec_execution(func=func, iot=iot, loc_sec=loc_sec, cr_ik=cr_ik)
                # 没有策略3
                else:
                    return float('inf')
                # 计算归一化cost并累加
                cost += norm_to_cost(latency=latency, energy=energy)
            return cost

        for func in self.func_lst:
            # 计算 prev_cost
            prev_cost = _calc_cost()

            # 模拟将当前任务卸载到本地SEC，然后计算 next_cost
            self.sp.offload_to_loc_sec(func.id)
            next_cost = _calc_cost()

            # 判断是否获得正收益，如果是负收益，则回退策略，在本地IoT执行
            if prev_cost < next_cost:
                self.sp.execution_on_iot(func.id)

    def run(self) -> StrategicProfile:
        self._algo_1_leao()
        return self.sp

    def get_cost(self):
        return self.sp.get_cost(alloc_method=self.alloc_method)
