from core.system_state import SystemState
from core.strategic_profile import StrategicProfile


# 根据本地资源视图按顺序卸载，短视的Latency-Energy-Aware Offloading：M-LEAO
class MyopicLEAO:
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
            # 计算 prev_cost
            prev_cost = self.get_cost()

            # 模拟将当前任务卸载到本地SEC，然后计算 after_cost
            self.sp.offload_to_loc_sec(func.id)
            after_cost = self.get_cost()

            # 判断是否获得正收益，如果是负收益，则回退策略至本地IoT执行
            if prev_cost < after_cost:
                self.sp.execution_on_iot(func.id)
        return self.sp

    def get_cost(self):
        return self.sp.get_cost(alloc_method=self.alloc_method)
