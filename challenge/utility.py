import logging
import socket
from typing import Optional


logger = logging.getLogger(__name__)


def get_free_port(start_port: int, end_port: int, host: str = "localhost") -> Optional[int]:
    for port in range(start_port, end_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex((host, port))
            if result == 111:
                logger.info("Port %s is available", port)
                return port
    return None
