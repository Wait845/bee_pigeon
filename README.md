# Bee Pigeon
像配置crontab那样通知设备,支持插件扩展。目前已支持对[Bark](https://github.com/Finb/Bark)设备的通知，后续会增加对pushdeer, 企业微信等的支持。目前已自带两个插件：查询地区的实时天气 和 查询当前汇率。
> **Note**
>
> 使用查询天气插件时，需要在插件的conf.py里配置自己的key
# 配置
```Python3
# tasks.py
from plugins import weather, api, exchange


task_list = [
    {
        "schedule": "*/1 * * * *",
        "uid": [
            {
                "bark": {"uuid": "aaaaaaaaaaaaaaa"}
            }
        ],
        "function": exchange.get_exchange_rate,
        "args": ("英镑",),
        "kwargs": {}
    }
]
```
所有的task都放在task_list中，task_list是一个由字典组成的列表。

字典的属性有:
+ schedule: 字符串，crontab表达式
+ uid: 列表, 列表里的每个字典表示一个用户。因为一个用户可能会有多个设备，所以不同设备之间通过同一个字典进行关联。
+ function: 异步/同步函数，由插件提供。当有多个uid时，会创建多个函数，每个函数都会传入uid里的一个字典。是否通知一个uid字典的所有用户由函数决定。
+ args: 元组。包含函数的参数
+ kwargs: 字典。包含函数的参数


### 如果需要直接调用通知api，也可以按如下配置
```Python3
task_list = [
    {
        "schedule": "*/1 * * * *",
        "function": api.notify_bark,
        "args": (
            ["aaaaaaaaaaaaaaa","bbbbbbbbbbbbbbb"],
            "hello, test"),
        "kwargs": {}
    }
]
```
该配置表示同时对两个设备'aaa..'&'bbb..'调用bark通知api，并且发送内容为'hello, test'

# 插件
所有的插件都是一个Python包，放在plugins文件夹下。
每个包都包含'__init__.py'入口文件，'__version__.py'版本管理文件。以及开发者自定义的文件。如果需要将函数暴露的话，需要在'__init__.py'文件中引用:
```Python3
"""
exchange包入口文件
"""
from .__version__ import __title__, __description__, __version__
from .search import get_exchange_rate
```
函数可以是同步函数，也可以是异步函数。函数的入口必须包含一个字典类型的变量，这个参数对用户是不可见的。当脚步执行时，会自动将配置中uid里的字典传入函数。
```Python3
async def get_exchange_rate(
        uid_dict: dict,
        currency: str) -> Union[Iterable[Coroutine], Coroutine]:
```
函数可以不返回，也可以构建好api函数后返回，只支持异步函数。可以返回单个函数，也可以返回由函数组成的可迭代对象。返回的函数通常为调用通知的api,返回后脚步则会执行这些函数，对用户进行一个统一的推送。
```Python3
# 构建回调函数
callback_func = notify_bark(
    uuid=uid_dict.get("bark", {}).get("uuid"),
    content=f"{exchange_rate} / {base_cny}RMB",
    title=f"最新{currency}汇率",
)

return callback_func
```

# 部署
通过crontab部署
```Python3
* * * * * python bee_pigeon.py
```