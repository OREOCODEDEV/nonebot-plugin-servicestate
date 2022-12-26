from __future__ import annotations
from httpx import AsyncClient
from typing import Union, Dict, List
from .protocol import BaseProtocol

from nonebot.log import logger


class HTTP_Protocol(BaseProtocol):
    _PROTOCOL_NAME = "HTTP"
    _EXTEND_PARAMS = {"proxies": "代理"}

    def __init__(self, name: str, host: str) -> None:
        super().__init__(name=name, host=host)
        self.proxies: Union[str, None] = None

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

    @classmethod
    def load(cls, source: Dict) -> HTTP_Protocol:
        instance = cls(source["name"], source["host"])
        instance.timeout = source.get("timeout", 5)
        instance.proxies = source.get("proxies", None)
        if not isinstance(instance.timeout, int):
            instance.timeout = int(instance.timeout)
        return instance
