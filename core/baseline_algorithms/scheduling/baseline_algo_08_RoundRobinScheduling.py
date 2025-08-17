import random

from core.strategic_profile import StrategicProfile
from core.system_state import SystemState


# 轮询算法的负载均衡调度
class RoundRobinScheduling:
    def __init__(self, ss: SystemState, sp: StrategicProfile, alloc_method: str = 'WF'):
        self.ss = ss
        self.sp = sp  # 接收一个已有的策略剖面
        self.alloc_method = alloc_method  # 使用的资源分配方法：ES-平均分配，LP-线性负载比例，WF-注水算法

        # 函数列表
        self.func_lst = ss.get_function_list()

    def __repr__(self):
        return f'Algorithm {self.__class__.__name__} with {self.alloc_method} resource alloc method'

    def run(self) -> StrategicProfile:
        # SEC服务器列表
        sec_lst = self.ss.get_sec_list()
        random.shuffle(sec_lst)

        # 轮询服务器的编号
        sec_idx = 0

        for func in self.func_lst:
            strategy = self.sp.get_func_strategy(func.id)
            if strategy == 1:
                continue

            # 轮询选择一个目标SEC
            target_sec = sec_lst[sec_idx]
            sec_idx = (sec_idx + 1) % len(sec_lst)

            # 调度到轮询的SEC中
            self.sp.schedule_to_target_sec(func.id, target_sec.id)

        return self.sp

    def get_cost(self):
        return self.sp.get_cost(alloc_method=self.alloc_method)
