from __future__ import annotations
from typing import Union, Dict, List, Any
from asyncio import gather
from .protocol import BaseProtocol, support_protocol
from .exception import NameNotFoundError, UnsupportedProtocolError


class ServiceStatus:
    def __init__(self) -> None:
        self.bind_services: List[BaseProtocol] = []

    def get_service_instance_by_name(self, name: str) -> BaseProtocol:
        for i in self.bind_services:
            if name == i.name:
                return i
        raise NameNotFoundError

    def bind_service(self, service: BaseProtocol):
        self.bind_services.append(service)

    def unbind_service(self, unbind_service: BaseProtocol) -> bool:
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
            if key not in support_protocol():
                raise UnsupportedProtocolError(f"Unsopported protocol: {key} !")
            for this_service_config in value:
                this_service_instance = BaseProtocol._support_protocol[key].load(
                    this_service_config
                )
                instance.bind_services.append(this_service_instance)
        return instance

    def export(self) -> Dict[str, List[Dict]]:
        ret_dict = {}
        for i in support_protocol():
            ret_dict[i] = []
            for j in self.bind_services:
                ret_dict[i].append(j.export())
        return ret_dict


class ServiceStatusGroup:
    def __init__(self) -> None:
        self.bind_services_group: Dict[str, ServiceStatus] = {}

    def bind_group(
        self,
        services: List[BaseProtocol],
        name: str,
    ):
        self.bind_services_group[name] = ServiceStatus()
        for this_service in services:
            self.bind_services_group[name].bind_service(this_service)
            # service_status_instance.unbind_service(this_service) # 由NonebotPluginServiceStateManager实现

    def unbind_group_by_name(self, unbind_service_group_name: str) -> bool:
        if unbind_service_group_name not in self.bind_services_group:
            return False
        del self.bind_services_group[unbind_service_group_name]
        return True

    async def get_detect_result(self) -> Dict[str, bool]:
        ret_result = {}
        for name, this_service_group in self.bind_services_group.items():
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
            instance.bind_services_group[name] = ServiceStatus.load(
                service_status_config
            )
        return instance

    def export(self) -> Dict[str, Dict[str, List]]:
        ret_dict = {}
        for name, service_status_instance in self.bind_services_group.items():
            ret_dict[name] = service_status_instance.export()
        return ret_dict
