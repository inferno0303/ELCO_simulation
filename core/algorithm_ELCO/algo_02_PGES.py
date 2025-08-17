from config import *
from core.strategic_profile import StrategicProfile
from core.system_state import SystemState


class PGES:
    def __init__(self, ss: SystemState, sp: StrategicProfile, alloc_method: str = 'WF', max_iter: int = 100000):
        self.ss = ss
        self.sp = sp  # 接收一个已有的策略剖面
        self.alloc_method = alloc_method  # 使用的资源分配方法：ES-平均分配，LP-线性负载比例，WF-注水算法
        self.max_iter = max_iter  # 最大博弈迭代次数

        # 函数列表
        self.func_lst = ss.get_function_list()
        self.func_lst = sorted(self.func_lst, key=lambda f: (f.invocations * f.workload), reverse=True)

    def __repr__(self):
        return f'Algorithm PGES with {self.alloc_method} resource alloc method'

    def run(self) -> StrategicProfile:
        # 当前迭代次数
        iter_count = 0

        # 是否收敛
        converged = False

        # 开始博弈循环
        while iter_count < self.max_iter and converged == False:
            iter_count += 1
            migrated = False  # 是否有协作改进（如果没有博弈改进动作，则达到了纳什均衡）

            # 遍历所有函数
            for func_id, _val in self.sp.strategy.items():
                # 跳过在本地IoT执行的函数
                strategy = self.sp.get_func_strategy(func_id)
                if strategy == 1:
                    continue

                func = self.ss.get_function_instance(func_id)
                iot = self.ss.f2u_mapping(func.id)
                curr_sec = self.sp.get_func_current_sec(func_id=func.id)
                curr_cr_ik = self.sp.get_cr_ik(func=func, sec=curr_sec, alloc_method=self.alloc_method)

                # === （1）计算函数任务当前策略的效用 ===
                # 1. 计算 T^s2s
                curr_T_s2s = 0.0
                loc_sec = self.ss.f2s_mapping(func.id)
                if curr_sec.id != loc_sec.id:
                    lat, bw = self.ss.sec_network.get_latency_and_bandwidth(loc_sec.id, curr_sec.id)
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
                for hyp_sec in self.ss.get_sec_list():
                    if hyp_sec.id == curr_sec.id:
                        continue

                    # 模拟卸载到目标sec，计算假想分配得到的资源
                    self.sp.schedule_to_target_sec(func_id=func.id, target_sec_id=hyp_sec.id)
                    hyp_cr_ik = self.sp.get_cr_ik(func=func, sec=hyp_sec, alloc_method=self.alloc_method)
                    self.sp.schedule_to_target_sec(func_id=func.id, target_sec_id=curr_sec.id)

                    # 1. 计算假想T^s2s
                    hyp_T_s2s = 0.0
                    loc_sec = self.ss.f2s_mapping(func.id)
                    if hyp_sec.id != loc_sec.id:
                        lat, bw = self.ss.sec_network.get_latency_and_bandwidth(loc_sec.id, hyp_sec.id)
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
                    hyp_T_d2s = (func.invocations * func.data_size) / (iot.uplink_rate / 8)

                    # 计算当前效用
                    u_hyp = -(hyp_T_d2s + hyp_T_s2s + hyp_T_cold + hyp_T_exe)

                    # === （3）判断效用改进 ===
                    if u_hyp > u_best:
                        u_best = u_hyp
                        best_sec = hyp_sec

                # 判断是否需要改变策略
                if best_sec.id != curr_sec.id:
                    # 更新决策剖面
                    self.sp.schedule_to_target_sec(func_id=func.id, target_sec_id=best_sec.id)
                    migrated = True
                    # print(f'* 博弈动作：函数{func.id} SEC{curr_sec.id}->SEC{best_sec.id}')

            # 取得纳什均衡，结束博弈
            if not migrated:
                converged = True

        return self.sp

    def get_cost(self):
        return self.sp.get_cost(alloc_method=self.alloc_method)
