from core.system_models.resource_model import *
from core.system_models.cost_model import *
from core.system_state import SystemState


class StrategicProfile:
    def __init__(self, system_state: SystemState):
        self.system_state = system_state
        self.strategy = {}
        self.reset_strategy()  # 初始化策略剖面

    def __repr__(self):
        return f'StrategicProfile'

    # 初始化策略剖面：offloading = 0, scheduling = None
    def reset_strategy(self):
        self.strategy = {
            func_id: {
                'offloading': 0,
                'scheduling': None
            }
            for func_id in self.system_state.functions.keys()
        }

    # 计算单个函数的成本
    def calc_single_function_cost(self, func_id: int | str):
        # 获取该函数实例
        func: FunctionTask = self.system_state.functions[func_id]['instance']

        # 获取该函数的执行策略
        strategy = self.strategy[func_id]
        offloading: int = strategy['offloading']
        scheduling: int | str = strategy['scheduling']

        # 获取该函数所在的IoT设备 F->U
        iot: IoTDevice = self.system_state.f2u_mapping(func_id=func_id)

        # 获取该函数所在的SEC服务器 F->S
        sec: SECServer = self.system_state.f2s_mapping(func_id=func_id)

        # 策略1：本地设备执行
        if offloading == 0:
            latency, energy = local_device_execution(func=func, iot=iot)

        # 策略2或策略3
        else:

            # 策略2：本地SEC执行
            if scheduling == sec.id:
                # 获取目标SEC服务器的函数列表
                sec_func_list = self.get_sec_func_list(sec_id=sec.id)

                # 计算最优资源分配
                opt_alloc, opt_total_exe_time = optimal_continuous_allocation(sec=sec,
                                                                              func_list=sec_func_list, ratio=RATIO)

                # 获取该函数的最优分配计算资源
                cr_ik = opt_alloc[func_id]['opt_cr_ik']

                latency, energy = local_sec_execution(func=func, iot=iot, sec=sec,
                                                      cr_ik=cr_ik)

            # 策略3：协作SEC执行
            else:
                # 获取该函数执行的目标SEC服务器
                target_sec: SECServer = self.system_state.sec_servers[scheduling]['instance']

                # 获取目标SEC服务器的函数列表（注意：这里是协作SEC，不是本地SEC）
                sec_func_list = self.get_sec_func_list(sec_id=target_sec.id)

                # 计算最优资源分配（注意：这里是协作SEC，不是本地SEC）
                opt_alloc, opt_total_exe_time = optimal_continuous_allocation(sec=sec,
                                                                              func_list=sec_func_list, ratio=RATIO)

                # 获取该函数的最优分配计算资源（注意：这里是协作SEC，不是本地SEC）
                cr_ik = opt_alloc[func_id]['opt_cr_ik']

                latency, energy = collaborative_sec_execution(func=func, iot=iot,
                                                              local_sec=sec,
                                                              target_sec=target_sec,
                                                              sec_network=self.system_state.sec_network,
                                                              cr_ik=cr_ik)

        # 计算归一化成本 (公式33)
        normalized_latency = latency / T_ref
        normalized_energy = energy / E_ref
        cost = OMEGA * normalized_latency + (1 - OMEGA) * normalized_energy
        return cost

    # 计算该策略面总成本
    def calc_total_cost(self):
        total_cost = 0.0
        for func_id in self.system_state.functions.keys():
            total_cost += self.calc_single_function_cost(func_id=func_id)
        return total_cost

    # 获取SEC服务器的函数任务列表
    def get_sec_func_list(self, sec_id: int | str) -> List[FunctionTask]:
        rst = []
        for func_id, strategy in self.strategy.items():
            if strategy['scheduling'] == sec_id:
                function: FunctionTask = self.system_state.functions[func_id]['instance']
                rst.append(function)
        return rst
