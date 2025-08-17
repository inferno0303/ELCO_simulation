from core.system_state import SystemState
from core.strategic_profile import StrategicProfile


# 在每个步骤进行详尽的搜索后，迭代地卸载单个最佳任务，Cost贪心卸载
class CostGreedyOffloading:
    def __init__(self, ss: SystemState, alloc_method: str = 'WF'):
        self.ss = ss
        self.sp = StrategicProfile(ss)  # 初始化一个策略
        self.alloc_method = alloc_method  # 使用的资源分配方法：ES-平均分配，LP-线性负载比例，WF-注水算法

        # 函数列表
        self.func_lst = ss.get_function_list()

    def __repr__(self):
        return f'Algorithm {self.__class__.__name__} with {self.alloc_method} resource alloc method'

    def run(self) -> StrategicProfile:
        func_lst = self.func_lst.copy()
        while len(func_lst):
            # 记录待卸载任务的收益
            cost_benefit = {}

            # 迭代每个任务，计算每个任务卸载的潜在 cost 收益
            for func in func_lst:
                # 计算 prev_cost
                prev_cost = self.get_cost()

                # 模拟将当前任务卸载到本地SEC，然后计算 after_cost
                self.sp.offload_to_loc_sec(func.id)
                after_cost = self.get_cost()
                self.sp.execution_on_iot(func.id)

                # 记录cost收益
                cost_benefit[func.id] = prev_cost - after_cost

            # 选择收益最高的函数任务
            max_benefit_func_id = max(cost_benefit, key=cost_benefit.get)
            max_benefit = cost_benefit[max_benefit_func_id]

            # 如果收益为正，则将函数任务卸载到本地SEC
            if max_benefit > 0:
                self.sp.offload_to_loc_sec(max_benefit_func_id)
                func_lst.remove(self.ss.get_function_instance(max_benefit_func_id))
            # 如果收益为负，则说明无改进空间
            else:
                break

        return self.sp

    def get_cost(self):
        return self.sp.get_cost(alloc_method=self.alloc_method)
