from pathlib import Path

from .manager import manager
from .logger import logger


def config_file_compatible_v011_lower():
    """
    旧版本配置文件数据存放位置兼容处理
    v0.1.1或以下版本
    """
    service_count = manager.get_service_count()
    logger.debug(f"Service count: {service_count}")
    OLD_CONFIG_FILE_PATH = Path(__file__).parent.joinpath("config.txt")
    if service_count[0] != 0 or service_count[2] != 0:
        return
    logger.info("Checking compatible config...")
    if not OLD_CONFIG_FILE_PATH.is_file:
        logger.info("Unable to found compatible config file")
        return
    logger.info("Compatible config file found")
    logger.info("Loading exist config file...")
    manager.load(OLD_CONFIG_FILE_PATH)
    logger.info("Saving config file...")
    manager.save()
    logger.info("Config file upgrade complete: v0.1.1 ==> v0.2.0+")


config_file_compatible_v011_lower()
