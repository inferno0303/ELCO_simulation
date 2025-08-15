from core.strategic_profile import StrategicProfile
from core.system_state import SystemState


class IoTOnly:
    def __init__(self, ss: SystemState):
        self.ss = ss
        self.sp = StrategicProfile(ss)

        # 函数列表
        self.func_lst = ss.get_function_list()

    def __repr__(self):
        return f'Algorithm {self.__class__.__name__} with {None} resource alloc method'

    def run(self) -> StrategicProfile:
        for func in self.func_lst:
            self.sp.execution_on_iot(func.id)
        return self.sp

    def get_cost(self):
        return self.sp.get_cost()
