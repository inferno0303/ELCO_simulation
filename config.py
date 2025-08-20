# 数据集相关的参数
DATASET_SIZES = {
    "tiny": {
        "seed": 42,
        "bs_and_sec": 4,
        "iot_device": 10,
        "function_type": 6,
        "function_task": 50
    },
    "smaller": {
        "seed": 42,
        "bs_and_sec": 6,
        "iot_device": 15,
        "function_type": 8,
        "function_task": 100
    },
    "small": {
        "seed": 42,
        "bs_and_sec": 8,
        "iot_device": 15,
        "function_type": 10,
        "function_task": 150
    },
    "medium": {
        "seed": 43,
        "bs_and_sec": 10,
        "iot_device": 20,
        "function_type": 12,
        "function_task": 200
    },
    "large": {
        "seed": 44,
        "bs_and_sec": 12,
        "iot_device": 25,
        "function_type": 14,
        "function_task": 250
    },
    "larger": {
        "seed": 44,
        "bs_and_sec": 14,
        "iot_device": 30,
        "function_type": 15,
        "function_task": 300
    }
}

SEC = {
    'SEC_CPU': [2500 * 4, 2500 * 8, 2800 * 12, 3200 * 16],
    'SEC_MEM': [8 * 1024, 16 * 1024, 24 * 1024, 32 * 1024, 64 * 1024],
    'SEC_BH_BW': [100, 120, 140, 160, 180, 200]
}

# SEC 异构实验
# SEC = {
#     'SEC_CPU': [2500 * 1, 3200 * 32],
#     'SEC_MEM': [2 * 1024, 128 * 1024],
#     'SEC_BH_BW': [100, 120, 140, 160, 180, 200]
# }

FUNC = {
    'DATA_SIZE': [0.2, 0.4, 0.6, 0.8, 1.0],
    'WORKLOAD': [20, 200, 1500, 3000],
    'INVOCATION': [2, 5, 10, 15]
}

IOT_EXE_EFFICIENT = 1e-8  # IoT设备计算能耗系数 \eta
IOT_TX_EFFICIENT = 0.25  # IoT 发射时的能量效率
SEC_CONT_INIT_EFFI = 2.5  # SEC初始化容器效率 \xi，单位：MHz/MB
RATIO = 1.5  # cr与m的比例，计算资源MHz=内存MB*r
T_ref = 5  # 延迟归一化参考值(s)
E_ref = 5  # 能耗归一化参考值(J=W*s)
OMEGA = 0.5  # 延迟的权重
