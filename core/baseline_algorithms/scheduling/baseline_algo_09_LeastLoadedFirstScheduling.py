from core.strategic_profile import StrategicProfile
from core.system_state import SystemState


# 最小负载优先的负载均衡调度
class LeastLoadedFirstScheduling:
    def __init__(self, ss: SystemState, sp: StrategicProfile, alloc_method: str = 'WF'):
        self.ss = ss
        self.sp = sp  # 接收一个已有的策略剖面
        self.alloc_method = alloc_method  # 使用的资源分配方法：ES-平均分配，LP-线性负载比例，WF-注水算法

        # 函数列表
        self.func_lst = ss.get_function_list()

    def __repr__(self):
        return f'Algorithm {self.__class__.__name__} with {self.alloc_method} resource alloc method'

    def run(self) -> StrategicProfile:
        for func in self.func_lst:
            strategy = self.sp.get_func_strategy(func.id)
            if strategy == 1:
                continue

            # 选择一个当前负载最低的SEC
            sec_workload = {sec.id: self.sp.get_sec_workload(sec) for sec in self.ss.get_sec_list()}
            target_sec_id = min(sec_workload, key=sec_workload.get)

            # 调度到负载最低的SEC
            self.sp.schedule_to_target_sec(func_id=func.id, target_sec_id=target_sec_id)

        return self.sp

    def get_cost(self):
        return self.sp.get_cost(alloc_method=self.alloc_method)
