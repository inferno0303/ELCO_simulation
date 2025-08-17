from core.system_state import SystemState
from core.strategic_profile import StrategicProfile


class NoScheduling:
    def __init__(self, ss: SystemState, sp: StrategicProfile, alloc_method: str = 'WF'):
        self.ss = ss
        self.sp = sp  # 接收一个已有的策略剖面
        self.alloc_method = alloc_method  # 使用的资源分配方法：ES-平均分配，LP-线性负载比例，WF-注水算法

    def __repr__(self):
        return f'Algorithm {self.__class__.__name__} with {self.alloc_method} resource alloc method'

    def run(self) -> StrategicProfile:
        # 不做任何事
        return self.sp

    def get_cost(self):
        return self.sp.get_cost(alloc_method=self.alloc_method)
