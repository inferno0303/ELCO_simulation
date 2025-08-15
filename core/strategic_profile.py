from core.system_models.resource_model import *
from core.system_models.cost_model import *
from core.system_state import SystemState


class StrategicProfile:
    def __init__(self, ss: SystemState):
        self.ss = ss

        # 初始化策略剖面：offloading = 0, scheduling = None
        self.strategy = {
            func_id: {
                'offloading': 0,
                'scheduling': None
            }
            for func_id in ss.functions.keys()
        }

    # 策略1：在本地IoT执行
    def execution_on_iot(self, func_id: int | str):
        self.strategy[func_id]['offloading'] = 0
        self.strategy[func_id]['scheduling'] = None

    # 策略2：在本地SEC执行
    def offload_to_loc_sec(self, func_id: int | str):
        loc_sec: SECServer = self.ss.f2s_mapping(func_id=func_id)
        self.strategy[func_id]['offloading'] = 1
        self.strategy[func_id]['scheduling'] = loc_sec.id

    # 策略3：在协作SEC执行
    def schedule_to_target_sec(self, func_id: int | str, target_sec_id: int | str):
        self.strategy[func_id]['offloading'] = 1
        self.strategy[func_id]['scheduling'] = target_sec_id

    # 判断函数任务的策略 -> 1/2/3
    def get_func_strategy(self, func_id: int | str) -> int:
        if self.strategy[func_id]['offloading'] == 0:
            return 1
        else:
            if self.strategy[func_id]['scheduling'] == self.ss.f2s_mapping(func_id=func_id).id:
                return 2
            else:
                return 3

    # 获取sec的函数数量
    def get_sec_func_count(self, sec: SECServer) -> int:
        count = 0
        for func_id, _val in self.strategy.items():
            if _val['offloading'] == 1 and _val['scheduling'] == sec.id:
                count += 1
        return count

    # 获取sec的负载量（单位：MHz）
    def get_sec_workload(self, sec: SECServer) -> float:
        workload = 0.0
        for func_id, _val in self.strategy.items():
            if _val['offloading'] == 1 and _val['scheduling'] == sec.id:
                func = self.ss.get_function_instance(func_id)
                workload += (func.invocations * func.workload)
        return workload

    # 获取sec的负载因子（单位：MHz） C_k = sum(sqrt(n_i * c*i))
    def get_sec_workload_factor(self, sec: SECServer) -> float:
        workload_factor = 0.0
        for func_id, _val in self.strategy.items():
            if _val['offloading'] == 1 and _val['scheduling'] == sec.id:
                func = self.ss.get_function_instance(func_id)
                workload_factor += math.sqrt(func.invocations * func.workload)
        return workload_factor

    # 获取所有已卸载的函数的负载量 (单位: MHz, 仅ELCO第一阶段LEAO使用)
    def get_offload_workload(self) -> float:
        workload = 0.0
        for func_id, _val in self.strategy.items():
            if _val['offloading'] == 1:
                func: FunctionTask = self.ss.get_function_instance(func_id)
                workload += func.invocations * func.workload
        return workload

    # 获取所有已卸载的函数的负载因子 (单位: MHz, 仅ELCO第一阶段LEAO使用)
    def get_offload_workload_factor(self) -> float:
        workload_factor = 0.0
        for func_id, _val in self.strategy.items():
            if _val['offloading'] == 1:
                func: FunctionTask = self.ss.get_function_instance(func_id)
                workload_factor += math.sqrt(func.invocations * func.workload)
        return workload_factor

    # 计算卸载数
    def get_offload_count(self) -> int:
        return sum(1 for val in self.strategy.values() if val.get('offloading', 0) == 1)

    # 计算卸载率
    def get_offload_ratio(self) -> float:
        total_count = len(self.strategy.keys())
        if total_count == 0:
            return 0.0
        return self.get_offload_count() / total_count

    # 计算cost
    def get_cost(self, alloc_method: str = 'WF') -> float:
        cost = 0.0
        for func_id, _val in self.strategy.items():
            func: FunctionTask = self.ss.get_function_instance(func_id)
            iot = self.ss.f2u_mapping(func.id)
            loc_sec = self.ss.f2s_mapping(func.id)
            strategy = self.get_func_strategy(func.id)

            # 策略1
            if strategy == 1:
                latency, energy = iot_execution(func=func, iot=iot)

            # 策略2
            elif strategy == 2:
                # FAIR-平均分配资源
                if alloc_method == 'FAIR':
                    CR_k = calc_effective_res(loc_sec) * RATIO
                    func_count = self.get_sec_func_count(sec=loc_sec)
                    cr_ik = CR_k / func_count
                # LP-线性负载比例
                elif alloc_method == 'LP':
                    CR_k = calc_effective_res(loc_sec) * RATIO
                    sec_workload = self.get_sec_workload(sec=loc_sec)
                    func_workload = func.invocations * func.workload
                    cr_ik = func_workload / sec_workload * CR_k
                # WF-注水算法
                elif alloc_method == 'WF':
                    CR_k = calc_effective_res(loc_sec) * RATIO
                    sec_workload_factor = self.get_sec_workload_factor(sec=loc_sec)
                    func_workload_factor = math.sqrt(func.invocations * func.workload)
                    cr_ik = func_workload_factor / sec_workload_factor * CR_k
                # FIXED-固定分配
                else:
                    fixed_mem = int(alloc_method.split('-')[1])
                    func_count = self.get_sec_func_count(sec=loc_sec)
                    S_k = calc_effective_res(loc_sec)
                    if fixed_mem * func_count > S_k:
                        return float('inf')
                    cr_ik = fixed_mem * RATIO
                latency, energy = loc_sec_execution(func=func, iot=iot, loc_sec=loc_sec, cr_ik=cr_ik)

            # 策略3
            else:
                target_sec_id = self.strategy[func.id]['scheduling']
                target_sec = self.ss.get_sec_server_instance(target_sec_id)
                # FAIR-平均分配资源
                if alloc_method == 'FAIR':
                    CR_k = calc_effective_res(target_sec) * RATIO
                    func_count = self.get_sec_func_count(sec=target_sec)
                    cr_ik = CR_k / func_count
                # LP-线性负载比例
                elif alloc_method == 'LP':
                    CR_k = calc_effective_res(target_sec) * RATIO
                    sec_workload = self.get_sec_workload(sec=target_sec)
                    func_workload = func.invocations * func.workload
                    cr_ik = func_workload / sec_workload * CR_k
                # WF-注水算法
                elif alloc_method == 'WF':
                    CR_k = calc_effective_res(target_sec) * RATIO
                    sec_workload_factor = self.get_sec_workload_factor(sec=target_sec)
                    func_workload_factor = math.sqrt(func.invocations * func.workload)
                    cr_ik = func_workload_factor / sec_workload_factor * CR_k
                # FIXED-固定分配（512MB * r）
                else:
                    fixed_mem = int(alloc_method.split('-')[1])
                    func_count = self.get_sec_func_count(sec=loc_sec)
                    S_k = calc_effective_res(loc_sec)
                    if fixed_mem * func_count > S_k:
                        return float('inf')
                    cr_ik = fixed_mem * RATIO
                latency, energy = collab_sec_execution(func=func, iot=iot, loc_sec=loc_sec, target_sec=target_sec,
                                                       sec_network=self.ss.sec_network, cr_ik=cr_ik)
            # 计算归一化cost并累加
            cost += norm_to_cost(latency=latency, energy=energy)
        return cost

    # 初始化策略剖面：offloading = 0, scheduling = None
    def reset_strategy(self):
        self.strategy = {
            func_id: {
                'offloading': 0,
                'scheduling': None
            }
            for func_id in self.ss.functions.keys()
        }

    # 计算单个函数的成本
    def calc_single_function_cost(self, func_id: int | str):
        # 获取该函数实例
        func: FunctionTask = self.ss.get_function_instance(func_id=func_id)

        # 获取该函数的执行策略
        offloading: int = self.strategy[func_id]['offloading']
        scheduling: int | str = self.strategy[func_id]['scheduling']

        iot: IoTDevice = self.ss.f2u_mapping(func_id=func_id)

        # 策略1：本地设备执行
        if offloading == 0:
            latency, energy = iot_execution(func=func, iot=iot)

        # 策略2或策略3
        else:
            # 策略2：本地SEC执行
            loc_sec: SECServer = self.ss.f2s_mapping(func_id=func_id)
            if scheduling == loc_sec.id:
                # 计算最优资源分配
                opt_alloc, _ = calc_sec_optim_res_alloc(sec=loc_sec,
                                                        func_list=self.get_sec_func_list(sec_id=loc_sec.id))

                # 获取该函数的最优分配计算资源
                cr_ik = opt_alloc[func_id]['opt_cr_ik']

                latency, energy = loc_sec_execution(func=func, iot=iot, loc_sec=loc_sec, cr_ik=cr_ik)


            # 策略3：协作SEC执行
            else:
                # 获取协作SEC
                target_sec: SECServer = self.ss.get_sec_server_instance(sec_id=scheduling)

                # 计算最优资源分配（注意：这里是协作SEC，不是本地SEC）
                opt_alloc, _ = calc_sec_optim_res_alloc(sec=target_sec,
                                                        func_list=self.get_sec_func_list(sec_id=target_sec.id))

                # 获取该函数的最优分配计算资源（注意：这里是协作SEC，不是本地SEC）
                cr_ik = opt_alloc[func_id]['opt_cr_ik']

                latency, energy = collab_sec_execution(func=func, iot=iot, loc_sec=loc_sec, target_sec=target_sec,
                                                       sec_network=self.ss.sec_network, cr_ik=cr_ik)

        # 计算归一化成本 (公式33)
        cost = OMEGA * (latency / T_ref) + (1 - OMEGA) * (energy / E_ref)

        if LOG_LEVEL == 'debug':
            output = f'*决策：函数{func.id}'
            if self.strategy[func.id]['offloading'] == 0:
                output += f'在本地IoT{self.ss.f2u_mapping(func.id).id}执行，成本{cost:3f}：'
            else:
                scheduling: int | str = self.strategy[func.id]['scheduling']
                if scheduling == self.ss.f2s_mapping(func.id).id == scheduling:
                    output += f'在本地SEC{scheduling}执行，成本{cost:3f}：'
                else:
                    output += f'在协作SEC{scheduling}执行，成本{cost:3f}：'
            output += f'其中延迟{latency / T_ref:3f}, 能耗{energy / E_ref:3f}'
            print(output)

        return cost

    # 计算该策略面总成本
    def calc_total_cost(self):
        total_cost = 0.0
        for func_id in self.ss.functions.keys():
            total_cost += self.calc_single_function_cost(func_id=func_id)
        return total_cost

    # 获取SEC服务器的函数任务列表
    def get_sec_func_list(self, sec_id: int | str) -> List[FunctionTask]:
        rst = []
        for func_id, strategy in self.strategy.items():
            if strategy['scheduling'] == sec_id:
                func: FunctionTask = self.ss.functions[func_id]['instance']
                rst.append(func)
        return rst
