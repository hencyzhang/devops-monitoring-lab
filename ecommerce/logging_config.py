import logging, os
from logging.handlers import TimedRotatingFileHandler

os.makedirs('logs', exist_ok=True)

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh = TimedRotatingFileHandler(f'logs/{name}.log', when='midnight', interval=1, backupCount=7)
    fh.setFormatter(fmt)
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
