import random
from typing import Dict, Tuple

from core.strategic_profile import StrategicProfile
from core.system_models.resource_model import *
from core.system_models.cost_model import *
from core.system_state import *
from config import *


def algorithm_2_PGES(ss: SystemState, sp: StrategicProfile, max_iter: int = 1000, delta: float = 10e-3) \
        -> Tuple[Dict[str, int], Dict[str, float], Dict[str, float]]:
    # Init：返回值
    beta = {
        func_id: ss.f2s_mapping(func_id=func_id).id
        for func_id in ss.functions.keys()
    }
    mem_alloc = {
        func_id: 0.0
        for func_id in ss.functions.keys()
    }

    comp_res_alloc = {
        func_id: 0.0
        for func_id in ss.functions.keys()
    }

    # 选取 offloading = 1 的函数任务（SEC side function）
    sec_side_func_list = [
        func_id for func_id, _val in sp.strategy.items()
        if _val['offloading'] == 1
    ]

    # 获取SEC列表
    sec_id_list = [sec_id for sec_id in ss.sec_servers.keys()]

    # 初始化一个随机调度 scheduling 决策
    for func_id in sec_side_func_list:
        _rd_sec_id = random.choice(sec_id_list)  # 随机选取一个SEC
        sp.strategy[func_id]['scheduling'] = _rd_sec_id  # 随机调度

    iter_count = 0  # 当前迭代次数
    converged = False  # 是否收敛
    while iter_count < max_iter and converged == False:
        migrated = False
        random.shuffle(sec_side_func_list)  # 将 SEC side function list 随机化

        for func_id in sec_side_func_list:
            # 准备变量
            func: FunctionTask = ss.functions[func_id]['instance']
            iot: IoTDevice = ss.f2u_mapping(func_id=func.id)
            local_sec = ss.f2s_mapping(func_id=func.id)
            curr_sec: SECServer = ss.sec_servers[sp.strategy[func.id]['scheduling']]['instance']

            # === 计算当前策略的效用 ===
            # 1. 计算 T^s2s
            T_s2s = 0
            if local_sec.id != curr_sec.id:
                latency, bandwidth = ss.sec_network.get_connection(server_id1=local_sec.id,
                                                                   server_id2=curr_sec.id)
                T_s2s = (func.invocations * func.data_size) / bandwidth + latency

            # 2. 计算 T^cold，其中 T^cold = T^pull + T^init
            # T^pull
            if func.func_type.id in curr_sec.cached_functions:
                T_pull = 0
            else:
                T_pull = func.func_type.image_size / curr_sec.backhaul_bw

            # T^init
            sec_func_list = sp.get_sec_func_list(sec_id=curr_sec.id)
            opt_alloc, _ = optimal_continuous_allocation(sec=curr_sec, func_list=sec_func_list, ratio=RATIO)
            T_init = (INITIALIZATION_COEFFICIENT * func.func_type.image_size) / opt_alloc[func.id]['opt_cr_ik']

            T_cold = T_pull + T_init

            # 3. 计算 T^exe
            sec_func_list = sp.get_sec_func_list(sec_id=curr_sec.id)
            opt_alloc, _ = optimal_continuous_allocation(sec=curr_sec, func_list=sec_func_list, ratio=RATIO)
            T_exe = (func.invocations * func.workload) / opt_alloc[func.id]['opt_cr_ik']

            # 4. 计算 T^d2s
            T_d2s = (func.invocations * func.data_size) / iot.uplink_rate

            # 计算当前效用函数值
            u_curr = -(T_d2s + T_s2s + T_cold + T_exe)
            u_best = u_curr
            best_sec = curr_sec

            # 遍历所有 sec，计算假想效用
            C_k_curr = calculate_workload_normalization(sec_func_list) - (func.invocations * func.workload) ** 0.5
            for sec_id, _val in ss.sec_servers.items():
                new_sec: SECServer = _val['instance']
                if sec_id == curr_sec.id:
                    continue

                sec_func_list = sp.get_sec_func_list(sec_id=new_sec.id)
                C_k_new = calculate_workload_normalization(sec_func_list) + (func.invocations * func.workload) ** 0.5

                cr_ik_new = RATIO * ((func.invocations * func.workload) ** 0.5) * calculate_effective_capacity(new_sec,
                                                                                                               RATIO) / C_k_new

                # === 计算计算假想效用 ===
                # 1. 计算 T^s2s
                T_s2s = 0
                if local_sec.id != new_sec.id:
                    latency, bandwidth = ss.sec_network.get_connection(server_id1=local_sec.id, server_id2=new_sec.id)
                    T_s2s = (func.invocations * func.data_size) / bandwidth + latency

                # 2. 计算 T^cold，其中 T^cold = T^pull + T^init
                # T^pull
                if func.func_type.id in new_sec.cached_functions:
                    T_pull = 0
                else:
                    T_pull = func.func_type.image_size / new_sec.backhaul_bw

                # T^init
                sec_func_list = sp.get_sec_func_list(sec_id=new_sec.id) + [func]
                opt_alloc, _ = optimal_continuous_allocation(sec=new_sec, func_list=sec_func_list, ratio=RATIO)
                T_init = (INITIALIZATION_COEFFICIENT * func.func_type.image_size) / opt_alloc[func.id]['opt_cr_ik']

                T_cold = T_pull + T_init

                # 3. 计算 T^exe
                sec_func_list = sp.get_sec_func_list(sec_id=new_sec.id) + [func]
                opt_alloc, _ = optimal_continuous_allocation(sec=new_sec, func_list=sec_func_list, ratio=RATIO)
                T_exe = (func.invocations * func.workload) / opt_alloc[func.id]['opt_cr_ik']

                # 计算假想效用函数值
                u_new = -(T_d2s + T_s2s + T_cold + T_exe)

                # 判断效用改进
                if u_new > u_best + delta:
                    u_best = u_new
                    best_sec = new_sec

            # 判断是否需要改变策略
            if best_sec.id != curr_sec.id:
                # 更新调度策略
                beta[func.id] = best_sec.id
                sp.strategy[func.id]['scheduling'] = best_sec.id

                # 表示有函数需要改变策略
                migrated = True

        # 结束遍历所有函数
        if not migrated:
            converged = True  # 取得纳什均衡

        iter_count += 1

    for func_id in sec_side_func_list:
        func: FunctionTask = ss.functions[func_id]['instance']
        sec_id = beta[func.id]
        sec: SECServer = ss.sec_servers[sec_id]['instance']
        sec_func_list = sp.get_sec_func_list(sec_id=sec.id)
        m_ik = ((func.invocations * func.workload) * calculate_effective_capacity(sec_server=sec, ratio=RATIO)
                / calculate_workload_normalization(func_list=sec_func_list))
        if m_ik > 1792:
            m_ik = 1792
        elif m_ik < 128:
            m_ik = 128
        mem_alloc[func.id] = m_ik
        comp_res_alloc[func.id] = RATIO * m_ik

    return beta, mem_alloc, comp_res_alloc
