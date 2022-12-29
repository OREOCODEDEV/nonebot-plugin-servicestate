import pytest
from nonebug import App
from pathlib import Path
from typing import TYPE_CHECKING, Set
import pytest
import json
import random

if TYPE_CHECKING:
    from nonebot.plugin import Plugin

DEFAULT_CONFIG = {"service": {"HTTP": [], "TCP": []}, "service_group": {}}
DEFAULT_CONFIG_FILE_PATH = r".\nonebot_plugin_servicestate\config.txt"
print("Restoreing settings...")
with open(DEFAULT_CONFIG_FILE_PATH, "w") as f:
    f.write(json.dumps(DEFAULT_CONFIG))


@pytest.fixture
def load_plugins_servicestate(nonebug_init: None) -> Set["Plugin"]:
    import nonebot  # 这里的导入必须在函数内

    print("Loading plugins...")
    # 加载插件
    return nonebot.load_plugins("nonebot_plugin_servicestate")


@pytest.mark.asyncio
async def test_weather(app: App, load_plugins_servicestate):
    from nonebot.adapters.onebot.v11 import (
        Message,
        MessageEvent,
        PrivateMessageEvent,
    )
    from nonebot.adapters.onebot.v11.event import Sender
    from nonebot_plugin_servicestate import (
        service_add_matcher,
        service_status_matcher,
        service_del_matcher,
        service_group_matcher,
        service_ungroup_matcher,
        service_set_matcher,
        reload_config_matcher,
    )

    def make_private_message_event(content: str) -> PrivateMessageEvent:
        return PrivateMessageEvent(
            time=2333,
            self_id=1125598078,
            post_type="message",
            sub_type="friend",
            user_id=1064988363,
            message_type="private",
            message_id=2333,
            message=Message(content),
            original_message=Message(content),
            raw_message=content,
            font=2333,
            sender=Sender(),
            to_me=True,
        )

    # print("=" * 20)
    # print("nonebot-plugin-servicestate NoneBug test start...")
    # print("=" * 20)
    async def simple_tester(matcher, message: str, out_message: str):
        message = "/" + message
        async with app.test_matcher(matcher) as ctx:
            bot = ctx.create_bot()
            event = make_private_message_event(message)
            ctx.receive_event(bot, event)
            ctx.should_ignore_permission()
            ctx.should_call_send(event, out_message, True)
            ctx.should_finished()

    await simple_tester(service_status_matcher, "服务状态", "您未绑定任何服务！")
    await simple_tester(service_add_matcher, "服务添加", "参数不足\n添加服务 <协议> <名称> <地址>")
    await simple_tester(service_add_matcher, "添加服务 HTTPS", "参数不足\n添加服务 <协议> <名称> <地址>")
    await simple_tester(
        service_add_matcher,
        "添加服务 HTTPS BaiDu http://www.baidu.com",
        '暂不支持协议 "HTTPS" ！\n支持的协议： HTTP、TCP',
    )
    await simple_tester(
        service_add_matcher, "添加服务 HTTP BaiDu http://www.baidu.com", "HTTP 协议绑定成功"
    )
    await simple_tester(service_status_matcher, "服务状态", "O 正常 | BaiDu")
    await simple_tester(
        service_add_matcher,
        "添加服务 HTTP BaiDu http://www.baidu.com",
        "服务名称冲突！\n请修改新增服务名称或移除同名服务后再试",
    )
    await simple_tester(
        service_add_matcher,
        "添加服务 HTTP2 BaiDu http://www.baidu.com",
        '暂不支持协议 "HTTP2" ！\n支持的协议： HTTP、TCP',
    )
    await simple_tester(
        service_add_matcher,
        "添加服务 HTTP BaiDu2 http://www.baidu.com",
        "HTTP 协议绑定成功",
    )
    await simple_tester(
        service_status_matcher,
        "服务状态",
        "O 正常 | BaiDu\nO 正常 | BaiDu2",
    )
    await simple_tester(
        service_group_matcher,
        "服务合并",
        "参数不足\n合并服务 <名称1> <名称2> <群组名称>",
    )
    await simple_tester(
        service_group_matcher,
        "服务合并 BaiDu BaiDu3 BaiDuAll",
        "操作失败：合并的服务名称中有一个或多个无法找到！",
    )
    await simple_tester(
        service_group_matcher,
        "服务合并 BaiDu BaiDu3 BaiDuAll",
        "操作失败：合并的服务名称中有一个或多个无法找到！",
    )
    await simple_tester(
        service_group_matcher,
        "服务合并 BaiDu BaiDu2 BaiDuAll",
        "已成功合并 2 个服务",
    )
