from datetime import datetime

from config import DATASET_SIZES
from core.system_state import SystemState
from utils.dataset_loader import load_dataset
from utils.results_recorder import write_csv, new_csv_file
from experimental_procedure import header, experimental_01, experimental_02, experimental_03, experimental_04, \
    experimental_05


def main():
    curr_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f'result_{curr_time}.csv'
    new_csv_file(file_name, header)

    for scale in DATASET_SIZES.keys():
        print('\n')
        print(f'============ 加载数据集 {scale} ============')
        ss: SystemState = load_dataset(scale=scale, datasets_root='datasets')

        # 运行实验
        results = experimental_05(ss)
        write_csv(file_name, results)

        print(f'============ 完成数据集 {scale} ============')
        print('\n')


if __name__ == '__main__':
    main()
