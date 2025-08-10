from typing import Tuple

from core.system_models.resource_model import *
from core.system_models.cost_model import *
from core.system_state import SystemState


class StrategicProfile:
    def __init__(self, system_state: SystemState):
        self.ss = system_state
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
            for func_id in self.ss.functions.keys()
        }

    # 计算单个函数的成本
    def calc_single_function_cost(self, func_id: int | str):
        # 获取该函数实例
        func: FunctionTask = self.ss.get_function_instance(func_id=func_id)

        # 获取该函数的执行策略
        offloading: int = self.strategy[func_id]['offloading']
        scheduling: int | str = self.strategy[func_id]['scheduling']

        iot: IoTDevice = self.ss.f2u_mapping(func_id=func_id)

        # 策略1：本地设备执行
        if offloading == 0:
            latency, energy = local_device_execution(func=func, iot=iot)

        # 策略2或策略3
        else:
            # 策略2：本地SEC执行
            loc_sec: SECServer = self.ss.f2s_mapping(func_id=func_id)
            if scheduling == loc_sec.id:
                # 计算最优资源分配
                opt_alloc, _ = calc_sec_optim_res_alloc(sec=loc_sec,
                                                        func_list=self.get_sec_func_list(sec_id=loc_sec.id))

                # 获取该函数的最优分配计算资源
                cr_ik = opt_alloc[func_id]['opt_cr_ik']

                latency, energy = local_sec_execution(func=func, iot=iot, sec=loc_sec, cr_ik=cr_ik)


            # 策略3：协作SEC执行
            else:
                # 获取协作SEC
                target_sec: SECServer = self.ss.get_sec_server_instance(sec_id=scheduling)

                # 计算最优资源分配（注意：这里是协作SEC，不是本地SEC）
                opt_alloc, _ = calc_sec_optim_res_alloc(sec=target_sec,
                                                        func_list=self.get_sec_func_list(sec_id=target_sec.id))

                # 获取该函数的最优分配计算资源（注意：这里是协作SEC，不是本地SEC）
                cr_ik = opt_alloc[func_id]['opt_cr_ik']

                latency, energy = collab_sec_execution(func=func, iot=iot, local_sec=loc_sec, target_sec=target_sec,
                                                       sec_network=self.ss.sec_network, cr_ik=cr_ik)

        # 计算归一化成本 (公式33)
        cost = OMEGA * (latency / T_ref) + (1 - OMEGA) * (energy / E_ref)

        if LOG_LEVEL == 'debug':
            output = f'*决策：函数{func.id}'
            if self.strategy[func.id]['offloading'] == 0:
                output += f'在本地IoT{self.ss.f2u_mapping(func.id).id}执行，成本{cost:3f}：'
            else:
                scheduling: int | str = self.strategy[func.id]['scheduling']
                if scheduling == self.ss.f2s_mapping(func.id).id == scheduling:
                    output += f'在本地SEC{scheduling}执行，成本{cost:3f}：'
                else:
                    output += f'在协作SEC{scheduling}执行，成本{cost:3f}：'
            output += f'其中延迟{latency / T_ref:3f}, 能耗{energy / E_ref:3f}'
            print(output)

        return cost

    # 计算该策略面总成本
    def calc_total_cost(self):
        total_cost = 0.0
        for func_id in self.ss.functions.keys():
            total_cost += self.calc_single_function_cost(func_id=func_id)
        return total_cost

    # 获取SEC服务器的函数任务列表
    def get_sec_func_list(self, sec_id: int | str) -> List[FunctionTask]:
        rst = []
        for func_id, strategy in self.strategy.items():
            if strategy['scheduling'] == sec_id:
                func: FunctionTask = self.ss.functions[func_id]['instance']
                rst.append(func)
        return rst
