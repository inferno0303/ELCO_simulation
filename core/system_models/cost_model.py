from core.system_models.network_model import FunctionTask, IoTDevice, SECServer, SECNetwork
from config import *


def local_device_execution(func: FunctionTask, iot: IoTDevice):
    """
    策略1：本地设备执行
    :param func: 函数任务对象
    :param iot: IoT设备对象
    :return: (延迟, 能耗)
    """
    # 计算执行延迟 (公式15)
    latency = (func.invocations * func.workload) / iot.comp_resource

    # 计算能耗 (公式16)
    energy = ENERGY_COEFFICIENT * func.invocations * func.workload * (iot.comp_resource ** 2)

    print(f'函数{func.id} di {func.data_size}MB ci {func.workload}MHz ni {func.invocations}次，IoT执行真实值：延迟{latency}s，能耗{energy}J，iot能力{iot.comp_resource}')

    return latency, energy


def local_sec_execution(func: FunctionTask, iot: IoTDevice, sec: SECServer, cr_ik: float) -> tuple:
    """
    策略2：本地SEC执行
    :param func: 函数任务对象
    :param iot: IoT设备对象
    :param sec: SEC服务器对象
    :param cr_ik: CPU分配(MHz)
    :return: (总延迟, 能耗)
    """
    # 1. 计算上行传输延迟 (公式17)
    T_d2s = func.invocations * func.data_size / (iot.uplink_rate / 8)

    # 2. 计算冷启动延迟 (公式18-20)
    # 检查容器是否已缓存
    if func.func_type.id in sec.cached_functions:
        T_pull = 0
    else:
        T_pull = func.func_type.image_size / (sec.backhaul_bw / 8)

    # 容器初始化时间 (公式20)
    T_init = (INITIALIZATION_COEFFICIENT * func.func_type.image_size) / cr_ik
    T_cold = T_pull + T_init

    # 3. 计算执行时间 (公式21)
    T_exe = func.invocations * func.workload / cr_ik

    # 总延迟 (公式22)
    total_latency = T_d2s + T_cold + T_exe

    # 能耗 (公式23)
    energy = iot.tx_power * T_d2s

    print(f'函数{func.id} di {func.data_size}MB ci {func.workload}MHz ni {func.invocations}次，Local SEC执行真实值：延迟{total_latency}s=T_d2s{T_d2s}s+T_pull{T_pull}+T_init{T_init}+T_exe{T_exe}，能耗{energy}J=TX_power*T_d2s{iot.tx_power}*{T_d2s}，iot能力{iot.comp_resource}')

    return total_latency, energy


def collaborative_sec_execution(func: FunctionTask, iot: IoTDevice, local_sec: SECServer, target_sec: SECServer,
                                sec_network: SECNetwork, cr_ik: float) -> tuple:
    """
    策略3：协作SEC执行
    :param sec_network: SECNetwork
    :param func: 函数任务对象
    :param iot: IoT设备对象
    :param local_sec: 本地SEC服务器
    :param target_sec: 目标SEC服务器
    :param cr_ik: CPU分配(MHz)
    :return: (总延迟, 能耗)
    """
    # 1. 计算上行传输延迟 (同策略2)
    T_d2s = func.invocations * func.data_size / (iot.uplink_rate / 8)

    # 2. 计算服务器间传输延迟 (公式24)
    # 获取服务器间连接参数
    latency, bandwidth = sec_network.get_connection(local_sec.id, target_sec.id)
    if latency and bandwidth:
        T_s2s = func.invocations * func.data_size / (bandwidth / 8) + latency
    else:
        T_s2s = float('inf')

    # 3. 计算目标服务器的冷启动延迟 (同策略2)
    if func.func_type in target_sec.cached_functions:
        T_pull = 0
    else:
        T_pull = func.func_type.image_size / (target_sec.backhaul_bw / 8)

    T_init = (INITIALIZATION_COEFFICIENT * func.func_type.image_size) / cr_ik
    T_cold = T_pull + T_init

    # 4. 计算执行时间 (公式26)
    T_exe = (func.invocations * func.workload) / cr_ik

    # 总延迟 (公式27)
    total_latency = T_d2s + T_s2s + T_cold + T_exe

    # 能耗 (与策略2相同)
    energy = iot.tx_power * T_d2s

    return total_latency, energy
