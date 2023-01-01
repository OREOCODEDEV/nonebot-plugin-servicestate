from typing import Dict, List, Any, Tuple
from pathlib import Path
from pydantic import ValidationError

from nonebot.plugin.on import on_command
from nonebot.params import CommandArg, Depends
from nonebot.adapters.onebot.v11 import Message
import nonebot.log as nb_log
from nonebot.permission import SUPERUSER

from .logger import set_logger, logger

set_logger(nb_log.logger)

from .service import SupportProtocol
from .exception import (
    ProtocolUnsopportError,
    NameConflictError,
    ParamCountInvalidError,
    NameEscapeCharacterCountError,
    NameNotFoundError,
)
from .manager import manager
from .utils import Escharacter

service_status_matcher = on_command("服务状态")


@service_status_matcher.handle()
async def _():
    result_dict = await manager.get_detect_result()
    if result_dict == {}:
        await service_status_matcher.finish("您未绑定任何服务！")
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
    await service_status_matcher.finish(pretty_text)


def extract_str_list(command_arg: Message = CommandArg()):
    return command_arg.extract_plain_text().split()


service_add_matcher = on_command(
    "添加服务",
    aliases={"服务添加", "服务增加", "服务新增", "增加服务", "新增服务"},
    permission=SUPERUSER,
)


@service_add_matcher.handle()
async def _(command_arg_list: List[str] = Depends(extract_str_list)):
    if len(command_arg_list) < 3:
        await service_add_matcher.finish(f"参数不足\n添加服务 <协议> <名称> <地址>")
    protocol = command_arg_list[0]
    name = command_arg_list[1]
    host = command_arg_list[2]
    try:
        manager.bind_new_service(protocol, name, host)
    except ProtocolUnsopportError:
        await service_add_matcher.finish(
            f"暂不支持协议 \"{protocol}\" ！\n支持的协议： {'、'.join(SupportProtocol.get())}"
        )
    except NameConflictError:
        await service_add_matcher.finish("服务名称冲突！\n请修改新增服务名称或移除同名服务后再试")
    manager.save()
    await service_add_matcher.finish(f"{protocol} 协议绑定成功")


service_del_matcher = on_command("服务删除", aliases={"删除服务"}, permission=SUPERUSER)


@service_del_matcher.handle()
async def _(command_arg: Message = CommandArg()):
    try:
        manager.unbind_service_by_name(command_arg.extract_plain_text())
    except KeyError:
        await service_del_matcher.finish("操作失败：未找到该服务名称！")
    except NameNotFoundError:
        await service_del_matcher.finish("操作失败：未找到该服务名称！")
    manager.save()
    await service_del_matcher.finish("已删除服务：" + command_arg)


service_group_matcher = on_command(
    "服务合并", aliases={"合并服务", "群组服务", "服务群组"}, permission=SUPERUSER
)


@service_group_matcher.handle()
async def _(command_arg_list: List[str] = Depends(extract_str_list)):
    if len(command_arg_list) < 3:
        await service_group_matcher.finish(f"参数不足\n合并服务 <名称1> <名称2> <群组名称>")
    bind_service_name_list = command_arg_list[:-1]
    name = command_arg_list[-1]
    try:
        manager.bind_group_by_name(bind_service_name_list, name)
    except KeyError:
        await service_group_matcher.finish("操作失败：合并的服务名称中有一个或多个无法找到！")
    manager.save()
    await service_group_matcher.finish(f"已成功合并 {len(bind_service_name_list)} 个服务")


service_ungroup_matcher = on_command("服务解散", aliases={"解散服务"}, permission=SUPERUSER)


@service_ungroup_matcher.handle()
async def _(name_msg: Message = CommandArg()):
    name = name_msg.extract_plain_text()
    try:
        manager.unbind_group_by_name(name)
    except KeyError:
        await service_ungroup_matcher.finish("操作失败：无法找到该名称的群组服务")
    except NameConflictError:
        await service_ungroup_matcher.finish("操作失败：即将解散的群组服务中与现有名称重复")
    except:
        await service_ungroup_matcher.finish("操作失败：内部错误")
    manager.save()
    await service_ungroup_matcher.finish(f"已成功解散群组")


service_set_matcher = on_command("服务修改", aliases={"修改服务"}, permission=SUPERUSER)


@service_set_matcher.handle()
async def _(command_arg_list: List[str] = Depends(extract_str_list)):
    if len(command_arg_list) < 3:
        await service_group_matcher.finish(f"参数不足\n修改服务 <名称> <参数> <值>")
    try:
        name = Escharacter(command_arg_list[0])
    except NameEscapeCharacterCountError:
        await service_group_matcher.finish("操作失败：@ 转义符解析错误\n修改服务 <群组名>@<服务名> <参数名> <值>")
    command_arg_list = command_arg_list[1:]
    if len(command_arg_list) % 2 != 0:
        await service_set_matcher.finish("操作失败：修改的参数需成对以 <参数名> <值> 方法提供")
    settings_list: List[Tuple[str, str]] = []
    for i in range(0, len(command_arg_list) - 1, 2):
        settings_list.append((command_arg_list[i], command_arg_list[i + 1]))
    logger.debug(f"Modifying settings: {name} @ {settings_list}")
    try:
        for key, value in settings_list:
            if name.is_group:
                manager.modify_service_group_param(*name.group_name, key, value)
                continue
            manager.modify_service_param(name.name, key, value)
    except KeyError:
        await service_set_matcher.finish("操作失败：修改的服务名或参数名未找到")
    except ValidationError:
        await service_set_matcher.finish("操作失败：参数格式或类型不正确")
    except:
        await service_set_matcher.finish("操作失败：内部错误")
    manager.save()
    await service_set_matcher.finish(f"服务 {name} 参数修改成功")


reload_config_matcher = on_command("服务重载", permission=SUPERUSER)


@reload_config_matcher.handle()
async def _():
    manager.load()
    await reload_config_matcher.finish("已重新载入服务状态配置")
