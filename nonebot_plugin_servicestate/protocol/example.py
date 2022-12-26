from __future__ import annotations

from typing import Union, Dict, List
import random

from .protocol import BaseProtocol


class HTTP_Protocol(BaseProtocol):
    _PROTOCOL_NAME = "EXAMPLE"
    _EXTEND_PARAMS = {"rate": "正常机率"}

    def __init__(self, name: str, host: str) -> None:
        super().__init__(name=name, host=host)
        self.rate: int = 50

    async def detect(self) -> bool:
        return random.random() > self.rate / 100

    @classmethod
    def load(cls, source: Dict) -> HTTP_Protocol:
        instance = cls(source["name"], source["host"])
        instance.timeout = source.get("timeout", 5)
        instance.rate = source.get("rate", 50)
        return instance
