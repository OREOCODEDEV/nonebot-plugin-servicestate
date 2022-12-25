import asyncio
from service import ServiceStatus, ServiceStatusGroup
from typing import Dict, List, Any
from exception import NameConflictException, BindFailedException

config = {
    "HTTP": [
        {"name": "会战面板", "host": "https://524266386o.eicp.vip/yobot/", "timeout": 5},
        {"name": "映射状态", "host": "http://103.46.128.44", "timeout": 5},
        {"name": "涩图API", "host": "http://api.lolicon.app", "timeout": 5},
        {"name": "涩图图床", "host": "http://i.pixiv.re", "timeout": 5},
    ]
}


class NonebotPluginServiceStateManager:
    __service_status: ServiceStatus = None
    __service_status_group: ServiceStatusGroup = None

    def __init__(self) -> None:
        pass

    def load(self):
        self.__service_status = ServiceStatus.load(config)
        self.__service_status_group = ServiceStatusGroup()
        print(self.__service_status.bind_service)

    def bind_group_by_name(self, service_name_list: List[str], name: str):
        self.__service_status_group.bind_group_by_name(
            self.__service_status, service_name_list, name
        )

    async def get_detect_result(self):
        return dict(
            (await self.__service_status.get_detect_result()),
            **(await self.__service_status_group.get_detect_result())
        )

    async def get_detect_result_text(self) -> str:
        result_dict = await self.get_detect_result()
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


demo = NonebotPluginServiceStateManager()


async def demo_test():
    demo.load()
    print(await demo.get_detect_result_text())
    demo.bind_group_by_name(["涩图API", "涩图图床"], "涩图")
    print(await demo.get_detect_result_text())


asyncio.run(demo_test())
