from .service import ServiceStatus, ServiceStatusGroup, BaseProtocol, support_protocol
from .exception import (
    UnsupportedProtocolError,
    NameConflictError,
    NameNotFoundError,
    ConfigError,
)
from typing import Dict, List, Any, Tuple
from pathlib import Path
import json


from nonebot.plugin.on import on_command
from nonebot.params import CommandArg, Depends
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.log import logger

CONFIG_FILE_PATH = Path(__file__).parent.joinpath("config.txt")


class NonebotPluginServiceStateManager:
    __service_status: ServiceStatus = ServiceStatus()
    __service_status_group: ServiceStatusGroup = ServiceStatusGroup()

    def __init__(self) -> None:
        pass

    def load(self, path: Path):
        with open(path, "r", encoding="utf-8") as f:
            load_dict = json.loads(f.read())
        print(type(load_dict))
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
            raise UnsupportedProtocolError
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
            if j.name == name:
                temp_config = j.export()
                if key not in temp_config:
                    raise ConfigError
                temp_config[key] = value
                self.__service_status.bind_services[i] = j.load(temp_config)
                return
        raise NameNotFoundError

    async def get_detect_result(self):
        return dict(
            (await self.__service_status.get_detect_result()),
            **(await self.__service_status_group.get_detect_result()),
        )

    async def get_detect_result_text(self) -> str:
        result_dict = await self.get_detect_result()
        if result_dict == {}:
            return "您未绑定任何监控的服务！"
        pretty_text = ""
        for name, result in result_dict.items():
            pretty_text += "O" if result else "X"
            pretty_text += "" if result else " "  # QQ字符O和X宽度不一致
            pretty_text += " "
            pretty_text += "正常" if result else "故障"
            pretty_text += " | "
            pretty_text += name
            pretty_text += "\n"
        pretty_text = pretty_text[:-1]
        return pretty_text

    def debug(self):
        print(self.__service_status.export())
        print(self.__service_status_group.export())


manager = NonebotPluginServiceStateManager()
manager.load(CONFIG_FILE_PATH)

service_status_matcher = on_command("服务状态")


@service_status_matcher.handle()
async def _():
    await service_status_matcher.finish(await manager.get_detect_result_text())


def extract_str_list(command_arg: Message = CommandArg()):
    return command_arg.extract_plain_text().split()


service_add_matcher = on_command(
    "监控服务新增", aliases={"监控服务添加", "监控服务增加", "添加监控服务", "增加监控服务", "新增监控服务"}
)


@service_add_matcher.handle()
async def _(command_arg_list: List[str] = Depends(extract_str_list)):
    if len(command_arg_list) < 3:
        await service_add_matcher.finish(f"参数不足\n监控服务新增 <协议> <名称> <地址>")
    protocol = command_arg_list[0]
    name = command_arg_list[1]
    host = command_arg_list[2]
    try:
        manager.bind_new_service(protocol, name, host)
    except UnsupportedProtocolError:
        await service_add_matcher.finish(
            f"暂不支持协议 \"{protocol}\" ！\n支持的协议： {'、'.join(support_protocol())}"
        )
    except NameConflictError:
        await service_add_matcher.finish("服务名称冲突！\n请修改新增服务名称或移除同名服务监控后再试")
    manager.save(CONFIG_FILE_PATH)
    await service_add_matcher.finish(f"{protocol} 协议绑定成功")


service_del_matcher = on_command("监控服务删除", aliases={"删除监控服务"})


@service_del_matcher.handle()
async def _(command_arg: Message = CommandArg()):
    try:
        manager.unbind_service_by_name(command_arg.extract_plain_text())
    except NameNotFoundError:
        await service_del_matcher.finish("操作失败：未找到该服务名称！")
    manager.save(CONFIG_FILE_PATH)
    await service_del_matcher.finish("已删除服务：" + command_arg)


service_group_matcher = on_command("监控服务合并", aliases={"合并监控服务"})


@service_group_matcher.handle()
async def _(command_arg_list: List[str] = Depends(extract_str_list)):
    bind_service_name_list = command_arg_list[:-1]
    name = command_arg_list[-1]
    try:
        manager.bind_group_by_name(bind_service_name_list, name)
    except NameNotFoundError:
        await service_group_matcher.finish("操作失败：合并的服务名称中有一个或多个无法找到！")
    manager.save(CONFIG_FILE_PATH)
    await service_group_matcher.finish(f"已成功合并 {len(bind_service_name_list)} 个服务")


service_set_matcher = on_command("监控服务修改", aliases={"修改监控服务"})


@service_set_matcher.handle()
async def _(command_arg_list: List[str] = Depends(extract_str_list)):
    name = command_arg_list[0]
    command_arg_list = command_arg_list[1:]
    if len(command_arg_list) % 2 != 0:
        await service_set_matcher.finish("操作失败：修改的参数需成对以 <参数名> <值> 方法提供")
    settings_list: List[Tuple[str, str]] = []
    for i in range(0, len(command_arg_list) - 1, 2):
        settings_list.append((command_arg_list[i], command_arg_list[i + 1]))
    logger.debug(f"Modifying settings: {settings_list}")
    manager.save(CONFIG_FILE_PATH)
    try:
        for key, value in settings_list:
            if value == "None" or value == "空":
                value = None
            manager.modify_service_param(name, key, value)
    except NameNotFoundError:
        manager.load(CONFIG_FILE_PATH)
        await service_set_matcher.finish("操作失败：修改的服务名或参数名未找到")
    except ConfigError:
        manager.load(CONFIG_FILE_PATH)
        await service_set_matcher.finish("操作失败：参数格式不正确")
    except:
        manager.load(CONFIG_FILE_PATH)
        await service_set_matcher.finish("操作失败：内部错误")
    manager.save(CONFIG_FILE_PATH)
    await service_set_matcher.finish(f"服务 {name} 参数修改成功")


reload_config_matcher = on_command("服务状态载入配置")


@reload_config_matcher.handle()
async def _():
    manager.load(CONFIG_FILE_PATH)
    await reload_config_matcher.finish("已重新载入服务状态配置")
