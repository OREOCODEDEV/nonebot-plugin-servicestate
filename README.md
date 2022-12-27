<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# NoneBot Plugin ServiceState

_✨ NoneBot 服务状态查询插件 ✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/nonebot/plugin-apscheduler/master/LICENSE">
    <img src="https://img.shields.io/github/license/nonebot/plugin-apscheduler.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-apscheduler">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-apscheduler.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
</p>

## 简介

可通过 `服务状态` 查询当前服务器各功能 API 可用状态

例如：

```
O 可用 | 会战面板
O 可用 | SSH登录
X 故障 | 涩图
O 可用 | 画图
X 故障 | ChatGPT
```


## 特色

- 易于上手：所有配置项的增删查改都可通过文本交互实现，无需修改任何配置文件
- 异步支持：所有协议均通过异步实现，无需担心探测过程中造成堵塞
- 易于拓展：开发者只需实现核心方法即可增添新协议支持，详情参考[添加协议](#添加协议)


## 安装

使用 `nb-cli` 安装（推荐）：
```
nb plugin install nonebot-plugin-servicestate
```

使用 `pip` 安装：
```
pip install nonebot-plugin-servicestate
```

使用 `git clone` 安装：
```
git clone https://github.com/OREOCODEDEV/nonebot-plugin-servicestate.git
```


## 使用

### 服务状态查询
可通过发送 `服务状态` 获取当前绑定的监控服务可用状态

**只有服务状态查询无权限要求，监控服务的增删查改均需要 NoneBot 管理员权限，若监控服务增删查改命令不响应，请检查 NoneBot 是否已正确配置管理员**

### 新增监控服务
可通过发送 `添加监控服务 <协议> <名称> <地址>` 以新增需要监控的服务
* 可在[此处](#协议支持)查看所有受支持的协议
```
添加监控服务 HTTP git截图 https://github.com
```

### 修改监控服务
可通过发送 `修改监控服务 <名称> <参数名> <参数内容>` 以修改监控服务的参数
* 不同协议支持修改的参数字段不同，具体请参考[协议支持](#协议支持)
```
修改监控服务 git截图 proxies http://127.0.0.1:10809
```

### 群组监控服务
**当前版本服务群组后暂未支持修改及解散群组，只能删除群组，请注意** ~~除非改配置文件~~

当多个API共同支持某项服务时，可通过 `群组监控服务 <名称1> <名称2> <群组名称>` 群组多个服务为一个显示

* 只有当群组中的所有服务都为可用状态时，群组才显示为可用，当有一个或多个服务为故障状态时，群组都显示为故障

例：假设当前已设置好 涩图信息API 和 涩图图床 两个监控服务，可通过下列命令组合为一个服务
```
群组监控服务 涩图信息API 涩图图床 涩图
```
群组命令前：
```
O 可用 | 涩图信息API
X 故障 | 涩图图床
```
群组命令后：
```
X 故障 | 涩图
```

### 删除监控服务
可通过发送 `删除监控服务 <名称>` 以不再监测该服务
```
删除监控服务 git截图
```


## 协议支持

以下是项目当前支持的协议，以及可被通过修改命令配置的字段

### HTTP GET
- 协议名称：`HTTP`
- [x] 状态查询：探测地址超时前返回状态 200 为可用
- [x] 服务名称：`name` @ [str]
- [x] 监测地址：`host` @ [str]
- [x] 超时时间：`timeout` @ [int]
- [x] 代理地址：`proxies` @ [str, None]
- [ ] 请求头：暂未支持
- [ ] UA：暂未支持
- [ ] Cookie：暂未支持
- [ ] 有效响应码：暂未支持
- [ ] 内容正则判定：暂未支持

### TCP
- 协议名称：`TCP`
- [x] 状态查询：探测地址超时前成功建立连接为可用
- [x] 服务名称：`name` @ [str]
- [x] 监测地址：`host` @ [str]
- [x] 端口：`port` @ [int]
- [ ] 代理地址：暂未支持
- [ ] 超时时间：暂未支持

### PING
- [ ] 状态查询：暂未支持
- [ ] 监测地址：暂未支持
- [ ] 代理地址：暂未支持
- [ ] 超时时间：暂未支持


## 添加协议

### 说明
**本段内容面向开发者，如不理解可跳过本段** 

若某项服务可用需要特殊的可用性检查逻辑，且无法通过通用协议支持实现（如动态解析内容并获取链接跳转）或当前协议暂未支持该判定特性时，可通过添加新的协议快速实现

### 编写
项目`.\protocol`中内置了一个demo协议
[demo.py](https://github.com/OREOCODEDEV/nonebot-plugin-servicestate/blob/main/nonebot_plugin_servicestate/protocol/demo.py)
实现了一个可用概率为随机的协议，你可以参照内部的注释，编写自己的自定义协议方法

下列步骤中默认均按照demo协议编写，如需要自定义协议请按照实际情况操作

### 注册
在`.\protocol\__init__.py`中导入需要注册的demo协议
```
from .demo import DEMOProtocol
```

### 使用
现在，你已经完成自定义协议的所有步骤，可直接使用你的自定义协议了

添加demo协议命令：`添加监控服务 DemoProtocol DemoName demo_url`

修改随机可用概率为 25% ：`修改监控服务 DemoName normal_rate 25`

修改为永远故障状态：`修改监控服务 DemoName always_malfunction True`

使用上述命令并通过`服务状态`命令观察它们的变化吧！



## Todo
- [x] 核心pydantic支持
- [ ] 支持更多配置字段
- [ ] 协议配置项合法检查接口支持
- [ ] 协议载入配置方法统一实现
- [ ] 协议必填配置项接口支持
- [ ] 鲁棒性增强
- [ ] 群组~~增删~~查改支持
- [ ] OneBotV11配置文件收发
- [ ] 不同用户监控服务绑定支持（咕咕咕
- [ ] 还有上面一大堆协议中暂未支持的内容
