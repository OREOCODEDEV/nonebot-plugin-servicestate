from __future__ import annotations

from typing import Dict, List, Any, Tuple, Union
from pathlib import Path
import json

from nonebot.log import logger

from nonebot.plugin.load import require

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

from .service import ServiceStatus, ServiceStatusGroup, BaseProtocol, SupportProtocol
from .exception import (
    ProtocolUnsopportError,
    NameConflictError,
    NameNotFoundError,
    ParamInvalidError,
)

plugin_config_file_path = Path(store.get_data_file("nonebot-plugin-servicestate", "protocol_settings.json"))


def modify_exception_recovery(func):
    def inner(*args, **kw):
        try:
            manager.save()
            return func(*args, **kw)
        except Exception as e:
            manager.load()
            logger.error(f"Modify railed: {e}")
            raise e

    return inner


class CommandManager:
    __service_status: ServiceStatus = ServiceStatus()
    __service_status_group: ServiceStatusGroup = ServiceStatusGroup()

    def __init__(self) -> None:
        pass

    def load(self, path: Path = plugin_config_file_path) -> None:
        with open(path, "r", encoding="utf-8") as f:
            load_dict = json.loads(f.read())
        self.__service_status = ServiceStatus.load(load_dict["service"])
        self.__service_status_group = ServiceStatusGroup.load(load_dict["service_group"])

    def save(self, path: Path = plugin_config_file_path) -> None:
        save_dict = {
            "service": self.__service_status.export(),
            "service_group": self.__service_status_group.export(),
        }
        if not path.exists():
            logger.debug("Creating plugin folder")
            path.parent.mkdir(parents=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    save_dict,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=4,
                )
            )

    def bind_new_service(self, protocol: str, name: Union[str, List[str]], host: str) -> None:
        if protocol not in SupportProtocol.get():
            raise ProtocolUnsopportError
        if isinstance(name, List):
            return self.__bind_new_group_service(protocol, *name, host=host)
        if name in self.__service_status:
            raise NameConflictError
        if name in self.__service_status_group:
            raise NameConflictError
        self.__service_status.register_service(protocol, name=name, host=host)

    def __bind_new_group_service(self, protocol: str, group_name: str, service_name: str, host: str) -> None:
        self.__service_status_group[group_name].register_service(protocol, name=service_name, host=host)

    def unbind_service_by_name(self, name: Union[str, List[str]]) -> None:
        if isinstance(name, List):
            return self.__unbind_service_group_by_name(*name)
        if name in self.__service_status:
            self.__service_status.unbind_service(name)
            return
        if name in self.__service_status_group:
            self.__service_status_group.unbind_group(name)
            return
        raise NameNotFoundError

    def __unbind_service_group_by_name(self, group_name: str, name: str) -> None:
        if group_name not in self.__service_status_group:
            raise NameNotFoundError
        self.__service_status_group[group_name].unbind_service(name)

    def bind_group_by_name(self, service_name_list: List[str], name: str) -> None:
        service_instance_list: List[BaseProtocol] = [self.__service_status[i] for i in service_name_list]
        self.__service_status_group.bind_group(service_instance_list, name)
        for i in service_instance_list:
            self.__service_status.unbind_service(i)

    @modify_exception_recovery
    def unbind_group_by_name(self, name: str) -> None:
        if name not in self.__service_status_group:
            raise NameNotFoundError
        for i in self.__service_status_group[name]:
            if i.name in self.__service_status or i.name in self.__service_status_group:
                raise NameConflictError
            self.__service_status.bind_service(i)
        self.__service_status_group.unbind_group(name)

    @modify_exception_recovery
    def modify_service_param(self, name: Union[str, List[str]], key: str, value: str) -> None:
        if isinstance(name, List):
            return self.__modify_service_group_param(*name, key=key, value=value)
        protocol_instance = self.__service_status[name]
        temp_config = protocol_instance.export()
        if key not in temp_config:
            raise ParamInvalidError
        temp_config[key] = value
        self.__service_status[name] = protocol_instance.load(temp_config)

    @modify_exception_recovery
    def __modify_service_group_param(self, group_name: str, service_name, key: str, value: str):
        if group_name not in self.__service_status_group:
            raise NameNotFoundError
        original_instance = self.__service_status_group[group_name][service_name]
        temp_config = original_instance.export()
        if key not in temp_config:
            raise ParamInvalidError
        temp_config[key] = value
        self.__service_status_group[group_name][service_name] = original_instance.load(temp_config)

    async def get_detect_result(self):
        return dict(
            (await self.__service_status.get_detect_result()),
            **(await self.__service_status_group.get_detect_result()),
        )

    def get_service_count(self) -> Tuple[int, int, int]:
        single_count = len(self.__service_status)
        group_count = len(self.__service_status_group)
        group_service_count = 0
        for i in self.__service_status_group:
            group_service_count += len(i)
        return single_count, group_count, group_service_count


manager = CommandManager()
if not plugin_config_file_path.is_file():
    logger.info("Creating config file")
    manager.save()
manager.load(plugin_config_file_path)
