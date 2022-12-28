from __future__ import annotations

from typing import Union, Dict, List, Any, Tuple
from asyncio import gather

from .protocol import BaseProtocol, support_protocol
from .exception import ProtocolUnsopportError


class ServiceStatus:
    def __init__(self) -> None:
        self.__bind_services: List[BaseProtocol] = []

    def __contains__(self, item) -> bool:
        if isinstance(item, str):
            for i in self:
                if i == item:
                    return True
        if isinstance(item, BaseProtocol):
            return item in self.__bind_services
        return False

    def __iter__(self) -> ServiceStatus:
        self.__iterator = self.__bind_services.__iter__()
        return self

    def __next__(self) -> BaseProtocol:
        return self.__iterator.__next__()

    def __getitem__(self, key: Union[str, BaseProtocol]) -> BaseProtocol:
        for i in self:
            if i == key:
                return i
        raise KeyError(key)

    def __setitem__(self, key: Union[str, BaseProtocol], value: BaseProtocol) -> None:
        for i, j in enumerate(self.__bind_services):
            if key == j:
                self.__bind_services[i] = value
                return
        raise KeyError(key)

    def register_service(self, protocol: str, *args, **kw):
        if protocol not in support_protocol():
            raise ProtocolUnsopportError
        self.bind_service(BaseProtocol._support_protocol[protocol](*args, **kw))

    def bind_service(self, service: BaseProtocol) -> None:
        self.__bind_services.append(service)

    def unbind_service(self, unbind_service: Union[BaseProtocol, str]) -> None:
        if isinstance(unbind_service, str):
            unbind_service = self[unbind_service]
        if unbind_service not in self:
            raise KeyError
        self.__bind_services.pop(self.__bind_services.index(unbind_service))

    async def get_detect_result(self) -> Dict[str, bool]:
        tasks = [service.detect() for service in self]
        result = await gather(*tasks)
        ret_dict = {}
        for i, j in zip(self, result):
            ret_dict[i.name] = j
        return ret_dict

    @classmethod
    def load(cls, source: Dict[str, List]) -> ServiceStatus:
        instance = cls()
        for key, value in source.items():
            if key not in support_protocol():
                raise ProtocolUnsopportError(f"Unsopported protocol: {key} !")
            for this_service_config in value:
                this_service_instance = BaseProtocol._support_protocol[key].load(
                    this_service_config
                )
                instance.bind_service(this_service_instance)
        return instance

    def export(self) -> Dict[str, List[Dict]]:
        ret_dict = {}
        for i in support_protocol():
            ret_dict[i] = []
            for j in self:
                if j._PROTOCOL_NAME != i:
                    continue
                ret_dict[i].append(j.export())
        return ret_dict


class ServiceStatusGroup:
    def __init__(self) -> None:
        self.__bind_services_group: Dict[str, ServiceStatus] = {}

    def __contains__(self, item) -> bool:
        if isinstance(item, str):
            return item in self.__bind_services_group.keys()
        if isinstance(item, ServiceStatus):
            return item in self.__bind_services_group.values()
        return False

    def __iter__(self) -> ServiceStatusGroup:
        self.__iterator = self.__bind_services_group.values().__iter__()
        return self

    def __next__(self) -> ServiceStatus:
        return self.__iterator.__next__()

    def __getitem__(self, key: Union[str, ServiceStatus]) -> ServiceStatus:
        if isinstance(key, str):
            return self.__bind_services_group[key]
        for i in self:
            if i == key:
                return i
        raise KeyError(key)

    def __setitem__(self, key: Union[str, ServiceStatus], value: ServiceStatus) -> None:
        if isinstance(key, str):
            key = self[key]
        for i, j in self.items():
            if key == j:
                self.__bind_services_group[i] = value
                return
        raise KeyError(key)

    def items(self):
        return self.__bind_services_group.items()

    def bind_group(
        self,
        services: List[BaseProtocol],
        name: str,
    ) -> None:
        self.__bind_services_group[name] = ServiceStatus()
        for this_service in services:
            self.__bind_services_group[name].bind_service(this_service)

    def unbind_group(self, key: str) -> None:
        if key not in self:
            raise KeyError
        del self.__bind_services_group[key]

    async def get_detect_result(self) -> Dict[str, bool]:
        ret_result = {}
        for name, this_service_group in self.items():
            ret_result[name] = True
            for i in (await this_service_group.get_detect_result()).values():
                if not i:
                    ret_result[name] = False
                    break
        return ret_result

    @classmethod
    def load(cls, source: Dict[str, Dict[str, List]]) -> ServiceStatusGroup:
        instance = cls()
        for name, service_status_config in source.items():
            instance.__bind_services_group[name] = ServiceStatus.load(
                service_status_config
            )
        return instance

    def export(self) -> Dict[str, Dict[str, List]]:
        ret_dict = {}
        for name, service_status_instance in self.__bind_services_group.items():
            ret_dict[name] = service_status_instance.export()
        return ret_dict
