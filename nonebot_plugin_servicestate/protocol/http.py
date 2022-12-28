from __future__ import annotations

from httpx import AsyncClient
from typing import Union, Dict, List, Any

from .protocol import BaseProtocol, BaseProtocolData

from nonebot.log import logger


class HTTPProtocolData(BaseProtocolData):
    proxies: Union[str, None] = None


class HTTPProtocol(BaseProtocol):
    _PROTOCOL_NAME = "HTTP"
    _DATA_MODEL = HTTPProtocolData

    async def detect(self) -> bool:
        async with AsyncClient(
            proxies=self.proxies,
            verify=False,
            follow_redirects=True,
            timeout=self.timeout,
        ) as client:
            try:
                respond = await client.get(url=self.host)
            except:
                logger.debug(f"GET -> {self.host} FAIL")
                return False
            if not respond:
                logger.debug(f"GET -> {self.host} FAIL")
                return False
            if respond.status_code != 200:
                logger.debug(f"GET -> {self.host} FAIL")
                return False
            logger.debug(f"GET -> {self.host} OK")
            return True
