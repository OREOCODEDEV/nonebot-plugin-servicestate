from typing import Dict, List, Any, Tuple
from pathlib import Path
from pydantic import ValidationError

from nonebot.plugin.on import on_command
from nonebot.params import CommandArg, Depends
from nonebot.adapters.onebot.v11 import Message
from nonebot.log import logger
from nonebot.permission import SUPERUSER

from .service import support_protocol
from .exception import (
    ProtocolUnsopportError,
    NameConflictError,
    NameNotFoundError,
    ParamCountInvalidError,
)
from .manager import CommandManager

CONFIG_FILE_PATH = Path(__file__).parent.joinpath("config.txt")
manager = CommandManager()
manager.load(CONFIG_FILE_PATH)

service_status_matcher = on_command("服务状态")


@service_status_matcher.handle()
async def _():
    result_dict = await manager.get_detect_result()
    if result_dict == {}:
        await service_status_matcher.finish("您未绑定任何监控的服务！")
    pretty_text = ""
    for name, result in result_dict.items():
        pretty_text += "O" if result else "X"
        # pretty_text += "" if result else " "  # QQ字符O和X宽度不一致
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
    "监控服务新增",
    aliases={"监控服务添加", "监控服务增加", "添加监控服务", "增加监控服务", "新增监控服务"},
    permission=SUPERUSER,
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
    except ProtocolUnsopportError:
        await service_add_matcher.finish(
            f"暂不支持协议 \"{protocol}\" ！\n支持的协议： {'、'.join(support_protocol())}"
        )
    except NameConflictError:
        await service_add_matcher.finish("服务名称冲突！\n请修改新增服务名称或移除同名服务监控后再试")
    manager.save(CONFIG_FILE_PATH)
    await service_add_matcher.finish(f"{protocol} 协议绑定成功")


service_del_matcher = on_command("监控服务删除", aliases={"删除监控服务"}, permission=SUPERUSER)


@service_del_matcher.handle()
async def _(command_arg: Message = CommandArg()):
    try:
        manager.unbind_service_by_name(command_arg.extract_plain_text())
    except NameNotFoundError:
        await service_del_matcher.finish("操作失败：未找到该服务名称！")
    manager.save(CONFIG_FILE_PATH)
    await service_del_matcher.finish("已删除服务：" + command_arg)


service_group_matcher = on_command(
    "监控服务合并", aliases={"合并监控服务", "群组监控服务"}, permission=SUPERUSER
)


@service_group_matcher.handle()
async def _(command_arg_list: List[str] = Depends(extract_str_list)):
    if len(command_arg_list) < 3:
        await service_group_matcher.finish(f"参数不足\n合并监控服务 <名称1> <名称2> <群组名称>")
    bind_service_name_list = command_arg_list[:-1]
    name = command_arg_list[-1]
    try:
        manager.bind_group_by_name(bind_service_name_list, name)
    except NameNotFoundError:
        await service_group_matcher.finish("操作失败：合并的服务名称中有一个或多个无法找到！")
    manager.save(CONFIG_FILE_PATH)
    await service_group_matcher.finish(f"已成功合并 {len(bind_service_name_list)} 个服务")


service_set_matcher = on_command("监控服务修改", aliases={"修改监控服务"}, permission=SUPERUSER)


@service_set_matcher.handle()
async def _(command_arg_list: List[str] = Depends(extract_str_list)):
    if len(command_arg_list) < 3:
        await service_group_matcher.finish(f"参数不足\n修改监控服务 <名称> <参数> <值>")
    name = command_arg_list[0]
    command_arg_list = command_arg_list[1:]
    if len(command_arg_list) % 2 != 0:
        await service_set_matcher.finish("操作失败：修改的参数需成对以 <参数名> <值> 方法提供")
    settings_list: List[Tuple[str, str]] = []
    for i in range(0, len(command_arg_list) - 1, 2):
        settings_list.append((command_arg_list[i], command_arg_list[i + 1]))
    logger.debug(f"Modifying settings: {name} @ {settings_list}")
    manager.save(CONFIG_FILE_PATH)
    try:
        for key, value in settings_list:
            manager.modify_service_param(name, key, value)
    except NameNotFoundError:
        manager.load(CONFIG_FILE_PATH)
        await service_set_matcher.finish("操作失败：修改的服务名或参数名未找到")
    except ValidationError:
        manager.load(CONFIG_FILE_PATH)
        await service_set_matcher.finish("操作失败：参数格式或类型不正确")
    except:
        manager.load(CONFIG_FILE_PATH)
        await service_set_matcher.finish("操作失败：内部错误")
    manager.save(CONFIG_FILE_PATH)
    await service_set_matcher.finish(f"服务 {name} 参数修改成功")


reload_config_matcher = on_command("服务状态载入配置", permission=SUPERUSER)


@reload_config_matcher.handle()
async def _():
    manager.load(CONFIG_FILE_PATH)
    await reload_config_matcher.finish("已重新载入服务状态配置")
