import random
import string

from core.system_models.resource_model import *
from core.system_state import *
from core.strategic_profile import *
from config import *

from core.algorithm.algorithm_1_LEAO import *
from core.algorithm.algorithm_2_PGES import *


def main():
    ss = SystemState()

    for i in range(15):
        bs = BaseStation(id=i)
        rd_CR = random.randint(2500 * 4, 4000 * 16)
        rd_M = random.randint(4 * 1024, 128 * 1024)
        rd_bhBW = random.randint(20, 200)
        sec = SECServer(id=i, comp_resource=rd_CR, memory=rd_M, backhaul_bw=rd_bhBW)
        ss.add_base_station(bs=bs, associated_sec_id=sec.id)
        ss.add_sec_server(sec=sec)

    for i in range(150):
        rd_CR = random.randint(400, 800)
        iot = IoTDevice(id=i, comp_resource=rd_CR, tx_power=0.1, bandwidth=10_000_000, channel_gain=1,
                        noise_power=10e-5)
        bs_id = random.randint(0, ss.get_base_station_count() - 1)  # 注意这里生成的随机数范围 a <= rd <= b
        ss.add_iot_device(iot=iot, associated_bs_id=bs_id)

    for i in range(6):
        type_id = random.choice(string.ascii_uppercase[:10])
        image_size = random.randint(100, 500)
        func_type = FunctionType(id=type_id, image_size=image_size)
        ss.add_function_type(func_type=func_type)

    for i in range(1500):
        # 关联到 FunctionType
        _rd_key = random.choice(list(ss.function_types.keys()))
        func_type: FunctionType = ss.function_types.get(_rd_key)['instance']
        rd_d = random.uniform(0.1, 1.5)
        rd_c = random.randint(5, 50)
        rd_n = random.randint(2, 20)
        func = FunctionTask(id=i, data_size=rd_d, workload=rd_c, invocations=rd_n, func_type=func_type)

        # 关联到 IoTDevice
        _rd_key = random.choice(list(ss.iot_devices.keys()))
        iot: IoTDevice = ss.iot_devices.get(_rd_key).get('instance')

        ss.add_function(func=func, associated_iot_id=iot.id)

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
            rd_bandwidth = random.randint(10, 200)
            sn.add_connection(server_id1=s1.id, server_id2=s2.id, latency=rd_latency, bandwidth=rd_bandwidth)

    ss.set_sec_network(sn)

    # 创建一个策略剖面
    sp = StrategicProfile(system_state=ss)

    total_cost = sp.calc_total_cost()
    print(total_cost)

    # 算法1：LEAO
    alpha: Dict[str, int] = algorithm_1_LEAO(system_state=ss)

    # 更新策略剖面
    for func_id, offloading in alpha.items():
        sp.strategy[func_id]['offloading'] = offloading
        sp.strategy[func_id]['scheduling'] = ss.f2s_mapping(func_id=func_id).id

    total_cost = sp.calc_total_cost()
    print(total_cost)

    # 算法2：PGES
    beta, mem_alloc, cr_alloc = algorithm_2_PGES(ss=ss, sp=sp, max_iter=10000, delta=10e-3)

    total_cost = sp.calc_total_cost()
    print(total_cost)


if __name__ == '__main__':
    main()
