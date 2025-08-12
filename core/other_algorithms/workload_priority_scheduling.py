import random
from typing import List

from core.system_models.cost_model import local_device_execution, local_sec_execution, collab_sec_execution
from core.system_models.network_model import SECServer, IoTDevice, FunctionTask
from core.system_models.resource_model import calc_effective_res
from core.system_state import SystemState
from core.strategic_profile import StrategicProfile
from config import *


class WorkloadPriorityScheduling:
    def __init__(self, ss: SystemState):
        self.ss = ss
        self.sp = StrategicProfile(system_state=ss)
        self.sp.reset_strategy()

        # 获取函数列表（按负载优先）
        self.func_list: List[FunctionTask] = sorted(
            ss.get_function_list(),
            key=lambda f: f.workload,
            reverse=True
        )

        # 统计每个 SEC 的任务数量
        self.sec_func_counts = {sec.id: 0 for sec in ss.get_sec_list()}

        # 随机负载均衡 SEC 列表
        self.sec_list: List[SECServer] = ss.get_sec_list()
        random.shuffle(self.sec_list)
        self.sec_idx = 0

    def run(self) -> StrategicProfile:
        for func in self.func_list:
            loc_sec: SECServer = self.ss.f2s_mapping(func_id=func.id)

            # Step 1: 如果本地 SEC 有资源并且能降低 cost，就用本地 SEC
            if self.try_assign(func, loc_sec):
                continue

            # Step 2: 如果本地 SEC 超载，则尝试协作 SEC
            self.try_assign_to_collab_sec(func, exclude_sec_id=loc_sec.id)

        return self.sp

    def try_assign(self, func: FunctionTask, sec: SECServer) -> bool:
        """尝试将 func 卸载到指定 SEC，如果 cost 下降则成功"""
        # 判断是否有资源
        cr_ik = calc_effective_res(sec) / (self.sec_func_counts[sec.id] + 1)
        if cr_ik < 128 * RATIO:
            return False

        prev_cost = self.calc_cost()

        # 执行卸载
        self.sp.strategy[func.id]['offloading'] = 1
        self.sp.strategy[func.id]['scheduling'] = sec.id
        self.sec_func_counts[sec.id] += 1

        # 检查是否降低了 cost
        next_cost = self.calc_cost()
        if next_cost > prev_cost:
            # 回滚
            self.sp.strategy[func.id]['offloading'] = 0
            self.sp.strategy[func.id]['scheduling'] = None
            self.sec_func_counts[sec.id] -= 1
            return False
        return True

    def try_assign_to_collab_sec(self, func: FunctionTask, exclude_sec_id: str):
        """尽力而为地寻找可用的协作 SEC"""
        tried_count = 0
        while tried_count < len(self.sec_list):
            sec = self.sec_list[self.sec_idx]
            self.sec_idx = (self.sec_idx + 1) % len(self.sec_list)
            tried_count += 1

            if sec.id == exclude_sec_id:
                continue

            if self.try_assign(func, sec):
                break  # 成功分配

    def calc_cost(self) -> float:
        """计算系统总成本"""
        cost = 0.0
        for func in self.ss.get_function_list():
            iot: IoTDevice = self.ss.f2u_mapping(func_id=func.id)

            if self.sp.strategy[func.id]['offloading'] == 0:
                latency, energy = local_device_execution(func, iot)
            else:
                loc_sec: SECServer = self.ss.f2s_mapping(func_id=func.id)
                target_id = self.sp.strategy[func.id]['scheduling']

                # 策略2：本地 SEC
                if target_id == loc_sec.id:
                    cr_ik = calc_effective_res(loc_sec) / self.sec_func_counts[loc_sec.id]
                    latency, energy = local_sec_execution(func, iot, loc_sec, cr_ik)
                # 策略3：协作 SEC
                else:
                    target_sec: SECServer = self.ss.get_sec_server_instance(target_id)
                    cr_ik = calc_effective_res(target_sec) / self.sec_func_counts[target_sec.id]
                    latency, energy = collab_sec_execution(func, iot, loc_sec, target_sec, self.ss.sec_network, cr_ik)

            # 计算归一化成本 (公式33)
            cost += OMEGA * (latency / T_ref) + (1 - OMEGA) * (energy / E_ref)

        return cost
