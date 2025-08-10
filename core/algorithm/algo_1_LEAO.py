from typing import Dict
from core.system_models.resource_model import *
from core.system_models.cost_model import *
from core.system_state import *
from config import *


def algo_1_LEAO(ss: SystemState) -> Dict[str, int]:
    # Init：返回值
    alpha = dict.fromkeys(ss.functions.keys(), 0)

    # Init：计算资源池可用资源
    S_total = 0.0
    for sec_id, _val in ss.sec_servers.items():
        sec: SECServer = _val['instance']
        S_total += calc_effective_res(sec_server=sec)

    # Init：计算如果每个函数都卸载，按注水算法，给每个函数分多少计算资源
    opt_alloc = {}

    C_total = 0.0
    for func_id, _val in ss.functions.items():
        func: FunctionTask = _val['instance']
        C_total += func.invocations * func.workload

    C_k = calc_workload_normalization(func_list=ss.get_function_list())

    for func in ss.get_function_list():
        sqrt_nc = (func.invocations * func.workload) ** 0.5
        m_ik = (sqrt_nc * S_total) / C_k
        m_ik = max(128, min(1792, m_ik))  # 剪切至取值范围
        cr_ik = RATIO * m_ik
        opt_alloc[func.id] = {'opt_m_ik': m_ik, 'opt_cr_ik': cr_ik}

    # 算法开始
    _delta_cost = dict.fromkeys(ss.functions.keys(), float('-inf'))
    for func_id, _val in ss.functions.items():
        func: FunctionTask = _val['instance']
        iot: IoTDevice = ss.f2u_mapping(func_id=func_id)
        sec: SECServer = ss.f2s_mapping(func_id=func_id)

        # 计算策略1的cost
        # print(f'LEAO-策略1：')
        latency, energy = local_device_execution(func=func, iot=iot)
        cost_s1 = OMEGA * (latency / T_ref) + (1 - OMEGA) * (energy / E_ref)

        # 计算策略2的cost
        # print(f'LEAO-策略2：')
        latency, energy = local_sec_execution(func=func, iot=iot, sec=sec, cr_ik=opt_alloc[func.id]['opt_cr_ik'])
        cost_s2 = OMEGA * (latency / T_ref) + (1 - OMEGA) * (energy / E_ref)
        # print("------")

        # 计算并记录 delta_cost
        _delta_cost[func_id] = cost_s1 - cost_s2

    # 对 delta_cost 降序排列
    for func_id, delta in sorted(_delta_cost.items(), key=lambda item: item[1], reverse=True):

        # 如果有正收益，则卸载到本地SEC，并扣减资源池资源
        if delta > 0 and S_total >= opt_alloc[func_id]['opt_m_ik']:
            alpha[func_id] = 1
            S_total -= opt_alloc[func_id]['opt_m_ik']
        else:
            break

    return alpha
