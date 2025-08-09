from typing import Dict
from core.system_models.resource_model import *
from core.system_models.cost_model import *
from core.system_state import *
from config import *


def algorithm_1_LEAO(system_state: SystemState) -> Dict[str, int]:
    # Init：返回值
    alpha = dict.fromkeys(system_state.functions.keys(), 0)

    # Init：计算资源池可用资源
    S_avail = 0.0
    for sec_id, _val in system_state.sec_servers.items():
        sec: SECServer = _val['instance']
        S_avail += calculate_effective_capacity(sec_server=sec, ratio=RATIO)

    _delta_cost = dict.fromkeys(system_state.functions.keys(), float('-inf'))
    for func_id, _val in system_state.functions.items():
        func: FunctionTask = _val['instance']
        iot: IoTDevice = system_state.f2u_mapping(func_id=func_id)
        sec: SECServer = system_state.f2s_mapping(func_id=func_id)

        # 计算策略1的cost
        print(f'LEAO 策略1：')
        latency, energy = local_device_execution(func=func, iot=iot)
        cost_s1 = OMEGA * (latency / T_ref) + (1 - OMEGA) * (energy / E_ref)
        print("------")


        # 计算策略2的cost
        print(f'LEAO 策略2：')
        latency, energy = local_sec_execution(func=func, iot=iot, sec=sec, cr_ik=256 * RATIO)
        cost_s2 = OMEGA * (latency / T_ref) + (1 - OMEGA) * (energy / E_ref)
        print("------")

        # 计算并记录 delta_cost
        _delta_cost[func_id] = cost_s1 - cost_s2

    # 对 delta_cost 降序排列
    for func_id, delta in sorted(_delta_cost.items(), key=lambda item: item[1], reverse=True):

        # 如果有正收益，则卸载到本地SEC，并扣减资源池资源
        if delta > 0 and S_avail > 256:
            alpha[func_id] = 1
            S_avail -= 256
        else:
            break

    return alpha
