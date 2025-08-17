from datetime import datetime

from config import DATASET_SIZES
from core.system_state import SystemState
from simulation import Simulation
from utils.dataset_loader import load_dataset
from utils.result_record import write_csv, new_csv_file


def main():
    # 记录实验结果
    header = [
        'Base Station Count', 'SEC Server Count', 'IoT Device Count', 'Function Type Count', 'Function Task Count',
        'Latency Weight (OMEGA)', 'CPU MEM RATIO', 'Latency REF (s)', 'Energy REF (J)',
        'Algorithm Full Name', 'Offloading Algorithm', 'Scheduling Algorithm', 'Resource Allocation Algorithm',
        'System Cost', 'Real Latency (s)', 'Real Energy (J)', 'Offloading Ratio', 'Execution Time (s)'
    ]

    curr_time = datetime.now().strftime('%Y%m%d_%H%M')
    file_name = f'result_{curr_time}.csv'
    new_csv_file(file_name, header)

    for scale in DATASET_SIZES.keys():
        print('\n')
        print(f'============ 加载数据集 {scale} ============')
        ss: SystemState = load_dataset(scale=scale, datasets_root='datasets')

        # 运行实验
        simulation = Simulation(ss=ss)
        results_iterator = simulation.run()
        for rows in results_iterator:
            write_csv(file_name, rows)

        print(f'============ 完成数据集 {scale} ============')
        print('\n')


if __name__ == '__main__':
    main()
