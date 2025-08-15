from core.system_state import SystemState
from utils.dataset_loader import load_dataset
from utils.result_record import write_csv

from core.algorithm.algo_01_LEAO import LEAO
from core.algorithm.algo_02_PGES import PGES
from core.algorithm.algo_03_IoTOnly import IoTOnly
from core.algorithm.algo_04_SECOnlyLocal import SECOnlyLocal
from core.algorithm.algo_05_OptimalOffload import OptimalOffload
from core.algorithm.algo_06_RandomOffload import RandomOffload
from core.algorithm.algo_07_SECOnlyRRLB import SECOnlyRRLB
from core.algorithm.algo_08_RandomSchedule import RandomSchedule
from core.algorithm.algo_09_LEAORRLB import LEAORRLB
from core.algorithm.algo_10_GASchedule import GASchedule


def main():
    scale = 'large'
    ss: SystemState = load_dataset(scale, datasets_root='datasets')

    # 记录实验结果
    header = ['dataset scale', 'algorithm name', 'offload method', 'schedule method', 'res alloc method',
              'offload ratio', 'system cost']
    rows = []

    algo_inst = LEAO(ss=ss, alloc_method='FIXED-512')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'LEAO', 'LEAO', '', 'FIXED-512', offload_ratio, cost])

    algo_inst = LEAO(ss=ss, alloc_method='FAIR')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'LEAO', 'LEAO', '', 'FAIR', offload_ratio, cost])

    algo_inst = LEAO(ss=ss, alloc_method='LP')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'LEAO', 'LEAO', '', 'LP', offload_ratio, cost])

    algo_inst = LEAO(ss=ss, alloc_method='WF')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    leao_sp = algo_inst.sp
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'LEAO', 'LEAO', '', 'WF', offload_ratio, cost])

    algo_inst = PGES(ss=ss, sp=leao_sp, alloc_method='WF')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'LEAO+PGES', 'LEAO', 'PGES', 'WF', offload_ratio, cost])

    print("=================== 其他卸载算法 ===================")

    algo_inst = IoTOnly(ss=ss)
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'IoTOnly', '', '', '', offload_ratio, cost])

    algo_inst = SECOnlyLocal(ss=ss, alloc_method='FAIR')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'SECOnlyLocal', 'SECOnlyLocal', '', 'FAIR', offload_ratio, cost])

    algo_inst = SECOnlyLocal(ss=ss, alloc_method='LP')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'SECOnlyLocal', 'SECOnlyLocal', '', 'LP', offload_ratio, cost])

    algo_inst = SECOnlyLocal(ss=ss, alloc_method='WF')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'SECOnlyLocal', 'SECOnlyLocal', '', 'WF', offload_ratio, cost])

    algo_inst = OptimalOffload(ss=ss, alloc_method='FAIR')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'OptimalOffload', 'Optimal', '', 'FAIR', offload_ratio, cost])

    algo_inst = OptimalOffload(ss=ss, alloc_method='LP')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'OptimalOffload', 'Optimal', '', 'LP', offload_ratio, cost])

    algo_inst = OptimalOffload(ss=ss, alloc_method='WF')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'OptimalOffload', 'Optimal', '', 'WF', offload_ratio, cost])

    algo_inst = RandomOffload(ss=ss, alloc_method='FAIR')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'RandomOffload', 'Random', '', 'FAIR', offload_ratio, cost])

    algo_inst = RandomOffload(ss=ss, alloc_method='LP')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'RandomOffload', 'Random', '', 'LP', offload_ratio, cost])

    algo_inst = RandomOffload(ss=ss, alloc_method='WF')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'RandomOffload', 'Random', '', 'WF', offload_ratio, cost])

    print("=================== 其他调度算法 ===================")

    algo_inst = SECOnlyRRLB(ss=ss, alloc_method='WF')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'SECOnlyRRLB', 'SECOnly', 'RRLB', 'WF', offload_ratio, cost])

    algo_inst = RandomSchedule(ss=ss, alloc_method='WF')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'RandomSchedule', 'Random', 'Random', 'WF', offload_ratio, cost])

    algo_inst = GASchedule(ss=ss, alloc_method='WF')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'GASchedule', 'GA', 'GA', 'WF', offload_ratio, cost])

    print("=================== 消融实验 ===================")

    algo_inst = LEAORRLB(ss=ss, alloc_method='WF')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：{algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'LEAORRLB', 'LEAO', 'RRLB', 'WF', offload_ratio, cost])

    algo_inst = PGES(ss=ss, sp=SECOnlyLocal(ss=ss, alloc_method='WF').run(), alloc_method='WF')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：SECOnlyLocal + {algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'SECOnlyLocal+PGES', 'SECOnlyLocal', 'PGES', 'WF', offload_ratio, cost])

    algo_inst = PGES(ss=ss, sp=RandomOffload(ss=ss, alloc_method='WF').run(), alloc_method='WF')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：RandomOffload + {algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'RandomOffload+PGES', 'Random', 'PGES', 'WF', offload_ratio, cost])

    algo_inst = PGES(ss=ss, sp=OptimalOffload(ss=ss, alloc_method='WF').run(), alloc_method='WF')
    algo_inst.run()
    cost = algo_inst.get_cost()
    offload_ratio = algo_inst.sp.get_offload_ratio()
    print(f'* 结果：OptimalOffload + {algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')
    rows.append([scale, 'OptimalOffload+PGES', 'Optimal', 'PGES', 'WF', offload_ratio, cost])

    print("=================== 理论线性最优上界 ===================")

    # algo_inst = TheoreticalOptimal(ss=ss, sp=OptimalOffload(ss=ss, alloc_method='WF').run(), alloc_method='WF')
    # algo_inst.run()
    # cost = algo_inst.get_cost()
    # offload_ratio = algo_inst.sp.get_offload_ratio()
    # print(f'* 结果：OptimalOffload + {algo_inst}, cost: {cost:.2f}, offload ratio {offload_ratio * 100:.2f}%')

    print("=================== 记录实验数据 ===================")
    write_csv(file_name=f'result_{scale}.csv', header=header, rows=rows)


if __name__ == '__main__':
    main()
