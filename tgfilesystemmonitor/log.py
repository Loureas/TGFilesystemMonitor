"""Initial setup of the logging system"""
import os
import sys
from loguru import logger
from config import config

if not os.path.exists(config.log_path):
    os.mkdir(config.log_path)

logger.remove()
logger.add(
    os.path.join(config.log_path, "tgfsm.log"),
    level=config.log_level,
    format="[{level: <1}] {time:YYYY-MM-DD HH:mm:ss.SSSSSSZZ} - {message}",
    backtrace=True,
    diagnose=True,
    catch=True,
    rotation="1 day",
    compression="gz",
    encoding="UTF-8",
)
logger.add(
    sys.stdout,
    filter=lambda record: record["level"].no < 30,
    level=config.log_level,
    format="[<bold><level>{level: <1}</level></bold>] {time:YYYY-MM-DD HH:mm:ss.SSSSSSZZ} - {message}",
    backtrace=True,
    diagnose=True,
    catch=True,
)
logger.add(
    sys.stderr,
    level="WARNING",
    format="<bold>[<level>{level: <1}</level>] {time:YYYY-MM-DD HH:mm:ss.SSSSSSZZ} - {message}</bold>",
    backtrace=True,
    diagnose=True,
    catch=True,
)
