from __future__ import annotations
from abc import ABC, abstractmethod, abstractclassmethod
from typing import Union, Dict, List, Type, Any
from pydantic import BaseModel


class BaseProtocolData(BaseModel):
    name: str = "Unknown"
    host: str = "127.0.0.1"
    timeout: int = 2


class BaseProtocol(ABC):
    _support_protocol: dict = {}
    _PROTOCOL_NAME = None
    _DATA_MODEL = BaseProtocolData

    def __init__(self, *args, **kw) -> None:
        self.__data = self._DATA_MODEL(*args, **kw)

    def __init_subclass__(cls) -> None:
        for this_subclass in BaseProtocol.__subclasses__():
            if this_subclass._PROTOCOL_NAME is None:
                raise NotImplementedError('Protocol should have "_PROTOCOL_NAME"')
            if this_subclass._PROTOCOL_NAME in BaseProtocol._support_protocol:
                continue
            BaseProtocol._support_protocol[this_subclass._PROTOCOL_NAME] = this_subclass
        return super().__init_subclass__()

    def __eq__(self, __o: Union[str, BaseProtocol]) -> bool:
        if isinstance(__o, str):
            return True if __o == self.name else False
        if not isinstance(__o, BaseProtocol):
            return False
        if self.name != __o.name:
            return False
        if self.host != __o.host:
            return False
        if self._PROTOCOL_NAME != __o._PROTOCOL_NAME:
            return False
        return True

    def __getattr__(self, __name: str) -> Any:
        return self.__data.dict()[__name]

    @abstractmethod
    async def detect(self) -> bool:
        return False

    def export(self) -> Dict:
        return self.__data.dict()

    @classmethod
    def load(cls, source: Dict[str, Union[str, int, None]]):
        return cls(**source)


def support_protocol() -> List[str]:
    return list(BaseProtocol._support_protocol.keys())
