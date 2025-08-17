import random

from core.system_models.network_model import SECServer
from core.system_state import SystemState
from core.strategic_profile import StrategicProfile


class RandomScheduling:
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

        for func in self.func_lst:
            strategy = self.sp.get_func_strategy(func.id)
            if strategy == 1:
                continue

            # 如果函数被卸载到SEC侧，则调度到随机的SEC服务器
            random_sec: SECServer = random.choice(sec_lst)
            self.sp.schedule_to_target_sec(func_id=func.id, target_sec_id=random_sec.id)

        return self.sp

    def get_cost(self):
        return self.sp.get_cost(alloc_method=self.alloc_method)
