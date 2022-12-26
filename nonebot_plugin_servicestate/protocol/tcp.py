from __future__ import annotations

from typing import Union, Dict, List

from .protocol import BaseProtocol

from nonebot.log import logger
import asyncio


class TCP_Protocol(BaseProtocol):
    _PROTOCOL_NAME = "TCP"
    _EXTEND_PARAMS = {"port": "端口"}

    def __init__(self, name: str, host: str) -> None:
        super().__init__(name=name, host=host)
        self.port: int = 80

    async def detect(self) -> bool:
        try:
            await asyncio.open_connection(self.host, self.port)
            logger.debug(f"TCP -> {self.host}:{self.port} OK")
            return True
        except:
            logger.debug(f"TCP -> {self.host}:{self.port} FAIL")
            return False

    @classmethod
    def load(cls, source: Dict) -> TCP_Protocol:
        instance = cls(source["name"], source["host"])
        instance.timeout = source.get("timeout", 5)
        instance.port = source.get("port", 80)
        if not isinstance(instance.port, int):
            instance.port = int(instance.port)
        return instance
