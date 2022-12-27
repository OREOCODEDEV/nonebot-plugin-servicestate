from __future__ import annotations

from typing import Dict, List, Any, Tuple
from pathlib import Path
import json

from .service import ServiceStatus, ServiceStatusGroup, BaseProtocol, support_protocol
from .exception import (
    ProtocolUnsopportError,
    NameConflictError,
    NameNotFoundError,
    ParamInvalidError,
)


class CommandManager:
    __service_status: ServiceStatus = ServiceStatus()
    __service_status_group: ServiceStatusGroup = ServiceStatusGroup()

    def __init__(self) -> None:
        pass

    def load(self, path: Path):
        with open(path, "r", encoding="utf-8") as f:
            load_dict = json.loads(f.read())
        self.__service_status = ServiceStatus.load(load_dict["service"])
        self.__service_status_group = ServiceStatusGroup.load(
            load_dict["service_group"]
        )

    def save(self, path: Path):
        save_dict = {
            "service": self.__service_status.export(),
            "service_group": self.__service_status_group.export(),
        }
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(save_dict))

    def bind_new_service(self, protocol: str, name: str, host: str):
        if protocol not in support_protocol():
            raise ProtocolUnsopportError
        if name in self.__service_status:
            raise NameConflictError
        if name in self.__service_status_group:
            raise NameConflictError
        self.__service_status.bind_service(
            BaseProtocol._support_protocol[protocol](name=name, host=host)
        )

    def unbind_service_by_name(self, name: str):
        if name in self.__service_status:
            self.__service_status.unbind_service_by_name(name)
            return
        if name in self.__service_status_group:
            self.__service_status_group.unbind_group_by_name(name)
            return
        raise NameNotFoundError

    def bind_group_by_name(self, service_name_list: List[str], name: str):
        service_instance_list: List[BaseProtocol] = []
        for i in service_name_list:
            service_instance_list.append(
                self.__service_status.get_service_instance_by_name(i)
            )
        self.__service_status_group.bind_group(service_instance_list, name)
        for i in service_instance_list:
            self.__service_status.unbind_service(i)

    def modify_service_param(self, name: str, key: str, value: str):
        for i, j in enumerate(self.__service_status.bind_services):
            if j == name:
                temp_config = j.export()
                if key not in temp_config:
                    raise ParamInvalidError
                temp_config[key] = value
                self.__service_status.bind_services[i] = j.load(temp_config)
                return
        raise NameNotFoundError

    async def get_detect_result(self):
        return dict(
            (await self.__service_status.get_detect_result()),
            **(await self.__service_status_group.get_detect_result()),
        )
