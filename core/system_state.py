from typing import List

from core.system_models.network_model import BaseStation, SECServer, IoTDevice, FunctionType, FunctionTask, SECNetwork
from config import *


class SystemState:
    def __init__(self):
        self.base_stations = {}
        self.sec_servers = {}
        self.iot_devices = {}
        self.function_types = {}
        self.functions = {}
        self.sec_network = None

    # === setter方法 ===

    def add_base_station(self, bs: BaseStation, associated_sec_id: int | str):
        self.base_stations[bs.id] = {
            'instance': bs,
            'associated_sec_id': associated_sec_id
        }

    def add_sec_server(self, sec: SECServer):
        self.sec_servers[sec.id] = {
            'instance': sec
        }

    def add_iot_device(self, iot: IoTDevice, associated_bs_id: int | str):
        self.iot_devices[iot.id] = {
            'instance': iot,
            'associated_bs_id': associated_bs_id
        }

    def add_function_type(self, func_type: FunctionType):
        self.function_types[func_type.id] = {
            'instance': func_type
        }

    def add_function(self, func: FunctionTask, associated_iot_id: int | str):
        self.functions[func.id] = {
            'instance': func,
            'associated_iot_id': associated_iot_id
        }

    def set_sec_network(self, sec_network: SECNetwork):
        self.sec_network = sec_network

    # === getter方法 ===

    # === 数量 ===

    def get_base_station_count(self) -> int:
        return len(self.base_stations.keys())

    def get_sec_server_count(self) -> int:
        return len(self.sec_servers.keys())

    def get_iot_device_count(self) -> int:
        return len(self.iot_devices.keys())

    def get_function_type_count(self) -> int:
        return len(self.function_types.keys())

    def get_function_count(self) -> int:
        return len(self.functions.keys())

    # === 实例 ===

    def get_sec_server_instance(self, sec_id: int | str) -> SECServer:
        return self.sec_servers[sec_id]['instance']

    def get_function_instance(self, func_id: int | str) -> FunctionTask:
        return self.functions[func_id]['instance']

    # === 实例列表 ===

    def get_sec_list(self) -> List[SECServer]:
        return [_val['instance'] for _val in self.sec_servers.values()]

    def get_function_type_list(self) -> List[FunctionType]:
        return [_val['instance'] for _val in self.function_types.values()]

    def get_function_list(self) -> List[FunctionTask]:
        return [_val['instance'] for _val in self.functions.values()]

    # === 复杂属性计算 ===

    # 获取某个sec的总可用内存（S_k = min(M_K, CR_k / RATIO)，单位：MB）
    @staticmethod
    def get_sec_available_mem(sec: SECServer) -> float:
        return min(sec.memory, sec.comp_resource / RATIO)

    # 获取某个sec的总可用计算资源（CR_K = min(M_k * RATIO, CR_k)，单位：MHz）
    @staticmethod
    def get_sec_available_cr(sec: SECServer) -> float:
        return min(sec.memory * RATIO, sec.comp_resource)

    # 计算系统总内存 (单位: MB)
    def get_system_available_mem(self) -> float:
        return sum(self.get_sec_available_mem(sec) for sec in self.get_sec_list())

    # 计算SEC侧总计算资源 (单位: MHz)
    def get_system_available_cr(self) -> float:
        return sum(self.get_sec_available_cr(sec) for sec in self.get_sec_list())

    # === 映射函数，规则: F->U->BS->S ===

    # F->U mapping
    def f2u_mapping(self, func_id: int | str) -> IoTDevice:
        try:
            iot_id = self.functions[func_id]['associated_iot_id']
            return self.iot_devices[iot_id]['instance']
        except KeyError as e:
            raise KeyError(e)

    # U->S mapping
    def u2s_mapping(self, iot_id: int | str) -> SECServer:
        try:
            bs_id = self.iot_devices[iot_id]['associated_bs_id']
            sec_id = self.base_stations[bs_id]['associated_sec_id']
            return self.sec_servers[sec_id]['instance']
        except KeyError as e:
            raise KeyError(e)

    # F->S mapping
    def f2s_mapping(self, func_id: int | str) -> SECServer:
        try:
            iot_id = self.functions[func_id]['associated_iot_id']
            bs_id = self.iot_devices[iot_id]['associated_bs_id']
            sec_id = self.base_stations[bs_id]['associated_sec_id']
            return self.sec_servers[sec_id]['instance']
        except KeyError as e:
            raise KeyError(e)

    # F->F_type mapping
    def f2f_type_mapping(self, func_id: int | str) -> FunctionType:
        try:
            func: FunctionTask = self.functions.get(func_id)['instance']
            return func.func_type
        except Exception as e:
            raise Exception(e)
