from core.strategic_profile import StrategicProfile
from core.system_state import SystemState
import random


# 随机卸载决策
class RandomOffloading:
    def __init__(self, ss: SystemState, alloc_method: str = 'WF'):
        self.ss = ss
        self.sp = StrategicProfile(ss)  # 初始化一个策略
        self.alloc_method = alloc_method  # 使用的资源分配方法：ES-平均分配，LP-线性负载比例，WF-注水算法

        # 函数列表
        self.func_lst = ss.get_function_list()

    def __repr__(self):
        return f'Algorithm {self.__class__.__name__} with {self.alloc_method} resource alloc method'

    def run(self) -> StrategicProfile:
        for func in self.func_lst:
            if random.choice([0, 1]) == 0:
                self.sp.execution_on_iot(func.id)
            else:
                self.sp.offload_to_loc_sec(func.id)
        return self.sp

    def get_cost(self):
        return self.sp.get_cost(alloc_method=self.alloc_method)
