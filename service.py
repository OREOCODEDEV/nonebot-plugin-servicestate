from __future__ import annotations
from typing import Union, Dict, List, Any
from asyncio import gather
from abc import ABC, abstractmethod, abstractclassmethod
from network import detect_http


class BaseDetectService(ABC):
    _support_protocol: dict = {}
    _PROTOCOL_NAME = None

    def __init__(self, name: str, host: str, protocol_name: str, timeout=3) -> None:
        self.name: str = name
        self.host: str = host
        self.timeout: int = timeout

    def __init_subclass__(cls) -> None:
        for this_subclass in BaseDetectService.__subclasses__():
            if this_subclass._PROTOCOL_NAME is None:
                raise NotImplementedError('Protocol should have "_PROTOCOL_NAME"')
            if this_subclass._PROTOCOL_NAME in BaseDetectService._support_protocol:
                continue
            BaseDetectService._support_protocol[
                this_subclass._PROTOCOL_NAME
            ] = this_subclass
        return super().__init_subclass__()

    def __eq__(self, __o: BaseDetectService) -> bool:
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

    def get_service_instance_by_name(self, name: str) -> BaseDetectService:
        for i in self.bind_services:
            if name == i.name:
                return i
        raise ValueError("Unable find service instance!")

    def bind_service(self, service: BaseDetectService):
        self.bind_services.append(service)

    def unbind_service(self, unbind_service: BaseDetectService) -> bool:
        for this_service in self.bind_services:
            if this_service == unbind_service:
                self.bind_services.pop(self.bind_services.index(this_service))
                return True
        return False

    def unbind_service_by_name(self, unbind_service_name: str) -> bool:
        service_instance = self.get_service_instance_by_name(unbind_service_name)
        if service_instance is not None:
            return self.unbind_service(service_instance)
        return False

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


class ServiceStatusGroup:
    def __init__(self) -> None:
        self.bind_services_group: Dict[str, ServiceStatus] = {}

    def bind_group(
        self,
        service_status_instance: ServiceStatus,
        services: List[BaseDetectService],
        name: str,
    ):
        self.bind_services_group[name] = ServiceStatus()
        for this_service in services:
            self.bind_services_group[name].bind_service(this_service)
            service_status_instance.unbind_service(this_service)

    def bind_group_by_name(
        self,
        service_status_instance: ServiceStatus,
        services_name: List[str],
        name: str,
    ):
        service_instance_list: List[BaseDetectService] = []
        for i in services_name:
            service_instance_list.append(
                service_status_instance.get_service_instance_by_name(i)
            )
        self.bind_group(service_status_instance, service_instance_list, name)

    async def get_detect_result(self) -> Dict[str, bool]:
        ret_result = {}
        for name, this_service_group in self.bind_services_group.items():
            ret_result[name] = True
            for i in (await this_service_group.get_detect_result()).values():
                if not i:
                    ret_result[name] = False
                    break
        return ret_result
