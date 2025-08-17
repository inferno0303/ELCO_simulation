import logging
import sys
from datetime import datetime
import os
from pathlib import Path

# 从配置文件中导入宏变量
try:
    from config import ENABLE_FILE_LOGGING, ENABLE_CONSOLE_LOGGING
except ImportError:
    # 如果找不到配置文件，则默认启用所有日志
    ENABLE_FILE_LOGGING = True
    ENABLE_CONSOLE_LOGGING = True
    print("Warning: config.py not found. Defaulting to all logging enabled.")


def setup_logger(name, log_file_name='debug.log'):
    """
    配置并返回一个日志器。

    Args:
        name (str): 日志器的名称，通常是 __name__。
        log_file_name (str): 日志文件的名称。

    Returns:
        logging.Logger: 配置好的日志器对象。
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # 设置日志器的最低日志级别
    logger.propagate = False  # 防止日志重复输出

    # 创建一个通用的格式器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 如果启用了文件日志
    if ENABLE_FILE_LOGGING:
        # 确保日志目录存在'
        log_dir = Path(__file__).resolve().parent.parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        # 创建一个文件处理器，用于写入文件
        file_handler = logging.FileHandler(os.path.join(log_dir, log_file_name))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # 如果启用了控制台日志
    if ENABLE_CONSOLE_LOGGING:
        # 创建一个流处理器，用于打印到控制台
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# 全局日志器实例，方便在其他模块中导入和使用
logging = setup_logger('main')
