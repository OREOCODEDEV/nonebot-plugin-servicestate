from __future__ import annotations

from typing import Union, Dict, List

from .protocol import BaseProtocol, BaseProtocolData

from nonebot.log import logger
import asyncio


class TCPPRotocolData(BaseProtocolData):
    port: int = 80


class TCP_Protocol(BaseProtocol):
    _PROTOCOL_NAME = "TCP"
    _DATA_MODEL = TCPPRotocolData

    async def detect(self) -> bool:
        connect_func = asyncio.open_connection(self.data.host, self.data.port)
        try:
            await asyncio.wait_for(connect_func, self.data.timeout)
            logger.debug(f"TCP -> {self.data.host}:{self.data.port} OK")
            return True
        except:
            logger.debug(f"TCP -> {self.data.host}:{self.data.port} FAIL")
            return False
