from core.system_models.network_model import SECServer, IoTDevice, FunctionTask
from core.system_models.resource_model import calc_effective_res
from core.system_models.cost_model import iot_execution, loc_sec_execution, collab_sec_execution, norm_to_cost
from core.system_state import SystemState
from core.strategic_profile import StrategicProfile
from config import *


class OptimalOffload:
    def __init__(self, ss: SystemState, alloc_method: str = 'WF'):
        self.ss = ss
        self.sp = StrategicProfile(ss)
        self.alloc_method = alloc_method  # 使用的资源分配方法：FAIR-平均分配，LP-线性负载比例，WF-注水算法

        # 函数列表
        self.func_lst = ss.get_function_list()
        # self.func_lst = sorted(self.func_lst, key=lambda f: (f.invocations * f.workload), reverse=True)

    def __repr__(self):
        return f'Algorithm {self.__class__.__name__} with {self.alloc_method} resource alloc method'

    def run(self) -> StrategicProfile:
        func_lst = self.func_lst.copy()
        for i in range(len(self.func_lst)):
            delta_cost_result = {}
            for func in func_lst:
                prev_cost = self.get_cost()
                self.sp.offload_to_loc_sec(func.id)
                next_cost = self.get_cost()
                self.sp.execution_on_iot(func.id)

                # 记录cost变化
                delta_cost_result[func.id] = prev_cost - next_cost

            # 每次都贪心选择对cost改进最大的策略
            max_func_id = max(delta_cost_result, key=delta_cost_result.get)
            max_delta = delta_cost_result[max_func_id]
            if max_delta > 0:
                self.sp.offload_to_loc_sec(max_func_id)
                func_lst.remove(self.ss.get_function_instance(max_func_id))
            else:
                break

        return self.sp

    def get_cost(self):
        return self.sp.get_cost(alloc_method=self.alloc_method)
