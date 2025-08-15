import random
from core.strategic_profile import StrategicProfile
from core.system_models.network_model import SECServer
from core.system_state import SystemState


class GASchedule:
    def __init__(self, ss: SystemState, alloc_method: str = 'WF', max_iter: int = 10000):
        self.ss = ss
        self.sp = StrategicProfile(ss)
        self.alloc_method = alloc_method  # 使用的资源分配方法：FAIR-平均分配，LP-线性负载比例，WF-注水算法
        self.max_iter = max_iter  # 最大迭代次数

        # 函数列表
        self.func_lst = ss.get_function_list()

        # SEC列表
        self.sec_lst = ss.get_sec_list()

    def __repr__(self):
        return f'Algorithm {self.__class__.__name__} with {self.alloc_method} resource alloc method'

    def run(self) -> StrategicProfile:
        # 随机初始化一个状态
        for func in self.func_lst:
            rd = random.choice([0, 1, 2])
            if rd == 0:
                self.sp.offload_to_loc_sec(func.id)
            elif rd == 1:
                self.sp.execution_on_iot(func.id)
            elif rd == 2:
                sec_id_lst = [sec.id for sec in self.ss.get_sec_list()]
                sec_id_lst.remove(self.ss.f2s_mapping(func.id).id)  # 排除本地SEC
                target_sec_id = random.choice(sec_id_lst)
                self.sp.schedule_to_target_sec(func.id, target_sec_id)

        curr_iter = 0
        while curr_iter < self.max_iter:
            curr_iter += 1

            # 计算cost
            prev_cost = self.get_cost()

            # 备份旧策略
            old_strategy = self.sp.strategy.copy()

            # 随机改变
            func = random.choice(self.func_lst)
            if self.sp.strategy[func.id]['offloading'] == 0:
                target_sec = random.choice(self.sec_lst)
                self.sp.schedule_to_target_sec(func.id, target_sec.id)
            else:
                if random.choice([0, 1]):
                    self.sp.execution_on_iot(func.id)
                else:
                    target_sec = random.choice(self.sec_lst)
                    self.sp.schedule_to_target_sec(func.id, target_sec.id)

            # 计算改变之后的cost
            next_cost = self.get_cost()

            # 如果是负收益, 则回退
            if next_cost > prev_cost:
                self.sp.strategy = {}
                self.sp.strategy = old_strategy

        return self.sp

    def get_cost(self):
        return self.sp.get_cost(alloc_method=self.alloc_method)
