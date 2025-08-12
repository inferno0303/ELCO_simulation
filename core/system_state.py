from typing import List

from core.system_models.network_model import BaseStation, SECServer, IoTDevice, FunctionType, FunctionTask, SECNetwork


class SystemState:
    def __init__(self):
        self.base_stations = {}
        self.sec_servers = {}
        self.iot_devices = {}
        self.function_types = {}
        self.functions = {}
        self.sec_network = None

    def __repr__(self):
        # return f'EntityManager: \n {self.get_base_station_count()} base_station: {self.base_station}, \n {self.get_sec_server_count()} sec_server: {self.sec_server}, \n {self.get_iot_device_count()} iot_device: {self.iot_device}, \n {self.get_function_type_count()} function_type: {self.function_type}, \n {self.get_function_count()} function: {self.function}'
        return f'EntityManager: \n {self.get_function_count()} bs: {self.base_stations}, \n {self.get_sec_server_count()} se: {self.sec_servers}'

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

    def get_base_station_count(self) -> int:
        return len(self.base_stations.keys())

    def get_sec_server_count(self) -> int:
        return len(self.sec_servers.keys())

    def get_iot_device_count(self) -> int:
        return len(self.iot_devices.keys())

    def get_function_type_count(self) -> int:
        return len(self.function_types.keys())

    def get_sec_server_instance(self, sec_id: int | str) -> SECServer:
        return self.sec_servers[sec_id]['instance']

    def get_sec_list(self) -> List[SECServer]:
        return [_val['instance'] for _val in self.sec_servers.values()]

    def get_function_type_list(self) -> List[FunctionType]:
        return [_val['instance'] for _val in self.function_types.values()]

    def get_function_count(self) -> int:
        return len(self.functions.keys())

    def get_function_instance(self, func_id: int | str) -> FunctionTask:
        return self.functions[func_id]['instance']

    def get_function_list(self) -> List[FunctionTask]:
        return [_val['instance'] for _val in self.functions.values()]

    '''Mapping Rule: F->U->BS->S'''

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
