LOG_LEVEL = 'no'

IOT_EXE_EFFICIENT = 5e-9  # IoT设备计算能耗系数
IOT_TX_EFFICIENT = 0.2  # IoT 发射时的能量效率
SEC_CONT_INIT_EFFI = 2.5  # SEC初始化容器效率 \eta，单位：MHz/MB

RATIO = 1.5  # cr与m的比例，计算资源MHz=内存MB*r

T_ref = 5  # 延迟归一化参考值(s)
E_ref = 5  # 能耗归一化参考值(J=W*s)

OMEGA = 0.5  # 延迟的权重
