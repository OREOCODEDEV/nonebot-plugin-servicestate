from __future__ import annotations
from abc import ABC, abstractmethod, abstractclassmethod
from network import detect_http
from typing import Union, Dict, List


class BaseProtocol(ABC):
    _support_protocol: dict = {}
    _PROTOCOL_NAME = None

    def __init__(self, name: str, host: str, protocol_name: str, timeout=3) -> None:
        self.name: str = name
        self.host: str = host
        self.timeout: int = timeout

    def __init_subclass__(cls) -> None:
        for this_subclass in BaseProtocol.__subclasses__():
            if this_subclass._PROTOCOL_NAME is None:
                raise NotImplementedError('Protocol should have "_PROTOCOL_NAME"')
            if this_subclass._PROTOCOL_NAME in BaseProtocol._support_protocol:
                continue
            BaseProtocol._support_protocol[this_subclass._PROTOCOL_NAME] = this_subclass
        return super().__init_subclass__()

    def __eq__(self, __o: BaseProtocol) -> bool:
        if self.name != __o.name:
            return False
        if self.host != __o.host:
            return False
        if self._PROTOCOL_NAME != __o._PROTOCOL_NAME:
            return False
        return True

    @abstractmethod
    async def detect(self):
        pass

    def export(self):
        export_dict = self.__dict__
        return_dict = {}
        for key, value in export_dict.items():
            if key.endswith("_") or key.startswith("_"):
                continue
            return_dict[key] = value
        return return_dict

    @abstractclassmethod
    def load(cls):
        pass


class Protocols:
    @classmethod
    @property
    def support_protocol(cls) -> List:
        return list(BaseProtocol._support_protocol.keys())

    """
    直接在下方拓展协议即可
    """

    class http(BaseProtocol):
        _PROTOCOL_NAME = "HTTP"

        def __init__(self, name: str, host: str) -> None:
            super().__init__(name=name, host=host, protocol_name=self._PROTOCOL_NAME)
            self.proxies: Union[str, None] = None

        async def detect(self) -> bool:
            return await detect_http(
                host=self.host, proxies=self.proxies, timeout=self.timeout
            )

        @classmethod
        def load(cls, source: Dict) -> Protocols.http:
            instance = cls(source["name"], source["host"])
            instance.timeout = source["timeout"]
            instance.proxies = source.get("proxies", None)
            return instance
