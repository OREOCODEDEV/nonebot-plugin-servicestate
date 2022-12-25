import asyncio
from service import ServiceStatus, ServiceStatusGroup, BaseProtocol, Protocols
from typing import Dict, List, Any
from exception import NameConflictException, BindFailedException
from pathlib import Path
import json

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

    def bind_new_service(self, service: BaseProtocol):
        self.__service_status.bind_service(service)

    def bind_group_by_name(self, service_name_list: List[str], name: str):
        service_instance_list: List[BaseProtocol] = []
        for i in service_name_list:
            service_instance_list.append(
                self.__service_status.get_service_instance_by_name(i)
            )
        self.__service_status_group.bind_group(service_instance_list, name)
        for i in service_instance_list:
            self.__service_status.unbind_service(i)

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


async def demo_test():
    manager.load(CONFIG_FILE_PATH)
    manager.debug()
    print(await manager.get_detect_result_text())
    print("=" * 20)
    # manager.bind_group_by_name(["涩图API", "涩图图床"], "涩图")
    print(await manager.get_detect_result_text())
    # manager.save(CONFIG_FILE_PATH)


asyncio.run(demo_test())
