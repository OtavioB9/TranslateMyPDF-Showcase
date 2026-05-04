import logging
import sys
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Configura e retorna um logger padronizado para o sistema LayrPDF.
    Garante que os logs tenham um formato profissional e sejam direcionados para o stdout.
    """
    logger = logging.getLogger(name or "LayrPDF")

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
