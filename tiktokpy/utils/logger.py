import logging
import sys

from loguru import logger


def init_logger(log_level: int = logging.INFO):
    logging.disable(logging.CRITICAL)
    logger.remove()
    logger.add(
        sink=sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level}</level> | "
        "<level>{message}</level>",
    )
