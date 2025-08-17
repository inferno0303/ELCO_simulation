from core.strategic_profile import StrategicProfile
from core.system_models.cost_model import loc_sec_execution
from core.system_state import SystemState


# 最小执行时间优先的调度
class MinExecutionTimeScheduling:
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

            # 计算当前函数在每个SEC的执行时间
            execution_time = {}
            for sec in self.ss.get_sec_list():
                iot = self.ss.f2u_mapping(func.id)
                curr_sec = self.sp.get_func_current_sec(func.id)

                # 计算该函数在每个sec上分配的计算资源
                if sec.id == curr_sec.id:
                    cr_ik = self.sp.get_cr_ik(func=func, sec=sec, alloc_method=self.alloc_method)
                else:
                    # 临时改变策略面，将函数调度到该sec上
                    self.sp.schedule_to_target_sec(func_id=func.id, target_sec_id=sec.id)
                    cr_ik = self.sp.get_cr_ik(func=func, sec=sec, alloc_method=self.alloc_method)
                    self.sp.schedule_to_target_sec(func_id=func.id, target_sec_id=curr_sec.id)

                execution = func.invocations * func.workload / cr_ik
                execution_time[sec.id] = execution

            # 选择执行时间最小的SEC
            target_sec_id = min(execution_time, key=execution_time.get)

            # 调度到执行时间最小的SEC
            self.sp.schedule_to_target_sec(func_id=func.id, target_sec_id=target_sec_id)

        return self.sp

    def get_cost(self):
        return self.sp.get_cost(alloc_method=self.alloc_method)
