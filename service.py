from __future__ import annotations
from typing import Union, Dict, List, Any
from asyncio import gather, run
from abc import ABC, abstractmethod, abstractclassmethod
from network import detect_http


class BaseDetectService(ABC):
    _support_protocol: dict = {}
    _PROTOCOL_NAME = None

    def __init__(self, name: str, host: str, protocol_name: str, timeout=3) -> None:
        self.name: str = name
        self.host: str = host
        self.timeout: int = timeout
        self.protocol_name: str = protocol_name
        BaseDetectService._support_protocol[self.protocol_name] = self

    def __init_subclass__(cls) -> None:
        for this_subclass in BaseDetectService.__subclasses__():
            if this_subclass._PROTOCOL_NAME is None:
                raise NotImplementedError(
                    'Protocol should have "_PROTOCOL_NAME" property'
                )
            if this_subclass._PROTOCOL_NAME in BaseDetectService._support_protocol:
                continue
            BaseDetectService._support_protocol[
                this_subclass._PROTOCOL_NAME
            ] = this_subclass
        return super().__init_subclass__()

    @abstractmethod
    async def detect(self):
        pass

    @abstractmethod
    def export(self):
        pass

    @abstractclassmethod
    def load(cls):
        pass


class DetectServices:
    @classmethod
    @property
    def support_protocol(cls) -> List:
        return list(BaseDetectService._support_protocol.keys())

    class http(BaseDetectService):
        _PROTOCOL_NAME = "HTTP"

        def __init__(self, name: str, host: str) -> None:
            super().__init__(name=name, host=host, protocol_name=self._PROTOCOL_NAME)
            self.proxies: Union[str, None] = None

        async def detect(self) -> bool:
            return await detect_http(
                host=self.host, proxies=self.proxies, timeout=self.timeout
            )

        def export(self) -> Dict[str, Union[str, int, None]]:
            result_dict = {}
            result_dict["name"] = self.name
            result_dict["host"] = self.host
            result_dict["timeout"] = self.timeout
            result_dict["proxies"] = self.proxies
            return result_dict

        @classmethod
        def load(cls, source: Dict) -> DetectServices.http:
            instance = cls(source["name"], source["host"])
            instance.timeout = source["timeout"]
            instance.proxies = source.get("proxies", None)
            return instance


class ServiceStatus:
    def __init__(self) -> None:
        self.bind_services: List[BaseDetectService] = []

    async def get_detect_result(self) -> Dict[str, bool]:
        tasks = [service.detect() for service in self.bind_services]
        result = await gather(*tasks)
        ret_dict = {}
        for i, j in zip(self.bind_services, result):
            ret_dict[i.name] = j
        return ret_dict

    @classmethod
    def load(cls, source: Dict[str, List]) -> ServiceStatus:
        instance = cls()
        for key, value in source.items():
            if key not in DetectServices.support_protocol:
                raise ValueError(f"Unsopported protocol: {key} !")
            for this_service_config in value:
                this_service_instance = BaseDetectService._support_protocol[key].load(
                    this_service_config
                )
                instance.bind_services.append(this_service_instance)
        return instance


config = {
    "HTTP": [
        {"name": "百度搜索", "host": "http://www.baidu.com", "timeout": 3},
        {"name": "网关", "host": "http://192.168.3.1", "timeout": 3},
        {"name": "ConnectError测试1", "host": "http://192.168.110.1", "timeout": 1},
        {"name": "ConnectError测试2", "host": "http://192.168.110.2", "timeout": 1},
        {"name": "会战面板", "host": "https://524266386o.eicp.vip/yobot/", "timeout": 1},
        {"name": "会战面板2", "host": "https://524266386o.eicp.vip", "timeout": 1},
    ]
}


demo = ServiceStatus.load(config)
run(demo.get_detect_result())
