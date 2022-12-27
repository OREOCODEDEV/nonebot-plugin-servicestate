from __future__ import annotations

from typing import Union, Dict, List
import random

"""
自定义协议DEMO

该demo将演示如何自定义一个可用概率为随机的协议（概率可调节）

更多说明请前往：https://github.com/OREOCODEDEV/nonebot-plugin-servicestate

该协议将有 2 个可调节参数
always_malfunction：是否总是返回故障状态
normal_rate: always_malfunction为False时，返回可用状态的机率

注意：该文件仅保证适用于当前版本的nonebot-plugin-servicestate
若后续插件版本更新，自定义协议需要的某些方法或字段可能会产生变更
"""

from .protocol import BaseProtocol  # 从内部继承抽象基类BaseProtocol


class DEMO_Protocol(BaseProtocol):  # 类名可随意填写，但记得继承上面导入的BaseProtocol
    _PROTOCOL_NAME = "DemoProtocol"  # 协议名称，用于使用创建命令时用于区分和指定该协议的名称

    def __init__(
        self, name: str, host: str
    ) -> None:  # name: 服务名, host: 地址；这两个参数是所有协议强制要求的
        super().__init__(name=name, host=host)  # 使用父类__init__方法，如不理解请勿改动此处
        """
        在这里声明你的自定义参数变量以及协议初始化时的行为
        """
        self.always_malfunction: bool = False  # 该协议的自定义参数，是否总是返回故障状态
        self.normal_rate: int = 50  # 该协议的自定义参数，可用状态的机率

    async def detect(self) -> bool:  # 实现探测方法，返回bool，注意该方法名不可更改
        """
        在此处实现你的自定义协议的处理代码
        最终返回bool（True为可用，False为故障）
        """
        if self.always_malfunction:
            # 自定义参数中always_malfunction参数为True，永远返回不可用状态
            return False  # 永远返回不可用状态
        random_result: bool = random.random() > self.normal_rate / 100  # 按照概率生成随机可用状态
        return random_result  # 返回随机生成的可用状态（bool型）

    @classmethod  # 类方法装饰器，如不理解请勿改动此处
    def load(cls, source: Dict) -> DEMO_Protocol:  # 实现参数导入方法，注意该方法名不可更改
        protocol_instance = cls(source["name"], source["host"])  # 实例化该协议，如不理解请勿改动此处
        protocol_instance.always_malfunction = source.get(
            "always_malfunction", False
        )  # 从导入数据中提取always_malfunction参数，没有时默认为False
        protocol_instance.normal_rate = source.get(
            "normal_rate", 50
        )  # 从导入数据中提取normal_rate参数
        """
        参数类型转换
        """
        if not isinstance(protocol_instance.always_malfunction, bool):
            if isinstance(protocol_instance.always_malfunction, str):
                protocol_instance.always_malfunction = (
                    True if protocol_instance.always_malfunction == "True" else False
                )
            else:
                protocol_instance.always_malfunction = False
        protocol_instance.normal_rate = int(protocol_instance.normal_rate)
        return protocol_instance
