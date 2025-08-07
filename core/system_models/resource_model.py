from typing import List
from core.system_models.network_model import *


def calculate_effective_capacity(sec_server: SECServer, ratio: float) -> float:
    """
    计算服务器的有效可分配容量 S_k^*
    :param sec_server: SECServer
    :param ratio: 内存*ratio=CPU计算资源
    :return: 有效容量(MB)
    """
    # S_k^* = min(M_k, CR_k / r)
    return min(sec_server.memory, sec_server.comp_resource / ratio)


def calculate_workload_normalization(func_list: List[FunctionTask]) -> float:
    """
    计算工作负载归一化因子 C_k = Σ√(n_j c_j)
    :param func_list: 服务器上的任务列表
    :return: 归一化因子值
    """
    return sum((func.invocations * func.workload) ** 0.5 for func in func_list)


def optimal_continuous_allocation(sec: SECServer, func_list: List[FunctionTask], ratio: float):
    """
    计算连续最优资源分配（公式11-14）
    :param ratio: 内存*ratio=CPU计算资源
    :param sec: SECServer对象
    :param func_list: 服务器上的任务列表
    :return: (allocations, total_time)
      opt_alloc: 每个任务的资源分配字典 {task_id: {'opt_m_ik': m_ik, 'opt_cr_ik': cr_ik}}
      opt_total_exe_time: 服务器总完成时间
    """

    # 计算参数
    S_k = calculate_effective_capacity(sec, ratio)
    C_k = calculate_workload_normalization(func_list)

    opt_alloc = {}
    for func in func_list:
        # 计算√(n_i c_i)
        sqrt_nc = (func.invocations * func.workload) ** 0.5

        # 公式11: 最优内存分配
        m_ik = (sqrt_nc * S_k) / C_k

        # 公式12: 最优CPU分配
        cr_ik = ratio * m_ik

        # 存储分配结果
        opt_alloc[func.id] = {'opt_m_ik': m_ik, 'opt_cr_ik': cr_ik}

    # 公式14: 最小总完成时间
    opt_total_exe_time = (C_k ** 2) / (ratio * S_k)

    return opt_alloc, opt_total_exe_time
