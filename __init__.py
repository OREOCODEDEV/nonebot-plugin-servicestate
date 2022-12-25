import asyncio
from service import ServiceStatus, ServiceStatusGroup
from typing import Dict, List, Any


def nonebot_pretty_output(result_dict: Dict) -> str:
    pretty_text = ""
    for name, result in result_dict.items():
        pretty_text += "O" if result else "X"
        pretty_text += "" if result else " "  # QQ字符O和X宽度不一致
        pretty_text += " "
        pretty_text += "可用" if result else "故障"
        pretty_text += " | "
        pretty_text += name
        pretty_text += "\n"
    pretty_text = pretty_text[:-1]
    return pretty_text


class NonebotPluginServiceStateManager:
    def __init__(self) -> None:
        pass


config = {
    "HTTP": [
        {"name": "会战面板", "host": "https://524266386o.eicp.vip/yobot/", "timeout": 5},
        {"name": "映射状态", "host": "http://103.46.128.44", "timeout": 5},
        {"name": "涩图API", "host": "http://api.lolicon.app", "timeout": 5},
        {"name": "涩图图床", "host": "http://i.pixiv.re", "timeout": 5},
    ]
}

service_status = ServiceStatus.load(config)
service_status_group = ServiceStatusGroup()


async def demo_test():
    result = await service_status.get_detect_result()
    text = nonebot_pretty_output(result)
    print(text)
    print("======")
    service_status_group.bind_group_by_name(service_status, ["涩图API", "涩图图床"], "涩图")
    result = await service_status.get_detect_result()
    result_group = await service_status_group.get_detect_result()
    text = nonebot_pretty_output(result)
    text += "\n"
    text += nonebot_pretty_output(result_group)
    print(text)
    print(service_status.bind_services[0].export())


asyncio.run(demo_test())
