import random
import string
from typing import List, Dict

from config import *
from core.system_models.network_model import *
from core.system_state import SystemState
from core.strategic_profile import StrategicProfile
from core.algorithm.algo_1_LEAO import algo_1_LEAO
from core.algorithm.algo_2_PGES import algo_2_PGES


def main():
    ss = SystemState()

    # 初始化BS和SEC
    for i in range(15):
        bs = BaseStation(id=i)
        rd_CR = random.randint(2500 * 4, 4000 * 16)
        rd_M = random.randint(16 * 1024, 64 * 1024)
        rd_bhBW = random.randint(100, 200)
        sec = SECServer(id=i, comp_resource=rd_CR, memory=rd_M, backhaul_bw=rd_bhBW)
        ss.add_base_station(bs=bs, associated_sec_id=sec.id)
        ss.add_sec_server(sec=sec)

    # 初始化IoT设备
    for i in range(100):
        rd_CR = random.randint(400, 800)
        iot = IoTDevice(id=i, comp_resource=rd_CR, tx_power=0.1, bandwidth=5_000_000, channel_gain=1e-5,
                        noise_power=1e-7)  # 10dB的SNR
        bs_id = random.randint(0, ss.get_base_station_count() - 1)  # 注意这里生成的随机数范围 a <= rd <= b
        ss.add_iot_device(iot=iot, associated_bs_id=bs_id)

    # 初始化函数类型
    for i in range(10):
        type_id = ord('A') + i
        image_size = random.randint(50, 150)
        func_type = FunctionType(id=type_id, image_size=image_size)
        ss.add_function_type(func_type=func_type)

    # 关联到SEC的已缓存列表
    for sec_id, _val in ss.sec_servers.items():
        sec: SECServer = _val['instance']
        # 获取函数类型列表并随机抽取2个
        cached_func_type: List[FunctionType] = random.sample(ss.get_function_type_list(), 3)

        # 使用列表推导式直接获取它们的ID，并转换为集合
        sec.cached_functions = {func_type.id for func_type in cached_func_type}

    # 初始化函数任务
    for i in range(1000):
        # 关联到 FunctionType
        _rd_key = random.choice(list(ss.function_types.keys()))

        func_type: FunctionType = ss.function_types.get(_rd_key)['instance']
        rd_d = random.uniform(0.01, 0.5)
        rd_c = random.randint(200, 800)
        rd_n = random.randint(5, 15)
        func = FunctionTask(id=i, data_size=rd_d, workload=rd_c, invocations=rd_n, func_type=func_type)

        # 关联到 IoTDevice
        _rd_key = random.choice(list(ss.iot_devices.keys()))
        iot: IoTDevice = ss.iot_devices.get(_rd_key).get('instance')

        ss.add_function(func=func, associated_iot_id=iot.id)

    # 初始化SEC互联网络
    sn = SECNetwork()
    for sec_id, _val in ss.sec_servers.items():
        sec: SECServer = _val['instance']
        sn.add_server(server=sec)

    for s1_id, _val1 in ss.sec_servers.items():
        s1: SECServer = _val1['instance']
        for s2_id, _val2 in ss.sec_servers.items():
            s2: SECServer = _val2['instance']

            if s1.id == s2.id:
                continue

            rd_latency = random.uniform(0.02, 0.5)
            rd_bandwidth = random.randint(100, 1000)
            sn.add_connection(server_id1=s1.id, server_id2=s2.id, latency=rd_latency, bandwidth=rd_bandwidth)

    ss.set_sec_network(sn)

    # 初始化策略剖面
    sp = StrategicProfile(system_state=ss)
    sp.reset_strategy()

    print(f'*结果 IoT_Only 系统总成本：{sp.calc_total_cost():4f}')

    # 算法1：LEAO
    alpha: Dict[str, int] = algo_1_LEAO(ss=ss)

    # 更新策略剖面
    for func_id, offloading in alpha.items():
        if offloading == 1:
            sp.strategy[func_id]['offloading'] = offloading
            sp.strategy[func_id]['scheduling'] = ss.f2s_mapping(func_id=func_id).id  # 卸载到本地SEC

    print(f'*结果 算法1-LEAO 优化后系统总成本：{sp.calc_total_cost():4f}')

    offloading_count = 0
    for func_id, _val in sp.strategy.items():
        if _val['offloading'] == 1:
            offloading_count += 1
    print(
        f'*结果 卸载到SEC侧的百分比为：{offloading_count / len(sp.strategy.keys()) * 100:.2f}%，数量：{offloading_count}，总数：{len(sp.strategy.keys())}')

    # 算法2：PGES
    beta, mem_alloc, cr_alloc = algo_2_PGES(ss=ss, sp=sp)

    # 更新策略面
    for func_id, scheduling in beta.items():
        if sp.strategy[func_id]['offloading'] == 1:
            sp.strategy[func_id]['scheduling'] = scheduling

    print(f'*结果 算法2-PGES 优化后系统总成本：{sp.calc_total_cost():4f}')


if __name__ == '__main__':
    main()
