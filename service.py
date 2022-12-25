from __future__ import annotations
from typing import Union, Dict, List, Any
from asyncio import gather
from protocol import BaseProtocol, Protocols


class ServiceStatus:
    def __init__(self) -> None:
        self.bind_services: List[BaseProtocol] = []

    def get_service_instance_by_name(self, name: str) -> BaseProtocol:
        for i in self.bind_services:
            if name == i.name:
                return i
        raise ValueError("Unable find service instance!")

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
            if key not in Protocols.support_protocol:
                raise ValueError(f"Unsopported protocol: {key} !")
            for this_service_config in value:
                this_service_instance = BaseProtocol._support_protocol[key].load(
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
        services: List[BaseProtocol],
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
        service_instance_list: List[BaseProtocol] = []
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
