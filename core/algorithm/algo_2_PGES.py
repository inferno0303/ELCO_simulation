import random
from typing import Dict, Tuple

from core.strategic_profile import StrategicProfile
from core.system_models.resource_model import *
from core.system_state import *
from config import *


def algo_2_PGES(ss: SystemState, sp: StrategicProfile, max_iter: int = 10000):
    # Init beta, mem_alloc, cr_alloc
    beta = {
        func_id: _val['scheduling'] for func_id, _val in sp.strategy.items()
    }
    mem_alloc = {}
    cr_alloc = {}
    for func_id, _val in sp.strategy.items():
        func: FunctionTask = ss.get_function_instance(func_id=func_id)
        if _val['offloading'] == 0:
            mem_alloc[func.id] = ss.f2u_mapping(func_id=func.id).comp_resource / RATIO
            cr_alloc[func.id] = ss.f2u_mapping(func_id=func.id).comp_resource
        elif _val['offloading'] == 1:
            sec: SECServer = ss.get_sec_server_instance(sec_id=_val['scheduling'])
            curr_opt_alloc, _ = calc_sec_optim_res_alloc(sec=sec, func_list=sp.get_sec_func_list(sec_id=sec.id))
            mem_alloc[func.id] = curr_opt_alloc[func.id]['opt_m_ik']
            cr_alloc[func.id] = curr_opt_alloc[func.id]['opt_cr_ik']

    iter_count = 0  # 当前迭代次数
    converged = False  # 是否收敛
    while iter_count < max_iter and converged == False:
        iter_count += 1
        migrated = False  # 是否有协作改进（如果没有博弈改进动作，则达到了纳什均衡）

        # 遍历所有函数
        for func_id, scheduling in beta.items():
            if scheduling is None: continue  # 跳过在本地IoT设备执行的函数
            # 准备变量
            func: FunctionTask = ss.get_function_instance(func_id=func_id)  # 函数实例
            iot: IoTDevice = ss.f2u_mapping(func_id=func.id)  # 函数对应的IoT设备
            curr_sec: SECServer = ss.get_sec_server_instance(sec_id=scheduling)  # 函数当前所处的SEC
            curr_sec_f_lst: List[FunctionTask] = [
                ss.get_function_instance(_f_id) for _f_id, _sd in beta.items() if _sd == curr_sec.id
            ]  # 函数当前所处的SEC的函数列表
            curr_opt_alloc, _ = calc_sec_optim_res_alloc(curr_sec, func_list=curr_sec_f_lst)  # 函数当前所处的SEC的最佳分配
            curr_cr_ik = curr_opt_alloc[func.id]['opt_cr_ik']  # 函数当前被分配的最佳计算资源

            # === （1）计算函数任务当前策略的效用 ===
            # 1. 计算 T^s2s
            curr_T_s2s = 0.0
            if ss.f2s_mapping(func_id=func.id).id != curr_sec.id:
                lat, bw = ss.sec_network.get_connection(sec_id_1=ss.f2s_mapping(func_id=func_id).id,
                                                        sec_id_2=curr_sec.id)
                curr_T_s2s = (func.invocations * func.data_size) / bw + lat

            # 2. 计算 T^cold
            if func.func_type.id in curr_sec.cached_functions:
                curr_T_pull = 0.0
            else:
                curr_T_pull = func.func_type.image_size / (curr_sec.backhaul_bw / 8)

            curr_T_init = (SEC_CONT_INIT_EFFI * func.func_type.image_size) / curr_cr_ik

            curr_T_cold = curr_T_pull + curr_T_init

            # 3. 计算 T^exe
            curr_T_exe = (func.invocations * func.workload) / curr_cr_ik

            # 4. 计算 T^d2s
            T_d2s = (func.invocations * func.data_size) / (iot.uplink_rate / 8)

            # 计算当前效用
            u_curr = -(T_d2s + curr_T_s2s + curr_T_cold + curr_T_exe)
            u_best = u_curr
            best_sec = curr_sec

            # === （2）计算假想效用 ===
            for sec_id in ss.sec_servers.keys():
                hyp_sec: SECServer = ss.get_sec_server_instance(sec_id=sec_id)
                if hyp_sec.id == curr_sec.id: continue  # 跳过当前SEC

                hyp_sec_f_lst: List[FunctionTask] = [func] + [
                    ss.get_function_instance(_f_id) for _f_id, _sd in beta.items() if _sd == hyp_sec.id
                ]  # 假想SEC的函数列表（注意：这里假设当前函数也在假想SEC里）
                hyp_opt_alloc, _ = calc_sec_optim_res_alloc(hyp_sec, func_list=hyp_sec_f_lst)  # 假想SEC的最佳分配
                hyp_cr_ik = hyp_opt_alloc[func.id]['opt_cr_ik']  # 函数当前被分配的最佳计算资源

                # 1. 计算假想T^s2s
                hyp_T_s2s = 0.0
                if ss.f2s_mapping(func_id=func.id).id != hyp_sec.id:
                    lat, bw = ss.sec_network.get_connection(sec_id_1=ss.f2s_mapping(func_id=func_id).id,
                                                            sec_id_2=hyp_sec.id)
                    hyp_T_s2s = (func.invocations * func.data_size) / bw + lat

                # 2. 计算 T^cold
                if func.func_type.id in hyp_sec.cached_functions:
                    hyp_T_pull = 0.0
                else:
                    hyp_T_pull = func.func_type.image_size / (hyp_sec.backhaul_bw / 8)

                hyp_T_init = (SEC_CONT_INIT_EFFI * func.func_type.image_size) / hyp_cr_ik

                hyp_T_cold = hyp_T_pull + hyp_T_init

                # 3. 计算 T^exe
                hyp_T_exe = (func.invocations * func.workload) / hyp_cr_ik

                # 4. 计算 T^d2s
                T_d2s = (func.invocations * func.data_size) / (iot.uplink_rate / 8)

                # 计算当前效用
                u_hyp = -(T_d2s + hyp_T_s2s + hyp_T_cold + hyp_T_exe)

                # === （3）判断效用改进 ===
                if u_hyp > u_best:
                    u_best = u_hyp
                    best_sec = hyp_sec

            # 函数f_i已经遍历完所有s_k，判断是否需要改变策略
            if best_sec.id != curr_sec.id:
                # 更新调度策略beta
                beta[func.id] = best_sec.id
                migrated = True
                # print(f'*博弈动作：函数{func.id} SEC{curr_sec.id}->SEC{best_sec.id}')

        # 结束博弈
        if not migrated:
            converged = True  # 取得纳什均衡

    # 准备返回值
    for func_id, scheduling in beta.items():
        func: FunctionTask = ss.get_function_instance(func_id=func_id)
        if scheduling is None:
            cr_alloc[func.id] = ss.f2u_mapping(func_id=func.id).comp_resource
            mem_alloc[func_id] = ss.f2u_mapping(func_id=func.id).comp_resource / RATIO
        else:
            sec: SECServer = ss.get_sec_server_instance(sec_id=scheduling)
            sec_f_lst = [
                ss.get_function_instance(func_id)
                for _f_id, _s in beta.items() if _s == sec.id
            ]  # 函数当前所处的SEC的函数列表
            sec_opt_alloc, _ = calc_sec_optim_res_alloc(sec, func_list=sec_f_lst)
            m_ik = sec_opt_alloc[func.id]['opt_m_ik']
            m_ik = max(128, min(m_ik, 1792))
            cr_ik = m_ik * RATIO
            mem_alloc[func.id] = m_ik
            cr_alloc[func.id] = cr_ik

    return beta, mem_alloc, cr_alloc
