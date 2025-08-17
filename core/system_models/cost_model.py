from core.system_models.network_model import FunctionTask, IoTDevice, SECServer, SECNetwork
from config import *


def iot_execution(func: FunctionTask, iot: IoTDevice):
    """
    策略1：本地设备执行
    :param func: 函数任务对象
    :param iot: IoT设备对象
    :return: (延迟, 能耗)
    """
    # 计算执行延迟 (公式15)
    latency = (func.invocations * func.workload) / iot.comp_resource

    # 计算能耗 (公式16)
    energy = IOT_EXE_EFFICIENT * func.invocations * func.workload * (iot.comp_resource ** 2)

    return latency, energy


def loc_sec_execution(func: FunctionTask, iot: IoTDevice, loc_sec: SECServer, cr_ik: float) -> tuple:
    """
    策略2：本地SEC执行
    :param func: 函数任务对象
    :param iot: IoT设备对象
    :param loc_sec: SEC服务器对象
    :param cr_ik: CPU分配(MHz)
    :return: (总延迟, 能耗)
    """
    # 1. 计算上行传输延迟 (公式17)
    T_d2s = (func.invocations * func.data_size) / (iot.uplink_rate / 8)

    # 2. 计算冷启动延迟 (公式18-20)
    # 检查容器是否已缓存
    if func.func_type.id in loc_sec.cached_functions:
        T_pull = 0
    else:
        T_pull = func.func_type.image_size / (loc_sec.backhaul_bw / 8)

    # 容器初始化时间 (公式20)
    T_init = (SEC_CONT_INIT_EFFI * func.func_type.image_size) / cr_ik
    T_cold = T_pull + T_init

    # 3. 计算执行时间 (公式21)
    T_exe = func.invocations * func.workload / cr_ik

    # 总延迟 (公式22)
    total_latency = T_d2s + T_cold + T_exe

    # 能耗 (公式23)
    energy = iot.tx_power * T_d2s / IOT_TX_EFFICIENT

    return total_latency, energy


def collab_sec_execution(func: FunctionTask, iot: IoTDevice, loc_sec: SECServer, target_sec: SECServer,
                         sec_network: SECNetwork, cr_ik: float) -> tuple:
    """
    策略3：协作SEC执行
    :param sec_network: SECNetwork
    :param func: 函数任务对象
    :param iot: IoT设备对象
    :param loc_sec: 本地SEC服务器
    :param target_sec: 目标SEC服务器
    :param cr_ik: CPU分配(MHz)
    :return: (总延迟, 能耗)
    """
    # 1. 计算上行传输延迟 (同策略2)
    T_d2s = (func.invocations * func.data_size) / (iot.uplink_rate / 8)

    # 2. 计算服务器间传输延迟 T^s2s (公式24)
    lat, bw = sec_network.get_latency_and_bandwidth(loc_sec.id, target_sec.id)
    if lat and bw:
        T_s2s = (func.invocations * func.data_size) / (bw / 8) + lat
    else:
        T_s2s = float('inf')

    # 3. 计算目标服务器的冷启动延迟 T^cold (同策略2)
    if func.func_type.id in target_sec.cached_functions:
        T_pull = 0
    else:
        T_pull = func.func_type.image_size / (target_sec.backhaul_bw / 8)

    T_init = (SEC_CONT_INIT_EFFI * func.func_type.image_size) / cr_ik
    T_cold = T_pull + T_init

    # 4. 计算执行时间 T^exe (公式26)
    T_exe = (func.invocations * func.workload) / cr_ik

    # 总延迟 (公式27)
    total_latency = T_d2s + T_s2s + T_cold + T_exe

    # 能耗 (与策略2相同)
    energy = iot.tx_power * T_d2s / IOT_TX_EFFICIENT

    return total_latency, energy


def norm_to_cost(latency: float, energy: float) -> float:
    # 计算归一化成本 (公式33)
    cost = OMEGA * (latency / T_ref) + (1 - OMEGA) * (energy / E_ref)
    return cost
