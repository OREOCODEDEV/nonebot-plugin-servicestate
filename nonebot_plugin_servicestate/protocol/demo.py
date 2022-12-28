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

# 从内部继承抽象基类BaseProtocol以及协议参数类BaseProtocolData
from .protocol import BaseProtocol, BaseProtocolData
from nonebot.log import logger  # 导入 NoneBot2 日志模块


class DemoProtocolData(BaseProtocolData):  # 继承协议参数类BaseProtocolData
    """
    在这里声明你的自定义参数变量
    """

    always_malfunction: bool = False  # 该协议的自定义参数：是否总是返回故障状态
    normal_rate: int = 50  # 该协议的自定义参数：可用状态的机率


class DEMOProtocol(BaseProtocol):  # 类名可随意填写，但记得继承上面导入的BaseProtocol
    _PROTOCOL_NAME = "DemoProtocol"  # 协议名称，不得与正在使用的协议名称相同
    _DATA_MODEL = DemoProtocolData  # 声明该协议的参数类

    async def detect(self) -> bool:  # 实现探测方法，返回bool，注意该方法名不可更改
        """
        在此处实现你的自定义协议的处理代码
        最终返回bool（True为可用，False为故障）
        """
        if self.always_malfunction:
            # 自定义参数中always_malfunction参数为True，永远返回不可用状态
            logger.info("Custom protocol refused")  # 在控制台记录一些信息
            return False  # 永远返回不可用状态
        random_result: bool = (
            random.random() < self.normal_rate / 100
        )  # 按概率随机生成可用状态
        logger.info(f"Custom protocol random state: {random_result}")  # 在控制台记录一些信息
        return random_result  # 返回随机生成的可用状态（bool型）
