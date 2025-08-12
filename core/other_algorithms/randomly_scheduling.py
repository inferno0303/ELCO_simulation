import random
from typing import List, Dict

from core.system_models.cost_model import local_device_execution, local_sec_execution, collab_sec_execution
from core.system_models.network_model import SECServer, IoTDevice, FunctionTask
from core.system_models.resource_model import calc_effective_res
from core.system_state import SystemState
from core.strategic_profile import StrategicProfile
from config import *


class RandomlyScheduling:
    def __init__(self, ss: SystemState, const_cr: int = 512):
        self.ss = ss
        self.const_cr = const_cr

        # 初始化一个策略剖面
        self.sp = StrategicProfile(system_state=ss)
        self.sp.reset_strategy()

        # 获取函数列表
        self.func_list: List[FunctionTask] = ss.get_function_list()

        # 获取SEC列表
        self.sec_list: List[SECServer] = ss.get_sec_list()

    def run(self) -> StrategicProfile:
        # 随机化函数列表
        random.shuffle(self.func_list)

        # build initial residual resource mapping for each SEC (unit: MB)
        sec_residual: Dict[int, float] = {sec.id: calc_effective_res(sec_server=sec) for sec in self.sec_list}

        # 分别卸载到随机SEC，直到所有SEC资源限制
        for func in self.func_list:
            secs_to_try = self.sec_list.copy()
            random.shuffle(secs_to_try)
            assigned = False
            for sec in secs_to_try:
                # if this sec has enough residual resource, assign and decrement
                if sec_residual[sec.id] >= self.const_cr:
                    sec_residual[sec.id] -= self.const_cr
                    self.sp.strategy[func.id]['offloading'] = 1
                    self.sp.strategy[func.id]['scheduling'] = sec.id
                    assigned = True
                    break  # assigned successfully, move to next function

            # if we couldn't assign this function to any SEC, stop the whole scheduling loop
            if not assigned:
                # All SECs have insufficient resource for this function (global exhaustion)
                break

        return self.sp

    def calc_cost(self) -> float:
        cost = 0.0
        for func in self.ss.get_function_list():
            iot: IoTDevice = self.ss.f2u_mapping(func_id=func.id)

            # 策略1：本地IoT执行
            if self.sp.strategy[func.id]['offloading'] == 0:
                latency, energy = local_device_execution(func=func, iot=iot)
            else:
                loc_sec: SECServer = self.ss.f2s_mapping(func_id=func.id)

                # 如果是策略2：卸载到了本地SEC
                if loc_sec.id == self.sp.strategy[func.id]['scheduling']:
                    latency, energy = local_sec_execution(func=func, iot=iot, sec=loc_sec, cr_ik=RATIO * self.const_cr)

                # 策略3：卸载到了协作SEC
                else:
                    target_sec: SECServer = self.ss.get_sec_server_instance(self.sp.strategy[func.id]['scheduling'])
                    latency, energy = collab_sec_execution(func=func, iot=iot, local_sec=loc_sec, target_sec=target_sec,
                                                           sec_network=self.ss.sec_network, cr_ik=RATIO * self.const_cr)

            # 计算归一化成本 (公式33)
            cost += OMEGA * (latency / T_ref) + (1 - OMEGA) * (energy / E_ref)

        return cost
