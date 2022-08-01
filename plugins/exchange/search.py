"""
函数文件
"""
from typing import Coroutine, Iterable, Union
import httpx
from bs4 import BeautifulSoup
from logger import logger
from ..api import notify_bark
from .conf import SEARCH_URL, AVAILABLE_CURRENCY


async def get_exchange_rate(
        uid_dict: dict,
        currency: str) -> Union[Iterable[Coroutine], Coroutine]:
    """ 获取实时汇率

    :param uid_dict: 用户id字典
    :param currency: 货币名称

    :return: 调用通知api的函数
    """
    if not currency or \
            currency not in AVAILABLE_CURRENCY:
        logger.warning("所选的货币不支持:%s", currency)
        return None

    # 发送请求
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url=SEARCH_URL,
            data={
                "pjname": currency
            }
        )

    if resp and resp.status_code != 200:
        logger.error("获取汇率请求失败 %s", currency)

    # 解析html页面
    soup = BeautifulSoup(resp.text, "html.parser")
    html_div = soup.find("div", attrs={"class": ['BOC_main', 'publish']})
    if not html_div:
        logger.error("加载汇率页面失败 %s", currency)
        return None

    html_table = html_div.find("table")
    if not html_table:
        logger.error("加载汇率页面失败 %s", currency)
        return None

    # 获取汇率
    exchange_rate = float(html_table.findAll("tr")[1].text
                          .split("\n")[7][:-1])

    if exchange_rate > 100:
        exchange_rate = round(exchange_rate / 100, 2)
        base_cny = 100
    else:
        exchange_rate = round(100 / exchange_rate, 2)
        base_cny = 1

    # 构建回调函数
    callback_func = notify_bark(
        uuid=uid_dict.get("bark", {}).get("uuid"),
        content=f"{exchange_rate} / {base_cny}RMB",
        title=f"最新{currency}汇率",
    )

    return callback_func
