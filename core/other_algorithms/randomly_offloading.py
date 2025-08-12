"""
随机卸载策略（Randomly Offloading）

功能：
    - 作为一个基线（baseline）策略，用于对比更复杂的优化算法效果
    - 随机打乱任务列表，并尽可能地将任务卸载到本地 SEC Server，直到资源上限
    - 固定为每个被卸载的任务分配相同的计算资源（const_cr）

属性：
    ss (SystemState): 系统状态对象，包含当前 IoT 设备、SEC 服务器、任务等信息
    const_cr (int): 固定为每个任务分配的计算资源（单位：MB）
    sp (StrategicProfile): 策略剖面对象，记录每个任务的决策变量（是否卸载、调度位置）
    func_list (List[FunctionTask]): 系统中的所有函数任务实例列表
"""

import random
from typing import List, Dict

from core.system_models.cost_model import local_device_execution, local_sec_execution
from core.system_models.network_model import SECServer, IoTDevice, FunctionTask
from core.system_models.resource_model import calc_effective_res
from core.system_state import SystemState
from core.strategic_profile import StrategicProfile
from config import *


class RandomlyOffloading:
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

        # 分别卸载到本地SEC，直到本地SEC资源限制
        for func in self.func_list:

            # 获取本地SEC
            loc_sec: SECServer = self.ss.f2s_mapping(func_id=func.id)

            if sec_residual[loc_sec.id] >= self.const_cr:
                sec_residual[loc_sec.id] -= self.const_cr
                self.sp.strategy[func.id]['offloading'] = 1
                self.sp.strategy[func.id]['scheduling'] = loc_sec.id

        return self.sp

    def calc_cost(self) -> float:
        cost = 0.0
        for func in self.ss.get_function_list():
            iot: IoTDevice = self.ss.f2u_mapping(func_id=func.id)
            if self.sp.strategy[func.id]['offloading'] == 0:
                latency, energy = local_device_execution(func=func, iot=iot)
            else:
                loc_sec: SECServer = self.ss.f2s_mapping(func_id=func.id)
                latency, energy = local_sec_execution(func=func, iot=iot, sec=loc_sec, cr_ik=RATIO * self.const_cr)

            # 计算归一化成本 (公式33)
            cost += OMEGA * (latency / T_ref) + (1 - OMEGA) * (energy / E_ref)

        return cost
