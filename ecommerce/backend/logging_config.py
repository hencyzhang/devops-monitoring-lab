"""
统一日志配置 - 按模块分文件
- startup.log  : 服务启动/连接
- api.log      : HTTP 请求
- order.log    : 订单业务
- notify.log   : 通知消费
- error.log    : 所有 ERROR/CRITICAL 单独一份
- 标准级别: DEBUG/INFO/WARNING/ERROR/CRITICAL
- 控制台彩色, 文件纯文本
- 每天切分, 50MB 分片, 保留 7 天
"""
import logging, os
from logging.handlers import TimedRotatingFileHandler

# ============ 可配置项 ============
LOG_DIR = '/app/logs'
MAX_BYTES = 50 * 1024 * 1024
BACKUP_DAYS = 7
# ==================================

os.makedirs(LOG_DIR, exist_ok=True)

class Colors:
    RESET     = '\033[0m'
    DEBUG     = '\033[37m'
    INFO      = '\033[32m'
    WARNING   = '\033[33m'
    ERROR     = '\033[31m'
    CRITICAL  = '\033[1;41m'

LEVEL_COLORS = {
    logging.DEBUG:     Colors.DEBUG,
    logging.INFO:      Colors.INFO,
    logging.WARNING:   Colors.WARNING,
    logging.ERROR:     Colors.ERROR,
    logging.CRITICAL:  Colors.CRITICAL,
}

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        color = LEVEL_COLORS.get(record.levelno, Colors.RESET)
        record.levelname = f"{color}{record.levelname:<8}{Colors.RESET}"
        return super().format(record)

class SizeAndTimeRotatingHandler(TimedRotatingFileHandler):
    def __init__(self, filename):
        super().__init__(
            filename, when='midnight', interval=1,
            backupCount=BACKUP_DAYS, encoding='utf-8'
        )
        self.max_bytes = MAX_BYTES

    def shouldRollover(self, record):
        if super().shouldRollover(record):
            return True
        if self.stream.tell() >= self.max_bytes:
            return True
        return False

FMT = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
DATEFMT = '%Y-%m-%d %H:%M:%S'

def _build_handlers(filename):
    """为每个模块创建: 文件handler + 控制台handler + error单独文件handler"""
    fmt = logging.Formatter(FMT, datefmt=DATEFMT)

    file_handler = SizeAndTimeRotatingHandler(f'{LOG_DIR}/{filename}.log')
    file_handler.setFormatter(fmt)

    console = logging.StreamHandler()
    console.setFormatter(ColoredFormatter(FMT, datefmt=DATEFMT))

    # ERROR 级别以上单独写一份 error.log
    error_handler = SizeAndTimeRotatingHandler(f'{LOG_DIR}/error.log')
    error_handler.setFormatter(fmt)
    error_handler.setLevel(logging.ERROR)

    return [file_handler, console, error_handler]

def setup_logger(module_name, level=logging.DEBUG):
    """
    按模块创建 logger, 每个模块写自己的日志文件
    用法:
        startup_log = setup_logger('startup')
        api_log     = setup_logger('api')
        order_log   = setup_logger('order')
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(level)
    logger.handlers = []
    logger.propagate = False

    for h in _build_handlers(module_name):
        logger.addHandler(h)

    return logger
